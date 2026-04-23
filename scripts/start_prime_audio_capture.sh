#!/bin/bash
# Start Audio Capture for Prime Video
# Records audio while you watch in your existing Firefox window

set -euo pipefail

OUTPUT_DIR="${1:-/home/johnny5/Sherlock/prime_video_processing/age_of_disclosure}"

echo "========================================================================"
echo "PRIME VIDEO AUDIO CAPTURE"
echo "========================================================================"
echo "Output: $OUTPUT_DIR"
echo "========================================================================"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Set up audio loopback
echo "Setting up audio capture..."
SINK_NAME="prime_video_capture"

# Try to create sink (ignore if exists)
pactl load-module module-null-sink sink_name="$SINK_NAME" sink_properties=device.description="Prime_Video_Capture" 2>/dev/null || {
    echo "Audio sink may already exist - continuing..."
}

# Try to create loopback (ignore if exists)
pactl load-module module-loopback source="${SINK_NAME}.monitor" 2>/dev/null || {
    echo "Loopback may already exist - continuing..."
}

echo "✅ Audio system ready"
echo ""

# Show instructions
echo "========================================================================"
echo "NEXT STEPS:"
echo "========================================================================"
echo "1. Open PulseAudio Volume Control:"
echo "   pavucontrol &"
echo ""
echo "2. In the 'Playback' tab, find Firefox"
echo "   Change its output to: 'Prime_Video_Capture'"
echo ""
echo "3. Press Enter here when ready to start recording..."
echo "========================================================================"
echo ""

read -p "Press Enter to start recording..."

# Start FFmpeg recording
echo ""
echo "🔴 RECORDING STARTED"
echo ""
echo "Now:"
echo "  1. Go to your Firefox window with Age of Disclosure"
echo "  2. Enable Closed Captions (CC)"
echo "  3. Press Play"
echo "  4. Let it run for 1hr 50min"
echo "  5. Press Ctrl+C here when done"
echo ""
echo "Recording to: $OUTPUT_DIR/raw_audio.mp3"
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
        DURATION=$(ffprobe -i "$OUTPUT_DIR/raw_audio.mp3" -show_entries format=duration -v quiet -of csv="p=0" 2>/dev/null | awk '{print int($1/60)" min"}')
        echo "📁 Audio file: $SIZE ($DURATION)"
        echo "📂 Location: $OUTPUT_DIR/raw_audio.mp3"
    fi

    echo ""
    echo "Next: Process with Whisper"
    echo "  source /home/johnny5/Sherlock/primevideo_env/bin/activate"
    echo "  python3 -c \""
    echo "import sys"
    echo "sys.path.insert(0, '/home/johnny5/Sherlock')"
    echo "from voice_engine import VoiceEngineManager"
    echo "from intelligent_model_selector import QualityPreference"
    echo "voice = VoiceEngineManager(max_ram_gb=16.0)"
    echo "result = voice.transcribe_sherlock('$OUTPUT_DIR/raw_audio.mp3', QualityPreference.BALANCED)"
    echo "import json"
    echo "with open('$OUTPUT_DIR/transcript.json', 'w') as f:"
    echo "    json.dump({'text': result.text, 'segments': result.segments if hasattr(result, 'segments') else []}, f, indent=2)"
    echo "print('Transcript saved to: $OUTPUT_DIR/transcript.json')"
    echo "\""
}

trap cleanup EXIT INT TERM

# Start recording
ffmpeg -f pulse -i "${SINK_NAME}.monitor" -acodec libmp3lame -q:a 0 -y "${OUTPUT_DIR}/raw_audio.mp3" 2>&1 | grep --line-buffered -E "(size=|time=)" &

FFMPEG_PID=$!

# Wait for FFmpeg or Ctrl+C
wait $FFMPEG_PID 2>/dev/null || true
