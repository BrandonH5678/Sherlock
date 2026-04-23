#!/usr/bin/env python3
"""Generated diarization script for Buhler/Exodus Propulsion episode"""

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

from pyannote.audio import Pipeline
import whisperx
import pandas as pd

EPISODE_DIR = Path("/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/buhler_exodus_mOWwdIuyaQA")
ALIGNED_JSON = EPISODE_DIR / "audio_transcription" / "alignment_audio_enhanced" / "audio_aligned.json"
WAV_FILE = EPISODE_DIR / "audio_diarize.wav"
OUTPUT_DIR = EPISODE_DIR / "audio_transcription" / "alignment_audio_enhanced" / "diarization_audio_aligned"
OUTPUT_FILE = OUTPUT_DIR / "audio_diarized.json"

# Load HF token
hf_token = "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"

# Load aligned transcript
with open(ALIGNED_JSON, "r") as f:
    data = json.load(f)
    aligned_segments = {"segments": data["segments"]}

# Initialize diarization pipeline
diarization_pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=hf_token
)

device = "cuda" if torch.cuda.is_available() else "cpu"
diarization_pipeline.to(torch.device(device))

# Run diarization — 3 speakers: Jesse Michels (host), Dr. Buhler (main), David Chester (enters ~1:52:26)
print("Running diarization (min_speakers=2, max_speakers=3)...")
diarization = diarization_pipeline(str(WAV_FILE), min_speakers=2, max_speakers=3)

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
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_FILE, 'w') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"✓ Diarized transcript saved: {OUTPUT_FILE}")

# Print speaker distribution
from collections import Counter
speaker_counts = Counter()
for seg in result["segments"]:
    spk = seg.get("speaker", "UNKNOWN")
    speaker_counts[spk] += 1
for spk, count in speaker_counts.most_common():
    pct = count / len(result["segments"]) * 100
    print(f"  {spk}: {count} segments ({pct:.1f}%)")
