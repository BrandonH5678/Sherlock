#!/usr/bin/env python3
"""Generated WhisperX alignment script for Buhler/Exodus Propulsion episode"""

import sys
import json
import re
from pathlib import Path

# Fix PyTorch 2.8+ weights_only issue
import torch
torch.serialization.add_safe_globals([torch.torch_version.TorchVersion])
_orig_load = torch.load
def _patched_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _orig_load(*args, **kwargs)
torch.load = _patched_load

import whisperx

EPISODE_DIR = Path("/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/buhler_exodus_mOWwdIuyaQA")
TRANSCRIPT_JSON = EPISODE_DIR / "audio.json"
AUDIO_FILE = EPISODE_DIR / "audio.mp3"
OUTPUT_FILE = EPISODE_DIR / "audio_transcription" / "alignment_audio_enhanced" / "audio_aligned.json"

# Load faster-whisper transcript
with open(TRANSCRIPT_JSON, "r") as f:
    transcript = json.load(f)

# Separate segments with markers ([inaudible], [unclear]) from alignable segments
marker_pattern = re.compile(r'^\s*\[(inaudible|unclear)[^\]]*\]\s*$', re.IGNORECASE)
alignable_segments = []
marker_segments = []

for seg in transcript.get("segments", []):
    text = seg.get("text", "").strip()
    if marker_pattern.match(text):
        marker_segments.append(seg)
    else:
        alignable_segments.append(seg)

print(f"Segments: {len(alignable_segments)} alignable, {len(marker_segments)} markers preserved")

# Load audio
audio = whisperx.load_audio(str(AUDIO_FILE))

# Detect language
language = transcript.get("language", "en")

# Load alignment model
device = "cuda" if torch.cuda.is_available() else "cpu"
model_a, metadata = whisperx.load_align_model(
    language_code=language,
    device=device
)

# Run alignment
print(f"Running alignment on {device}...")
result = whisperx.align(
    alignable_segments,
    model_a,
    metadata,
    audio,
    device,
    return_char_alignments=False
)

# Merge marker segments back in (sorted by start time)
all_segments = result["segments"] + marker_segments
all_segments.sort(key=lambda s: s.get("start", 0))
result["segments"] = all_segments

# Save output
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_FILE, 'w') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"✓ Aligned transcript saved: {OUTPUT_FILE}")
print(f"  Total segments: {len(all_segments)}")
