#!/usr/bin/env python3
"""Generated diarization script"""

import sys
import json
from pathlib import Path
import os

# Fix PyTorch 2.8+ weights_only issue
import torch
torch.serialization.add_safe_globals([torch.torch_version.TorchVersion])
_orig_load = torch.load
def _patched_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _orig_load(*args, **kwargs)
torch.load = _patched_load

from pyannote.audio import Pipeline
import whisperx
import pandas as pd

# Load HF token
hf_token = "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"

# Load aligned transcript
with open("/home/johnny5/Sherlock/freelance_transcripts/weaponized/immaculate_part3/audio_transcription/alignment_audio/audio_aligned.json", "r") as f:
    data = json.load(f)
    aligned_segments = {"segments": data["segments"]}

# Initialize diarization pipeline
diarization_pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=hf_token
)

device = "cuda" if torch.cuda.is_available() else "cpu"
diarization_pipeline.to(torch.device(device))

# Run diarization with speaker count hints (if provided)
# pyannote supports: num_speakers, min_speakers, max_speakers
diarization = diarization_pipeline("/home/johnny5/Sherlock/freelance_transcripts/weaponized/immaculate_part3/audio_diarize.wav", num_speakers=3)

print(f"Speaker hints: num_speakers=3")

# Convert to DataFrame
diarization_data = []
for segment, _, speaker in diarization.itertracks(yield_label=True):
    diarization_data.append({
        'start': segment.start,
        'end': segment.end,
        'speaker': speaker
    })

diarize_df = pd.DataFrame(diarization_data)
print(f"Diarization found {len(diarize_df['speaker'].unique())} speakers across {len(diarize_df)} segments")

# Assign speakers to words
result = whisperx.assign_word_speakers(diarize_df, aligned_segments)

# Save output
output_file = Path("/home/johnny5/Sherlock/freelance_transcripts/weaponized/immaculate_part3/audio_transcription/alignment_audio/diarization_audio_aligned") / "audio_diarized.json"
with open(output_file, 'w') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"✓ Diarized transcript saved: {output_file}")
