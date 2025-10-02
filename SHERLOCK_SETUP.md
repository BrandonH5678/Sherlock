# Sherlock Intelligence Analysis System - Setup Guide

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/BrandonH5678/Sherlock.git
   cd Sherlock
   ```

2. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Verify databases are present:**
   ```bash
   ls -lh *.db
   # Should see: evidence.db, gladio_intelligence.db, etc.
   ```

4. **Run a test query:**
   ```bash
   python3 src/sherlock_query_minimal.py "What was Operation Gladio?"
   ```

## What's Included in the Repository

### ✅ Core Intelligence Data (All Included)
- **Evidence databases** (~700KB total via Git LFS)
  - `evidence.db` - Main evidence and claims database
  - `gladio_intelligence.db` - Operation Gladio analysis
  - Additional operation databases

- **Evidence documents** (~64MB)
  - Congressional testimonies (Knapp, Hardway)
  - Declassified documents (Thread 3, S-Force)
  - Intelligence reports and cross-references

- **Analysis outputs** (~16MB)
  - `resource_flows.json` - Gladio resource flow analysis (17+ hours of processing)
  - Entity dossiers and relationship mappings
  - Timeline reconstructions
  - Intelligence synthesis reports

- **Source code**
  - Query engines (minimal, hybrid, MMR)
  - Intelligence extractors and builders
  - Cross-reference tools
  - Targeting officer CLI

### ❌ Files NOT Included (Must Obtain Separately)

#### 1. Audio Source Files (~2-4GB)
**Why excluded:** GitHub has 100MB file limits; audiobooks are copyrighted material

**Operation Gladio audiobook:**
- Title: "Operation Gladio: The Unholy Alliance Between the Vatican, the CIA, and the Mafia"
- Author: Paul L. Williams
- Format: Audible audiobook or MP3

**Where to obtain:**
- Audible.com
- Your local library (digital audiobook lending)
- Purchase from major retailers

**Setup after obtaining:**
```bash
mkdir -p audiobooks/operation_gladio
# Place your audio file here:
# audiobooks/operation_gladio/Operation_Gladio.mp3
# (or .aaxc for Audible format)
```

#### 2. Large Visualizations (Regenerable)
**Why excluded:** 51MB PNG network visualization

**Files:**
- `audiobooks/operation_gladio/gladio_network.png` - Network graph visualization

**How to regenerate:**
```bash
# Requires graphviz installed
sudo apt-get install graphviz
python3 gladio_network_builder.py
# Generates PNG from existing .dot/.svg/.pdf files (which ARE included)
```

## System Requirements

### Minimum:
- Python 3.10+
- 4GB RAM (for basic queries)
- 10GB disk space

### Recommended:
- Python 3.12
- 8GB+ RAM (for large-scale analysis)
- 20GB+ disk space (if processing audio files)

### Optional (for audio processing):
- ffmpeg (for audio decoding)
- audible-cli (for .aaxc conversion)

## Architecture Overview

```
Sherlock/
├── evidence.db              # Main SQLite database with claims/speakers/evidence
├── src/
│   ├── sherlock_query_minimal.py    # Simple query interface
│   ├── sherlock_hybrid_retriever.py # Advanced semantic search
│   └── sherlock_targeting_officer.py # Intelligence targeting CLI
├── evidence/                # Source documents (PDFs, text files)
├── audiobooks/              # Audio processing outputs (JSON, checkpoints)
│   └── operation_gladio/
│       ├── entity_dossiers.json     # 17+ hours of entity extraction
│       ├── resource_flows.json      # Resource flow analysis
│       └── entity_checkpoints/      # Incremental saves
└── research_outputs/        # Automated research package outputs
```

## Intelligence Operations Available

The system includes complete intelligence analysis for:

1. **Operation Gladio** (NATO stay-behind networks, 1940s-1990s)
2. **Thread 3** (Soviet UFO research, 1978-1993)
3. **JFK Assassination** (1963 investigation)
4. **S-Force** (Classified military/intelligence operations)
5. **Sullivan & Cromwell** (Corporate-state fusion)
6. **MK-Ultra** (CIA mind control experiments, 1953-1973)
7. **Italy UFO** (1933 crash, Gabinetto RS/33)
8. **Operation Mockingbird** (CIA media manipulation)
9. **TSMC** (Taiwan semiconductor strategy)

## Usage Examples

### Basic Query:
```bash
python3 src/sherlock_query_minimal.py "Who ran Operation Mockingbird?"
```

### Advanced Semantic Search:
```bash
python3 src/sherlock_hybrid_retriever.py \
  --query "CIA operations in Italy during 1950s" \
  --operation gladio \
  --top-k 10
```

### Generate Intelligence Report:
```bash
python3 sherlock_targeting_cli.py --operation gladio --report
```

### Cross-Reference Analysis:
```bash
python3 cross_reference_sforce_jfk.py
# Generates: SFORCE_JFK_CROSS_REFERENCE.md
```

## Processing Your Own Audio

If you have audio files to analyze:

1. Place audio in `audiobooks/[operation_name]/`
2. Run extraction with checkpointing:
   ```bash
   python3 gladio_batch_entity_extractor.py \
     --audio audiobooks/operation_gladio/Operation_Gladio.mp3 \
     --checkpoint-dir audiobooks/operation_gladio/entity_checkpoints
   ```

3. Build intelligence products:
   ```bash
   python3 gladio_dossier_builder.py
   python3 gladio_timeline_constructor.py
   python3 gladio_network_builder.py
   ```

## Troubleshooting

### "Database is locked" error:
```bash
# Close any other processes accessing the database
pkill -f sherlock
# Or use a different database connection
sqlite3 evidence.db .timeout 10000
```

### "No module named anthropic":
```bash
pip3 install anthropic
export ANTHROPIC_API_KEY="your-key-here"
```

### Missing graphviz:
```bash
sudo apt-get update
sudo apt-get install graphviz
```

## Data Integrity

All evidence and analysis is:
- **Traceable** - Every claim links to source with timestamps/page numbers
- **Confidence-weighted** - 0.0-1.0 scale based on evidence type
- **Cross-referenced** - Entities and events linked across operations
- **Incremental** - Checkpointed processing prevents data loss

## Contributing

When adding new intelligence operations:

1. Create evidence files in `evidence/`
2. Use incremental checkpoint pattern (see gladio_batch_entity_extractor.py)
3. Update cross-reference matrices
4. Generate intelligence reports with synthesis

## License & Ethical Use

This system is designed for:
- ✅ Historical research and analysis
- ✅ Pattern recognition in declassified intelligence
- ✅ Cross-referencing public domain evidence
- ✅ Educational purposes

NOT for:
- ❌ Creating or spreading disinformation
- ❌ Targeting individuals
- ❌ Illegal intelligence gathering

All evidence sources are public domain or fair use educational material.

## Support

- Issues: https://github.com/BrandonH5678/Sherlock/issues
- Documentation: See intelligence reports in repository root
- Example queries: See `TARGETING_OFFICER.md`
