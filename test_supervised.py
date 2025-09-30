#!/usr/bin/env python3
import sys
import time
from resemblyzer import VoiceEncoder, preprocess_wav

print("Testing supervised script components...")

# Test 1: Voice encoder initialization
print("1. Testing VoiceEncoder initialization...")
start = time.time()
try:
    encoder = VoiceEncoder()
    print(f"   ✅ VoiceEncoder loaded in {time.time() - start:.1f}s")
except Exception as e:
    print(f"   ❌ VoiceEncoder failed: {e}")
    sys.exit(1)

# Test 2: Anchor loading
print("2. Testing anchor loading...")
anchors = {"A": "anchors/A.wav", "B": "anchors/B.wav", "C": "anchors/C.wav"}

for label, path in anchors.items():
    start = time.time()
    try:
        wav = preprocess_wav(path)
        emb = encoder.embed_utterance(wav)
        print(f"   ✅ Anchor {label}: {emb.shape} in {time.time() - start:.1f}s")
    except Exception as e:
        print(f"   ❌ Anchor {label} failed: {e}")

# Test 3: Main audio loading (first few seconds only)
print("3. Testing main audio loading...")
try:
    start = time.time()
    wav_full = preprocess_wav("build/yt2_full_stereo.wav")
    print(f"   ✅ Main audio loaded: {len(wav_full)} samples in {time.time() - start:.1f}s")

    # Test small segment embedding
    segment = wav_full[:int(0.9 * 16000)]  # First 0.9 seconds
    start = time.time()
    emb = encoder.embed_utterance(segment)
    print(f"   ✅ Sample embedding: {emb.shape} in {time.time() - start:.1f}s")

except Exception as e:
    print(f"   ❌ Main audio failed: {e}")

print("Component tests completed.")