# Constraint Evaluation Report

## Stage Gate Status
- **Stage**: S
- **Passed**: NO
- **FreeCAD Generation Allowed**: NO

## Stop Conditions Evaluated

| ID | Triggered | Action | Details |
|----|-----------|--------|---------|
| STOP-01 | **TRIGGERED** | halt_freecad_generation | Bedrock confidence: low |
| STOP-02 | OK | reject_portal_candidate | Portal candidate intersects avoid zone |
| STOP-03 | OK | halt_and_flag_groundwater_risk | High wet line density detected |
| STOP-04 | OK | require_vertical_access_or_abort | Mass wasting thickness: 0.0 ft > 60 ft threshold |

## Blocking Conditions
- **STOP-01**

## Required Next Data
- additional_well_logs
- geotech_boring_or_refraction
- field_outcrop_check

## Portal Candidates (Ranked)

### Accepted (1)
| Rank | ID | Score | Slope | Notes |
|------|----|-------|-------|-------|
| 1 | PC01 | 72.2 | 10.0° | OK |

### Rejected (0)
*No rejected candidates*

## Assumptions
- Bedrock depth uncertainty: +/- 20 ft
- Bedrock confidence level: low
- Bedrock depth envelope spread: 0.0 ft
- Target excavation medium: bedrock_flow_core
- Prohibited media: mass_wasting, flow_breccia, volcaniclastic_interbed, unknown

## Constraint Schema
- **Version**: butte_hill_constraints_v1
- **Site**: butte_hill_210_lahti_rd
