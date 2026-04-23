#!/bin/bash
# Setup Amazon Prime Video Environment on J5A Server
# Installs all dependencies needed for automated documentary capture

set -euo pipefail

echo "========================================================================"
echo "AMAZON PRIME VIDEO ENVIRONMENT SETUP"
echo "========================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check we're running as johnny5
if [ "$(whoami)" != "johnny5" ]; then
    echo -e "${RED}❌ Must run as johnny5 user${NC}"
    exit 1
fi

echo "Step 1: Creating virtual environment for Prime Video processing..."
echo ""

# Create dedicated venv for Prime Video
VENV_PATH="/home/johnny5/Sherlock/primevideo_env"

if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH" || {
        echo -e "${RED}❌ Failed to create virtual environment${NC}"
        exit 1
    }
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
fi

# Activate venv
source "$VENV_PATH/bin/activate"

echo "Installing browser automation tools in venv..."

# Install Playwright (for browser automation)
pip install playwright pyautogui python-xlib || {
    echo -e "${RED}❌ Failed to install Python packages${NC}"
    exit 1
}

# Install Playwright browsers (use system Firefox instead to save space)
echo -e "${GREEN}✅ Browser automation tools installed${NC}"
echo -e "${YELLOW}Note: Will use system Firefox (/usr/bin/firefox)${NC}"
echo ""

echo "Step 2: Installing OCR tools for subtitle capture..."
echo ""

# Install Tesseract OCR
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng python3-pil || {
    echo -e "${RED}❌ Failed to install Tesseract${NC}"
    exit 1
}

pip install pytesseract Pillow || {
    echo -e "${RED}❌ Failed to install Python OCR packages${NC}"
    exit 1
}

echo -e "${GREEN}✅ OCR tools installed${NC}"
echo ""

echo "Step 3: Installing audio capture tools..."
echo ""

# Install PulseAudio utilities (should already be there on Linux Mint)
sudo apt-get install -y pulseaudio pavucontrol pulseaudio-utils || {
    echo -e "${RED}❌ Failed to install audio tools${NC}"
    exit 1
}

echo -e "${GREEN}✅ Audio capture tools ready${NC}"
echo ""

echo "Step 4: Installing screen recording tools..."
echo ""

# Install screen capture tools
sudo apt-get install -y ffmpeg scrot xdotool wmctrl || {
    echo -e "${RED}❌ Failed to install screen tools${NC}"
    exit 1
}

echo -e "${GREEN}✅ Screen tools installed${NC}"
echo ""

echo "Step 5: Checking Widevine CDM (required for Prime Video DRM)..."
echo ""

# Check if Widevine is installed in Firefox
WIDEVINE_PATH=$(find ~/.mozilla -name "libwidevinecdm.so" 2>/dev/null | head -1)

if [ -z "$WIDEVINE_PATH" ]; then
    echo -e "${YELLOW}⚠️  Widevine CDM not found${NC}"
    echo ""
    echo "To enable Prime Video playback:"
    echo "1. Open Firefox manually: DISPLAY=:0 firefox"
    echo "2. Go to: about:preferences"
    echo "3. Search for: 'DRM'"
    echo "4. Enable: 'Play DRM-controlled content'"
    echo "5. Firefox will auto-download Widevine"
    echo "6. Visit Prime Video to test playback"
    echo ""
    echo "After setup, re-run this script to verify."
else
    echo -e "${GREEN}✅ Widevine CDM found: $WIDEVINE_PATH${NC}"
fi

echo ""
echo "========================================================================"
echo "SETUP SUMMARY"
echo "========================================================================"
echo ""
echo -e "${GREEN}✅ Playwright (browser automation)${NC}"
echo -e "${GREEN}✅ Tesseract OCR (subtitle capture)${NC}"
echo -e "${GREEN}✅ PulseAudio (audio capture)${NC}"
echo -e "${GREEN}✅ FFmpeg (recording)${NC}"

if [ -z "$WIDEVINE_PATH" ]; then
    echo -e "${YELLOW}⚠️  Widevine DRM (needs manual setup)${NC}"
    echo ""
    echo "NEXT STEPS:"
    echo "1. Enable DRM in Firefox (see instructions above)"
    echo "2. Log into Amazon Prime Video"
    echo "3. Get the URL for 'Age of Disclosure'"
    echo "4. Run: source $VENV_PATH/bin/activate && python3 /home/johnny5/Sherlock/scripts/test_prime_video_access.py"
else
    echo -e "${GREEN}✅ Widevine DRM${NC}"
    echo ""
    echo "NEXT STEPS:"
    echo "1. Log into Amazon Prime Video in Firefox"
    echo "2. Get the URL for 'Age of Disclosure'"
    echo "3. Run: source $VENV_PATH/bin/activate && python3 /home/johnny5/Sherlock/scripts/test_prime_video_access.py"
fi

echo ""
echo "Virtual environment created at: $VENV_PATH"
echo "To use: source $VENV_PATH/bin/activate"

echo ""
echo "========================================================================"
echo ""
