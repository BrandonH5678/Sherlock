# Targeting Officer Specification

## Overview

The **Targeting Officer** is an automated system within Sherlock that ensures research targets have valid targeting packages, generates collection plans, submits them to the J5A overnight queue, validates execution, and ingests outputs into the evidence database.

This document specifies the Targeting Officer's responsibilities, workflows, validation protocols, and integration with J5A.

---

## Responsibilities

### 1. Target Monitoring

**Goal**: Identify targets requiring attention.

**Process**:
- Query `targets` table for targets with `status IN ('new', 'under_research')`
- Check if target has valid packages:
  - No packages → create new package
  - Only failed packages → replan
  - Package in `draft` or `ready` → validate and submit
  - Package in `submitted`, `queued`, `running` → monitor progress
  - Package in `completed` → ingest outputs
  - Package in `outputs_ingested` → perform V2 validation
  - Package in `validated` → close package and update target status

**Frequency**: Run on-demand (`sherlock officer run --once`) or continuously (`sherlock officer run --daemon --interval 3600`)

### 2. Package Generation

**Goal**: Create targeting packages with collection URLs and expected outputs.

**Process**:
1. Identify target type (`person`, `org`, `event`, `location`, `tech`, `operation`)
2. Generate collection plan based on target type:
   - **YouTube**: Search for relevant hearings, interviews, documentaries
   - **Documents**: Identify FOIA releases, declassified files, official reports
   - **Composite**: Combine multiple source types
3. Populate `targeting_package` table:
   - `package_id`: `pkg_{target_id}_v{version}`
   - `package_type`: `youtube`, `document`, or `composite`
   - `status`: `draft`
   - `plan_summary`: Brief description of collection strategy
   - `collection_urls`: JSON array of URLs to ingest
   - `expected_outputs`: JSON array of expected file paths
4. Create initial `package_status_history` record

**Example Package**:
```json
{
  "package_id": "pkg_aaro_v1",
  "target_id": "aaro",
  "version": 1,
  "package_type": "youtube",
  "status": "draft",
  "plan_summary": "Collect congressional hearings featuring AARO officials (2023-2024)",
  "collection_urls": [
    "https://youtube.com/watch?v=...",
    "https://youtube.com/watch?v=..."
  ],
  "expected_outputs": [
    "/home/johnny5/Sherlock/media/aaro_hearing_2023_07_26.mp4",
    "/home/johnny5/Sherlock/diarization/aaro_hearing_2023_07_26.json",
    "/home/johnny5/Sherlock/media/aaro_hearing_2024_01_15.mp4",
    "/home/johnny5/Sherlock/diarization/aaro_hearing_2024_01_15.json"
  ],
  "validation_level": "V0"
}
```

### 3. Validation

**Goal**: Ensure packages meet quality requirements before submission and after completion.

#### V0 Validation (Schema)

**Timing**: Before submission to J5A

**Checks**:
- `package_id` is unique and follows naming convention
- `target_id` references valid target in `targets` table
- `package_type` is one of: `youtube`, `document`, `composite`
- `plan_summary` is non-empty and descriptive
- `collection_urls` is non-empty JSON array
- `expected_outputs` is non-empty JSON array
- All required fields are populated

**Result**: If valid, update `validation_level = 'V0'` and `status = 'ready'`

#### V1 Validation (Execution)

**Timing**: After J5A task completion

**Checks**:
- J5A `j5a_handoff.status = 'completed'` (not `failed`)
- J5A `result` JSON contains no critical errors
- At least one expected output file exists

**Result**: If valid, update `validation_level = 'V1'` and `status = 'completed'`

#### V2 Validation (Output Conformance)

**Timing**: After output ingestion

**Checks**:
- All expected outputs exist on filesystem
- All expected outputs have valid format (e.g., valid MP4, valid JSON)
- All expected outputs have been ingested into `media` and/or `evidence_card` tables
- No major ingestion errors in logs

**Implementation**:
```sql
-- Check expected vs actual outputs
SELECT
  expected_file,
  actual_file,
  validation_status
FROM package_output_manifest
WHERE package_id = :package_id
  AND validation_status IN ('missing', 'invalid')
```

**Result**: If all outputs valid, update `validation_level = 'V2'` and `status = 'validated'`

### 4. Submission

**Goal**: Submit validated packages to J5A overnight queue.

**Process**:
1. Check package `status = 'ready'` and `validation_level = 'V0'`
2. Create `j5a_handoff` record:
   ```json
   {
     "handoff_id": "handoff_{package_id}_{timestamp}",
     "package_id": "pkg_aaro_v1",
     "task_definition": {
       "task_id": "sherlock_pkg_aaro_v1",
       "task_type": "sherlock_collection",
       "package_id": "pkg_aaro_v1",
       "collection_urls": [...],
       "expected_outputs": [...],
       "resource_requirements": {
         "memory_gb": 2.5,
         "cpu_intensive": true,
         "thermal_sensitive": true
       },
       "priority": 1
     },
     "status": "pending",
     "submitted_at": "2025-10-01T12:00:00"
   }
   ```
3. Update package `status = 'submitted'`
4. Record state transition in `package_status_history`

**J5A Acceptance**:
- J5A queue manager polls `j5a_handoff` table for `status = 'pending'`
- If task passes J5A validation (statistical sampling, thermal safety, resource availability), J5A updates `j5a_handoff.status = 'accepted'`
- J5A updates `targeting_package.status = 'queued'`

### 5. Receipt

**Goal**: Monitor J5A task execution and update package status.

**Process**:
1. Poll `j5a_handoff` table for completed tasks:
   ```sql
   SELECT * FROM j5a_handoff
   WHERE status IN ('completed', 'failed')
     AND package_id IN (SELECT package_id FROM targeting_package WHERE status = 'running')
   ```
2. If `j5a_handoff.status = 'completed'`:
   - Run V1 validation
   - If V1 passes, update `targeting_package.status = 'completed'`
3. If `j5a_handoff.status = 'failed'`:
   - Update `targeting_package.status = 'failed'`
   - Record failure reason in `package_status_history`
   - Trigger replanning workflow

**Frequency**: Poll every 5 minutes in daemon mode, or once per `sherlock officer run --once`

### 6. Output Ingestion

**Goal**: Ingest completed package outputs into Sherlock evidence database.

**Process**:
1. Query packages with `status = 'completed'`
2. For each package:
   - Read `expected_outputs` JSON array
   - For each output file:
     - Check if file exists on filesystem
     - Determine file type (video, audio, document, JSON)
     - Run appropriate ingest command:
       - Video/Audio: `sherlock ingest media <file_path> --auto-diarize`
       - Document: `sherlock ingest document <file_path> --extract-claims`
       - JSON: Parse and ingest structured claims
     - Record ingestion result in `package_output_manifest`
3. Update package `status = 'outputs_ingested'`
4. Record state transition in `package_status_history`

**Example**:
```python
def ingest_package_outputs(package_id: str):
    package = db.query(TargetingPackage).filter_by(package_id=package_id).one()

    for expected_file in package.expected_outputs:
        if not Path(expected_file).exists():
            manifest.append({
                'expected_file': expected_file,
                'actual_file': None,
                'validation_status': 'missing'
            })
            continue

        file_type = detect_file_type(expected_file)

        if file_type in ['video', 'audio']:
            result = run_command(f"sherlock ingest media {expected_file} --auto-diarize")
        elif file_type == 'document':
            result = run_command(f"sherlock ingest document {expected_file} --extract-claims")
        elif file_type == 'json':
            result = ingest_structured_json(expected_file)

        manifest.append({
            'expected_file': expected_file,
            'actual_file': expected_file if result.success else None,
            'validation_status': 'valid' if result.success else 'invalid'
        })

    db.bulk_insert(PackageOutputManifest, manifest)
    package.status = 'outputs_ingested'
    db.commit()
```

### 7. Replanning

**Goal**: Handle failed packages by generating new collection plans.

**Trigger**: Package `status = 'failed'`

**Process**:
1. Analyze failure reason from `package_status_history`
2. Determine if failure is recoverable:
   - **Transient failures** (thermal limit exceeded, resource conflict): Resubmit same package
   - **Permanent failures** (invalid URLs, missing sources): Create new package with revised plan
3. If recoverable:
   - Update `targeting_package.status = 'ready'`
   - Resubmit to J5A
4. If not recoverable:
   - Increment package `version`
   - Create new package with revised `collection_urls` and `expected_outputs`
   - Update target `metadata` with failure notes
5. Record replanning decision in `package_status_history`

### 8. Reporting

**Goal**: Generate daily/weekly reports on targeting efficacy.

#### Daily Report

**Command**: `sherlock officer report --daily`

**Contents**:
- **State Totals**: Count of packages in each state (`draft`, `ready`, `submitted`, `queued`, `running`, `completed`, `outputs_ingested`, `validated`, `closed`, `failed`)
- **New Failures**: Packages that transitioned to `failed` in the last 24 hours
- **Collection Efficacy**: Ratio of URLs successfully ingested to URLs planned
- **Targets Coverage**: Percentage of `new` targets with valid packages

**Example Output**:
```markdown
# Targeting Officer Daily Report - 2025-10-01

## Package State Summary
- Draft: 3
- Ready: 2
- Submitted: 1
- Queued: 4
- Running: 2
- Completed: 5
- Outputs Ingested: 3
- Validated: 2
- Closed: 10
- Failed: 1

## New Failures (Last 24 Hours)
- `pkg_aaro_v1`: J5A thermal limit exceeded during execution
  - Action: Resubmit during cooler overnight hours

## Collection Efficacy
- URLs Planned: 50
- URLs Ingested: 42
- Success Rate: 84%

## Targets Coverage
- Total Targets: 25
- Targets with Valid Packages: 20
- Coverage: 80%

## Next Steps
- Replan `pkg_aaro_v1` for overnight submission
- Create packages for 5 new targets: AATIP, UAPTF, Lockheed Skunkworks, BAASS, Bigelow Aerospace
```

#### Weekly Report

**Command**: `sherlock officer report --weekly`

**Contents**:
- Trend analysis (package completion rate over time)
- Target coverage trends
- Bottleneck identification (e.g., J5A queue backlog, diarization delays)
- Replanning frequency and success rate
- Recommendations for process improvements

---

## Package Lifecycle

### State Diagram

```
                  ┌─────────────┐
                  │    draft    │
                  └─────┬───────┘
                        │ V0 validation passes
                        ↓
                  ┌─────────────┐
                  │    ready    │
                  └─────┬───────┘
                        │ Submit to J5A
                        ↓
                  ┌─────────────┐
                  │  submitted  │
                  └─────┬───────┘
                        │ J5A accepts
                        ↓
                  ┌─────────────┐
                  │  accepted   │
                  └─────┬───────┘
                        │ J5A queues
                        ↓
                  ┌─────────────┐
                  │   queued    │
                  └─────┬───────┘
                        │ J5A starts execution
                        ↓
                  ┌─────────────┐
                  │   running   │
                  └─────┬───────┘
                        │ J5A completes (V1 validation)
                        ↓
                  ┌─────────────┐
                  │  completed  │
                  └─────┬───────┘
                        │ Ingest outputs
                        ↓
        ┌───────────────────────────────┐
        │     outputs_ingested          │
        └───────────────┬───────────────┘
                        │ V2 validation passes
                        ↓
                  ┌─────────────┐
                  │  validated  │
                  └─────┬───────┘
                        │ Close package
                        ↓
                  ┌─────────────┐
                  │   closed    │
                  └─────────────┘

                  ┌─────────────┐
    ┌─────────────┤   failed    │◄────── Any state can transition to failed
    │             └─────────────┘
    │ Replan (create new version or resubmit)
    │
    └──────► draft (new version)
```

### State Transitions

| From State | To State | Trigger | Validation |
|------------|----------|---------|------------|
| `draft` | `ready` | V0 validation passes | Schema check |
| `ready` | `submitted` | Submit to J5A | - |
| `submitted` | `accepted` | J5A accepts task | J5A validation |
| `accepted` | `queued` | J5A queues task | - |
| `queued` | `running` | J5A starts execution | - |
| `running` | `completed` | J5A completes successfully | V1 validation |
| `completed` | `outputs_ingested` | All outputs ingested | Ingestion check |
| `outputs_ingested` | `validated` | V2 validation passes | Output conformance |
| `validated` | `closed` | Manual close or auto-close | - |
| Any | `failed` | Error occurs | - |
| `failed` | `draft` | Replan (new version) | - |
| `failed` | `ready` | Resubmit (transient failure) | - |

### State Persistence

All state transitions are recorded in `package_status_history`:

```sql
INSERT INTO package_status_history (
  history_id,
  package_id,
  from_status,
  to_status,
  timestamp,
  reason,
  metadata
) VALUES (
  'hist_' || gen_random_uuid(),
  'pkg_aaro_v1',
  'running',
  'failed',
  '2025-10-01T14:30:00',
  'J5A thermal limit exceeded during diarization',
  '{"cpu_temp": "85°C", "task_duration": "45min"}'
);
```

---

## J5A Integration

### Handoff Protocol

1. **Sherlock Creates Handoff**:
   - Insert record into `j5a_handoff` table with `status = 'pending'`
   - Populate `task_definition` JSON with collection plan

2. **J5A Accepts Handoff**:
   - Poll `j5a_handoff` for `status = 'pending'`
   - Perform J5A validation (statistical sampling, thermal safety, resource availability)
   - If valid, update `j5a_handoff.status = 'accepted'` and `targeting_package.status = 'queued'`
   - If invalid, update `j5a_handoff.status = 'failed'` with reason

3. **J5A Executes Task**:
   - Update `j5a_handoff.status = 'running'` and `targeting_package.status = 'running'`
   - Run collection commands (yt-dlp, ffmpeg, etc.)
   - Monitor thermal safety and memory limits

4. **J5A Completes Task**:
   - Update `j5a_handoff.status = 'completed'` and `completed_at` timestamp
   - Populate `result` JSON with execution summary
   - Update `targeting_package.status = 'completed'`

5. **Sherlock Ingests Outputs**:
   - Poll `j5a_handoff` for `status = 'completed'`
   - Run V1 validation
   - Ingest outputs into evidence database
   - Update `targeting_package.status = 'outputs_ingested'`

### Task Definition Format

```json
{
  "task_id": "sherlock_pkg_aaro_v1",
  "task_type": "sherlock_collection",
  "package_id": "pkg_aaro_v1",
  "collection_urls": [
    "https://youtube.com/watch?v=...",
    "https://youtube.com/watch?v=..."
  ],
  "expected_outputs": [
    "/home/johnny5/Sherlock/media/aaro_hearing_2023_07_26.mp4",
    "/home/johnny5/Sherlock/diarization/aaro_hearing_2023_07_26.json"
  ],
  "resource_requirements": {
    "memory_gb": 2.5,
    "cpu_intensive": true,
    "thermal_sensitive": true
  },
  "priority": 1,
  "commands": [
    "sherlock ingest youtube https://youtube.com/watch?v=... --auto-diarize",
    "sherlock ingest youtube https://youtube.com/watch?v=... --auto-diarize"
  ]
}
```

### J5A Constraints

- **Memory Limit**: 3.0GB safe threshold (system total: 3.7GB, minus 0.7GB buffer)
- **Thermal Limit**: 80°C maximum CPU temperature
- **Business Hours Priority**: LibreOffice absolute priority 6am-7pm Mon-Fri (WaterWizard operations)
- **Statistical Validation**: J5A performs 3-segment stratified sampling before resource allocation

Targeting Officer must respect these constraints when generating packages. Resource-intensive packages (e.g., multiple hours of video) should be submitted for overnight execution.

---

## Implementation Checklist

### Core Components

- [ ] `TargetingOfficer` class in `src/targeting_officer.py`
  - [ ] `monitor_targets()` - identify targets needing attention
  - [ ] `generate_package()` - create collection plans
  - [ ] `validate_v0()` - schema validation
  - [ ] `validate_v1()` - execution validation
  - [ ] `validate_v2()` - output conformance validation
  - [ ] `submit_package()` - J5A handoff
  - [ ] `poll_j5a_status()` - monitor execution
  - [ ] `ingest_outputs()` - import completed outputs
  - [ ] `replan_package()` - handle failures
  - [ ] `generate_daily_report()` - daily status report
  - [ ] `generate_weekly_report()` - weekly trend analysis

### CLI Commands

- [ ] `sherlock officer run --once` - single execution
- [ ] `sherlock officer run --daemon --interval 3600` - continuous monitoring
- [ ] `sherlock officer report --daily` - daily report
- [ ] `sherlock officer report --weekly` - weekly report
- [ ] `sherlock officer replan --package <package_id>` - manual replan

### Database Tables

- [x] `targets` - research targets
- [x] `targeting_package` - collection packages
- [x] `j5a_handoff` - J5A integration interface
- [x] `package_status_history` - audit trail
- [x] `package_output_manifest` - expected vs actual outputs

### Integration Points

- [ ] J5A handoff protocol implementation
- [ ] Ingest command wrappers (YouTube, media, document)
- [ ] File type detection and validation
- [ ] Output manifest generation and checking

### Testing

- [ ] Unit tests for validation logic (V0/V1/V2)
- [ ] Integration tests for J5A handoff workflow
- [ ] End-to-end test: target → package → submit → execute → ingest → validate → close
- [ ] Failure recovery tests: transient and permanent failures

---

## Usage Examples

### Example 1: Manual Package Creation and Submission

```bash
# Add new target
sherlock targets add "AARO" --type org --priority 1

# Create package
sherlock pkg create --target aaro --version 1 --type youtube

# Edit package plan (opens editor with template)
sherlock pkg edit pkg_aaro_v1

# Validate schema (V0)
sherlock pkg validate --package pkg_aaro_v1 --level 0

# Submit to J5A
sherlock pkg submit --package pkg_aaro_v1

# Check status
sherlock pkg status pkg_aaro_v1
```

### Example 2: Automated Targeting Officer

```bash
# Run once (check all targets, generate/submit packages, ingest outputs)
sherlock officer run --once

# Run daemon (continuous monitoring every hour)
sherlock officer run --daemon --interval 3600

# Generate daily report
sherlock officer report --daily --output targeting_report_2025-10-01.md
```

### Example 3: Failure Recovery

```bash
# Package failed due to thermal limit
# Targeting Officer automatically detects failure and replans

# Manual replan if needed
sherlock officer replan --package pkg_aaro_v1

# Check replan status
sherlock pkg status pkg_aaro_v2
```

---

## Performance Considerations

### Daemon Mode Interval

- **Recommended**: 3600 seconds (1 hour) for continuous monitoring
- **Justification**: Balances responsiveness with CPU/thermal impact
- **Adjustment**: Increase interval (7200s) if thermal limits frequently exceeded

### Package Batch Size

- **Recommendation**: Limit to 5 URLs per package for YouTube collections
- **Justification**: Prevents J5A memory/thermal violations
- **Large Targets**: Split into multiple packages (`pkg_aaro_v1`, `pkg_aaro_v2`, etc.)

### Validation Optimization

- **V0**: Fast (schema check only), run before every submission
- **V1**: Moderate (file existence check), run after J5A completion
- **V2**: Slow (full format validation), run in background after ingestion

### Database Query Optimization

- Index on `targeting_package.status` for fast state queries
- Index on `j5a_handoff.status` for efficient polling
- Composite index on `package_status_history(package_id, timestamp)` for audit queries

---

## Future Enhancements

### Phase 1 (Current)
- ✅ Basic package lifecycle
- ✅ V0/V1/V2 validation
- ✅ J5A handoff protocol
- ✅ Daily/weekly reporting

### Phase 2 (Planned)
- [ ] Machine learning for package plan generation (learn from successful packages)
- [ ] Automatic source discovery (web scraping for FOIA releases, hearing schedules)
- [ ] Predictive failure detection (thermal/resource usage forecasting)
- [ ] Multi-package coordination (parallel execution with resource balancing)

### Phase 3 (Future)
- [ ] Collaborative targeting (multi-user package sharing)
- [ ] Real-time collection monitoring dashboard
- [ ] Integration with external APIs (YouTube Data API, archive.org)
- [ ] Automated speaker anchor generation from previous diarizations

---

## Conclusion

The **Targeting Officer** automates the research-to-evidence pipeline in Sherlock, ensuring systematic collection, validation, and ingestion of intelligence for priority targets. By integrating with J5A's overnight queue system, it enables resource-intensive operations while respecting hardware constraints.

The package lifecycle, validation levels, and failure recovery mechanisms ensure reliable evidence collection with full audit trails for investigative work.
