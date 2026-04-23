#!/usr/bin/env python3
"""
Constraint Enforcer for Sherlock Geospatial Pipeline

Loads governance constraints and enforces hard stop conditions,
portal candidate validation, and stage gate evaluation.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class StopAction(Enum):
    """Actions triggered by stop conditions"""
    HALT_FREECAD_GENERATION = "halt_freecad_generation"
    REJECT_PORTAL_CANDIDATE = "reject_portal_candidate"
    HALT_AND_FLAG_GROUNDWATER_RISK = "halt_and_flag_groundwater_risk"
    REQUIRE_VERTICAL_ACCESS_OR_ABORT = "require_vertical_access_or_abort"


class ConfidenceLevel(Enum):
    """Confidence levels for data quality"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass
class PortalRejection:
    """Record of a rejected portal candidate"""
    candidate_id: str
    rejection_rule_id: str
    rejection_reason: str
    data_source: str
    distance_to_hazard_ft: Optional[float] = None
    hazard_feature: Optional[str] = None


@dataclass
class PortalCandidate:
    """Portal candidate with constraint evaluation"""
    candidate_id: str
    centroid_xy: Dict[str, float]
    elev_ft: float
    slope_deg: float
    accepted: bool = True
    rejection: Optional[PortalRejection] = None
    score: float = 0.0
    scoring_factors: Dict[str, float] = field(default_factory=dict)
    notes: str = ""


@dataclass
class StopConditionResult:
    """Result of evaluating a stop condition"""
    condition_id: str
    triggered: bool
    trigger_expression: str
    action: str
    required_next_data: List[str] = field(default_factory=list)
    details: str = ""


@dataclass
class StageGateStatus:
    """Overall stage gate status"""
    stage: str  # 'R' (retrieval), 'S' (sherlock), 'D' (design)
    passed: bool
    stop_conditions_evaluated: List[StopConditionResult] = field(default_factory=list)
    blocking_conditions: List[str] = field(default_factory=list)
    freecad_generation_allowed: bool = True
    required_next_data: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)


class ConstraintEnforcer:
    """
    Enforces governance constraints on pipeline outputs.

    Loads constraints from JSON and evaluates:
    - Hard stop conditions (STOP-01..04)
    - Portal candidate acceptance/rejection
    - Stage gate progression
    """

    def __init__(self, constraints_path: str):
        """
        Load constraints from JSON file

        Args:
            constraints_path: Path to constraints.json
        """
        self.constraints_path = Path(constraints_path)

        with open(self.constraints_path) as f:
            self.constraints = json.load(f)

        self.schema_version = self.constraints.get('schema_version', 'unknown')
        self.site_id = self.constraints.get('site_id', 'unknown')

        logger.info(f"Loaded constraints: {self.schema_version} for {self.site_id}")

    def evaluate_stop_conditions(
        self,
        bedrock_confidence: str,
        portal_in_avoid_zone: bool,
        wet_line_density_high: bool,
        mass_wasting_thickness_ft: float
    ) -> List[StopConditionResult]:
        """
        Evaluate all stop conditions against current data

        Returns:
            List of StopConditionResult with triggered status
        """
        stop_conditions = self.constraints.get('uncertainty_and_stage_gates', {}).get('stop_conditions', [])
        results = []

        for condition in stop_conditions:
            cond_id = condition['id']
            trigger = condition['trigger']
            action = condition['action']
            required_data = condition.get('required_next_data', [])

            triggered = False
            details = ""

            if cond_id == "STOP-01":
                triggered = bedrock_confidence.lower() == 'low'
                details = f"Bedrock confidence: {bedrock_confidence}"

            elif cond_id == "STOP-02":
                triggered = portal_in_avoid_zone
                details = "Portal candidate intersects avoid zone"

            elif cond_id == "STOP-03":
                triggered = wet_line_density_high
                details = "High wet line density detected"

            elif cond_id == "STOP-04":
                triggered = mass_wasting_thickness_ft > 60
                details = f"Mass wasting thickness: {mass_wasting_thickness_ft:.1f} ft > 60 ft threshold"

            results.append(StopConditionResult(
                condition_id=cond_id,
                triggered=triggered,
                trigger_expression=trigger,
                action=action,
                required_next_data=required_data if triggered else [],
                details=details
            ))

        return results

    def evaluate_portal_candidate(
        self,
        candidate: Dict[str, Any],
        avoid_zones: List[Dict[str, Any]],
        scarps: List[Dict[str, Any]] = None,
        wet_lines: List[Dict[str, Any]] = None
    ) -> PortalCandidate:
        """
        Evaluate a portal candidate against terrain constraints

        Args:
            candidate: Portal candidate dict with id, centroid_xy, elev_ft, slope_deg
            avoid_zones: List of avoid zone geometries
            scarps: List of scarp features (optional)
            wet_lines: List of wet line features (optional)

        Returns:
            PortalCandidate with acceptance status and scoring
        """
        terrain_constraints = self.constraints.get('terrain_constraints', {})
        portal_siting = terrain_constraints.get('portal_siting', {})
        buffers = terrain_constraints.get('avoid_zone_generation', {}).get('buffers_ft', {})

        candidate_id = candidate.get('id', 'unknown')
        slope_deg = candidate.get('slope_deg', 0)
        centroid = candidate.get('centroid_xy', {'x_m': 0, 'y_m': 0})
        elev_ft = candidate.get('elev_ft', 0)

        portal = PortalCandidate(
            candidate_id=candidate_id,
            centroid_xy=centroid,
            elev_ft=elev_ft,
            slope_deg=slope_deg,
            accepted=True,
            score=100.0  # Start with perfect score
        )

        # Check slope constraint
        max_slope = portal_siting.get('max_local_slope_deg', 18)
        if slope_deg > max_slope:
            portal.accepted = False
            portal.rejection = PortalRejection(
                candidate_id=candidate_id,
                rejection_rule_id="TERRAIN-SLOPE",
                rejection_reason=f"Slope {slope_deg:.1f}° exceeds max {max_slope}°",
                data_source="terrain_processor"
            )
            return portal

        # Score by slope (lower is better)
        slope_score = max(0, 100 - (slope_deg / max_slope) * 50)
        portal.scoring_factors['slope'] = slope_score

        # Check avoid zone intersection
        for az in avoid_zones:
            if self._point_in_polygon(centroid, az):
                portal.accepted = False
                portal.rejection = PortalRejection(
                    candidate_id=candidate_id,
                    rejection_rule_id="STOP-02",
                    rejection_reason="Portal intersects avoid zone",
                    data_source=az.get('source', 'avoid_zone_analysis'),
                    hazard_feature=az.get('type', 'avoid_zone')
                )
                return portal

        # Check distance to scarps (if provided)
        if scarps:
            min_scarp_dist = portal_siting.get('min_distance_from_head_scarp_ft', 300)
            for scarp in scarps:
                dist = self._distance_to_feature(centroid, scarp)
                if dist < min_scarp_dist:
                    portal.accepted = False
                    portal.rejection = PortalRejection(
                        candidate_id=candidate_id,
                        rejection_rule_id="TERRAIN-SCARP",
                        rejection_reason=f"Within {min_scarp_dist}ft of head scarp",
                        data_source="lidar_analysis",
                        distance_to_hazard_ft=dist,
                        hazard_feature="head_scarp"
                    )
                    return portal

            # Score by distance to nearest scarp
            nearest_scarp_dist = min(self._distance_to_feature(centroid, s) for s in scarps) if scarps else 1000
            scarp_score = min(100, nearest_scarp_dist / min_scarp_dist * 50)
            portal.scoring_factors['scarp_distance'] = scarp_score

        # Check wet lines (if provided)
        if wet_lines:
            min_wet_dist = buffers.get('wet_lines', 150)
            wet_line_count = 0
            for wl in wet_lines:
                dist = self._distance_to_feature(centroid, wl)
                if dist < min_wet_dist:
                    wet_line_count += 1

            # High density = more than 3 wet lines nearby
            if wet_line_count > 3:
                portal.scoring_factors['wet_line_density'] = 0
                portal.notes += f"High wet line density ({wet_line_count} within {min_wet_dist}ft). "
            else:
                portal.scoring_factors['wet_line_density'] = max(0, 100 - wet_line_count * 25)

        # Calculate final score
        if portal.scoring_factors:
            portal.score = sum(portal.scoring_factors.values()) / len(portal.scoring_factors)

        return portal

    def evaluate_stage_gate(
        self,
        stage: str,
        bedrock_confidence: str,
        bedrock_depth_envelope: Dict[str, float],
        portal_candidates: List[PortalCandidate],
        mass_wasting_thickness_ft: float = 0,
        wet_line_density_high: bool = False
    ) -> StageGateStatus:
        """
        Evaluate stage gate for pipeline progression

        Args:
            stage: Current stage ('R', 'S', or 'D')
            bedrock_confidence: Confidence level string
            bedrock_depth_envelope: Dict with min, likely, max
            portal_candidates: List of evaluated portal candidates
            mass_wasting_thickness_ft: Estimated thickness
            wet_line_density_high: True if high density detected

        Returns:
            StageGateStatus with pass/fail and blocking conditions
        """
        # Check if any portal is in avoid zone
        portal_in_avoid_zone = any(
            not p.accepted and p.rejection and p.rejection.rejection_rule_id == "STOP-02"
            for p in portal_candidates
        )

        # Evaluate stop conditions
        stop_results = self.evaluate_stop_conditions(
            bedrock_confidence=bedrock_confidence,
            portal_in_avoid_zone=portal_in_avoid_zone,
            wet_line_density_high=wet_line_density_high,
            mass_wasting_thickness_ft=mass_wasting_thickness_ft
        )

        # Determine blocking conditions
        blocking = [r.condition_id for r in stop_results if r.triggered]

        # Determine if FreeCAD generation is allowed
        freecad_blocked = any(
            r.triggered and r.action == StopAction.HALT_FREECAD_GENERATION.value
            for r in stop_results
        )

        # Collect required next data
        required_data = []
        for r in stop_results:
            if r.triggered:
                required_data.extend(r.required_next_data)
        required_data = list(set(required_data))  # Dedupe

        # Build assumptions list
        assumptions = self._build_assumptions(bedrock_confidence, bedrock_depth_envelope)

        return StageGateStatus(
            stage=stage,
            passed=len(blocking) == 0,
            stop_conditions_evaluated=stop_results,
            blocking_conditions=blocking,
            freecad_generation_allowed=not freecad_blocked,
            required_next_data=required_data,
            assumptions=assumptions
        )

    def rank_portal_candidates(
        self,
        candidates: List[PortalCandidate]
    ) -> List[PortalCandidate]:
        """
        Rank portal candidates by score (higher is better)

        Accepted candidates are ranked first, then rejected ones.
        """
        accepted = [c for c in candidates if c.accepted]
        rejected = [c for c in candidates if not c.accepted]

        accepted.sort(key=lambda c: c.score, reverse=True)
        rejected.sort(key=lambda c: c.score, reverse=True)

        return accepted + rejected

    def get_access_mode_recommendation(
        self,
        mass_wasting_thickness_ft: float,
        bedrock_confidence: str,
        portal_in_avoid_zone: bool
    ) -> Dict[str, Any]:
        """
        Recommend access mode based on constraints

        Returns:
            Dict with recommended mode and conditions
        """
        exc_constraints = self.constraints.get('excavation_envelope_constraints', {})
        access_modes = exc_constraints.get('access_modes', {})
        vertical = exc_constraints.get('vertical_access', {})
        adit = exc_constraints.get('adit_access', {})

        recommendation = {
            'recommended_mode': None,
            'allowed_modes': [],
            'prohibited_modes': access_modes.get('prohibited', []),
            'conditions_met': [],
            'conditions_failed': []
        }

        # Check vertical access conditions
        vertical_ok = True
        if portal_in_avoid_zone:
            vertical_ok = False
            recommendation['conditions_failed'].append("portal_outside_avoid_zones")
        else:
            recommendation['conditions_met'].append("portal_outside_avoid_zones")

        if mass_wasting_thickness_ft > 60:
            vertical_ok = False
            recommendation['conditions_failed'].append("mass_wasting_thickness <= 60ft")
        else:
            recommendation['conditions_met'].append("mass_wasting_thickness <= 60ft")

        if bedrock_confidence.lower() == 'low':
            vertical_ok = False
            recommendation['conditions_failed'].append("bedrock_confidence != low")
        else:
            recommendation['conditions_met'].append("bedrock_confidence != low")

        if vertical_ok:
            recommendation['allowed_modes'].append('vertical_access')

        # Check adit access conditions
        adit_ok = mass_wasting_thickness_ft <= 20 and bedrock_confidence.lower() != 'low'
        if adit_ok:
            recommendation['allowed_modes'].append('short_adit')
            recommendation['max_adit_length_ft'] = adit.get('max_adit_length_ft', 80)

        # Select recommended mode (prefer vertical)
        preferred = access_modes.get('preferred_order', [])
        for mode in preferred:
            if mode in recommendation['allowed_modes'] or mode.replace('_', ' ') in str(recommendation['allowed_modes']):
                recommendation['recommended_mode'] = mode
                break

        return recommendation

    def _point_in_polygon(self, point: Dict[str, float], polygon: Dict[str, Any]) -> bool:
        """Simple point-in-polygon check (placeholder - needs shapely for real impl)"""
        # For now, check if polygon has a 'contains_point' flag (set by terrain processor)
        if polygon.get('contains_portal'):
            return True
        return False

    def _distance_to_feature(self, point: Dict[str, float], feature: Dict[str, Any]) -> float:
        """Calculate distance to feature (placeholder - needs shapely for real impl)"""
        # Return distance if pre-calculated, otherwise assume far away
        return feature.get('distance_ft', 1000)

    def _build_assumptions(
        self,
        bedrock_confidence: str,
        bedrock_depth_envelope: Dict[str, float]
    ) -> List[str]:
        """Build list of assumptions for reporting"""
        assumptions = []

        bounds = self.constraints.get('uncertainty_and_stage_gates', {}).get('uncertainty_bounds', {})
        depth_uncertainty = bounds.get('bedrock_depth_ft_plus_minus', 20)

        assumptions.append(f"Bedrock depth uncertainty: +/- {depth_uncertainty} ft")
        assumptions.append(f"Bedrock confidence level: {bedrock_confidence}")

        if bedrock_depth_envelope:
            spread = bedrock_depth_envelope.get('max', 0) - bedrock_depth_envelope.get('min', 0)
            assumptions.append(f"Bedrock depth envelope spread: {spread:.1f} ft")

        geology = self.constraints.get('geology_constraints', {})
        target = geology.get('target_medium', {})
        assumptions.append(f"Target excavation medium: {', '.join(target.get('allowed', []))}")
        assumptions.append(f"Prohibited media: {', '.join(target.get('prohibited', []))}")

        return assumptions

    def generate_constraint_report(
        self,
        stage_gate: StageGateStatus,
        portal_candidates: List[PortalCandidate],
        output_path: str
    ) -> str:
        """
        Generate constraint evaluation report in markdown

        Args:
            stage_gate: Stage gate evaluation result
            portal_candidates: Ranked portal candidates
            output_path: Path to write report

        Returns:
            Path to generated report
        """
        accepted = [p for p in portal_candidates if p.accepted]
        rejected = [p for p in portal_candidates if not p.accepted]

        report = f"""# Constraint Evaluation Report

## Stage Gate Status
- **Stage**: {stage_gate.stage}
- **Passed**: {'YES' if stage_gate.passed else 'NO'}
- **FreeCAD Generation Allowed**: {'YES' if stage_gate.freecad_generation_allowed else 'NO'}

## Stop Conditions Evaluated

| ID | Triggered | Action | Details |
|----|-----------|--------|---------|
"""
        for sc in stage_gate.stop_conditions_evaluated:
            status = "**TRIGGERED**" if sc.triggered else "OK"
            report += f"| {sc.condition_id} | {status} | {sc.action} | {sc.details} |\n"

        if stage_gate.blocking_conditions:
            report += f"""
## Blocking Conditions
{chr(10).join(f'- **{c}**' for c in stage_gate.blocking_conditions)}

## Required Next Data
{chr(10).join(f'- {d}' for d in stage_gate.required_next_data)}
"""

        report += f"""
## Portal Candidates (Ranked)

### Accepted ({len(accepted)})
"""
        if accepted:
            report += "| Rank | ID | Score | Slope | Notes |\n"
            report += "|------|----|-------|-------|-------|\n"
            for i, p in enumerate(accepted, 1):
                report += f"| {i} | {p.candidate_id} | {p.score:.1f} | {p.slope_deg:.1f}° | {p.notes or 'OK'} |\n"
        else:
            report += "*No accepted candidates*\n"

        report += f"""
### Rejected ({len(rejected)})
"""
        if rejected:
            report += "| ID | Rule | Reason | Data Source | Distance |\n"
            report += "|----|------|--------|-------------|----------|\n"
            for p in rejected:
                r = p.rejection
                dist = f"{r.distance_to_hazard_ft:.0f} ft" if r and r.distance_to_hazard_ft else "-"
                report += f"| {p.candidate_id} | {r.rejection_rule_id if r else '-'} | {r.rejection_reason if r else '-'} | {r.data_source if r else '-'} | {dist} |\n"
        else:
            report += "*No rejected candidates*\n"

        report += f"""
## Assumptions
{chr(10).join(f'- {a}' for a in stage_gate.assumptions)}

## Constraint Schema
- **Version**: {self.schema_version}
- **Site**: {self.site_id}
"""

        with open(output_path, 'w') as f:
            f.write(report)

        logger.info(f"Generated constraint report: {output_path}")
        return output_path

    def to_dict(self, stage_gate: StageGateStatus, portal_candidates: List[PortalCandidate]) -> Dict[str, Any]:
        """Convert results to JSON-serializable dict for inclusion in freecad_site_inputs.json"""
        return {
            'stage_gate_status': {
                'stage': stage_gate.stage,
                'passed': stage_gate.passed,
                'freecad_generation_allowed': stage_gate.freecad_generation_allowed,
                'blocking_conditions': stage_gate.blocking_conditions,
                'required_next_data': stage_gate.required_next_data,
                'assumptions': stage_gate.assumptions,
                'stop_conditions': [
                    {
                        'id': sc.condition_id,
                        'triggered': sc.triggered,
                        'action': sc.action,
                        'details': sc.details
                    }
                    for sc in stage_gate.stop_conditions_evaluated
                ]
            },
            'portal_candidates_ranked': [
                {
                    'candidate_id': p.candidate_id,
                    'accepted': p.accepted,
                    'score': p.score,
                    'rejection_rule_id': p.rejection.rejection_rule_id if p.rejection else None,
                    'rejection_reason': p.rejection.rejection_reason if p.rejection else None
                }
                for p in portal_candidates
            ]
        }
