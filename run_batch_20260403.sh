#!/bin/bash
# Batch pipeline: Download + Transcribe + Stage for Intelligence Extraction
# 3 videos, ~8.5 hours total audio
# Background task launched 2026-04-03

set -o pipefail
BATCH_DIR="/home/johnny5/Sherlock/freelance_transcripts/batch_20260403"
LOGFILE="$BATCH_DIR/pipeline.log"
EVIDENCE_DIR="/home/johnny5/Sherlock/evidence"
WHISPER_CLI="/home/johnny5/Johny5Alive/j5a-nightshift/faster_whisper_cli.py"

exec > >(tee -a "$LOGFILE") 2>&1
echo "=== Batch pipeline started: $(date -u) ==="

# Define episodes inline (avoids JSON parsing in bash)
declare -a IDS=("CIA_MK_001" "NASA_AG_001" "WEIN_UFO_001")
declare -a TITLES=(
    "Exposing the CIA's Darkest Mind Control Secrets"
    "NASA Chief: We Just Built Antigravity Propulsion!"
    "Eric Weinstein Demands UFO Secrets From Pentagon Scientist"
)
declare -a URLS=(
    "https://youtu.be/UrHLTFvdEZk?si=1d6ELBSXKgHItezh"
    "https://youtu.be/mOWwdIuyaQA?si=drFcrd52EGnpI6eM"
    "https://youtu.be/xnxasfyHtfo?si=nPpLavZo0KY7Dh08"
)
declare -a SLUGS=("cia_darkest_mind_control" "nasa_antigravity_propulsion" "weinstein_pentagon_ufo")

SUCCEEDED=0
FAILED=0

for i in 0 1 2; do
    ID="${IDS[$i]}"
    TITLE="${TITLES[$i]}"
    URL="${URLS[$i]}"
    SLUG="${SLUGS[$i]}"
    OUTDIR="$BATCH_DIR/$SLUG"

    echo ""
    echo "================================================================"
    echo "[$((i+1))/3] $ID: $TITLE"
    echo "================================================================"

    mkdir -p "$OUTDIR"

    # --- Phase 1: Download ---
    AUDIO_FILE="$OUTDIR/audio.mp3"
    if [ -f "$AUDIO_FILE" ]; then
        echo "  SKIP download — audio.mp3 already exists ($(du -h "$AUDIO_FILE" | cut -f1))"
    else
        echo "  Downloading..."
        if yt-dlp --js-runtimes node --remote-components ejs:github \
            --extract-audio --audio-format mp3 --audio-quality 0 \
            --write-info-json \
            -o "$OUTDIR/audio.%(ext)s" \
            "$URL" 2>&1; then
            echo "  Download OK: $(du -h "$AUDIO_FILE" | cut -f1)"
        else
            echo "  DOWNLOAD FAILED — skipping episode"
            FAILED=$((FAILED+1))
            continue
        fi
    fi

    # --- Phase 2: Transcribe ---
    TRANSCRIPT="$OUTDIR/audio.txt"
    if [ -f "$TRANSCRIPT" ]; then
        echo "  SKIP transcription — audio.txt already exists ($(wc -w < "$TRANSCRIPT") words)"
    else
        echo "  Transcribing with faster-whisper large-v3 (GPU)..."
        START_T=$(date +%s)
        if python3 "$WHISPER_CLI" "$AUDIO_FILE" \
            --model large-v3 \
            --output_dir "$OUTDIR" \
            --output_format "txt,json" \
            --prefer_gpu true \
            --word_timestamps 2>&1; then
            END_T=$(date +%s)
            ELAPSED=$((END_T - START_T))
            WORDS=$(wc -w < "$TRANSCRIPT" 2>/dev/null || echo 0)
            echo "  Transcription OK: $WORDS words in ${ELAPSED}s"
        else
            echo "  TRANSCRIPTION FAILED — skipping intelligence staging"
            FAILED=$((FAILED+1))
            continue
        fi
    fi

    # --- Phase 3: Stage for Intelligence Extraction ---
    WORDS=$(wc -w < "$TRANSCRIPT")
    EVIDENCE_FILE="$EVIDENCE_DIR/${SLUG}_transcript.md"

    # Read metadata
    CHANNEL="Unknown"
    DURATION="0"
    META_FILE="$OUTDIR/audio.info.json"
    if [ -f "$META_FILE" ]; then
        CHANNEL=$(python3 -c "import json; d=json.load(open('$META_FILE')); print(d.get('channel','Unknown'))" 2>/dev/null || echo "Unknown")
        DURATION=$(python3 -c "import json; d=json.load(open('$META_FILE')); print(d.get('duration',0))" 2>/dev/null || echo "0")
    fi

    TRANSCRIPT_CONTENT=$(cat "$TRANSCRIPT")

    cat > "$EVIDENCE_FILE" <<MDEOF
# Intelligence Transcript: $TITLE

## Source Metadata
- **Title:** $TITLE
- **Channel:** $CHANNEL
- **Duration:** ${DURATION}s
- **Word Count:** $WORDS
- **Source URL:** $URL
- **Episode ID:** $ID
- **Ingestion Date:** $(date -u +%Y-%m-%d)
- **Pipeline:** Freelance Transcription (batch_20260403)
- **Model:** faster-whisper large-v3 (GPU)

## Status
- [x] Downloaded
- [x] Transcribed
- [ ] Intelligence extraction pending (Claude analysis)

## Raw Transcript

$TRANSCRIPT_CONTENT
MDEOF

    echo "  Evidence staged: $EVIDENCE_FILE ($WORDS words)"

    # Save receipt
    python3 -c "
import json
from datetime import datetime
json.dump({
    'episode_id': '$ID',
    'title': '''$TITLE''',
    'url': '$URL',
    'word_count': $WORDS,
    'transcript_path': '$TRANSCRIPT',
    'evidence_path': '$EVIDENCE_FILE',
    'timestamp': datetime.now().isoformat(),
    'status': 'transcript_ready',
    'next_step': 'intelligence_extraction_by_claude'
}, open('$OUTDIR/ingestion_receipt.json', 'w'), indent=2)
"

    SUCCEEDED=$((SUCCEEDED+1))
    echo "  COMPLETE"
done

echo ""
echo "================================================================"
echo "BATCH COMPLETE: $(date -u)"
echo "  Succeeded: $SUCCEEDED / 3"
echo "  Failed:    $FAILED / 3"
echo "================================================================"
echo ""
echo "Evidence files ready for Claude intelligence extraction:"
for SLUG in "${SLUGS[@]}"; do
    F="$EVIDENCE_DIR/${SLUG}_transcript.md"
    [ -f "$F" ] && echo "  - $F ($(wc -w < "$F") words)"
done
