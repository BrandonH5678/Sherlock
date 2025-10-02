# Sherlock: Local-First Deep Research System

## Overview

**Sherlock** is a local-first, database-backed system for analyzing fragmented, obscured, or multimodal evidence. It ingests audio, video, documents, images, and sensor data, normalizes them into a unified schema, applies speaker diarization, stores structured claims with weighted confidence, and provides retrieval + synthesis tools for investigative work.

**Core Mission:**
- Ingest, diarize, normalize, index, and analyze heterogeneous evidence
- Track speakers, claims, sources, and relationships across multiple intelligence operations
- Support both supervised and unsupervised speaker identification
- Provide query, search, and synthesis capabilities for investigative research
- Enable targeting workflows with package-based collection planning

---

## Design Principles

1. **Local-first**: All data stays on local hardware; no cloud dependencies for core operations
2. **Database-backed**: SQLite baseline with optional Postgres + pgvector for vector search
3. **Multimodal**: Audio, video, documents, images, sensor data all normalized to unified schema
4. **Speaker-centric**: Diarization and speaker tracking as first-class features
5. **Weighted confidence**: All claims have confidence scores based on source type and corroboration
6. **Audit trail**: Full provenance tracking from raw media → normalized claims
7. **CPU-optimized**: All ML models run on CPU (late-2012 Mac mini, 16GB RAM, Linux Mint MATE)
8. **Package-driven collection**: Targets Library + Targeting Officer for systematic research campaigns

---

## System Architecture

### High-Level Pipeline

```
User
  ↓
CLI (typer)
  ↓
┌─────────────────────────────────────────────────────────────────────┐
│ INGEST                                                              │
│  - yt-dlp for YouTube                                              │
│  - ffmpeg for local video/audio                                    │
│  - PDFMiner/OCR for documents                                      │
│  - pillow for images                                               │
│  - Custom parsers for sensor data                                  │
└─────────────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────────────┐
│ DIARIZATION (audio/video only)                                     │
│  - Transcription: faster-whisper (tiny/base INT8)                  │
│  - VAD: WebRTC VAD (30ms frames)                                   │
│  - Embeddings: Resemblyzer (0.9s window / 0.3s hop)               │
│  - Clustering: HDBSCAN or anchor-based supervised matching         │
└─────────────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────────────┐
│ NORMALIZE                                                           │
│  - Extract claims from transcripts, documents, sensor data         │
│  - Assign speakers (diarized or manual)                            │
│  - Apply confidence weighting based on source type                 │
│  - Store in unified schema: evidence_card, claim, speaker          │
└─────────────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────────────┐
│ INDEX                                                               │
│  - FTS5 for full-text search on claims                             │
│  - Optional: pgvector for semantic search on embeddings            │
│  - Temporal index on timestamps                                    │
│  - Entity extraction and indexing                                  │
└─────────────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────────────┐
│ RETRIEVE                                                            │
│  - Query by speaker, source, time range, entity, topic             │
│  - Full-text search across all claims                              │
│  - Optional semantic search with vector similarity                 │
│  - Cross-reference analysis between operations                     │
└─────────────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────────────┐
│ ANALYZE                                                             │
│  - Pattern detection across claims                                 │
│  - Speaker network analysis                                        │
│  - Timeline reconstruction                                         │
│  - Confidence aggregation and weighting                            │
└─────────────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────────────┐
│ SYNTHESIZE                                                          │
│  - Generate intelligence reports                                   │
│  - Cross-reference multiple operations                             │
│  - Pattern analysis across cases                                   │
│  - Export to markdown/JSON                                         │
└─────────────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────────────┐
│ AUDIT                                                               │
│  - Full provenance from raw media to final claims                  │
│  - Diarization quality metrics                                     │
│  - Confidence score explanations                                   │
│  - Source reliability tracking                                     │
└─────────────────────────────────────────────────────────────────────┘
  ↓
User (reports, queries, analysis)
```

---

## Data Model

### Core Tables

#### `media`
Raw media files ingested into the system.

```sql
CREATE TABLE media (
    media_id TEXT PRIMARY KEY,
    title TEXT,
    url TEXT,
    file_path TEXT,
    media_type TEXT CHECK(media_type IN ('audio', 'video', 'document', 'image', 'sensor')),
    duration REAL,  -- seconds (audio/video only)
    page_count INTEGER,  -- documents only
    created_at TEXT,
    ingested_at TEXT,
    metadata JSON
);
```

#### `diarization_run`
Tracks speaker diarization executions.

```sql
CREATE TABLE diarization_run (
    run_id TEXT PRIMARY KEY,
    media_id TEXT REFERENCES media(media_id),
    model_name TEXT,  -- e.g. "faster-whisper-tiny-int8"
    vad_mode TEXT,  -- e.g. "webrtc-aggressive"
    clustering_method TEXT,  -- "hdbscan" or "anchor_supervised"
    num_speakers_detected INTEGER,
    started_at TEXT,
    completed_at TEXT,
    quality_metrics JSON,
    config JSON
);
```

#### `speaker_local`
Local speaker identities (per-media).

```sql
CREATE TABLE speaker_local (
    local_speaker_id TEXT PRIMARY KEY,
    run_id TEXT REFERENCES diarization_run(run_id),
    speaker_label TEXT,  -- "SPEAKER_00", "SPEAKER_01", etc.
    avg_embedding BLOB,  -- serialized numpy array
    num_turns INTEGER,
    total_duration REAL,
    confidence REAL
);
```

#### `speaker_turn`
Individual speaker segments.

```sql
CREATE TABLE speaker_turn (
    turn_id TEXT PRIMARY KEY,
    run_id TEXT REFERENCES diarization_run(run_id),
    local_speaker_id TEXT REFERENCES speaker_local(local_speaker_id),
    start_time REAL,
    end_time REAL,
    transcript TEXT,
    confidence REAL,
    embedding BLOB
);
```

#### `speaker_alias`
Global speaker identities with aliases.

```sql
CREATE TABLE speaker_alias (
    global_speaker_id TEXT PRIMARY KEY,
    name TEXT,
    title TEXT,
    organization TEXT,
    voice_embedding BLOB,  -- reference embedding for supervised matching
    confidence REAL,
    first_seen TEXT,
    last_seen TEXT,
    metadata JSON
);

CREATE TABLE speaker_mapping (
    local_speaker_id TEXT REFERENCES speaker_local(local_speaker_id),
    global_speaker_id TEXT REFERENCES speaker_alias(global_speaker_id),
    confidence REAL,
    method TEXT,  -- "manual", "supervised_anchor", "voice_match"
    created_at TEXT,
    PRIMARY KEY (local_speaker_id, global_speaker_id)
);
```

#### `evidence_card`
Evidence sources (media or documents).

```sql
CREATE TABLE evidence_card (
    source_id TEXT PRIMARY KEY,
    media_id TEXT REFERENCES media(media_id),
    title TEXT,
    url TEXT,
    file_path TEXT,
    evidence_type TEXT CHECK(evidence_type IN ('hearing', 'interview', 'document', 'document_leaked', 'document_declassified', 'journalism', 'sensor', 'witness', 'official', 'speculative')),
    duration REAL,
    page_count INTEGER,
    created_at TEXT,
    ingested_at TEXT,
    metadata JSON
);
```

#### `claim`
Structured claims extracted from evidence.

```sql
CREATE TABLE claim (
    claim_id TEXT PRIMARY KEY,
    source_id TEXT REFERENCES evidence_card(source_id),
    speaker_id TEXT REFERENCES speaker_alias(global_speaker_id),
    claim_type TEXT CHECK(claim_type IN ('factual', 'testimonial', 'analytical', 'speculative')),
    text TEXT NOT NULL,
    confidence REAL CHECK(confidence >= 0 AND confidence <= 1),
    start_time REAL,  -- timestamp in media (if applicable)
    end_time REAL,
    page_number INTEGER,  -- page in document (if applicable)
    context TEXT,
    entities JSON,  -- extracted entities
    tags JSON,  -- topic tags
    created_at TEXT
);
```

#### `fts`
Full-text search index.

```sql
CREATE VIRTUAL TABLE fts USING fts5(
    claim_id,
    text,
    context,
    entities,
    tags
);
```

### Targets Library and Package Workflow

#### `targets`
Research targets requiring investigation.

```sql
CREATE TABLE targets (
    target_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    target_type TEXT CHECK(target_type IN ('person', 'org', 'event', 'location', 'tech', 'operation')),
    priority INTEGER CHECK(priority BETWEEN 1 AND 5),  -- 1=highest
    status TEXT CHECK(status IN ('new', 'under_research', 'validated', 'closed')),
    created_at TEXT,
    updated_at TEXT,
    metadata JSON
);
```

#### `targeting_package`
Collection packages for targets.

```sql
CREATE TABLE targeting_package (
    package_id TEXT PRIMARY KEY,
    target_id TEXT REFERENCES targets(target_id),
    version INTEGER,
    package_type TEXT CHECK(package_type IN ('youtube', 'document', 'composite')),
    status TEXT CHECK(status IN ('draft', 'ready', 'submitted', 'accepted', 'queued', 'running', 'completed', 'outputs_ingested', 'validated', 'closed', 'failed')),
    plan_summary TEXT,
    collection_urls JSON,  -- list of URLs to ingest
    expected_outputs JSON,  -- list of expected output files
    validation_level TEXT CHECK(validation_level IN ('V0', 'V1', 'V2')),
    created_at TEXT,
    updated_at TEXT,
    metadata JSON
);
```

#### `j5a_handoff`
Handoff interface to J5A overnight queue system.

```sql
CREATE TABLE j5a_handoff (
    handoff_id TEXT PRIMARY KEY,
    package_id TEXT REFERENCES targeting_package(package_id),
    task_definition JSON,  -- J5A task specification
    status TEXT CHECK(status IN ('pending', 'submitted', 'accepted', 'running', 'completed', 'failed')),
    submitted_at TEXT,
    completed_at TEXT,
    result JSON
);
```

#### `package_status_history`
Audit trail for package state transitions.

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

#### `package_output_manifest`
Tracks expected vs actual outputs from packages.

```sql
CREATE TABLE package_output_manifest (
    manifest_id TEXT PRIMARY KEY,
    package_id TEXT REFERENCES targeting_package(package_id),
    expected_file TEXT,
    actual_file TEXT,
    file_type TEXT,
    validation_status TEXT CHECK(validation_status IN ('pending', 'valid', 'invalid', 'missing')),
    validation_errors JSON,
    created_at TEXT,
    validated_at TEXT
);
```

---

## Confidence Weighting Rubric

Sherlock uses a weighted confidence system based on source type and corroboration.

### Base Weights by Evidence Type

| Evidence Type | Base Confidence | Rationale |
|---------------|----------------|-----------|
| `official` (government docs, court records) | 0.75 | High credibility, official provenance |
| `hearing` (congressional, parliamentary) | 0.70 | Under oath, adversarial questioning |
| `witness` (firsthand, on-record) | 0.55 | Direct observation, but subject to bias/error |
| `witness` (anonymous/secondhand) | 0.50 | Lower verification, potential reliability issues |
| `journalism` (reputable outlets) | 0.50 | Professional standards, but not primary source |
| `document_declassified` | 0.80 | Authenticated government records |
| `document_leaked` | 0.60 | Provenance uncertain, but often authentic |
| `sensor` (radar, thermal, photo) | 0.80 | Objective measurement, but interpretation varies |
| `analytical` (expert analysis) | 0.60 | Informed reasoning, but not direct evidence |
| `speculative` (hypothesis, theory) | 0.25 | Conjecture without direct evidence |

### Confidence Modifiers

- **Corroboration**: +0.10 per independent source (max +0.20)
- **Speaker credibility**: ±0.10 based on track record
- **Internal consistency**: -0.15 for contradictions within same source
- **Authentication concerns**: -0.40 for disputed/unverified provenance
- **Time decay**: -0.05 per decade for uncorroborated historical claims

### Final Confidence Score

```
final_confidence = min(1.0, base_weight + corroboration_bonus + speaker_modifier - consistency_penalty - authentication_penalty - time_penalty)
```

---

## CLI Interface

Sherlock provides a comprehensive CLI built with `typer` for all operations.

### Ingest Commands

```bash
# Ingest YouTube video with automatic diarization
sherlock ingest youtube <url> [--auto-diarize] [--speaker-anchors speaker1.json,speaker2.json]

# Ingest local audio/video file
sherlock ingest media <file_path> [--auto-diarize] [--speaker-anchors anchors.json]

# Ingest PDF document
sherlock ingest document <file_path> [--extract-claims] [--speaker speaker_id]

# Batch ingest from directory
sherlock ingest batch <directory> [--pattern "*.mp4"] [--auto-diarize]
```

### Diarization Commands

```bash
# Run unsupervised diarization
sherlock diarize <media_id> [--model tiny|base] [--vad-mode aggressive|moderate] [--clustering hdbscan]

# Run supervised diarization with speaker anchors
sherlock diarize <media_id> --anchors speaker1.json,speaker2.json [--threshold 0.75]

# Export diarization results
sherlock diarize export <run_id> [--format json|txt|srt]

# Map local speakers to global identities
sherlock speaker map <local_speaker_id> <global_speaker_id> [--confidence 0.90]
```

### Query Commands

```bash
# Full-text search across all claims
sherlock search "operation mockingbird" [--limit 50]

# Query by speaker
sherlock query speaker <speaker_id> [--time-range 1950-1980]

# Query by source
sherlock query source <source_id>

# Query by entity
sherlock query entity "CIA" [--entity-type organization]

# Query by operation/tag
sherlock query operation "gladio" [--include-cross-refs]

# Timeline query
sherlock query timeline --start 1953-01-01 --end 1973-12-31 [--speakers allen_dulles,frank_wisner]
```

### Analysis Commands

```bash
# Generate intelligence report for operation
sherlock analyze report <operation_name> [--output report.md]

# Cross-reference analysis between operations
sherlock analyze cross-ref <op1> <op2> [--output cross_ref.md]

# Speaker network analysis
sherlock analyze network <speaker_id> [--depth 2] [--output network.json]

# Pattern detection across operations
sherlock analyze patterns [--min-confidence 0.6] [--output patterns.md]

# Confidence aggregation for claim
sherlock analyze confidence <claim_id> [--explain]
```

### Targets Library Commands

```bash
# Add new research target
sherlock targets add <name> --type [person|org|event|location|tech|operation] --priority [1-5]

# List targets
sherlock targets list [--status new|under_research|validated|closed] [--priority 1]

# Update target status
sherlock targets update <target_id> --status under_research

# Show target details
sherlock targets show <target_id>
```

### Package Workflow Commands

```bash
# Create new targeting package
sherlock pkg create --target <target_id> --version 1 [--type youtube|document|composite]

# Edit package plan (opens editor)
sherlock pkg edit <package_id>

# Validate package (V0: schema, V1: execution, V2: output conformance)
sherlock pkg validate --package <package_id> --level [0|1|2]

# Submit package to J5A overnight queue
sherlock pkg submit --package <package_id>

# Check package status
sherlock pkg status <package_id>

# List all packages
sherlock pkg list [--status draft|ready|submitted|running|completed]

# Ingest package outputs into evidence database
sherlock pkg ingest --package <package_id>

# Mark package as validated and closed
sherlock pkg close --package <package_id>
```

### Targeting Officer Commands

```bash
# Run Targeting Officer once (check targets, generate plans, submit packages)
sherlock officer run --once

# Run Targeting Officer daemon (continuous monitoring)
sherlock officer run --daemon [--interval 3600]

# Generate daily/weekly report
sherlock officer report --daily [--output report.md]
sherlock officer report --weekly [--output report.md]

# Manual package replanning
sherlock officer replan --package <package_id>
```

### Speaker Management Commands

```bash
# Add new global speaker
sherlock speaker add <name> [--title "Title"] [--org "Organization"] [--embedding embedding.npy]

# List all speakers
sherlock speaker list [--organization CIA] [--active-after 1950-01-01]

# Merge speakers (alias resolution)
sherlock speaker merge <speaker_id1> <speaker_id2> --primary <speaker_id1>

# Update speaker profile
sherlock speaker update <speaker_id> [--title "New Title"] [--org "New Org"]
```

### Database Management Commands

```bash
# Initialize database schema
sherlock db init

# Run migrations
sherlock db migrate

# Export database to JSON
sherlock db export [--output export.json]

# Import database from JSON
sherlock db import <file_path>

# Reset database (DANGER: deletes all data)
sherlock db reset --confirm

# Database statistics
sherlock db stats
```

---

## Targeting Officer

The **Targeting Officer** is an automated system that ensures research targets have valid targeting packages, generates collection plans, submits them via J5A handoff, validates execution, and ingests outputs.

### Responsibilities

1. **Target Monitoring**: Identify targets in `new` or `under_research` status without valid packages
2. **Package Generation**: Create targeting packages with collection URLs and expected outputs
3. **Validation**: Perform V0 (schema), V1 (execution), V2 (output conformance) validation
4. **Submission**: Submit validated packages to J5A overnight queue via `j5a_handoff` table
5. **Receipt**: Monitor J5A task completion and update package status
6. **Output Ingestion**: Ingest completed package outputs into evidence database
7. **Reporting**: Generate daily/weekly reports on targeting efficacy

### Package Lifecycle

```
draft → ready → submitted → accepted → queued → running → completed → outputs_ingested → validated → closed
```

**Failure States**: Any state can transition to `failed` with reason in `package_status_history`. Failed packages trigger replanning.

### Validation Levels

- **V0 (Schema)**: Package has required fields (URLs, expected outputs, plan summary). Required before submission.
- **V1 (Execution)**: J5A task executed without errors. Checked after J5A completion.
- **V2 (Output Conformance)**: All expected outputs generated and valid. Checked before `validated` status.

### J5A Handoff Protocol

1. **Submission**: Targeting Officer creates `j5a_handoff` record with task definition
2. **Acceptance**: J5A queue manager accepts task and updates `j5a_handoff.status = 'accepted'`
3. **Execution**: J5A runs task overnight, updates status to `running` → `completed` or `failed`
4. **Receipt**: Targeting Officer polls `j5a_handoff` table for completion
5. **Ingestion**: If successful, Targeting Officer ingests outputs and updates package status

### Reporting

- **Daily Report**: State totals, new failures, collection efficacy (URLs ingested / URLs planned)
- **Weekly Report**: Trend analysis, target coverage, replanning needs, bottleneck identification

---

## Environment and Constraints

### Hardware

- **System**: Late-2012 Mac mini
- **RAM**: 16GB
- **OS**: Linux Mint MATE
- **CPU**: Intel Core i7 (no GPU)
- **Storage**: SSD with sufficient space for media archives

### Software

- **Python**: 3.10+
- **Database**: SQLite (baseline), optional Postgres + pgvector
- **Speech Recognition**: faster-whisper (tiny/base models, INT8 quantization)
- **VAD**: WebRTC VAD
- **Speaker Embeddings**: Resemblyzer
- **Clustering**: HDBSCAN or anchor-based supervised matching
- **Video Ingest**: yt-dlp, ffmpeg
- **Document Processing**: PDFMiner, OCR (tesseract)
- **CLI**: typer

### Performance Constraints

- **Memory Limit**: 3.0GB safe threshold for long-running processes (J5A constraint)
- **CPU-only**: All ML models must run on CPU (no CUDA/GPU dependencies)
- **Thermal Limit**: 80°C maximum CPU temperature (J5A thermal safety protocol)
- **Processing Time**: Diarization typically 30 minutes per hour of audio (faster-whisper tiny/base)

---

## Example Workflows

### Workflow 1: Ingest and Analyze Congressional Hearing

```bash
# 1. Ingest YouTube hearing with known speakers
sherlock ingest youtube "https://youtube.com/watch?v=..." --speaker-anchors grusch.json,burchett.json

# 2. Run supervised diarization
sherlock diarize <media_id> --anchors grusch.json,burchett.json --threshold 0.75

# 3. Export diarization for review
sherlock diarize export <run_id> --format json > diarization.json

# 4. Query claims by speaker
sherlock query speaker david_grusch --time-range 2023-07-26

# 5. Generate intelligence report
sherlock analyze report "AARO Hearing 2023" --output aaro_hearing_report.md
```

### Workflow 2: Cross-Reference Two Operations

```bash
# 1. Query Operation Mockingbird claims
sherlock query operation "mockingbird" > mockingbird_claims.json

# 2. Query MK-Ultra claims
sherlock query operation "mkultra" > mkultra_claims.json

# 3. Run cross-reference analysis
sherlock analyze cross-ref mockingbird mkultra --output mockingbird_mkultra_cross_ref.md

# 4. Search for shared entities
sherlock search "Sidney Gottlieb" --operation mockingbird,mkultra
```

### Workflow 3: Target-Driven Collection with Targeting Officer

```bash
# 1. Add new target
sherlock targets add "AARO" --type org --priority 1

# 2. Create targeting package
sherlock pkg create --target aaro --version 1 --type youtube

# 3. Edit package plan (opens editor)
sherlock pkg edit pkg_aaro_v1

# 4. Validate package schema (V0)
sherlock pkg validate --package pkg_aaro_v1 --level 0

# 5. Submit package to J5A overnight queue
sherlock pkg submit --package pkg_aaro_v1

# 6. Run Targeting Officer to monitor and ingest
sherlock officer run --once

# 7. Check package status
sherlock pkg status pkg_aaro_v1

# 8. Query ingested claims
sherlock query operation "aaro" --output aaro_analysis.md
```

---

## Integration with J5A

Sherlock integrates with the **J5A Overnight Queue/Batch Management System** for resource-intensive operations like overnight collection and processing.

### J5A Handoff Interface

- **Table**: `j5a_handoff`
- **Workflow**: Sherlock creates handoff records → J5A accepts and executes → Sherlock ingests outputs
- **Constraints**: 3.0GB memory limit, 80°C thermal limit, business hours LibreOffice priority

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
  "priority": 1
}
```

### J5A Validation Protocol

J5A performs statistical validation (3-segment stratified sampling) before resource allocation. Sherlock package validation (V0/V1/V2) complements J5A validation to ensure output delivery.

---

## Future Enhancements

### Phase 1 (Current)
- ✅ Core ingest, diarization, claim extraction
- ✅ Speaker mapping and aliases
- ✅ Full-text search and query interface
- ✅ Intelligence report generation
- ✅ Targets Library and Package Workflow
- ✅ Targeting Officer automation
- ✅ J5A integration

### Phase 2 (Planned)
- Vector embeddings for semantic search (pgvector)
- Entity extraction and relationship mapping
- Advanced pattern detection (temporal, network, linguistic)
- Web UI for visualization and exploration
- Export to graph databases (Neo4j)

### Phase 3 (Future)
- Multi-language support (non-English transcription)
- Real-time streaming ingest
- Collaborative research features
- Encrypted evidence handling
- Mobile companion app

---

## License and Attribution

**Sherlock** is developed by johnny5 as part of the Johny5Alive (J5A) AI systems ecosystem.

**Dependencies**: See `requirements.txt` for complete dependency list and licenses.

**Usage**: Local research and analysis only. Not for production deployment or public-facing services.

---

## Appendix: Integration History

Sherlock currently contains evidence from the following intelligence operations:

1. **Operation Gladio** - NATO stay-behind networks in Europe (1940s-1990s)
2. **Thread 3** - Soviet UFO research program (1978-1993)
3. **JFK Assassination** - Investigation and evidence analysis (1963)
4. **S-Force** - Classified military/intelligence operations
5. **Sullivan & Cromwell** - Corporate-state fusion (Iran 1953, Guatemala 1954, Chile 1973)
6. **TSMC** - Taiwan semiconductor industrial strategy (1987-present)
7. **MK-Ultra** - CIA mind control experiments (1953-1973)
8. **Italy UFO** - Alleged 1933 crash and Gabinetto RS/33 investigation
9. **Operation Mockingbird** - CIA media manipulation network (1950s-1970s+)

Each operation has dedicated integration scripts, intelligence reports, and cross-reference analyses in the `/home/johnny5/Sherlock/` directory.
