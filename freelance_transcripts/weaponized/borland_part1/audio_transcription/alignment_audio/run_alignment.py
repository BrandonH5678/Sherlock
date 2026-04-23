#!/usr/bin/env python3
"""Generated WhisperX alignment script"""

import sys
import json
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
with open("/home/johnny5/Sherlock/freelance_transcripts/weaponized/borland_part1/audio_transcription/audio.json", "r") as f:
    transcript = json.load(f)

# Load audio
audio = whisperx.load_audio("/home/johnny5/Sherlock/freelance_transcripts/weaponized/borland_part1/audio.mp3")

# Detect language (or use from transcript metadata)
language = transcript.get("language", "en")

# Load alignment model
device = "cuda" if torch.cuda.is_available() else "cpu"
model_a, metadata = whisperx.load_align_model(
    language_code=language,
    device=device
)

# Align whisper output
result_aligned = whisperx.align(
    transcript["segments"],
    model_a,
    metadata,
    audio,
    device
)

# Save aligned transcript
output_file = Path("/home/johnny5/Sherlock/freelance_transcripts/weaponized/borland_part1/audio_transcription/alignment_audio") / "audio_aligned.json"
with open(output_file, 'w') as f:
    json.dump(result_aligned, f, indent=2, ensure_ascii=False)

print(f"✓ Word-aligned transcript saved: {output_file}")
