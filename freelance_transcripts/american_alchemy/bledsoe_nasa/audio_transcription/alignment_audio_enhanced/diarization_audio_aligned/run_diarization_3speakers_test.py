#!/usr/bin/env python3
"""
Bledsoe NASA Episode - Fresh Diarization Test
Date: 2026-01-16
Test: Manual speaker hints (num_speakers=3)

Speaker Expectation:
- Speaker 1: Jesse Michels (appearing in 2 acoustic roles)
  - Role A: Narrator/Voiceover (documentary style, studio-recorded)
  - Role B: Interviewer (conversational)
- Speaker 2: Chris Bledsoe (guest)

NOTE: pyannote detects speakers by ACOUSTIC characteristics, not identity.
Therefore we tell pyannote num_speakers=3 because:
- Narrator-Jesse sounds different from Interviewer-Jesse
- The identity merging (Narrator + Interviewer = Jesse) happens in post-processing

This test SKIPS Claude API enhancement.
"""

import sys
import json
from pathlib import Path
import os
from datetime import datetime

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

print("="*70)
print("BLEDSOE NASA - DIARIZATION TEST WITH SPEAKER HINTS")
print("="*70)
print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Load HF token
hf_token_path = Path.home() / ".hf_token"
if hf_token_path.exists():
    hf_token = hf_token_path.read_text().strip()
else:
    raise ValueError("HuggingFace token not found at ~/.hf_token")

# Paths
AUDIO_PATH = "/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/bledsoe_nasa/audio_diarize.wav"
ALIGNED_JSON = "/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/bledsoe_nasa/audio_transcription/alignment_audio_enhanced/audio_aligned.json"
OUTPUT_DIR = Path("/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/bledsoe_nasa/audio_transcription/alignment_audio_enhanced/diarization_audio_aligned")

# Manual speaker hint - KEY TEST PARAMETER
NUM_SPEAKERS = 3  # Jesse (narrator) + Jesse (interviewer) + Chris Bledsoe

print("Configuration:")
print(f"  Audio: {AUDIO_PATH}")
print(f"  Speaker Hint: num_speakers={NUM_SPEAKERS}")
print(f"    Rationale: Jesse appears as 2 acoustic roles + 1 guest")
print()

# Load aligned transcript
print("Loading aligned transcript...")
with open(ALIGNED_JSON, "r") as f:
    data = json.load(f)
    aligned_segments = {"segments": data["segments"]}
print(f"  Loaded {len(data['segments'])} segments")

# Initialize diarization pipeline
print("\nInitializing pyannote speaker-diarization-3.1...")
diarization_pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=hf_token
)

device = "cuda" if torch.cuda.is_available() else "cpu"
diarization_pipeline.to(torch.device(device))
print(f"  Device: {device}")

# Run diarization WITH speaker count hint
print(f"\nRunning diarization with num_speakers={NUM_SPEAKERS}...")
print("  (This may take ~15-30 minutes for a 3.5h episode)")
print()

diarization = diarization_pipeline(AUDIO_PATH, num_speakers=NUM_SPEAKERS)

# Convert to DataFrame
diarization_data = []
for segment, _, speaker in diarization.itertracks(yield_label=True):
    diarization_data.append({
        'start': segment.start,
        'end': segment.end,
        'speaker': speaker
    })

diarize_df = pd.DataFrame(diarization_data)
detected_speakers = len(diarize_df['speaker'].unique())
total_segments = len(diarize_df)

print("="*70)
print("DIARIZATION RESULTS")
print("="*70)
print(f"Detected Speakers: {detected_speakers} (expected: {NUM_SPEAKERS})")
print(f"Total Segments: {total_segments}")
print()

# Speaker distribution
print("Speaker Distribution:")
for speaker in sorted(diarize_df['speaker'].unique()):
    count = len(diarize_df[diarize_df['speaker'] == speaker])
    duration = diarize_df[diarize_df['speaker'] == speaker]['end'].max() - diarize_df[diarize_df['speaker'] == speaker]['start'].min()
    print(f"  {speaker}: {count} segments")

# Assign speakers to words
print("\nAssigning speakers to words...")
result = whisperx.assign_word_speakers(diarize_df, aligned_segments)

# Save output with unique filename for this test
output_file = OUTPUT_DIR / "audio_diarized_3speakers_test.json"
with open(output_file, 'w') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"\n✓ Test diarization saved: {output_file}")
print()
print("="*70)
print("NEXT STEPS (Manual - No Claude API)")
print("="*70)
print("1. Review speaker distribution in output file")
print("2. Sample check: Do narrator segments have distinct speaker label?")
print("3. Sample check: Do interviewer segments have distinct speaker label?")
print("4. Human validation before deciding on speaker name assignment")
print()
print("NOTE: Claude API enhancement SKIPPED per test parameters")
