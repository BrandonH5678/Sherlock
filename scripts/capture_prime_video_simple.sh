#!/bin/bash
# Simple Prime Video Capture Using Existing Firefox
# Controls your logged-in Firefox browser to play and capture Age of Disclosure

set -euo pipefail

# Configuration
VIDEO_URL="$1"
RUNTIME_MINUTES="${2:-110}"
OUTPUT_DIR="$3"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================================================"
echo "SIMPLE PRIME VIDEO CAPTURE"
echo "========================================================================"
echo "Video URL: $VIDEO_URL"
echo "Runtime: $RUNTIME_MINUTES minutes"
echo "Output: $OUTPUT_DIR"
echo "========================================================================"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Set up audio loopback
echo -e "${GREEN}Setting up audio capture...${NC}"
SINK_NAME="prime_video_capture"

pactl load-module module-null-sink sink_name="$SINK_NAME" sink_properties=device.description="Prime_Video_Capture" 2>/dev/null || {
    echo "Audio sink already exists or error - continuing..."
}

pactl load-module module-loopback source="${SINK_NAME}.monitor" 2>/dev/null || {
    echo "Loopback already exists - continuing..."
}

echo -e "${GREEN}✅ Audio loopback ready${NC}"
echo ""

# Start audio capture in background
echo -e "${GREEN}Starting audio recording...${NC}"
ffmpeg -f pulse -i "${SINK_NAME}.monitor" -acodec libmp3lame -q:a 0 -y "${OUTPUT_DIR}/raw_audio.mp3" 2>&1 | grep -v "^size=" &
FFMPEG_PID=$!
echo -e "${GREEN}✅ Recording to: ${OUTPUT_DIR}/raw_audio.mp3 (PID: $FFMPEG_PID)${NC}"
echo ""

# Wait for FFmpeg to initialize
sleep 2

# Open video in Firefox
echo -e "${GREEN}Opening video in Firefox...${NC}"
firefox "$VIDEO_URL" &
FIREFOX_PID=$!
sleep 5

echo ""
echo "========================================================================"
echo "MANUAL STEPS REQUIRED:"
echo "========================================================================"
echo "1. In the Firefox window that just opened:"
echo "   - Enable Closed Captions (CC button)"
echo "   - Click Play"
echo ""
echo "2. The video will capture for $RUNTIME_MINUTES minutes"
echo ""
echo "3. Audio is being recorded automatically"
echo ""
echo "4. Press Ctrl+C in this terminal when the video ends (or wait)"
echo "========================================================================"
echo ""

# Function to cleanup
cleanup() {
    echo ""
    echo -e "${GREEN}Stopping capture...${NC}"

    # Kill FFmpeg
    if kill -0 $FFMPEG_PID 2>/dev/null; then
        kill $FFMPEG_PID
        wait $FFMPEG_PID 2>/dev/null || true
    fi

    # Remove audio loopback
    for module in $(pactl list short modules | grep "$SINK_NAME" | cut -f1); do
        pactl unload-module $module 2>/dev/null || true
    done

    echo -e "${GREEN}✅ Capture stopped${NC}"
    echo ""
    echo "Output saved to: ${OUTPUT_DIR}/raw_audio.mp3"
    echo ""

    # Check audio file
    if [ -f "${OUTPUT_DIR}/raw_audio.mp3" ]; then
        SIZE=$(du -h "${OUTPUT_DIR}/raw_audio.mp3" | cut -f1)
        echo -e "${GREEN}Audio file: $SIZE${NC}"
    fi
}

trap cleanup EXIT INT TERM

# Wait for specified runtime
echo "Capturing... (Press Ctrl+C to stop early)"
sleep $(($RUNTIME_MINUTES * 60))

echo ""
echo -e "${GREEN}Runtime complete!${NC}"
