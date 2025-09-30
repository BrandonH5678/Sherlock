#!/usr/bin/env python3
"""
Quick validator to check transcription quality of individual Operation Gladio chunks
"""

import sys
from pathlib import Path
from faster_whisper import WhisperModel

def validate_chunk(chunk_number: int = 1):
    """Transcribe a specific chunk and display results"""

    chunk_dir = Path("/home/johnny5/Sherlock/audiobooks/operation_gladio/decrypted/processing_chunks")
    chunk_file = chunk_dir / f"chunk_{chunk_number:03d}.wav"

    if not chunk_file.exists():
        print(f"❌ Chunk file not found: {chunk_file}")
        return

    print(f"🎤 Loading faster-whisper small model...")
    model = WhisperModel("small", device="cpu", compute_type="int8")

    print(f"🎤 Transcribing chunk {chunk_number}...")
    segments, info = model.transcribe(
        str(chunk_file),
        language="en",
        beam_size=5,
        vad_filter=True
    )

    print(f"\n📊 Audio Info:")
    print(f"   Duration: {info.duration:.2f}s ({info.duration/60:.2f} minutes)")
    print(f"   Language: {info.language} (probability: {info.language_probability:.2%})")

    # Collect segments
    all_text = []
    segment_count = 0

    print(f"\n📝 Transcription Preview (first 10 segments):")
    print("-" * 80)

    for i, segment in enumerate(segments):
        segment_count += 1
        all_text.append(segment.text)

        # Show first 10 segments
        if i < 10:
            print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text}")

    full_text = " ".join(all_text)

    print("-" * 80)
    print(f"\n📊 Transcription Stats:")
    print(f"   Total segments: {segment_count}")
    print(f"   Total characters: {len(full_text):,}")
    print(f"   Total words: {len(full_text.split()):,}")
    print(f"\n📝 First 500 characters:")
    print("-" * 80)
    print(full_text[:500])
    print("-" * 80)
    print(f"\n✅ Chunk {chunk_number} validation complete")

if __name__ == "__main__":
    chunk_num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    validate_chunk(chunk_num)