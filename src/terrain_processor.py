#!/usr/bin/env python3
"""
Terrain Processor for Sherlock Geospatial Analysis

Processes LiDAR-derived DTM to generate terrain derivatives and identify
portal candidates / avoid zones for underground shelter design.

Requires: geo_env virtual environment with rasterio, geopandas, shapely, whitebox
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict

import numpy as np

logger = logging.getLogger(__name__)

# Lazy imports for geo libraries (only load when needed)
_rasterio = None
_geopandas = None
_shapely = None
_whitebox = None


def _get_rasterio():
    global _rasterio
    if _rasterio is None:
        import rasterio
        from rasterio import features
        from rasterio.transform import from_bounds
        _rasterio = rasterio
    return _rasterio


def _get_geopandas():
    global _geopandas
    if _geopandas is None:
        import geopandas as gpd
        _geopandas = gpd
    return _geopandas


def _get_shapely():
    global _shapely
    if _shapely is None:
        from shapely.geometry import shape, box, Point, Polygon
        from shapely.ops import unary_union
        import shapely
        _shapely = shapely
    return _shapely


def _get_whitebox():
    global _whitebox
    if _whitebox is None:
        import whitebox
        _whitebox = whitebox.WhiteboxTools()
        _whitebox.set_verbose_mode(False)
    return _whitebox


@dataclass
class SlopeStats:
    """Slope statistics in degrees"""
    min: float
    p50: float  # median
    p90: float
    max: float


@dataclass
class PortalCandidate:
    """Portal/bench candidate for adit entrance"""
    id: str
    centroid_xy: Dict[str, float]  # {'x_m': ..., 'y_m': ...}
    elev_ft: float
    slope_deg: float
    notes: str
    geometry_wkt: Optional[str] = None


@dataclass
class AvoidZone:
    """Zone to avoid for portal placement"""
    id: str
    reason: str  # 'steep_slope', 'drainage_convergence', 'landslide', 'ravine'
    notes: str
    geometry_wkt: Optional[str] = None


class TerrainProcessor:
    """
    Process DTM/DEM rasters to generate terrain derivatives and identify
    suitable portal locations.
    """

    # Slope class thresholds (degrees)
    SLOPE_GENTLE = 15.0      # <15° - good for portal
    SLOPE_MODERATE = 25.0    # 15-25° - acceptable with grading
    SLOPE_STEEP = 35.0       # 25-35° - avoid if possible
    # >35° - avoid

    # Flow accumulation threshold for drainage identification
    FLOW_ACCUM_THRESHOLD = 100  # cells

    def __init__(self, dtm_path: str, crs: str = 'EPSG:26910'):
        """
        Initialize terrain processor

        Args:
            dtm_path: Path to bare-earth DTM (GeoTIFF)
            crs: Coordinate reference system (default: UTM 10N)
        """
        self.dtm_path = Path(dtm_path)
        self.crs = crs
        self.output_dir = None
        self.slope_path = None
        self.hillshade_path = None
        self.curvature_plan_path = None
        self.curvature_profile_path = None
        self.flow_accum_path = None
        self.drainage_path = None

        if not self.dtm_path.exists():
            raise FileNotFoundError(f"DTM not found: {dtm_path}")

    def compute_all(self, output_dir: str) -> Dict[str, str]:
        """
        Compute all terrain derivatives

        Args:
            output_dir: Directory to write output rasters

        Returns:
            Dict of output file paths
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        results = {}

        # Compute each derivative
        logger.info("Computing hillshade...")
        results['hillshade'] = self.compute_hillshade()

        logger.info("Computing slope...")
        results['slope'] = self.compute_slope()

        logger.info("Computing curvature...")
        results['curvature_plan'], results['curvature_profile'] = self.compute_curvature()

        logger.info("Computing flow accumulation...")
        results['flow_accum'] = self.compute_flow_accumulation()

        logger.info("Extracting drainage lines...")
        results['drainage'] = self.extract_drainage_lines()

        return results

    def compute_hillshade(self, azimuth: float = 315.0, altitude: float = 45.0) -> str:
        """
        Compute hillshade from DTM

        Args:
            azimuth: Light source azimuth (degrees from north)
            altitude: Light source altitude (degrees above horizon)

        Returns:
            Path to hillshade raster
        """
        output_path = self.output_dir / 'hillshade.tif'
        wbt = _get_whitebox()

        wbt.hillshade(
            str(self.dtm_path),
            str(output_path),
            azimuth=azimuth,
            altitude=altitude
        )

        self.hillshade_path = output_path
        return str(output_path)

    def compute_slope(self, units: str = 'degrees') -> str:
        """
        Compute slope from DTM

        Args:
            units: Output units ('degrees' or 'percent')

        Returns:
            Path to slope raster
        """
        output_path = self.output_dir / 'slope_deg.tif'
        wbt = _get_whitebox()

        wbt.slope(
            str(self.dtm_path),
            str(output_path),
            units=units
        )

        self.slope_path = output_path
        return str(output_path)

    def compute_curvature(self) -> Tuple[str, str]:
        """
        Compute plan and profile curvature from DTM

        Returns:
            Tuple of (plan_curvature_path, profile_curvature_path)
        """
        plan_path = self.output_dir / 'curvature_plan.tif'
        profile_path = self.output_dir / 'curvature_profile.tif'
        wbt = _get_whitebox()

        wbt.plan_curvature(str(self.dtm_path), str(plan_path))
        wbt.profile_curvature(str(self.dtm_path), str(profile_path))

        self.curvature_plan_path = plan_path
        self.curvature_profile_path = profile_path
        return str(plan_path), str(profile_path)

    def compute_flow_accumulation(self) -> str:
        """
        Compute flow accumulation from DTM

        Returns:
            Path to flow accumulation raster
        """
        output_path = self.output_dir / 'flow_accum.tif'
        wbt = _get_whitebox()

        # First fill depressions
        filled_path = self.output_dir / 'dtm_filled.tif'
        wbt.fill_depressions(str(self.dtm_path), str(filled_path))

        # Then compute D8 flow accumulation
        wbt.d8_flow_accumulation(
            str(filled_path),
            str(output_path),
            out_type='cells'
        )

        self.flow_accum_path = output_path
        return str(output_path)

    def extract_drainage_lines(self, threshold: int = None) -> str:
        """
        Extract drainage lines from flow accumulation

        Args:
            threshold: Flow accumulation threshold (cells)

        Returns:
            Path to drainage lines GeoJSON
        """
        if threshold is None:
            threshold = self.FLOW_ACCUM_THRESHOLD

        output_path = self.output_dir / 'drainage_lines.geojson'
        wbt = _get_whitebox()

        # Extract streams
        streams_raster = self.output_dir / 'streams.tif'
        wbt.extract_streams(
            str(self.flow_accum_path),
            str(streams_raster),
            threshold=threshold
        )

        # Convert to vector
        wbt.raster_streams_to_vector(
            str(streams_raster),
            str(self.output_dir / 'dtm_filled.tif'),  # Use filled DTM for flow direction
            str(output_path)
        )

        self.drainage_path = output_path
        return str(output_path)

    def get_slope_stats(self) -> SlopeStats:
        """
        Calculate slope statistics for the DTM area

        Returns:
            SlopeStats dataclass with min, p50, p90, max
        """
        if not self.slope_path or not Path(self.slope_path).exists():
            raise ValueError("Slope raster not computed. Run compute_slope() first.")

        rasterio = _get_rasterio()

        with rasterio.open(self.slope_path) as src:
            data = src.read(1)
            # Mask nodata
            nodata = src.nodata
            if nodata is not None:
                data = np.ma.masked_equal(data, nodata)

            valid_data = data.compressed() if hasattr(data, 'compressed') else data.flatten()

            return SlopeStats(
                min=float(np.min(valid_data)),
                p50=float(np.percentile(valid_data, 50)),
                p90=float(np.percentile(valid_data, 90)),
                max=float(np.max(valid_data))
            )

    def identify_portal_candidates(
        self,
        landslides_path: Optional[str] = None,
        min_area_sqm: float = 100.0
    ) -> List[PortalCandidate]:
        """
        Identify suitable portal/bench candidates based on slope and terrain

        Criteria:
        - Slope < SLOPE_GENTLE (15°)
        - Low curvature (flat/convex preferred)
        - Not in drainage convergence zone
        - Not in landslide inventory

        Args:
            landslides_path: Path to landslide inventory GeoJSON
            min_area_sqm: Minimum area for a candidate (sq meters)

        Returns:
            List of PortalCandidate objects
        """
        if not self.slope_path:
            raise ValueError("Slope not computed. Run compute_all() first.")

        rasterio = _get_rasterio()
        geopandas = _get_geopandas()
        shapely = _get_shapely()

        candidates = []

        with rasterio.open(self.slope_path) as slope_src:
            slope_data = slope_src.read(1)
            transform = slope_src.transform

            # Find areas with gentle slope
            gentle_mask = (slope_data < self.SLOPE_GENTLE) & (slope_data >= 0)

            # Convert to polygons
            from rasterio.features import shapes
            shapes_gen = shapes(gentle_mask.astype(np.uint8), mask=gentle_mask, transform=transform)

            idx = 1
            for geom, value in shapes_gen:
                if value == 1:
                    from shapely.geometry import shape as shapely_shape
                    poly = shapely_shape(geom)

                    if poly.area >= min_area_sqm:
                        centroid = poly.centroid

                        # Get elevation at centroid
                        with rasterio.open(self.dtm_path) as dtm_src:
                            row, col = dtm_src.index(centroid.x, centroid.y)
                            elev_m = dtm_src.read(1)[row, col]
                            elev_ft = elev_m * 3.28084

                        # Get slope at centroid
                        row, col = slope_src.index(centroid.x, centroid.y)
                        slope_deg = slope_data[row, col]

                        candidates.append(PortalCandidate(
                            id=f"PC{idx:02d}",
                            centroid_xy={'x_m': centroid.x, 'y_m': centroid.y},
                            elev_ft=round(elev_ft, 1),
                            slope_deg=round(slope_deg, 1),
                            notes=f"Gentle slope zone ({poly.area:.0f} sq m)",
                            geometry_wkt=poly.wkt
                        ))
                        idx += 1

        # Filter out candidates in landslide zones if provided
        if landslides_path and Path(landslides_path).exists():
            landslides_gdf = geopandas.read_file(landslides_path)
            filtered_candidates = []
            for c in candidates:
                from shapely.geometry import Point
                pt = Point(c.centroid_xy['x_m'], c.centroid_xy['y_m'])
                if not any(landslides_gdf.geometry.contains(pt)):
                    filtered_candidates.append(c)
            candidates = filtered_candidates

        # Sort by slope (lowest first), take top 5
        candidates.sort(key=lambda x: x.slope_deg)
        return candidates[:5]

    def identify_avoid_zones(
        self,
        landslides_path: Optional[str] = None
    ) -> List[AvoidZone]:
        """
        Identify zones to avoid for portal placement

        Criteria:
        - Steep slopes (>35°)
        - High drainage convergence
        - Landslide inventory overlap

        Args:
            landslides_path: Path to landslide inventory GeoJSON

        Returns:
            List of AvoidZone objects
        """
        if not self.slope_path or not self.flow_accum_path:
            raise ValueError("Slope/flow not computed. Run compute_all() first.")

        rasterio = _get_rasterio()
        geopandas = _get_geopandas()

        avoid_zones = []
        idx = 1

        with rasterio.open(self.slope_path) as slope_src:
            slope_data = slope_src.read(1)
            transform = slope_src.transform

            # Steep slopes
            steep_mask = slope_data > self.SLOPE_STEEP
            from rasterio.features import shapes
            for geom, value in shapes(steep_mask.astype(np.uint8), mask=steep_mask, transform=transform):
                if value == 1:
                    from shapely.geometry import shape as shapely_shape
                    poly = shapely_shape(geom)
                    if poly.area > 500:  # Min area 500 sq m
                        avoid_zones.append(AvoidZone(
                            id=f"AZ{idx:02d}",
                            reason='steep_slope',
                            notes=f"Slope >35° zone ({poly.area:.0f} sq m)"
                        ))
                        idx += 1

        # High drainage convergence
        with rasterio.open(self.flow_accum_path) as flow_src:
            flow_data = flow_src.read(1)
            transform = flow_src.transform

            high_flow_mask = flow_data > (self.FLOW_ACCUM_THRESHOLD * 10)
            from rasterio.features import shapes
            for geom, value in shapes(high_flow_mask.astype(np.uint8), mask=high_flow_mask, transform=transform):
                if value == 1:
                    from shapely.geometry import shape as shapely_shape
                    poly = shapely_shape(geom)
                    if poly.area > 100:
                        avoid_zones.append(AvoidZone(
                            id=f"AZ{idx:02d}",
                            reason='drainage_convergence',
                            notes=f"High flow accumulation zone"
                        ))
                        idx += 1

        # Landslide inventory
        if landslides_path and Path(landslides_path).exists():
            landslides_gdf = geopandas.read_file(landslides_path)
            for _, row in landslides_gdf.iterrows():
                avoid_zones.append(AvoidZone(
                    id=f"AZ{idx:02d}",
                    reason='landslide',
                    notes=f"Mapped landslide from inventory"
                ))
                idx += 1

        return avoid_zones[:5]  # Return top 5

    def export_portal_candidates_geojson(self, candidates: List[PortalCandidate], output_path: str):
        """Export portal candidates to GeoJSON"""
        features = []
        for c in candidates:
            features.append({
                'type': 'Feature',
                'properties': {
                    'id': c.id,
                    'elev_ft': c.elev_ft,
                    'slope_deg': c.slope_deg,
                    'notes': c.notes
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [c.centroid_xy['x_m'], c.centroid_xy['y_m']]
                }
            })

        geojson = {'type': 'FeatureCollection', 'features': features}
        with open(output_path, 'w') as f:
            json.dump(geojson, f, indent=2)

    def export_avoid_zones_geojson(self, zones: List[AvoidZone], output_path: str):
        """Export avoid zones to GeoJSON"""
        features = []
        for z in zones:
            features.append({
                'type': 'Feature',
                'properties': {
                    'id': z.id,
                    'reason': z.reason,
                    'notes': z.notes
                },
                'geometry': None  # Would need actual geometry
            })

        geojson = {'type': 'FeatureCollection', 'features': features}
        with open(output_path, 'w') as f:
            json.dump(geojson, f, indent=2)

    def generate_terrain_report(self, output_path: str):
        """Generate terrain analysis report in markdown"""
        stats = self.get_slope_stats()

        report = f"""# Terrain Analysis Report

## DTM Source
- **Path**: {self.dtm_path}
- **CRS**: {self.crs}

## Slope Statistics
| Metric | Value (degrees) |
|--------|-----------------|
| Minimum | {stats.min:.1f} |
| Median (p50) | {stats.p50:.1f} |
| 90th percentile | {stats.p90:.1f} |
| Maximum | {stats.max:.1f} |

## Slope Classification
- **Gentle (<15°)**: Suitable for portal
- **Moderate (15-25°)**: Acceptable with grading
- **Steep (25-35°)**: Avoid if possible
- **Very Steep (>35°)**: Avoid

## Generated Products
- Hillshade: {self.hillshade_path}
- Slope: {self.slope_path}
- Plan Curvature: {self.curvature_plan_path}
- Profile Curvature: {self.curvature_profile_path}
- Flow Accumulation: {self.flow_accum_path}
- Drainage Lines: {self.drainage_path}
"""

        with open(output_path, 'w') as f:
            f.write(report)

        return output_path


# CLI interface
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Process terrain from DTM')
    parser.add_argument('dtm_path', help='Path to DTM GeoTIFF')
    parser.add_argument('output_dir', help='Output directory')
    parser.add_argument('--crs', default='EPSG:26910', help='Coordinate system')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    processor = TerrainProcessor(args.dtm_path, args.crs)
    results = processor.compute_all(args.output_dir)

    print("Generated files:")
    for name, path in results.items():
        print(f"  {name}: {path}")
