#!/usr/bin/env python3
"""Generated WhisperX alignment script"""

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

# Load faster-whisper transcript
with open("/home/johnny5/Sherlock/freelance_transcripts/weaponized/immaculate_part2/audio_transcription/audio_enhanced.json", "r") as f:
    transcript = json.load(f)

# Separate segments with markers ([inaudible], [unclear]) from alignable segments
# These markers cannot be force-aligned to audio - preserve them with original timestamps
marker_pattern = re.compile(r'^\s*\[(inaudible|unclear)[^\]]*\]\s*$', re.IGNORECASE)
alignable_segments = []
marker_segments = []

for seg in transcript.get("segments", []):
    text = seg.get("text", "").strip()
    if marker_pattern.match(text):
        # Preserve marker segment with original timestamps
        marker_segments.append(seg)
    else:
        alignable_segments.append(seg)

print(f"Segments: {len(alignable_segments)} alignable, {len(marker_segments)} markers preserved")

# Load audio
audio = whisperx.load_audio("/home/johnny5/Sherlock/freelance_transcripts/weaponized/immaculate_part2/audio.mp3")

# Detect language (or use from transcript metadata)
language = transcript.get("language", "en")

# Load alignment model
device = "cuda" if torch.cuda.is_available() else "cpu"
model_a, metadata = whisperx.load_align_model(
    language_code=language,
    device=device
)

# Align only alignable segments (skip markers)
if alignable_segments:
    result_aligned = whisperx.align(
        alignable_segments,
        model_a,
        metadata,
        audio,
        device
    )
else:
    result_aligned = {"segments": [], "word_segments": []}

# Merge marker segments back into aligned result (sorted by start time)
all_segments = result_aligned.get("segments", []) + marker_segments
all_segments.sort(key=lambda x: x.get("start", 0))
result_aligned["segments"] = all_segments

# Save aligned transcript
output_file = Path("/home/johnny5/Sherlock/freelance_transcripts/weaponized/immaculate_part2/audio_transcription/alignment_audio_enhanced") / "audio_aligned.json"
with open(output_file, 'w') as f:
    json.dump(result_aligned, f, indent=2, ensure_ascii=False)

print(f"✓ Word-aligned transcript saved: {output_file}")
print(f"  Total segments: {len(all_segments)} (including {len(marker_segments)} markers)")
