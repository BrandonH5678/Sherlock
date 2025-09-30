#!/usr/bin/env python3
"""
Test script for dual-engine voice processing system
"""

import sys
import time
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from voice_engine import VoiceEngineManager, TranscriptionMode, ProcessingPriority


def test_system_startup():
    """Test that the voice engine starts and loads correctly"""
    print("🧪 Testing Voice Engine Startup...")

    engine = VoiceEngineManager()
    status = engine.get_status()

    print(f"Available engines: {status['available_engines']}")
    print(f"Models loaded: {status['models_loaded']}")
    print(f"Queue size: {status['queue_size']}")

    return engine


def test_fast_transcription(engine, audio_file):
    """Test fast transcription mode"""
    print(f"\n🧪 Testing Fast Transcription Mode on {audio_file}...")

    results = []

    def callback(result):
        results.append(result)
        print(f"✅ Fast transcription completed:")
        print(f"   Model: {result.model_used}")
        print(f"   Processing time: {result.processing_time:.2f}s")
        print(f"   Confidence: {result.confidence:.3f}")
        print(f"   Text preview: {result.text[:100]}...")

    # Start engine
    engine.start()

    try:
        # Submit transcription request
        engine.transcribe_squirt(
            audio_path=audio_file,
            mode=TranscriptionMode.FAST,
            callback=callback
        )

        # Wait for completion
        timeout = 300  # 5 minutes
        start_time = time.time()

        while len(results) == 0 and (time.time() - start_time) < timeout:
            time.sleep(1)
            print(".", end="", flush=True)

        if len(results) == 0:
            print("\n❌ Fast transcription timed out")
            return False

        return True

    finally:
        engine.stop()


def test_accurate_transcription(engine, audio_file):
    """Test accurate transcription mode"""
    print(f"\n🧪 Testing Accurate Transcription Mode on {audio_file}...")

    results = []

    def callback(result):
        results.append(result)
        print(f"✅ Accurate transcription completed:")
        print(f"   Model: {result.model_used}")
        print(f"   Processing time: {result.processing_time:.2f}s")
        print(f"   Confidence: {result.confidence:.3f}")
        print(f"   Text preview: {result.text[:100]}...")

    # Start engine
    engine.start()

    try:
        # Submit transcription request
        engine.transcribe_squirt(
            audio_path=audio_file,
            mode=TranscriptionMode.ACCURATE,
            callback=callback
        )

        # Wait for completion
        timeout = 1200  # 20 minutes
        start_time = time.time()

        while len(results) == 0 and (time.time() - start_time) < timeout:
            time.sleep(2)
            print(".", end="", flush=True)

        if len(results) == 0:
            print("\n❌ Accurate transcription timed out")
            return False

        return True

    finally:
        engine.stop()


def main():
    """Main test function"""
    if len(sys.argv) < 2:
        print("Usage: python test_voice_engine.py <audio_file>")
        print("Example: python test_voice_engine.py anchors/A.wav")
        sys.exit(1)

    audio_file = sys.argv[1]

    if not Path(audio_file).exists():
        print(f"❌ Audio file not found: {audio_file}")
        sys.exit(1)

    print("🚀 Starting Voice Engine Testing Suite")
    print("=" * 50)

    # Test 1: System startup
    engine = test_system_startup()

    # Test 2: Fast transcription
    if not test_fast_transcription(engine, audio_file):
        print("❌ Fast transcription test failed")
        return False

    # Test 3: Accurate transcription (if time permits)
    print(f"\n⏳ Starting accurate transcription test (may take 15-20 minutes)...")
    proceed = input("Proceed with accurate mode test? (y/N): ")

    if proceed.lower() == 'y':
        if not test_accurate_transcription(engine, audio_file):
            print("❌ Accurate transcription test failed")
            return False
    else:
        print("⏭️ Skipping accurate transcription test")

    print("\n✅ All tests completed successfully!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)