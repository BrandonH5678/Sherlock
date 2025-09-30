#!/usr/bin/env python3
"""
Quick 30-second sample validator for Operation Gladio chunks
"""

import sys
import subprocess
from pathlib import Path
from faster_whisper import WhisperModel

def quick_validate(chunk_number: int = 1):
    """Validate first 30 seconds of a chunk"""

    chunk_dir = Path("/home/johnny5/Sherlock/audiobooks/operation_gladio/decrypted/processing_chunks")
    chunk_file = chunk_dir / f"chunk_{chunk_number:03d}.wav"
    sample_file = f"/tmp/gladio_sample_{chunk_number}.wav"

    if not chunk_file.exists():
        print(f"❌ Chunk file not found: {chunk_file}")
        return

    print(f"🎬 Extracting first 30 seconds of chunk {chunk_number}...")
    cmd = ['ffmpeg', '-y', '-i', str(chunk_file), '-t', '30', '-acodec', 'copy', sample_file]
    subprocess.run(cmd, capture_output=True, check=True)

    print(f"🎤 Loading faster-whisper small model...")
    model = WhisperModel("small", device="cpu", compute_type="int8")

    print(f"🎤 Transcribing 30-second sample...")
    segments, info = model.transcribe(
        sample_file,
        language="en",
        beam_size=5,
        vad_filter=True
    )

    print(f"\n📊 Audio Info:")
    print(f"   Duration: {info.duration:.2f}s")
    print(f"   Language: {info.language} (confidence: {info.language_probability:.2%})")

    # Collect and display segments
    print(f"\n📝 Transcription of first 30 seconds:")
    print("=" * 80)

    all_text = []
    for segment in segments:
        print(f"[{segment.start:5.1f}s] {segment.text}")
        all_text.append(segment.text)

    full_text = " ".join(all_text)

    print("=" * 80)
    print(f"\n📊 Stats: {len(all_text)} segments, {len(full_text.split())} words, {len(full_text)} characters")
    print(f"\n✅ Chunk {chunk_number} sample validation complete")

    # Cleanup
    Path(sample_file).unlink(missing_ok=True)

if __name__ == "__main__":
    chunk_num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    quick_validate(chunk_num)