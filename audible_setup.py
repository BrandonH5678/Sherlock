#!/usr/bin/env python3
"""
Audible-CLI Setup and Integration for Sherlock
Automated audiobook processing for Operation Gladio intelligence extraction
"""

import subprocess
import sys
import os
from pathlib import Path


def check_prerequisites():
    """Check system prerequisites for audible-cli"""
    print("🔍 Checking prerequisites for audible-cli setup...")

    # Check Python version
    python_version = sys.version_info
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")

    # Check pip
    try:
        subprocess.run(["pip3", "--version"], check=True, capture_output=True)
        print("✅ pip3 available")
    except subprocess.CalledProcessError:
        print("❌ pip3 not available")
        return False

    # Check ffmpeg (required for audio processing)
    try:
        result = subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True, text=True)
        print("✅ ffmpeg available")
    except subprocess.CalledProcessError:
        print("⚠️  ffmpeg not found - required for audio processing")
        print("Install with: sudo apt update && sudo apt install ffmpeg")
        return False

    return True


def install_audible_cli():
    """Install audible-cli and dependencies"""
    print("\n📦 Installing audible-cli...")

    try:
        # Install audible-cli
        subprocess.run([
            "pip3", "install", "audible-cli"
        ], check=True)
        print("✅ audible-cli installed successfully")

        # Install additional audio processing dependencies
        subprocess.run([
            "pip3", "install", "pydub", "mutagen"
        ], check=True)
        print("✅ Audio processing dependencies installed")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False


def setup_audible_auth():
    """Guide user through Audible authentication setup"""
    print("\n🔐 Setting up Audible authentication...")
    print("""
AUDIBLE AUTHENTICATION SETUP:

1. Run: audible quickstart
   - This will guide you through login process
   - Use your Amazon/Audible credentials
   - Choose your locale (US, UK, DE, etc.)

2. Verify setup: audible library
   - Should show your audiobook library

3. For Operation Gladio specifically:
   audible library | grep -i gladio
   - Verify the book is in your library

IMPORTANT NOTES:
- This uses your legitimate Audible account
- Only downloads books you've purchased
- For personal research/analysis use
- Keep authentication secure

Would you like to run the authentication setup now? (y/n)
""")

    response = input().strip().lower()
    if response in ['y', 'yes']:
        try:
            subprocess.run(["audible", "quickstart"], check=True)
            print("✅ Authentication setup completed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Authentication setup failed")
            return False
    else:
        print("⏭️  Authentication setup skipped - run 'audible quickstart' manually later")
        return True


def create_download_script():
    """Create automated download script for Operation Gladio"""
    script_content = '''#!/bin/bash
# Operation Gladio Audiobook Download Script
# Downloads and prepares audiobook for Sherlock processing

echo "🔍 Searching for Operation Gladio in library..."

# Search for the book
BOOK_INFO=$(audible library | grep -i "operation gladio" | head -1)

if [ -z "$BOOK_INFO" ]; then
    echo "❌ Operation Gladio not found in library"
    echo "Please verify:"
    echo "1. Book is purchased in your Audible account"
    echo "2. audible-cli is properly authenticated"
    echo "3. Try: audible library | grep -i gladio"
    exit 1
fi

echo "✅ Found: $BOOK_INFO"

# Extract ASIN (Audible book ID)
ASIN=$(echo "$BOOK_INFO" | awk '{print $1}')
echo "📖 Book ASIN: $ASIN"

# Create download directory
mkdir -p /home/johnny5/Sherlock/audiobooks/operation_gladio
cd /home/johnny5/Sherlock/audiobooks/operation_gladio

echo "⬇️  Downloading Operation Gladio..."

# Download the audiobook
audible download "$ASIN" --output-dir . --decrypt

# Check if download was successful
if [ $? -eq 0 ]; then
    echo "✅ Download completed successfully"

    # List downloaded files
    echo "📁 Downloaded files:"
    ls -la *.mp3 *.m4a *.wav 2>/dev/null || echo "No audio files found"

    # Prepare for Sherlock processing
    echo "🔧 Preparing for Sherlock processing..."

    # Convert to format suitable for voice processing if needed
    for file in *.m4a; do
        if [ -f "$file" ]; then
            echo "🔄 Converting $file to MP3..."
            ffmpeg -i "$file" -codec:a libmp3lame -b:a 128k "${file%.m4a}.mp3"
        fi
    done

    echo "🎯 Ready for Sherlock processing!"
    echo "Next step: python3 /home/johnny5/Sherlock/batch_gladio_processor.py"

else
    echo "❌ Download failed"
    echo "Troubleshooting:"
    echo "1. Check authentication: audible activation"
    echo "2. Verify book ownership: audible library"
    echo "3. Check quota: audible quota"
    exit 1
fi
'''

    script_path = "/home/johnny5/Sherlock/download_gladio.sh"
    with open(script_path, 'w') as f:
        f.write(script_content)

    # Make executable
    os.chmod(script_path, 0o755)

    print(f"✅ Download script created: {script_path}")
    return script_path


def test_audible_cli():
    """Test audible-cli installation and authentication"""
    print("\n🧪 Testing audible-cli installation...")

    try:
        # Test basic audible command
        result = subprocess.run(["audible", "--version"],
                              capture_output=True, text=True, check=True)
        print(f"✅ audible-cli version: {result.stdout.strip()}")

        # Test authentication (this might fail if not set up yet)
        try:
            result = subprocess.run(["audible", "activation"],
                                  capture_output=True, text=True, check=True)
            print("✅ Authentication verified")
            return True
        except subprocess.CalledProcessError:
            print("⚠️  Authentication not configured yet")
            print("Run: audible quickstart")
            return False

    except subprocess.CalledProcessError:
        print("❌ audible-cli not working properly")
        return False


def main():
    """Main setup process"""
    print("🚀 AUDIBLE-CLI SETUP FOR SHERLOCK")
    print("=" * 50)
    print("Setting up automated audiobook processing for Operation Gladio")

    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please install missing components.")
        return False

    # Install audible-cli
    if not install_audible_cli():
        print("\n❌ Installation failed.")
        return False

    # Test installation
    if not test_audible_cli():
        print("\n⚠️  Installation complete but authentication needed.")

    # Setup authentication
    setup_audible_auth()

    # Create download script
    script_path = create_download_script()

    print("\n🎯 SETUP COMPLETE!")
    print("=" * 50)
    print("Next steps:")
    print(f"1. Run authentication if not done: audible quickstart")
    print(f"2. Download Operation Gladio: {script_path}")
    print(f"3. Process with Sherlock: python3 batch_gladio_processor.py")
    print("\nFor troubleshooting:")
    print("- Check library: audible library")
    print("- Verify quota: audible quota")
    print("- Test download: audible download --help")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)