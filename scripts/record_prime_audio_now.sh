#!/bin/bash
# Record Prime Video Audio Immediately
# Just starts recording - no prompts

set -euo pipefail

OUTPUT_DIR="${1:-/home/johnny5/Sherlock/prime_video_processing/age_of_disclosure}"

echo "========================================================================"
echo "🔴 RECORDING PRIME VIDEO AUDIO"
echo "========================================================================"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Set up audio loopback
SINK_NAME="prime_video_capture"

# Create sink (ignore if exists)
pactl load-module module-null-sink sink_name="$SINK_NAME" sink_properties=device.description="Prime_Video_Capture" 2>/dev/null || true

# Create loopback to hear it (ignore if exists)
pactl load-module module-loopback source="${SINK_NAME}.monitor" 2>/dev/null || true

echo "✅ Audio capture configured"
echo ""
echo "📍 IMPORTANT: Route Firefox audio to 'Prime_Video_Capture'"
echo "   Run: pavucontrol"
echo "   Go to 'Playback' tab"
echo "   Find Firefox, change output to 'Prime_Video_Capture'"
echo ""
echo "🎬 Then press Play in your Firefox window"
echo ""
echo "📁 Recording to: $OUTPUT_DIR/raw_audio.mp3"
echo "⏱️  Press Ctrl+C when video ends (or after ~110 minutes)"
echo ""
echo "========================================================================"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "⏹️  Stopping recording..."

    # Remove audio modules
    for module in $(pactl list short modules | grep "$SINK_NAME" | cut -f1); do
        pactl unload-module $module 2>/dev/null || true
    done

    echo "✅ Recording stopped"
    echo ""

    if [ -f "$OUTPUT_DIR/raw_audio.mp3" ]; then
        SIZE=$(du -h "$OUTPUT_DIR/raw_audio.mp3" | cut -f1)
        echo "📁 Saved: $OUTPUT_DIR/raw_audio.mp3 ($SIZE)"
    fi
}

trap cleanup EXIT INT TERM

# Start recording NOW
ffmpeg -f pulse -i "${SINK_NAME}.monitor" -acodec libmp3lame -q:a 0 -y "${OUTPUT_DIR}/raw_audio.mp3" 2>&1 | grep --line-buffered -E "(size=|time=)"
