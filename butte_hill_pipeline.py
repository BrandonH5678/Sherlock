#!/usr/bin/env python3
"""
Butte Hill Site Characterization Pipeline

End-to-end orchestration for geospatial data retrieval and analysis
to produce FreeCAD-ready design inputs for underground shelter design.

Project: ButteHill_Bedrock_Characterization
Site: 210 Lahti Rd, Woodland WA 98674

Usage:
    # Activate geo_env first:
    source /home/johnny5/Sherlock/geo_env/bin/activate

    # Run full pipeline:
    python butte_hill_pipeline.py --full

    # Run with constraint enforcement:
    python butte_hill_pipeline.py --full --constraints evidence/butte_hill/design_inputs/constraints.json

    # Run specific phases:
    python butte_hill_pipeline.py --retriever-only
    python butte_hill_pipeline.py --sherlock-only
    python butte_hill_pipeline.py --freecad-only
"""
import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add paths
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, '/home/johnny5/Johny5Alive/j5a-nightshift/ops/fetchers')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('butte_hill_pipeline')

# Project configuration
PROJECT_CONFIG = {
    'project': 'ButteHill_Bedrock_Characterization',
    'site_address': '210 Lahti Rd, Woodland WA 98674',
    'aoi_radius_miles': 1.5,
    'terrain_radius_miles': 2.0,
    'well_radius_miles': 3.0,
    'well_radius_expand_miles': 5.0,
    'min_wells': 20,
    'crs_working': 'EPSG:26910',
    'crs_storage': 'EPSG:4326',
}

# Directory structure
DIRS = {
    'downloads_lidar': '/home/johnny5/Sherlock/downloads/butte_hill/lidar',
    'downloads_wells': '/home/johnny5/Sherlock/downloads/butte_hill/wells',
    'downloads_geology': '/home/johnny5/Sherlock/downloads/butte_hill/geology',
    'downloads_landslides': '/home/johnny5/Sherlock/downloads/butte_hill/landslides',
    'evidence_rasters': '/home/johnny5/Sherlock/evidence/butte_hill/rasters',
    'evidence_vectors': '/home/johnny5/Sherlock/evidence/butte_hill/vectors',
    'evidence_tables': '/home/johnny5/Sherlock/evidence/butte_hill/tables',
    'design_inputs': '/home/johnny5/Sherlock/evidence/butte_hill/design_inputs',
    'analysis': '/home/johnny5/Sherlock/analysis/butte_hill',
    'logs': '/home/johnny5/Sherlock/logs/butte_hill',
    'schemas': '/home/johnny5/Sherlock/schemas',
}


class ButteHillPipeline:
    """
    End-to-end pipeline for Butte Hill site characterization.
    """

    def __init__(self, config: Dict[str, Any] = None, constraints_path: str = None):
        self.config = config or PROJECT_CONFIG
        self.site_data = {}
        self.retriever_results = {}
        self.sherlock_results = {}
        self.freecad_inputs = None
        self.constraints_path = constraints_path
        self.constraint_enforcer = None
        self.stage_gate_status = None

        # Load constraints if provided
        if constraints_path and Path(constraints_path).exists():
            try:
                from constraint_enforcer import ConstraintEnforcer
                self.constraint_enforcer = ConstraintEnforcer(constraints_path)
                logger.info(f"Loaded constraints: {constraints_path}")
            except Exception as e:
                logger.warning(f"Could not load constraints: {e}")

        # Ensure directories exist
        for dir_path in DIRS.values():
            Path(dir_path).mkdir(parents=True, exist_ok=True)

    def run_full_pipeline(self) -> Dict[str, Any]:
        """Run complete pipeline: Retriever → Sherlock → FreeCAD"""
        logger.info("=" * 60)
        logger.info("BUTTE HILL SITE CHARACTERIZATION PIPELINE")
        logger.info("=" * 60)

        try:
            # Phase 1: Retriever
            logger.info("\n" + "=" * 40)
            logger.info("PHASE 1: DATA RETRIEVAL")
            logger.info("=" * 40)
            self.run_retriever_tasks()

            # Phase 2: Sherlock Analysis
            logger.info("\n" + "=" * 40)
            logger.info("PHASE 2: SHERLOCK ANALYSIS")
            logger.info("=" * 40)
            self.run_sherlock_tasks()

            # Phase 2.5: Constraint Enforcement
            if self.constraint_enforcer:
                logger.info("\n" + "=" * 40)
                logger.info("PHASE 2.5: CONSTRAINT ENFORCEMENT")
                logger.info("=" * 40)
                self.enforce_constraints()

            # Phase 3: FreeCAD Output
            logger.info("\n" + "=" * 40)
            logger.info("PHASE 3: FREECAD OUTPUT")
            logger.info("=" * 40)

            # Check if FreeCAD generation is allowed
            if self.stage_gate_status and not self.stage_gate_status.freecad_generation_allowed:
                logger.warning("STAGE GATE BLOCKED: FreeCAD generation halted")
                logger.warning(f"Blocking conditions: {self.stage_gate_status.blocking_conditions}")
                logger.warning(f"Required next data: {self.stage_gate_status.required_next_data}")
            else:
                self.generate_freecad_outputs()

            # Summary
            logger.info("\n" + "=" * 60)
            logger.info("PIPELINE COMPLETE")
            logger.info("=" * 60)
            self.print_summary()

            return {
                'success': True,
                'retriever': self.retriever_results,
                'sherlock': self.sherlock_results,
                'freecad_inputs': str(DIRS['design_inputs'] + '/freecad_site_inputs.json'),
                'freecad_macro': str(DIRS['design_inputs'] + '/butte_hill.FCMacro')
            }

        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    # =========================================================================
    # PHASE 1: RETRIEVER TASKS (R1-R7)
    # =========================================================================

    def run_retriever_tasks(self):
        """Execute Retriever tasks R1-R7"""
        try:
            from j5a_retrieval_gateway import J5ARetrievalGateway
            gateway = J5ARetrievalGateway()
        except ImportError:
            logger.warning("J5A Gateway not available - using mock data")
            self._run_retriever_mock()
            return

        # R1: Geocode site
        logger.info("R1: Geocoding site address...")
        try:
            geocode_result = gateway.geocode_address(
                self.config['site_address'],
                self.config['aoi_radius_miles']
            )
            if geocode_result.get('meta', {}).get('success'):
                self.site_data = geocode_result.get('data', {})
                self.retriever_results['R1_geocode'] = 'success'
                logger.info(f"  Site coordinates: {self.site_data.get('lat')}, {self.site_data.get('lon')}")
            else:
                raise ValueError("Geocoding failed")
        except Exception as e:
            logger.warning(f"  Geocoding failed: {e} - using fallback coordinates")
            # Fallback: approximate coordinates for 210 Lahti Rd, Woodland WA
            self.site_data = {
                'lat': 45.9067,
                'lon': -122.7700,
                'address': self.config['site_address']
            }
            self.retriever_results['R1_geocode'] = 'fallback'

        lat = self.site_data['lat']
        lon = self.site_data['lon']

        # R2: WA DNR LiDAR
        logger.info("R2: Querying WA DNR LiDAR Portal...")
        try:
            lidar_result = gateway.retrieve_lidar(
                lat, lon,
                radius_miles=self.config['terrain_radius_miles'],
                output_dir=DIRS['downloads_lidar'],
                download=False  # Just query for now
            )
            self.retriever_results['R2_lidar'] = lidar_result.get('data', {})
            tiles = lidar_result.get('data', {}).get('tiles_found', 0)
            logger.info(f"  Found {tiles} LiDAR tiles")
        except Exception as e:
            logger.warning(f"  LiDAR query failed: {e}")
            self.retriever_results['R2_lidar'] = {'error': str(e)}

        # R3: USGS 3DEP fallback (if needed)
        if self.retriever_results.get('R2_lidar', {}).get('tiles_found', 0) == 0:
            logger.info("R3: Querying USGS 3DEP as fallback...")
            try:
                dep_result = gateway.retrieve_geospatial({
                    'type': 'geospatial',
                    'source': 'usgs_3dep',
                    'aoi': {'lat': lat, 'lon': lon, 'radius_miles': 2.0},
                    'output_dir': DIRS['downloads_lidar']
                })
                self.retriever_results['R3_3dep'] = dep_result.get('data', {})
            except Exception as e:
                logger.warning(f"  3DEP query failed: {e}")
                self.retriever_results['R3_3dep'] = {'error': str(e)}

        # R4: Well logs
        logger.info("R4: Querying WA Ecology well logs...")
        try:
            wells_result = gateway.retrieve_wells(
                lat, lon,
                radius_miles=self.config['well_radius_miles'],
                min_wells=self.config['min_wells'],
                output_dir=DIRS['downloads_wells']
            )
            self.retriever_results['R4_wells'] = wells_result.get('data', {})
            well_count = wells_result.get('data', {}).get('wells_found', 0)
            logger.info(f"  Found {well_count} wells")
        except Exception as e:
            logger.warning(f"  Well query failed: {e}")
            self.retriever_results['R4_wells'] = {'error': str(e)}

        # R5: Geology maps
        logger.info("R5: Querying USGS geology maps...")
        try:
            geology_result = gateway.retrieve_geology(
                lat, lon,
                quadrangle='Woodland',
                output_dir=DIRS['downloads_geology']
            )
            self.retriever_results['R5_geology'] = geology_result.get('data', {})
            maps_found = geology_result.get('data', {}).get('maps_found', 0)
            logger.info(f"  Found {maps_found} geology map references")
        except Exception as e:
            logger.warning(f"  Geology query failed: {e}")
            self.retriever_results['R5_geology'] = {'error': str(e)}

        # R6: Landslide inventory
        logger.info("R6: Querying WA landslide inventory...")
        try:
            landslide_result = gateway.retrieve_landslides(
                lat, lon,
                radius_miles=self.config['terrain_radius_miles'],
                output_dir=DIRS['downloads_landslides']
            )
            self.retriever_results['R6_landslides'] = landslide_result.get('data', {})
            ls_count = landslide_result.get('data', {}).get('landslides_found', 0)
            logger.info(f"  Found {ls_count} landslide features")
        except Exception as e:
            logger.warning(f"  Landslide query failed: {e}")
            self.retriever_results['R6_landslides'] = {'error': str(e)}

        # R7: Normalize LiDAR (if downloaded)
        logger.info("R7: LiDAR normalization...")
        self.retriever_results['R7_normalize'] = 'pending_dtm'

        # Save retriever results
        results_path = DIRS['logs'] + '/retriever_results.json'
        with open(results_path, 'w') as f:
            json.dump(self.retriever_results, f, indent=2, default=str)
        logger.info(f"  Saved retriever results to {results_path}")

    def _run_retriever_mock(self):
        """Mock retriever results for testing without gateway"""
        logger.info("Using mock retriever data...")
        self.site_data = {
            'lat': 45.9067,
            'lon': -122.7700,
            'address': self.config['site_address']
        }
        self.retriever_results = {
            'R1_geocode': 'mock',
            'R2_lidar': {'tiles_found': 0, 'message': 'Mock - no actual query'},
            'R4_wells': {'wells_found': 0, 'message': 'Mock - no actual query'},
            'R5_geology': {'maps_found': 0, 'message': 'Mock - no actual query'},
            'R6_landslides': {'landslides_found': 0, 'message': 'Mock - no actual query'}
        }

    # =========================================================================
    # PHASE 2: SHERLOCK TASKS (S1-S5)
    # =========================================================================

    def run_sherlock_tasks(self):
        """Execute Sherlock analysis tasks S1-S5"""

        # Check if we have DTM
        dtm_path = self._find_dtm()

        if dtm_path:
            # S1: Terrain derivatives
            logger.info("S1: Computing terrain derivatives...")
            try:
                from terrain_processor import TerrainProcessor
                processor = TerrainProcessor(dtm_path, self.config['crs_working'])
                terrain_outputs = processor.compute_all(DIRS['evidence_rasters'])
                self.sherlock_results['S1_terrain'] = terrain_outputs

                # Get slope stats
                slope_stats = processor.get_slope_stats()
                self.sherlock_results['slope_stats'] = {
                    'min': slope_stats.min,
                    'p50': slope_stats.p50,
                    'p90': slope_stats.p90,
                    'max': slope_stats.max
                }
                logger.info(f"  Slope range: {slope_stats.min:.1f}° - {slope_stats.max:.1f}°")

                # S2: Portal candidates and avoid zones
                logger.info("S2: Identifying portal candidates and avoid zones...")
                landslides_path = DIRS['downloads_landslides'] + '/landslides_clipped.geojson'
                if not Path(landslides_path).exists():
                    landslides_path = None

                candidates = processor.identify_portal_candidates(landslides_path)
                avoid_zones = processor.identify_avoid_zones(landslides_path)

                self.sherlock_results['S2_candidates'] = [
                    {'id': c.id, 'centroid_xy': c.centroid_xy, 'elev_ft': c.elev_ft,
                     'slope_deg': c.slope_deg, 'notes': c.notes}
                    for c in candidates
                ]
                self.sherlock_results['S2_avoid_zones'] = [
                    {'id': z.id, 'reason': z.reason, 'notes': z.notes}
                    for z in avoid_zones
                ]
                logger.info(f"  Found {len(candidates)} portal candidates, {len(avoid_zones)} avoid zones")

                # Generate terrain report
                processor.generate_terrain_report(DIRS['analysis'] + '/terrain_report.md')

            except ImportError as e:
                logger.warning(f"  Terrain processing unavailable: {e}")
                self.sherlock_results['S1_terrain'] = {'error': str(e)}
        else:
            logger.warning("S1-S2: No DTM available - skipping terrain analysis")
            self.sherlock_results['S1_terrain'] = {'error': 'No DTM found'}
            # Use placeholder candidates
            self.sherlock_results['S2_candidates'] = [
                {'id': 'PC01', 'centroid_xy': {'x_m': 0, 'y_m': 0}, 'elev_ft': 500,
                 'slope_deg': 10, 'notes': 'Placeholder - awaiting terrain data'}
            ]
            self.sherlock_results['S2_avoid_zones'] = []

        # S3: Well log parsing
        logger.info("S3: Parsing well logs...")
        try:
            from well_log_parser import WellLogParser

            parser = WellLogParser()
            wells_csv = DIRS['downloads_wells'] + '/wells_raw.csv'

            if Path(wells_csv).exists():
                parser.parse_csv(wells_csv)
                logger.info(f"  Parsed {len(parser.wells)} wells from CSV")
            else:
                # Create from retriever results
                wells_data = self.retriever_results.get('R4_wells', {}).get('wells', [])
                if wells_data:
                    for w in wells_data:
                        from well_log_parser import WellRecord
                        parser.wells.append(WellRecord(
                            well_id=w.get('well_id', ''),
                            lat=w.get('lat', 0),
                            lon=w.get('lon', 0),
                            ground_elev_ft=0,
                            total_depth_ft=w.get('drilled_depth_ft', 0) or 0,
                            static_water_level_ft=w.get('static_water_level_ft'),
                            lithology=[],
                            inferred_bedrock_depth_ft=None,
                            clay_thickness_ft=None,
                            data_quality='fair',
                            notes=''
                        ))

            # Compute bedrock envelope
            lat = self.site_data.get('lat', 45.9067)
            lon = self.site_data.get('lon', -122.77)
            envelope = parser.compute_bedrock_envelope(lat, lon)

            self.sherlock_results['S3_envelope'] = {
                'min_ft': envelope.min_ft,
                'likely_ft': envelope.likely_ft,
                'max_ft': envelope.max_ft,
                'confidence_0to1': envelope.confidence_0to1,
                'nearest_wells': envelope.nearest_wells,
                'rationale': envelope.rationale
            }
            logger.info(f"  Bedrock envelope: {envelope.min_ft}-{envelope.max_ft} ft (conf: {envelope.confidence_0to1:.0%})")

            # Generate report
            parser.generate_subsurface_report(envelope, DIRS['analysis'] + '/subsurface_report.md')

        except Exception as e:
            logger.warning(f"  Well parsing failed: {e}")
            self.sherlock_results['S3_envelope'] = {
                'min_ft': 20, 'likely_ft': 35, 'max_ft': 60,
                'confidence_0to1': 0.3,
                'nearest_wells': [],
                'rationale': 'Estimated - no well data available'
            }

        # S4: Geology context
        logger.info("S4: Summarizing geology...")
        try:
            from geology_summarizer import GeologySummarizer, GeologySummary

            summarizer = GeologySummarizer()

            # Try to load geology data
            geology_files = list(Path(DIRS['downloads_geology']).glob('*.gpkg')) + \
                           list(Path(DIRS['downloads_geology']).glob('*.shp'))

            if geology_files:
                summarizer.load_geology(str(geology_files[0]))
                lat = self.site_data.get('lat', 45.9067)
                lon = self.site_data.get('lon', -122.77)
                geo_summary = summarizer.summarize_at_site(lat, lon)
            else:
                # Default summary for Columbia River Basalt region
                geo_summary = GeologySummary(
                    units_at_site=[],
                    dominant_unit='Columbia River Basalt Group (inferred)',
                    faults_nearby=[],
                    structural_notes='Site in Columbia River Basalt province - basalt flows expected at depth',
                    groundwater_implications='Basalt aquifers common; flow-contact zones may have water',
                    tunneling_recommendations='Basalt is excellent tunnel rock; verify with geophysics',
                    confidence='low'
                )

            self.sherlock_results['S4_geology'] = {
                'dominant_unit': geo_summary.dominant_unit,
                'structural_notes': geo_summary.structural_notes,
                'tunneling_recommendations': geo_summary.tunneling_recommendations,
                'confidence': geo_summary.confidence
            }

            summarizer.generate_geology_report(geo_summary, DIRS['analysis'] + '/geology_report.md')
            logger.info(f"  Dominant unit: {geo_summary.dominant_unit}")

        except Exception as e:
            logger.warning(f"  Geology summarization failed: {e}")
            self.sherlock_results['S4_geology'] = {'error': str(e)}

        # S5: Synthesis
        logger.info("S5: Synthesizing design inputs...")
        self._synthesize_freecad_inputs()

    def _find_dtm(self) -> Optional[str]:
        """Find DTM file in downloads or evidence"""
        search_patterns = ['*.tif', '*.TIF', '*dtm*.tif', '*dem*.tif']
        search_dirs = [DIRS['downloads_lidar'], DIRS['evidence_rasters']]

        for dir_path in search_dirs:
            for pattern in search_patterns:
                files = list(Path(dir_path).glob(pattern))
                if files:
                    return str(files[0])
        return None

    def _synthesize_freecad_inputs(self):
        """Synthesize all results into freecad_site_inputs.json"""
        # Load template
        template_path = DIRS['design_inputs'] + '/freecad_site_inputs_starter.json'
        with open(template_path) as f:
            inputs = json.load(f)

        # Update with analysis results
        inputs['meta']['date_generated'] = datetime.now().isoformat()
        inputs['meta']['data_sources'] = list(self.retriever_results.keys())

        # Site
        inputs['site']['latlon_wgs84'] = {
            'lat': self.site_data.get('lat', 0),
            'lon': self.site_data.get('lon', 0)
        }

        # Terrain
        slope_stats = self.sherlock_results.get('slope_stats', {})
        inputs['terrain']['slope_stats_deg'] = slope_stats if slope_stats else {
            'min': 0, 'p50': 0, 'p90': 0, 'max': 0
        }
        inputs['terrain']['portal_candidates'] = self.sherlock_results.get('S2_candidates', [])
        inputs['terrain']['avoid_zones'] = self.sherlock_results.get('S2_avoid_zones', [])

        # Subsurface
        envelope = self.sherlock_results.get('S3_envelope', {})
        inputs['subsurface']['wells_count'] = len(self.retriever_results.get('R4_wells', {}).get('wells', []))
        inputs['subsurface']['bedrock_depth_ft'] = {
            'min': envelope.get('min_ft', 0),
            'likely': envelope.get('likely_ft', 0),
            'max': envelope.get('max_ft', 0)
        }
        inputs['subsurface']['confidence_0to1'] = envelope.get('confidence_0to1', 0)
        inputs['subsurface']['notes'] = envelope.get('rationale', '')

        # Recommendations
        candidates = inputs['terrain']['portal_candidates']
        if candidates:
            inputs['recommendations']['recommended_portal_id'] = candidates[0]['id']

        # Check decision gates
        needs_geophysics = self._check_geophysics_gates(inputs)
        inputs['recommendations']['needs_geophysics'] = needs_geophysics
        if needs_geophysics:
            inputs['recommendations']['geophysics_recommendation'] = (
                "Recommended: 1 ERT line along proposed adit axis + 1 cross line. "
                "Optional: MASW seismic for confirmation."
            )

        # Adit axis (placeholder - would be calculated from portal to bedrock)
        bedrock_likely = envelope.get('likely_ft', 30)
        inputs['recommendations']['adit_axis']['target_station_bedrock_ft'] = bedrock_likely
        inputs['freecad_params']['adit']['length_ft'] = bedrock_likely + 10  # Extra 10ft into rock

        self.freecad_inputs = inputs

        # Save
        output_path = DIRS['design_inputs'] + '/freecad_site_inputs.json'
        with open(output_path, 'w') as f:
            json.dump(inputs, f, indent=2)

        self.sherlock_results['S5_synthesis'] = output_path
        logger.info(f"  Saved design inputs to {output_path}")

    def _check_geophysics_gates(self, inputs: Dict) -> bool:
        """Check if geophysics is needed based on PES decision gates"""
        bedrock = inputs['subsurface']['bedrock_depth_ft']
        spread = bedrock['max'] - bedrock['min']

        # Gate 1: Spread > 50 ft
        if spread > 50:
            logger.info("  Geophysics gate triggered: bedrock spread > 50 ft")
            return True

        # Gate 2: Low confidence
        if inputs['subsurface']['confidence_0to1'] < 0.5:
            logger.info("  Geophysics gate triggered: confidence < 50%")
            return True

        # Gate 3: Portal in landslide (check avoid zones)
        for zone in inputs['terrain']['avoid_zones']:
            if zone.get('reason') == 'landslide':
                logger.info("  Geophysics gate triggered: landslide near site")
                return True

        return False

    # =========================================================================
    # PHASE 2.5: CONSTRAINT ENFORCEMENT
    # =========================================================================

    def enforce_constraints(self):
        """Enforce governance constraints on pipeline outputs"""
        if not self.constraint_enforcer:
            logger.warning("No constraint enforcer loaded - skipping")
            return

        from constraint_enforcer import PortalCandidate

        logger.info("Evaluating portal candidates against constraints...")

        # Get raw candidates from sherlock results
        raw_candidates = self.sherlock_results.get('S2_candidates', [])
        avoid_zones = self.sherlock_results.get('S2_avoid_zones', [])

        # Evaluate each candidate
        evaluated_candidates = []
        for rc in raw_candidates:
            evaluated = self.constraint_enforcer.evaluate_portal_candidate(
                candidate=rc,
                avoid_zones=avoid_zones,
                scarps=[],  # Would be populated from terrain analysis
                wet_lines=[]  # Would be populated from terrain analysis
            )
            evaluated_candidates.append(evaluated)

        # Rank candidates
        ranked_candidates = self.constraint_enforcer.rank_portal_candidates(evaluated_candidates)

        # Log results
        accepted = [c for c in ranked_candidates if c.accepted]
        rejected = [c for c in ranked_candidates if not c.accepted]
        logger.info(f"  Accepted candidates: {len(accepted)}")
        logger.info(f"  Rejected candidates: {len(rejected)}")

        for r in rejected:
            logger.info(f"    {r.candidate_id}: {r.rejection.rejection_rule_id} - {r.rejection.rejection_reason}")

        # Determine confidence level
        envelope = self.sherlock_results.get('S3_envelope', {})
        confidence = envelope.get('confidence_0to1', 0)
        if confidence >= 0.7:
            bedrock_confidence = 'high'
        elif confidence >= 0.4:
            bedrock_confidence = 'medium'
        else:
            bedrock_confidence = 'low'

        # Check if any portal is in avoid zone
        portal_in_avoid_zone = any(
            not c.accepted and c.rejection and c.rejection.rejection_rule_id == "STOP-02"
            for c in ranked_candidates
        )

        # Mass wasting thickness (estimate from bedrock depth)
        mass_wasting_thickness = envelope.get('likely_ft', 30)

        # Evaluate stage gate
        logger.info("Evaluating stage gate conditions...")
        self.stage_gate_status = self.constraint_enforcer.evaluate_stage_gate(
            stage='S',
            bedrock_confidence=bedrock_confidence,
            bedrock_depth_envelope={
                'min': envelope.get('min_ft', 0),
                'likely': envelope.get('likely_ft', 0),
                'max': envelope.get('max_ft', 0)
            },
            portal_candidates=ranked_candidates,
            mass_wasting_thickness_ft=mass_wasting_thickness,
            wet_line_density_high=False  # Would be determined from terrain analysis
        )

        # Log stage gate results
        if self.stage_gate_status.passed:
            logger.info("  Stage gate: PASSED")
        else:
            logger.warning("  Stage gate: BLOCKED")
            for cond_id in self.stage_gate_status.blocking_conditions:
                logger.warning(f"    Blocking: {cond_id}")

        for sc in self.stage_gate_status.stop_conditions_evaluated:
            status = "TRIGGERED" if sc.triggered else "OK"
            logger.info(f"    {sc.condition_id}: {status}")

        # Store results
        self.sherlock_results['constraint_evaluation'] = self.constraint_enforcer.to_dict(
            self.stage_gate_status,
            ranked_candidates
        )

        # Generate constraint report
        report_path = DIRS['analysis'] + '/constraint_report.md'
        self.constraint_enforcer.generate_constraint_report(
            self.stage_gate_status,
            ranked_candidates,
            report_path
        )
        logger.info(f"  Generated constraint report: {report_path}")

        # Get access mode recommendation
        access_rec = self.constraint_enforcer.get_access_mode_recommendation(
            mass_wasting_thickness_ft=mass_wasting_thickness,
            bedrock_confidence=bedrock_confidence,
            portal_in_avoid_zone=portal_in_avoid_zone
        )
        self.sherlock_results['access_mode_recommendation'] = access_rec
        logger.info(f"  Recommended access mode: {access_rec.get('recommended_mode', 'none')}")

    # =========================================================================
    # PHASE 3: FREECAD OUTPUT
    # =========================================================================

    def generate_freecad_outputs(self):
        """Generate FreeCAD macro and validate outputs"""
        logger.info("Generating FreeCAD macro...")

        try:
            from freecad_macro_generator import FreeCADMacroGenerator

            inputs_path = DIRS['design_inputs'] + '/freecad_site_inputs.json'
            macro_path = DIRS['design_inputs'] + '/butte_hill.FCMacro'

            generator = FreeCADMacroGenerator(inputs_path)
            generator.generate_macro(macro_path)

            logger.info(f"  Generated macro: {macro_path}")

            # Validate JSON against schema
            self._validate_json_schema()

        except Exception as e:
            logger.error(f"  FreeCAD generation failed: {e}")

    def _validate_json_schema(self):
        """Validate freecad_site_inputs.json against schema"""
        try:
            import jsonschema

            inputs_path = DIRS['design_inputs'] + '/freecad_site_inputs.json'
            schema_path = DIRS['schemas'] + '/freecad_site_inputs.schema.json'

            with open(inputs_path) as f:
                inputs = json.load(f)
            with open(schema_path) as f:
                schema = json.load(f)

            jsonschema.validate(inputs, schema)
            logger.info("  JSON validated against schema ✓")

        except jsonschema.ValidationError as e:
            logger.warning(f"  Schema validation failed: {e.message}")
        except Exception as e:
            logger.warning(f"  Could not validate schema: {e}")

    def print_summary(self):
        """Print pipeline summary"""
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)

        print(f"\nSite: {self.config['site_address']}")
        print(f"Coordinates: {self.site_data.get('lat', 'N/A')}, {self.site_data.get('lon', 'N/A')}")

        print("\n--- Retriever Results ---")
        for key, value in self.retriever_results.items():
            if isinstance(value, dict):
                status = value.get('error', 'OK')
                print(f"  {key}: {status if 'error' in value else 'OK'}")
            else:
                print(f"  {key}: {value}")

        print("\n--- Analysis Results ---")
        envelope = self.sherlock_results.get('S3_envelope', {})
        print(f"  Bedrock depth: {envelope.get('min_ft', 'N/A')}-{envelope.get('max_ft', 'N/A')} ft")
        print(f"  Confidence: {envelope.get('confidence_0to1', 0):.0%}")

        candidates = self.sherlock_results.get('S2_candidates', [])
        print(f"  Portal candidates: {len(candidates)}")

        if self.freecad_inputs:
            print(f"  Needs geophysics: {self.freecad_inputs['recommendations']['needs_geophysics']}")

        # Constraint enforcement results
        if self.stage_gate_status:
            print("\n--- Stage Gate Status ---")
            print(f"  Stage: {self.stage_gate_status.stage}")
            print(f"  Passed: {'YES' if self.stage_gate_status.passed else 'NO'}")
            print(f"  FreeCAD allowed: {'YES' if self.stage_gate_status.freecad_generation_allowed else 'NO'}")

            if self.stage_gate_status.blocking_conditions:
                print(f"  Blocking: {', '.join(self.stage_gate_status.blocking_conditions)}")

            if self.stage_gate_status.required_next_data:
                print("  Required next data:")
                for d in self.stage_gate_status.required_next_data:
                    print(f"    - {d}")

        # Access mode recommendation
        access_rec = self.sherlock_results.get('access_mode_recommendation', {})
        if access_rec:
            print(f"\n--- Access Mode ---")
            print(f"  Recommended: {access_rec.get('recommended_mode', 'none')}")
            print(f"  Allowed modes: {', '.join(access_rec.get('allowed_modes', []))}")

        print("\n--- Output Files ---")
        print(f"  Design inputs: {DIRS['design_inputs']}/freecad_site_inputs.json")
        print(f"  FreeCAD macro: {DIRS['design_inputs']}/butte_hill.FCMacro")
        print(f"  Terrain report: {DIRS['analysis']}/terrain_report.md")
        print(f"  Subsurface report: {DIRS['analysis']}/subsurface_report.md")
        print(f"  Geology report: {DIRS['analysis']}/geology_report.md")
        if self.constraint_enforcer:
            print(f"  Constraint report: {DIRS['analysis']}/constraint_report.md")


def main():
    parser = argparse.ArgumentParser(description='Butte Hill Site Characterization Pipeline')
    parser.add_argument('--full', action='store_true', help='Run full pipeline')
    parser.add_argument('--retriever-only', action='store_true', help='Run retriever tasks only')
    parser.add_argument('--sherlock-only', action='store_true', help='Run sherlock analysis only')
    parser.add_argument('--freecad-only', action='store_true', help='Generate FreeCAD outputs only')
    parser.add_argument('--test', action='store_true', help='Run with mock data (no external queries)')
    parser.add_argument('--constraints', type=str, help='Path to constraints.json for governance enforcement')

    args = parser.parse_args()

    # Default constraints path if not specified
    constraints_path = args.constraints
    if not constraints_path:
        default_constraints = DIRS['design_inputs'] + '/constraints.json'
        if Path(default_constraints).exists():
            constraints_path = default_constraints

    pipeline = ButteHillPipeline(constraints_path=constraints_path)

    if args.full or not any([args.retriever_only, args.sherlock_only, args.freecad_only]):
        result = pipeline.run_full_pipeline()
    elif args.retriever_only:
        pipeline.run_retriever_tasks()
        result = {'retriever': pipeline.retriever_results}
    elif args.sherlock_only:
        # Need site data for sherlock
        pipeline.site_data = {'lat': 45.9067, 'lon': -122.7700}
        pipeline.run_sherlock_tasks()
        result = {'sherlock': pipeline.sherlock_results}
    elif args.freecad_only:
        pipeline.generate_freecad_outputs()
        result = {'freecad': 'generated'}

    print("\nPipeline execution complete.")
    return 0 if result.get('success', True) else 1


if __name__ == '__main__':
    sys.exit(main())
