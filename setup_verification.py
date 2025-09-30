#!/usr/bin/env python3
"""
Setup Verification for Operation Gladio Automated Processing
Verifies all components are ready for automated intelligence extraction
"""

import subprocess
import sys
import os
from pathlib import Path


def check_system_requirements():
    """Verify all system requirements are met"""
    print("🔍 SYSTEM REQUIREMENTS CHECK")
    print("=" * 40)

    checks = []

    # Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        checks.append(True)
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor} (need 3.8+)")
        checks.append(False)

    # FFmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✅ FFmpeg available")
        checks.append(True)
    except subprocess.CalledProcessError:
        print("❌ FFmpeg not found")
        checks.append(False)

    # Audio processing libraries
    try:
        import pydub
        print("✅ pydub available")
        checks.append(True)
    except ImportError:
        print("❌ pydub not installed (pip3 install pydub)")
        checks.append(False)

    return all(checks)


def check_sherlock_components():
    """Verify Sherlock components are ready"""
    print("\n🔍 SHERLOCK COMPONENTS CHECK")
    print("=" * 40)

    required_files = [
        "voice_engine.py",
        "evidence_schema_gladio.py",
        "batch_gladio_processor.py",
        "audible_setup.py"
    ]

    checks = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
            checks.append(True)
        else:
            print(f"❌ {file} missing")
            checks.append(False)

    return all(checks)


def test_voice_engine():
    """Test voice engine functionality"""
    print("\n🔍 VOICE ENGINE TEST")
    print("=" * 40)

    try:
        # Test basic voice engine import
        sys.path.append('.')
        from voice_engine import VoiceEngineManager
        print("✅ Voice engine import successful")

        # Test initialization
        engine = VoiceEngineManager()
        print("✅ Voice engine initialization successful")
        return True

    except Exception as e:
        print(f"❌ Voice engine test failed: {e}")
        return False


def check_audible_cli():
    """Check audible-cli status"""
    print("\n🔍 AUDIBLE-CLI STATUS")
    print("=" * 40)

    try:
        result = subprocess.run(["audible", "--version"],
                              capture_output=True, text=True, check=True)
        print(f"✅ audible-cli available: {result.stdout.strip()}")

        # Check authentication
        try:
            subprocess.run(["audible", "activation"],
                         capture_output=True, check=True)
            print("✅ Audible authentication configured")
            return True
        except subprocess.CalledProcessError:
            print("⚠️  Audible authentication needed (run: audible quickstart)")
            return False

    except subprocess.CalledProcessError:
        print("❌ audible-cli not installed")
        return False


def generate_setup_instructions():
    """Generate setup instructions based on missing components"""
    print("\n📋 SETUP INSTRUCTIONS")
    print("=" * 40)

    print("""
COMPLETE SETUP PROCESS:

1. Install audible-cli and dependencies:
   python3 audible_setup.py

2. Authenticate with Audible:
   audible quickstart

3. Download Operation Gladio:
   ./download_gladio.sh

4. Process the audiobook:
   python3 batch_gladio_processor.py audiobooks/operation_gladio/*.mp3

5. Analyze results:
   python3 gladio_analysis.py

AUTOMATED WORKFLOW:
- Downloads your purchased audiobook
- Splits into 5-minute segments for processing
- Transcribes each segment with high accuracy
- Extracts entities (people, organizations, dates)
- Builds comprehensive fact library automatically
- Generates intelligence analysis reports

ESTIMATED PROCESSING TIME:
- Download: 5-10 minutes
- Processing: 2-4 hours (depending on book length)
- Analysis: 10-15 minutes

RESULT:
Complete Operation Gladio fact library with:
- People dossiers with temporal timelines
- Organization profiles and relationships
- Resource flow analysis
- Network connection mapping
- Evidence validation and confidence scoring
""")


def main():
    """Main verification process"""
    print("🚀 OPERATION GLADIO SETUP VERIFICATION")
    print("=" * 50)

    # Check system requirements
    system_ok = check_system_requirements()

    # Check Sherlock components
    sherlock_ok = check_sherlock_components()

    # Test voice engine
    voice_ok = test_voice_engine()

    # Check audible-cli
    audible_ok = check_audible_cli()

    # Overall status
    print("\n📊 OVERALL STATUS")
    print("=" * 40)

    if system_ok and sherlock_ok and voice_ok:
        print("✅ Core system ready")

        if audible_ok:
            print("✅ Audible integration ready")
            print("\n🎯 READY FOR AUTOMATED PROCESSING!")
            print("Next step: ./download_gladio.sh")
        else:
            print("⚠️  Audible setup needed")
            print("Next step: python3 audible_setup.py")
    else:
        print("❌ Setup incomplete")
        print("Fix missing components first")

    # Always show setup instructions
    generate_setup_instructions()


if __name__ == "__main__":
    main()