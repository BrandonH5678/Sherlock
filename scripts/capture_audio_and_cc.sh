#!/bin/bash
# Capture Audio + Closed Caption OCR from Prime Video
# Captures both audio stream AND subtitle text with speaker labels

set -euo pipefail

OUTPUT_DIR="${1:-/home/johnny5/Sherlock/prime_video_processing/age_of_disclosure}"

echo "========================================================================"
echo "🔴 PRIME VIDEO: AUDIO + CC CAPTURE"
echo "========================================================================"
echo ""

# Create output directories
mkdir -p "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/cc_screenshots"

# Set up audio loopback
SINK_NAME="prime_video_capture"
pactl load-module module-null-sink sink_name="$SINK_NAME" sink_properties=device.description="Prime_Video_Capture" 2>/dev/null || true
pactl load-module module-loopback source="${SINK_NAME}.monitor" 2>/dev/null || true

echo "✅ Audio capture configured"
echo ""
echo "📍 SETUP REQUIRED:"
echo "   1. Run: pavucontrol"
echo "   2. Playback tab → Firefox → Change to 'Prime_Video_Capture'"
echo "   3. Restart video from beginning (0:00)"
echo "   4. Enable CC (Closed Captions)"
echo "   5. Press Play"
echo ""
echo "📁 Output: $OUTPUT_DIR/"
echo "   - raw_audio.mp3 (audio recording)"
echo "   - cc_labels.jsonl (timestamped CC text with speaker labels)"
echo ""
echo "Starting capture in 5 seconds..."
sleep 5

# Cleanup function
cleanup() {
    echo ""
    echo "⏹️  Stopping capture..."

    # Kill background processes
    jobs -p | xargs -r kill 2>/dev/null || true

    # Remove audio modules
    for module in $(pactl list short modules | grep "$SINK_NAME" | cut -f1); do
        pactl unload-module $module 2>/dev/null || true
    done

    echo "✅ Capture stopped"
    echo ""

    if [ -f "$OUTPUT_DIR/raw_audio.mp3" ]; then
        SIZE=$(du -h "$OUTPUT_DIR/raw_audio.mp3" | cut -f1)
        echo "📁 Audio: $OUTPUT_DIR/raw_audio.mp3 ($SIZE)"
    fi

    if [ -f "$OUTPUT_DIR/cc_labels.jsonl" ]; then
        LINES=$(wc -l < "$OUTPUT_DIR/cc_labels.jsonl")
        echo "📝 CC captures: $LINES entries"
    fi

    echo ""
    echo "Next: Process with Whisper + merge CC labels"
}

trap cleanup EXIT INT TERM

# Start audio capture in background
echo "🎙️  Starting audio recording..."
ffmpeg -f pulse -i "${SINK_NAME}.monitor" -acodec libmp3lame -q:a 0 -y "${OUTPUT_DIR}/raw_audio.mp3" 2>&1 | grep --line-buffered -E "(size=|time=)" &
AUDIO_PID=$!

sleep 2

# Start CC OCR capture in background
echo "📸 Starting CC screenshot capture..."
python3 << PYTHON_SCRIPT &
import time
import subprocess
import json
from datetime import datetime
from pathlib import Path
import re

OUTPUT_DIR = Path("$OUTPUT_DIR")
screenshots_dir = OUTPUT_DIR / "cc_screenshots"
cc_labels_file = OUTPUT_DIR / "cc_labels.jsonl"

# CC region coordinates (bottom 15% of 1920x1080 screen, centered)
# Adjust these if CC appears in different location
CC_X = 300
CC_Y = 900
CC_WIDTH = 1320
CC_HEIGHT = 150

start_time = time.time()
capture_count = 0

with open(cc_labels_file, 'w') as out_file:
    while True:
        try:
            elapsed = time.time() - start_time
            timestamp = f"{int(elapsed//60):02d}:{int(elapsed%60):02d}"

            # Capture screenshot of CC region
            screenshot = screenshots_dir / f"cc_{int(elapsed):06d}.png"

            subprocess.run([
                "scrot",
                "-a", f"{CC_X},{CC_Y},{CC_WIDTH},{CC_HEIGHT}",
                str(screenshot)
            ], check=True, capture_output=True)

            # Run OCR on screenshot
            result = subprocess.run([
                "tesseract",
                str(screenshot),
                "stdout",
                "-l", "eng",
                "--psm", "6"  # Assume uniform block of text
            ], capture_output=True, text=True)

            ocr_text = result.stdout.strip()

            if ocr_text:
                # Try to extract speaker label pattern: [Name]: text
                speaker_match = re.match(r'\[([^\]]+)\]:?\s*(.*)', ocr_text)

                if speaker_match:
                    speaker = speaker_match.group(1)
                    text = speaker_match.group(2)
                else:
                    speaker = None
                    text = ocr_text

                # Save to JSONL
                entry = {
                    "timestamp": timestamp,
                    "elapsed_seconds": elapsed,
                    "speaker": speaker,
                    "text": text,
                    "raw_ocr": ocr_text
                }

                out_file.write(json.dumps(entry) + '\n')
                out_file.flush()

                if speaker:
                    print(f"[{timestamp}] {speaker}: {text[:50]}...")

            capture_count += 1

            # Wait 2 seconds between captures
            time.sleep(2)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"OCR error: {e}")
            time.sleep(2)
            continue

print(f"\nCC OCR complete: {capture_count} captures")
PYTHON_SCRIPT

OCR_PID=$!

echo ""
echo "========================================================================"
echo "🔴 RECORDING IN PROGRESS"
echo "========================================================================"
echo "Audio PID: $AUDIO_PID"
echo "OCR PID: $OCR_PID"
echo ""
echo "Press Ctrl+C when video ends (~110 minutes)"
echo "========================================================================"
echo ""

# Wait for Ctrl+C
wait
