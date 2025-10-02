# Package Lifecycle Documentation

## Overview

The **Package Lifecycle** in Sherlock defines the state machine governing targeting packages from initial creation through validation, execution, output ingestion, and closure. This document provides detailed specifications for each state, transition conditions, and validation requirements.

---

## State Machine

### States

| State | Description | Entry Condition | Exit Condition |
|-------|-------------|-----------------|----------------|
| `draft` | Package created, awaiting V0 validation | Package creation | V0 validation passes |
| `ready` | V0 validated, ready for submission | V0 validation passes | Submitted to J5A |
| `submitted` | Sent to J5A, awaiting acceptance | Submitted to J5A | J5A accepts or rejects |
| `accepted` | J5A accepted task | J5A accepts | J5A queues task |
| `queued` | In J5A queue, awaiting execution | J5A queues task | J5A starts execution |
| `running` | J5A executing collection commands | J5A starts execution | J5A completes or fails |
| `completed` | J5A execution finished successfully | J5A completes + V1 passes | Outputs ingested |
| `outputs_ingested` | All outputs ingested into evidence DB | All outputs ingested | V2 validation passes |
| `validated` | V2 validation passed | V2 validation passes | Package closed |
| `closed` | Package complete, target updated | Manual or auto-close | Terminal state |
| `failed` | Error occurred at any stage | Any error | Replan or manual intervention |

### State Diagram

```
┌─────────────┐
│    draft    │ ◄─────────────────────────────┐
└─────┬───────┘                               │
      │ V0 validation                         │
      ↓                                       │
┌─────────────┐                               │
│    ready    │                               │
└─────┬───────┘                               │
      │ Submit to J5A                         │
      ↓                                       │
┌─────────────┐                               │
│  submitted  │                               │
└─────┬───────┘                               │
      │ J5A accepts                           │
      ↓                                       │
┌─────────────┐                               │
│  accepted   │                               │
└─────┬───────┘                               │
      │ J5A queues                            │
      ↓                                       │
┌─────────────┐                               │
│   queued    │                               │
└─────┬───────┘                               │
      │ J5A starts                            │
      ↓                                       │
┌─────────────┐                               │
│   running   │                               │
└─────┬───────┘                               │
      │ J5A completes (V1)                    │
      ↓                                       │
┌─────────────┐                               │
│  completed  │                               │
└─────┬───────┘                               │
      │ Ingest outputs                        │
      ↓                                       │
┌─────────────────┐                           │
│ outputs_ingested│                           │
└─────┬───────────┘                           │
      │ V2 validation                         │
      ↓                                       │
┌─────────────┐                               │
│  validated  │                               │
└─────┬───────┘                               │
      │ Close package                         │
      ↓                                       │
┌─────────────┐                               │
│   closed    │ (Terminal state)              │
└─────────────┘                               │
                                              │
┌─────────────┐                               │
│   failed    │ ◄─────── Any state            │
└─────┬───────┘                               │
      │ Replan                                │
      └───────────────────────────────────────┘
      (creates new version or resubmits)
```

---

## State Specifications

### `draft`

**Purpose**: Initial state for newly created packages requiring validation before submission.

**Entry**:
- Package created via `sherlock pkg create` or Targeting Officer auto-generation

**Characteristics**:
- Package has basic structure (`package_id`, `target_id`, `version`)
- `plan_summary`, `collection_urls`, `expected_outputs` may be incomplete
- No validation performed yet

**Actions**:
- User or Targeting Officer edits package via `sherlock pkg edit`
- Populate `plan_summary`, `collection_urls`, `expected_outputs`

**Exit**:
- V0 validation passes → transition to `ready`
- Package deleted → removed from database

**Validation**: None required in this state

---

### `ready`

**Purpose**: Package has passed V0 schema validation and is ready for J5A submission.

**Entry**:
- V0 validation passes (all required fields populated, valid format)

**Characteristics**:
- `validation_level = 'V0'`
- All required fields non-empty
- `collection_urls` contains valid URLs
- `expected_outputs` contains valid file paths

**Actions**:
- Package queued for submission to J5A
- Targeting Officer or user runs `sherlock pkg submit`

**Exit**:
- Submitted to J5A → transition to `submitted`
- V0 validation fails after edit → transition back to `draft`

**Validation**: V0 (schema) must be valid

---

### `submitted`

**Purpose**: Package submitted to J5A, awaiting acceptance validation.

**Entry**:
- `sherlock pkg submit` creates `j5a_handoff` record with `status = 'pending'`

**Characteristics**:
- `j5a_handoff` record exists with `status = 'pending'`
- Package waiting for J5A queue manager to accept

**Actions**:
- J5A polls `j5a_handoff` table
- J5A performs acceptance validation (statistical sampling, thermal safety, resource availability)

**Exit**:
- J5A accepts → transition to `accepted`
- J5A rejects → transition to `failed` with rejection reason

**Validation**: J5A acceptance validation (external)

---

### `accepted`

**Purpose**: J5A has accepted the package and will queue it for execution.

**Entry**:
- J5A updates `j5a_handoff.status = 'accepted'`

**Characteristics**:
- `j5a_handoff.status = 'accepted'`
- Package approved for execution but not yet queued

**Actions**:
- J5A adds task to execution queue

**Exit**:
- J5A queues task → transition to `queued`

**Validation**: None (transitional state)

---

### `queued`

**Purpose**: Package is in J5A execution queue awaiting resource availability.

**Entry**:
- J5A updates `targeting_package.status = 'queued'` when task enters queue

**Characteristics**:
- Task waiting for CPU/memory/thermal resources
- May wait hours if submitted during business hours or thermal constraints active

**Actions**:
- J5A monitors resource availability
- When resources available, J5A begins execution

**Exit**:
- J5A starts execution → transition to `running`
- Task cancelled → transition to `failed`

**Validation**: None (waiting for resources)

---

### `running`

**Purpose**: J5A is actively executing collection commands.

**Entry**:
- J5A starts task execution and updates `j5a_handoff.status = 'running'`

**Characteristics**:
- Collection commands running (yt-dlp, ffmpeg, etc.)
- Thermal safety and memory monitoring active
- Progress logged to J5A task logs

**Actions**:
- Download media from `collection_urls`
- Run diarization if specified
- Generate expected output files

**Exit**:
- Task completes successfully → transition to `completed`
- Task fails (error, thermal limit, timeout) → transition to `failed`

**Validation**: V1 (execution validation) performed after completion

---

### `completed`

**Purpose**: J5A task finished successfully, outputs await ingestion.

**Entry**:
- J5A updates `j5a_handoff.status = 'completed'` and `completed_at` timestamp
- V1 validation passes (at least one expected output exists)

**Characteristics**:
- `j5a_handoff.status = 'completed'`
- `j5a_handoff.result` contains execution summary
- Expected output files exist on filesystem
- `validation_level = 'V1'`

**Actions**:
- Targeting Officer polls `j5a_handoff` for completed tasks
- Targeting Officer triggers output ingestion

**Exit**:
- All outputs ingested → transition to `outputs_ingested`
- Ingestion fails → transition to `failed`

**Validation**: V1 (execution validation) must be valid

---

### `outputs_ingested`

**Purpose**: All package outputs have been ingested into Sherlock evidence database.

**Entry**:
- Targeting Officer successfully ingests all expected outputs
- `package_output_manifest` records created for each output

**Characteristics**:
- All expected outputs ingested into `media`, `evidence_card`, or `claim` tables
- `package_output_manifest` populated with ingestion results
- Evidence database updated with new sources, claims, speakers

**Actions**:
- Targeting Officer runs V2 validation (output conformance)

**Exit**:
- V2 validation passes → transition to `validated`
- V2 validation fails → transition to `failed`

**Validation**: V2 (output conformance) in progress

---

### `validated`

**Purpose**: All outputs validated, package ready for closure.

**Entry**:
- V2 validation passes (all outputs exist, valid format, successfully ingested)
- `validation_level = 'V2'`

**Characteristics**:
- `package_output_manifest` shows all outputs `validation_status = 'valid'`
- No missing or invalid outputs
- Evidence database fully updated

**Actions**:
- Update target `status` based on package success
- Generate completion report
- Optionally auto-close package

**Exit**:
- Package closed → transition to `closed`

**Validation**: V2 (output conformance) must be valid

---

### `closed`

**Purpose**: Package lifecycle complete, terminal state.

**Entry**:
- Manual close via `sherlock pkg close` or auto-close after validation
- Target `status` updated (e.g., `new` → `under_research`)

**Characteristics**:
- Terminal state (no further transitions)
- Full audit trail in `package_status_history`
- All outputs ingested and validated
- Target updated with new evidence

**Actions**:
- None (terminal state)

**Exit**:
- None (terminal state)

**Validation**: None (already fully validated)

---

### `failed`

**Purpose**: Error occurred during package lifecycle, requires intervention.

**Entry**:
- Any state can transition to `failed` on error

**Characteristics**:
- `package_status_history` contains failure reason
- May be transient (thermal limit, resource conflict) or permanent (invalid URLs, missing sources)

**Actions**:
- Targeting Officer or user analyzes failure reason
- Determine if recoverable:
  - **Transient**: Resubmit same package (back to `ready`)
  - **Permanent**: Create new package version (back to `draft`)

**Exit**:
- Resubmit (transient failure) → transition to `ready`
- Replan (permanent failure) → create new `draft` package with incremented version
- Manual intervention → user decides next steps

**Validation**: Root cause analysis required

---

## Validation Levels

### V0: Schema Validation

**Timing**: Before submission to J5A (in `draft` → `ready` transition)

**Purpose**: Ensure package has all required fields and valid format before J5A submission.

**Checks**:
1. `package_id` is unique and follows naming convention (`pkg_{target_id}_v{version}`)
2. `target_id` references valid target in `targets` table
3. `package_type` is one of: `youtube`, `document`, `composite`
4. `plan_summary` is non-empty string (min 10 characters)
5. `collection_urls` is non-empty JSON array of valid URLs
6. `expected_outputs` is non-empty JSON array of valid file paths
7. All required fields populated

**Implementation**:
```python
def validate_v0(package: TargetingPackage) -> tuple[bool, list[str]]:
    errors = []

    # Check package_id format
    if not re.match(r'^pkg_\w+_v\d+$', package.package_id):
        errors.append("Invalid package_id format (expected: pkg_{target_id}_v{version})")

    # Check target exists
    if not db.query(Target).filter_by(target_id=package.target_id).first():
        errors.append(f"Target {package.target_id} not found")

    # Check package_type
    if package.package_type not in ['youtube', 'document', 'composite']:
        errors.append(f"Invalid package_type: {package.package_type}")

    # Check plan_summary
    if not package.plan_summary or len(package.plan_summary) < 10:
        errors.append("plan_summary must be at least 10 characters")

    # Check collection_urls
    if not package.collection_urls or len(package.collection_urls) == 0:
        errors.append("collection_urls must be non-empty array")
    else:
        for url in package.collection_urls:
            if not is_valid_url(url):
                errors.append(f"Invalid URL: {url}")

    # Check expected_outputs
    if not package.expected_outputs or len(package.expected_outputs) == 0:
        errors.append("expected_outputs must be non-empty array")
    else:
        for path in package.expected_outputs:
            if not is_valid_path(path):
                errors.append(f"Invalid path: {path}")

    return (len(errors) == 0, errors)
```

**Success**: Update `validation_level = 'V0'`, `status = 'ready'`

**Failure**: Record errors in `package_status_history`, keep `status = 'draft'`

---

### V1: Execution Validation

**Timing**: After J5A task completion (in `running` → `completed` transition)

**Purpose**: Ensure J5A task executed without critical errors and produced expected outputs.

**Checks**:
1. `j5a_handoff.status = 'completed'` (not `failed`)
2. `j5a_handoff.result` JSON contains no critical errors
3. At least one expected output file exists on filesystem
4. No thermal emergency or memory violations during execution

**Implementation**:
```python
def validate_v1(package: TargetingPackage) -> tuple[bool, list[str]]:
    errors = []

    # Check J5A handoff status
    handoff = db.query(J5AHandoff).filter_by(package_id=package.package_id).order_by(J5AHandoff.submitted_at.desc()).first()
    if not handoff or handoff.status != 'completed':
        errors.append(f"J5A handoff status is {handoff.status if handoff else 'missing'}, expected 'completed'")
        return (False, errors)

    # Check result JSON for critical errors
    result = handoff.result or {}
    if result.get('critical_errors'):
        errors.append(f"Critical errors in J5A execution: {result['critical_errors']}")

    # Check at least one output exists
    outputs_found = 0
    for expected_path in package.expected_outputs:
        if Path(expected_path).exists():
            outputs_found += 1

    if outputs_found == 0:
        errors.append("No expected output files found on filesystem")

    return (len(errors) == 0, errors)
```

**Success**: Update `validation_level = 'V1'`, `status = 'completed'`

**Failure**: Update `status = 'failed'` with failure reason

---

### V2: Output Conformance Validation

**Timing**: After output ingestion (in `outputs_ingested` → `validated` transition)

**Purpose**: Ensure all expected outputs exist, have valid format, and successfully ingested into evidence database.

**Checks**:
1. All expected output files exist on filesystem
2. All expected output files have valid format (valid MP4, valid JSON, valid PDF, etc.)
3. All expected outputs ingested into `media` or `evidence_card` tables
4. No major ingestion errors in `package_output_manifest`

**Implementation**:
```python
def validate_v2(package: TargetingPackage) -> tuple[bool, list[str]]:
    errors = []

    # Query output manifest
    manifest_entries = db.query(PackageOutputManifest).filter_by(package_id=package.package_id).all()

    if len(manifest_entries) == 0:
        errors.append("No output manifest entries found")
        return (False, errors)

    # Check each manifest entry
    for entry in manifest_entries:
        if entry.validation_status == 'missing':
            errors.append(f"Expected output missing: {entry.expected_file}")
        elif entry.validation_status == 'invalid':
            errors.append(f"Invalid output format: {entry.expected_file}")
            if entry.validation_errors:
                errors.append(f"  Errors: {entry.validation_errors}")

    # Check all expected outputs accounted for
    expected_count = len(package.expected_outputs)
    manifest_count = len(manifest_entries)
    if manifest_count < expected_count:
        errors.append(f"Missing manifest entries: expected {expected_count}, found {manifest_count}")

    return (len(errors) == 0, errors)
```

**Success**: Update `validation_level = 'V2'`, `status = 'validated'`

**Failure**: Update `status = 'failed'` with validation errors

---

## State Transitions

### Transition Rules

| From | To | Trigger | Validation | Actor |
|------|-----|---------|------------|-------|
| - | `draft` | Package creation | None | User or Targeting Officer |
| `draft` | `ready` | V0 validation passes | V0 | User or Targeting Officer |
| `ready` | `submitted` | Submit to J5A | None | User or Targeting Officer |
| `submitted` | `accepted` | J5A accepts | J5A acceptance | J5A |
| `accepted` | `queued` | J5A queues | None | J5A |
| `queued` | `running` | J5A starts execution | None | J5A |
| `running` | `completed` | J5A completes | V1 | J5A + Targeting Officer |
| `completed` | `outputs_ingested` | Outputs ingested | Ingestion check | Targeting Officer |
| `outputs_ingested` | `validated` | V2 validation passes | V2 | Targeting Officer |
| `validated` | `closed` | Package closure | None | User or Targeting Officer |
| Any | `failed` | Error occurs | Root cause | System |
| `failed` | `draft` | Replan (new version) | None | Targeting Officer |
| `failed` | `ready` | Resubmit (transient) | None | Targeting Officer |

### Transition Recording

All transitions recorded in `package_status_history`:

```sql
CREATE TABLE package_status_history (
    history_id TEXT PRIMARY KEY,
    package_id TEXT REFERENCES targeting_package(package_id),
    from_status TEXT,
    to_status TEXT,
    timestamp TEXT,
    reason TEXT,
    metadata JSON
);
```

**Example Transition Record**:
```sql
INSERT INTO package_status_history VALUES (
    'hist_001',
    'pkg_aaro_v1',
    'draft',
    'ready',
    '2025-10-01T10:00:00',
    'V0 validation passed',
    '{"validation_errors": [], "validator": "targeting_officer"}'
);
```

---

## Failure Handling

### Failure Classification

#### Transient Failures
Temporary conditions that may resolve on retry.

**Examples**:
- Thermal limit exceeded during execution
- J5A resource conflict (other tasks running)
- Network timeout during download
- Temporary storage full

**Recovery**: Resubmit same package (back to `ready` state)

#### Permanent Failures
Conditions requiring package revision.

**Examples**:
- Invalid URLs (404 not found, private videos)
- Missing sources (documents not yet released)
- Format errors (corrupted files, unsupported formats)
- Authentication required (paywalled content)

**Recovery**: Create new package version (back to `draft` state with incremented version)

### Failure Recovery Workflow

```python
def handle_package_failure(package: TargetingPackage, failure_reason: str):
    # Analyze failure
    failure_type = classify_failure(failure_reason)

    if failure_type == FailureType.TRANSIENT:
        # Resubmit same package
        package.status = 'ready'
        package.metadata['retry_count'] = package.metadata.get('retry_count', 0) + 1
        package.metadata['last_failure'] = failure_reason

        # Record state transition
        record_status_transition(
            package_id=package.package_id,
            from_status='failed',
            to_status='ready',
            reason=f"Resubmitting after transient failure: {failure_reason}"
        )

    elif failure_type == FailureType.PERMANENT:
        # Create new package version
        new_version = package.version + 1
        new_package = create_package(
            target_id=package.target_id,
            version=new_version,
            package_type=package.package_type
        )

        # Copy plan with notes
        new_package.plan_summary = f"{package.plan_summary}\n\nReplanned from v{package.version} due to: {failure_reason}"
        new_package.collection_urls = package.collection_urls  # User will edit
        new_package.expected_outputs = package.expected_outputs  # User will edit

        # Record state transition for old package
        record_status_transition(
            package_id=package.package_id,
            from_status='failed',
            to_status='failed',  # Stays failed
            reason=f"Replanned as v{new_version} due to permanent failure: {failure_reason}"
        )

        # Update target metadata
        target = db.query(Target).filter_by(target_id=package.target_id).one()
        target.metadata['failed_packages'] = target.metadata.get('failed_packages', [])
        target.metadata['failed_packages'].append({
            'package_id': package.package_id,
            'version': package.version,
            'failure_reason': failure_reason
        })
```

### Retry Limits

**Transient Failures**: Maximum 3 retries per package
**After 3 Retries**: Classify as permanent failure and replan

---

## Output Manifest

### Purpose

Track expected vs actual outputs, enabling V2 validation.

### Schema

```sql
CREATE TABLE package_output_manifest (
    manifest_id TEXT PRIMARY KEY,
    package_id TEXT REFERENCES targeting_package(package_id),
    expected_file TEXT,
    actual_file TEXT,
    file_type TEXT,  -- 'video', 'audio', 'document', 'json', 'other'
    validation_status TEXT CHECK(validation_status IN ('pending', 'valid', 'invalid', 'missing')),
    validation_errors JSON,
    created_at TEXT,
    validated_at TEXT
);
```

### Population

**Timing**: During output ingestion (`completed` → `outputs_ingested` transition)

**Process**:
1. For each `expected_file` in package:
   - Check if file exists on filesystem
   - If exists:
     - Determine file type
     - Validate format (e.g., ffprobe for video, JSON parse for JSON)
     - Ingest into appropriate table (`media`, `evidence_card`, etc.)
     - Record `validation_status = 'valid'` or `'invalid'`
   - If missing:
     - Record `validation_status = 'missing'`
     - Record reason in `validation_errors`

**Example**:
```python
def populate_output_manifest(package: TargetingPackage):
    manifest_entries = []

    for expected_file in package.expected_outputs:
        entry = {
            'manifest_id': f"manifest_{uuid4()}",
            'package_id': package.package_id,
            'expected_file': expected_file,
            'created_at': datetime.now().isoformat()
        }

        if not Path(expected_file).exists():
            entry['actual_file'] = None
            entry['validation_status'] = 'missing'
            entry['validation_errors'] = {'error': 'File not found on filesystem'}
        else:
            entry['actual_file'] = expected_file
            file_type = detect_file_type(expected_file)
            entry['file_type'] = file_type

            # Validate format
            is_valid, errors = validate_file_format(expected_file, file_type)
            entry['validation_status'] = 'valid' if is_valid else 'invalid'
            entry['validation_errors'] = errors if errors else None
            entry['validated_at'] = datetime.now().isoformat()

        manifest_entries.append(entry)

    db.bulk_insert(PackageOutputManifest, manifest_entries)
```

---

## Audit Trail

### Purpose

Full provenance tracking from package creation to closure.

### Implementation

**Table**: `package_status_history`

**Query All Transitions**:
```sql
SELECT
    from_status,
    to_status,
    timestamp,
    reason,
    metadata
FROM package_status_history
WHERE package_id = 'pkg_aaro_v1'
ORDER BY timestamp ASC;
```

**Example Output**:
```
from_status  | to_status       | timestamp            | reason
-------------|-----------------|----------------------|----------------------------
NULL         | draft           | 2025-10-01T09:00:00 | Package created
draft        | ready           | 2025-10-01T10:00:00 | V0 validation passed
ready        | submitted       | 2025-10-01T10:05:00 | Submitted to J5A
submitted    | accepted        | 2025-10-01T10:10:00 | J5A accepted task
accepted     | queued          | 2025-10-01T10:15:00 | Added to J5A queue
queued       | running         | 2025-10-01T22:00:00 | J5A started execution
running      | completed       | 2025-10-01T23:30:00 | J5A completed successfully
completed    | outputs_ingested| 2025-10-02T00:00:00 | All outputs ingested
outputs_ingested | validated  | 2025-10-02T00:05:00 | V2 validation passed
validated    | closed          | 2025-10-02T00:10:00 | Package closed, target updated
```

---

## Performance Considerations

### Database Indexing

```sql
CREATE INDEX idx_package_status ON targeting_package(status);
CREATE INDEX idx_package_target ON targeting_package(target_id);
CREATE INDEX idx_handoff_status ON j5a_handoff(status);
CREATE INDEX idx_history_package_time ON package_status_history(package_id, timestamp);
CREATE INDEX idx_manifest_package ON package_output_manifest(package_id);
```

### State Query Optimization

**Fast Query for Active Packages**:
```sql
SELECT package_id, status, updated_at
FROM targeting_package
WHERE status IN ('ready', 'submitted', 'queued', 'running', 'completed', 'outputs_ingested')
ORDER BY updated_at ASC;
```

**Fast Query for Failed Packages**:
```sql
SELECT
    p.package_id,
    p.target_id,
    h.reason AS failure_reason,
    h.timestamp AS failed_at
FROM targeting_package p
JOIN package_status_history h ON p.package_id = h.package_id
WHERE p.status = 'failed'
  AND h.to_status = 'failed'
ORDER BY h.timestamp DESC;
```

---

## Integration with Targeting Officer

### Automatic State Management

Targeting Officer continuously monitors package states and triggers appropriate actions:

```python
class TargetingOfficer:
    def monitor_packages(self):
        # Check packages in each state
        self.handle_draft_packages()
        self.handle_ready_packages()
        self.handle_submitted_packages()
        self.handle_completed_packages()
        self.handle_outputs_ingested_packages()
        self.handle_validated_packages()
        self.handle_failed_packages()

    def handle_draft_packages(self):
        drafts = db.query(TargetingPackage).filter_by(status='draft').all()
        for pkg in drafts:
            is_valid, errors = validate_v0(pkg)
            if is_valid:
                transition_state(pkg, 'ready', 'V0 validation passed')

    def handle_ready_packages(self):
        ready = db.query(TargetingPackage).filter_by(status='ready').all()
        for pkg in ready:
            submit_to_j5a(pkg)
            transition_state(pkg, 'submitted', 'Submitted to J5A')

    def handle_completed_packages(self):
        completed = db.query(TargetingPackage).filter_by(status='completed').all()
        for pkg in completed:
            ingest_outputs(pkg)
            transition_state(pkg, 'outputs_ingested', 'All outputs ingested')

    # ... etc
```

---

## Conclusion

The **Package Lifecycle** provides robust state management for Sherlock's targeting workflow, ensuring systematic progression from package creation through validation, execution, output ingestion, and closure. The three-level validation system (V0/V1/V2) ensures quality at each stage, while the failure recovery mechanisms handle both transient and permanent errors.

The lifecycle integrates seamlessly with J5A's overnight queue system, enabling resource-intensive collection operations while maintaining full audit trails for investigative research.
