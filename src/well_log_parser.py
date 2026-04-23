#!/usr/bin/env python3
"""
Well Log Parser for Sherlock Geospatial Analysis

Parses WA Ecology well logs to extract lithology and estimate depth-to-bedrock.
"""
import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import csv
import math

logger = logging.getLogger(__name__)


@dataclass
class LithologyInterval:
    """Single lithology interval from a well log"""
    top_ft: float
    bottom_ft: float
    description: str
    material_type: str  # 'clay', 'sand', 'gravel', 'rock', 'other'
    is_refusal: bool = False  # True if drilling stopped here


@dataclass
class WellRecord:
    """Parsed well log record"""
    well_id: str
    lat: float
    lon: float
    ground_elev_ft: float
    total_depth_ft: float
    static_water_level_ft: Optional[float]
    lithology: List[LithologyInterval]
    inferred_bedrock_depth_ft: Optional[float]
    clay_thickness_ft: Optional[float]
    data_quality: str  # 'good', 'fair', 'poor'
    notes: str


@dataclass
class BedrockEnvelope:
    """Bedrock depth envelope estimate"""
    min_ft: float
    likely_ft: float
    max_ft: float
    confidence_0to1: float
    nearest_wells: List[str]
    rationale: str


class WellLogParser:
    """
    Parse WA Ecology well logs and estimate bedrock depth envelope.
    """

    # Keywords indicating bedrock/refusal
    BEDROCK_KEYWORDS = [
        'bedrock', 'rock', 'basalt', 'granite', 'sandstone', 'shale',
        'refusal', 'refused', 'hard', 'solid rock', 'boulder', 'boulders',
        'cobbles', 'hardpan', 'cemented'
    ]

    # Keywords indicating clay
    CLAY_KEYWORDS = [
        'clay', 'silt', 'silty', 'clayey', 'mud', 'glacial', 'till',
        'lacustrine', 'alluvium', 'colluvium'
    ]

    def __init__(self):
        self.wells: List[WellRecord] = []

    def parse_csv(self, csv_path: str) -> List[WellRecord]:
        """
        Parse wells from CSV file

        Expected columns: well_id, lat, lon, drilled_depth_ft, static_water_level_ft
        """
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    record = WellRecord(
                        well_id=str(row.get('well_id', '')),
                        lat=float(row.get('lat', 0) or 0),
                        lon=float(row.get('lon', 0) or 0),
                        ground_elev_ft=0.0,  # Will be populated from DTM
                        total_depth_ft=float(row.get('drilled_depth_ft', 0) or 0),
                        static_water_level_ft=self._parse_float(row.get('static_water_level_ft')),
                        lithology=[],
                        inferred_bedrock_depth_ft=None,
                        clay_thickness_ft=None,
                        data_quality='fair',
                        notes=''
                    )
                    self.wells.append(record)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing well row: {e}")

        return self.wells

    def parse_pdf_text(self, text: str, well_id: str) -> Optional[WellRecord]:
        """
        Parse lithology from extracted PDF text

        This is a simplified parser - actual WA Ecology PDFs have specific formats.
        """
        lines = text.split('\n')
        lithology = []

        # Look for depth-description patterns like "10-25 ft: brown clay"
        depth_pattern = re.compile(r'(\d+\.?\d*)\s*[-–to]+\s*(\d+\.?\d*)\s*(ft|feet|\')?:?\s*(.+)', re.I)

        for line in lines:
            match = depth_pattern.match(line.strip())
            if match:
                top = float(match.group(1))
                bottom = float(match.group(2))
                desc = match.group(4).strip()

                material = self._classify_material(desc)
                is_refusal = any(kw in desc.lower() for kw in ['refusal', 'refused', 'rock', 'bedrock'])

                lithology.append(LithologyInterval(
                    top_ft=top,
                    bottom_ft=bottom,
                    description=desc,
                    material_type=material,
                    is_refusal=is_refusal
                ))

        if not lithology:
            return None

        # Infer bedrock depth
        bedrock_depth = None
        clay_thickness = 0.0
        for interval in lithology:
            if interval.is_refusal or interval.material_type == 'rock':
                bedrock_depth = interval.top_ft
                break
            if interval.material_type == 'clay':
                clay_thickness += (interval.bottom_ft - interval.top_ft)

        return WellRecord(
            well_id=well_id,
            lat=0.0,
            lon=0.0,
            ground_elev_ft=0.0,
            total_depth_ft=max(i.bottom_ft for i in lithology) if lithology else 0.0,
            static_water_level_ft=None,
            lithology=lithology,
            inferred_bedrock_depth_ft=bedrock_depth,
            clay_thickness_ft=clay_thickness if clay_thickness > 0 else None,
            data_quality='fair',
            notes=f"Parsed from PDF, {len(lithology)} intervals"
        )

    def _classify_material(self, description: str) -> str:
        """Classify material type from description"""
        desc_lower = description.lower()

        if any(kw in desc_lower for kw in self.BEDROCK_KEYWORDS):
            return 'rock'
        elif any(kw in desc_lower for kw in ['sand', 'sandy', 'gravel', 'gravelly']):
            return 'sand' if 'sand' in desc_lower else 'gravel'
        elif any(kw in desc_lower for kw in self.CLAY_KEYWORDS):
            return 'clay'
        else:
            return 'other'

    def _parse_float(self, value: Any) -> Optional[float]:
        """Safely parse float, return None if invalid"""
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def join_ground_elevations(self, dtm_path: str):
        """
        Join ground elevations from DTM at well coordinates

        Requires: geo_env with rasterio
        """
        import rasterio

        with rasterio.open(dtm_path) as src:
            for well in self.wells:
                if well.lat and well.lon:
                    try:
                        # Transform lat/lon to raster coordinates
                        row, col = src.index(well.lon, well.lat)
                        elev_m = src.read(1)[row, col]
                        well.ground_elev_ft = elev_m * 3.28084
                    except Exception as e:
                        logger.warning(f"Could not get elevation for well {well.well_id}: {e}")

    def compute_bedrock_envelope(
        self,
        site_lat: float,
        site_lon: float,
        max_distance_miles: float = 3.0
    ) -> BedrockEnvelope:
        """
        Compute bedrock depth envelope at site based on nearby wells

        Args:
            site_lat: Site latitude
            site_lon: Site longitude
            max_distance_miles: Maximum distance to consider wells

        Returns:
            BedrockEnvelope with min/likely/max depths and confidence
        """
        nearby_wells = []

        for well in self.wells:
            if well.lat and well.lon:
                dist = self._haversine_miles(site_lat, site_lon, well.lat, well.lon)
                if dist <= max_distance_miles:
                    nearby_wells.append((well, dist))

        if not nearby_wells:
            return BedrockEnvelope(
                min_ft=0.0,
                likely_ft=0.0,
                max_ft=0.0,
                confidence_0to1=0.0,
                nearest_wells=[],
                rationale="No wells found within search radius"
            )

        # Sort by distance
        nearby_wells.sort(key=lambda x: x[1])

        # Collect bedrock depth estimates
        depths = []
        nearest_ids = []
        for well, dist in nearby_wells[:10]:  # Use closest 10
            nearest_ids.append(well.well_id)
            if well.inferred_bedrock_depth_ft:
                depths.append(well.inferred_bedrock_depth_ft)
            elif well.total_depth_ft > 0:
                # If no bedrock hit, use total depth as minimum estimate
                depths.append(well.total_depth_ft)

        if not depths:
            # Use total depths as rough estimates
            depths = [w.total_depth_ft for w, d in nearby_wells if w.total_depth_ft > 0]

        if not depths:
            return BedrockEnvelope(
                min_ft=0.0,
                likely_ft=0.0,
                max_ft=0.0,
                confidence_0to1=0.1,
                nearest_wells=nearest_ids,
                rationale="Wells found but no depth data available"
            )

        min_depth = min(depths)
        max_depth = max(depths)
        likely_depth = sum(depths) / len(depths)

        # Confidence based on:
        # - Number of wells (more = higher)
        # - Distance to nearest well (closer = higher)
        # - Spread of estimates (smaller = higher)
        n_wells = len(depths)
        nearest_dist = nearby_wells[0][1]
        spread = max_depth - min_depth

        conf_wells = min(n_wells / 10, 1.0) * 0.4
        conf_dist = max(1 - nearest_dist / max_distance_miles, 0) * 0.3
        conf_spread = max(1 - spread / 100, 0) * 0.3

        confidence = conf_wells + conf_dist + conf_spread

        rationale = (
            f"Based on {n_wells} wells within {max_distance_miles} mi. "
            f"Nearest well: {nearby_wells[0][0].well_id} at {nearest_dist:.1f} mi. "
            f"Depth range: {min_depth:.0f}-{max_depth:.0f} ft."
        )

        return BedrockEnvelope(
            min_ft=round(min_depth, 1),
            likely_ft=round(likely_depth, 1),
            max_ft=round(max_depth, 1),
            confidence_0to1=round(confidence, 2),
            nearest_wells=nearest_ids[:5],
            rationale=rationale
        )

    def _haversine_miles(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance in miles between two points"""
        R = 3958.8  # Earth radius in miles

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c

    def export_wells_csv(self, output_path: str):
        """Export parsed wells to CSV"""
        fieldnames = [
            'well_id', 'lat', 'lon', 'ground_elev_ft', 'total_depth_ft',
            'static_water_level_ft', 'inferred_bedrock_depth_ft',
            'clay_thickness_ft', 'data_quality', 'notes'
        ]

        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for well in self.wells:
                writer.writerow({
                    'well_id': well.well_id,
                    'lat': well.lat,
                    'lon': well.lon,
                    'ground_elev_ft': well.ground_elev_ft,
                    'total_depth_ft': well.total_depth_ft,
                    'static_water_level_ft': well.static_water_level_ft,
                    'inferred_bedrock_depth_ft': well.inferred_bedrock_depth_ft,
                    'clay_thickness_ft': well.clay_thickness_ft,
                    'data_quality': well.data_quality,
                    'notes': well.notes
                })

    def generate_subsurface_report(self, envelope: BedrockEnvelope, output_path: str):
        """Generate subsurface analysis report in markdown"""
        report = f"""# Subsurface Analysis Report

## Data Summary
- **Wells analyzed**: {len(self.wells)}
- **Confidence**: {envelope.confidence_0to1:.0%}

## Bedrock Depth Envelope
| Estimate | Depth (ft) |
|----------|------------|
| Minimum | {envelope.min_ft:.1f} |
| Likely | {envelope.likely_ft:.1f} |
| Maximum | {envelope.max_ft:.1f} |

## Nearest Wells Referenced
{chr(10).join(f'- {w}' for w in envelope.nearest_wells)}

## Rationale
{envelope.rationale}

## Data Quality Notes
- Wells with bedrock/refusal data provide highest confidence
- Wells that ended in overburden only provide minimum depth estimate
- Interpolation uncertainty increases with distance from wells
"""

        with open(output_path, 'w') as f:
            f.write(report)

        return output_path
