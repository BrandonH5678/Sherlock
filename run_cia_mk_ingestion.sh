#!/bin/bash
# Full pipeline: Download + Transcribe + Intelligence Extraction
# Video: "Exposing the CIA's Darkest Mind Control Secrets" (2:02:30)
# Background task launched 2026-04-03

set -e
LOGFILE="/home/johnny5/Sherlock/freelance_transcripts/cia_mind_control/pipeline.log"
EPISODE_JSON="/home/johnny5/Sherlock/freelance_transcripts/cia_mind_control/episode.json"
OUTPUT_DIR="/home/johnny5/Sherlock/freelance_transcripts/cia_mind_control/cia_darkest_mind_control"

exec > >(tee -a "$LOGFILE") 2>&1
echo "=== Pipeline started: $(date -u) ==="

# Phase 1: Download + Transcribe via existing pipeline
echo "--- Phase 1: Download & Transcription ---"
python3 /home/johnny5/Sherlock/process_sherlock_transcription.py "$EPISODE_JSON"

# Check transcription succeeded
if [ ! -f "$OUTPUT_DIR/audio.txt" ]; then
    echo "FATAL: Transcription failed — no audio.txt produced"
    exit 1
fi

WORD_COUNT=$(wc -w < "$OUTPUT_DIR/audio.txt")
echo "Transcript ready: $WORD_COUNT words"

# Phase 2: Intelligence Extraction
echo "--- Phase 2: Intelligence Extraction ---"
python3 - <<'PYEOF'
import json
from pathlib import Path
from datetime import datetime

output_dir = Path("/home/johnny5/Sherlock/freelance_transcripts/cia_mind_control/cia_darkest_mind_control")
evidence_dir = Path("/home/johnny5/Sherlock/evidence")
transcript_file = output_dir / "audio.txt"

# Read transcript
transcript = transcript_file.read_text()
word_count = len(transcript.split())

# Read metadata if available
metadata = {}
meta_file = output_dir / "metadata.json"
if meta_file.exists():
    with open(meta_file) as f:
        metadata = json.load(f)

# Generate intelligence extraction template
title = metadata.get("title", "Exposing the CIA's Darkest Mind Control Secrets")
channel = metadata.get("channel", "Unknown")
duration = metadata.get("duration", 7350)

# Create evidence file with transcript and extraction markers
report_path = evidence_dir / "cia_darkest_mind_control_transcript.md"
report_path.write_text(f"""# Intelligence Transcript: {title}

## Source Metadata
- **Title:** {title}
- **Channel:** {channel}
- **Duration:** {duration // 60}m {duration % 60}s
- **Word Count:** {word_count:,}
- **Source URL:** https://youtu.be/UrHLTFvdEZk
- **Ingestion Date:** {datetime.now().strftime('%Y-%m-%d')}
- **Pipeline:** Freelance Transcription (process_sherlock_transcription.py)
- **Model:** faster-whisper large-v3 (GPU)
- **Intelligence Context:** MK Programs — aligns with PKG-MK campaign

## Status
- [x] Downloaded
- [x] Transcribed
- [ ] Intelligence extraction pending (Claude analysis)

## Raw Transcript

{transcript}
""")

# Also save a processing receipt
receipt = {
    "episode_id": "CIA_MK_001",
    "title": title,
    "url": "https://youtu.be/UrHLTFvdEZk",
    "word_count": word_count,
    "transcript_path": str(transcript_file),
    "evidence_path": str(report_path),
    "ingestion_timestamp": datetime.now().isoformat(),
    "status": "transcript_ready",
    "next_step": "intelligence_extraction_by_claude"
}

receipt_path = output_dir / "ingestion_receipt.json"
with open(receipt_path, 'w') as f:
    json.dump(receipt, f, indent=2)

print(f"Evidence file: {report_path}")
print(f"Receipt: {receipt_path}")
print(f"Words: {word_count:,}")
print("READY FOR INTELLIGENCE EXTRACTION")
PYEOF

echo "=== Pipeline complete: $(date -u) ==="
echo "Next: Run Claude intelligence extraction on evidence/cia_darkest_mind_control_transcript.md"
