#!/usr/bin/env python3
"""
Geology Summarizer for Sherlock Geospatial Analysis

Summarizes geologic context for site characterization from USGS geologic maps.
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class GeologyUnit:
    """Geologic unit information"""
    symbol: str           # Map symbol (e.g., "Qal", "Tcr")
    name: str             # Full name
    age: str              # Geologic age
    lithology: str        # Rock/sediment type
    competence: str       # 'high', 'medium', 'low', 'variable'
    permeability: str     # 'high', 'medium', 'low'
    tunneling_notes: str  # Notes for underground construction


@dataclass
class GeologySummary:
    """Summary of geologic conditions at site"""
    units_at_site: List[GeologyUnit]
    dominant_unit: str
    faults_nearby: List[Dict[str, Any]]
    structural_notes: str
    groundwater_implications: str
    tunneling_recommendations: str
    confidence: str  # 'high', 'medium', 'low'


class GeologySummarizer:
    """
    Summarize geologic conditions for site characterization.
    """

    # Common geologic unit classifications for Pacific Northwest
    UNIT_LIBRARY = {
        # Quaternary
        'Qal': GeologyUnit('Qal', 'Quaternary Alluvium', 'Holocene', 'Sand, gravel, silt', 'low', 'high', 'Requires ground support; water likely'),
        'Qls': GeologyUnit('Qls', 'Quaternary Landslide', 'Holocene', 'Displaced debris', 'low', 'variable', 'AVOID - unstable material'),
        'Qvl': GeologyUnit('Qvl', 'Quaternary Volcanic Lahar', 'Pleistocene', 'Volcanic debris', 'medium', 'medium', 'Variable conditions; may be cemented'),
        'Qgt': GeologyUnit('Qgt', 'Quaternary Glacial Till', 'Pleistocene', 'Unsorted sediment', 'low', 'low', 'Dense but not rock; support needed'),

        # Tertiary Volcanics
        'Tcr': GeologyUnit('Tcr', 'Columbia River Basalt', 'Miocene', 'Basalt flows', 'high', 'low', 'Excellent tunnel rock; jointing controls'),
        'Tv': GeologyUnit('Tv', 'Tertiary Volcanic Rocks', 'Tertiary', 'Mixed volcanics', 'medium-high', 'variable', 'Generally good; check weathering'),
        'Tvc': GeologyUnit('Tvc', 'Volcanic Conglomerate', 'Tertiary', 'Volcanic debris', 'medium', 'medium', 'Cemented; may be tunnelable'),

        # Other
        'Ks': GeologyUnit('Ks', 'Cretaceous Sandstone', 'Cretaceous', 'Sandstone', 'medium-high', 'medium', 'Good tunnel rock if not weathered'),
    }

    def __init__(self):
        self.geology_gdf = None

    def load_geology(self, geopackage_path: str, aoi_geojson: Optional[Dict] = None):
        """
        Load geology from GeoPackage or Shapefile

        Args:
            geopackage_path: Path to geology GeoPackage/shapefile
            aoi_geojson: Optional AOI to clip to
        """
        import geopandas as gpd

        self.geology_gdf = gpd.read_file(geopackage_path)

        if aoi_geojson:
            from shapely.geometry import shape
            aoi_geom = shape(aoi_geojson['geometry'])
            self.geology_gdf = self.geology_gdf[self.geology_gdf.intersects(aoi_geom)]

    def summarize_at_site(
        self,
        site_lat: float,
        site_lon: float,
        buffer_m: float = 500.0
    ) -> GeologySummary:
        """
        Summarize geologic conditions at site

        Args:
            site_lat: Site latitude
            site_lon: Site longitude
            buffer_m: Buffer around site to check (meters)

        Returns:
            GeologySummary with units, faults, and recommendations
        """
        from shapely.geometry import Point

        site_point = Point(site_lon, site_lat)

        units_found = []
        faults_found = []

        if self.geology_gdf is not None:
            # Find units at site
            for _, row in self.geology_gdf.iterrows():
                if row.geometry.contains(site_point) or row.geometry.distance(site_point) < 0.001:
                    symbol = row.get('PTYPE', row.get('symbol', row.get('SYMBOL', 'UNK')))
                    unit = self._lookup_unit(symbol, row)
                    units_found.append(unit)

            # Find nearby faults
            site_buffer = site_point.buffer(buffer_m / 111000)  # Rough degree conversion
            for _, row in self.geology_gdf.iterrows():
                geom_type = row.geometry.geom_type
                if geom_type in ['LineString', 'MultiLineString']:
                    if row.geometry.intersects(site_buffer):
                        faults_found.append({
                            'type': row.get('FTYPE', 'unknown'),
                            'name': row.get('NAME', 'Unnamed'),
                            'distance_m': site_point.distance(row.geometry) * 111000
                        })

        if not units_found:
            # Return default if no data
            return GeologySummary(
                units_at_site=[],
                dominant_unit='Unknown',
                faults_nearby=[],
                structural_notes='No geologic mapping available at site',
                groundwater_implications='Unknown - requires field investigation',
                tunneling_recommendations='Geophysical survey required before design',
                confidence='low'
            )

        dominant = units_found[0] if units_found else None

        return GeologySummary(
            units_at_site=units_found,
            dominant_unit=dominant.name if dominant else 'Unknown',
            faults_nearby=faults_found,
            structural_notes=self._generate_structural_notes(units_found, faults_found),
            groundwater_implications=self._assess_groundwater(units_found),
            tunneling_recommendations=self._generate_tunnel_recommendations(units_found, faults_found),
            confidence='medium' if units_found else 'low'
        )

    def _lookup_unit(self, symbol: str, row: Any) -> GeologyUnit:
        """Look up unit in library or create from row data"""
        if symbol in self.UNIT_LIBRARY:
            return self.UNIT_LIBRARY[symbol]

        # Create from row data
        return GeologyUnit(
            symbol=symbol,
            name=row.get('GMAP_UNIT', row.get('name', symbol)),
            age=row.get('AGE', 'Unknown'),
            lithology=row.get('ROCKTYPE', row.get('description', 'Unknown')),
            competence='unknown',
            permeability='unknown',
            tunneling_notes='Site-specific investigation required'
        )

    def _generate_structural_notes(
        self,
        units: List[GeologyUnit],
        faults: List[Dict]
    ) -> str:
        """Generate structural geology notes"""
        notes = []

        if faults:
            notes.append(f"{len(faults)} fault(s) within 500m of site")
            for f in faults[:3]:
                notes.append(f"  - {f['type']}: {f['name']} ({f['distance_m']:.0f}m away)")

        for unit in units:
            if 'basalt' in unit.lithology.lower():
                notes.append("Basalt: expect columnar jointing, may control water flow")
            if 'landslide' in unit.name.lower():
                notes.append("CAUTION: Site within mapped landslide deposit")

        return '\n'.join(notes) if notes else 'No significant structural concerns identified'

    def _assess_groundwater(self, units: List[GeologyUnit]) -> str:
        """Assess groundwater implications"""
        assessments = []

        for unit in units:
            if unit.permeability == 'high':
                assessments.append(f"{unit.symbol}: High permeability - expect water inflow")
            elif unit.permeability == 'low':
                assessments.append(f"{unit.symbol}: Low permeability - may act as aquitard")

        if not assessments:
            return "Groundwater conditions unknown - piezometer installation recommended"

        return '\n'.join(assessments)

    def _generate_tunnel_recommendations(
        self,
        units: List[GeologyUnit],
        faults: List[Dict]
    ) -> str:
        """Generate tunneling recommendations"""
        recommendations = []

        # Check for problem units
        for unit in units:
            if 'landslide' in unit.name.lower():
                recommendations.append("CRITICAL: Avoid tunneling through landslide deposit")
            if 'alluvium' in unit.name.lower() or unit.competence == 'low':
                recommendations.append("Ground support (steel sets or shotcrete) required through overburden")
            if unit.competence == 'high':
                recommendations.append(f"Favorable rock conditions in {unit.symbol}")

        # Check faults
        if faults:
            closest = min(faults, key=lambda f: f['distance_m'])
            if closest['distance_m'] < 100:
                recommendations.append(f"CAUTION: Fault within 100m - may affect rock quality and water")

        if not recommendations:
            recommendations.append("Site-specific investigation required for tunnel design")

        return '\n'.join(recommendations)

    def generate_geology_report(self, summary: GeologySummary, output_path: str):
        """Generate geology report in markdown"""
        units_table = ""
        for unit in summary.units_at_site:
            units_table += f"| {unit.symbol} | {unit.name} | {unit.age} | {unit.competence} |\n"

        report = f"""# Geology Analysis Report

## Confidence Level
**{summary.confidence.upper()}**

## Geologic Units at Site
| Symbol | Name | Age | Competence |
|--------|------|-----|------------|
{units_table if units_table else '| - | No units mapped | - | - |'}

## Dominant Unit
{summary.dominant_unit}

## Structural Notes
{summary.structural_notes}

## Groundwater Implications
{summary.groundwater_implications}

## Tunneling Recommendations
{summary.tunneling_recommendations}

## Nearby Faults
{json.dumps(summary.faults_nearby, indent=2) if summary.faults_nearby else 'None identified within 500m'}
"""

        with open(output_path, 'w') as f:
            f.write(report)

        return output_path
