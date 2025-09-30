#!/usr/bin/env python3
import json
import subprocess
import os

# Load the analysis results
with open('bench/diarize_embed_full.json', 'r') as f:
    data = json.load(f)

# Group segments by speaker
speakers = {}
for turn in data['turns']:
    speaker = turn['speaker']
    if speaker not in speakers:
        speakers[speaker] = []
    speakers[speaker].append(turn)

# Select 3 segments per speaker (5-15 seconds each)
selected_segments = {}
for speaker in sorted(speakers.keys()):
    segments = speakers[speaker]
    # Filter for segments between 5-15 seconds
    valid_segments = [s for s in segments if 5 <= s['duration'] <= 15]

    if len(valid_segments) >= 3:
        # Select from different parts of the audio
        early = min(valid_segments[:len(valid_segments)//3], key=lambda x: x['start'])
        middle = min(valid_segments[len(valid_segments)//3:2*len(valid_segments)//3], key=lambda x: abs(x['start'] - 1441))  # middle of 48min
        late = min(valid_segments[2*len(valid_segments)//3:], key=lambda x: x['start'])
        selected_segments[speaker] = [early, middle, late]
    else:
        # Take best available
        selected_segments[speaker] = sorted(valid_segments, key=lambda x: x['duration'], reverse=True)[:3]

# Extract audio segments using ffmpeg
audio_file = "build/yt2_full_stereo.wav"
output_dir = "build/spot_check"
os.makedirs(output_dir, exist_ok=True)

print("🎵 EXTRACTING SPOT CHECK SEGMENTS")
print("=" * 50)

for speaker, segments in selected_segments.items():
    print(f"\n{speaker}:")
    for i, seg in enumerate(segments, 1):
        start_time = seg['start']
        duration = seg['duration']

        # Format times for display
        start_min = int(start_time // 60)
        start_sec = start_time % 60

        output_file = f"{output_dir}/{speaker}_sample_{i}.wav"

        # Extract segment with ffmpeg
        cmd = [
            "ffmpeg", "-y", "-i", audio_file,
            "-ss", str(start_time),
            "-t", str(duration),
            "-acodec", "pcm_s16le",
            output_file
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"  ✅ Sample {i}: {duration:.1f}s @ {start_min:02d}:{start_sec:05.2f} → {output_file}")
        else:
            print(f"  ❌ Sample {i}: Failed to extract")

print(f"\n📁 Samples saved to: {output_dir}/")
print("Ready for spot checking with JBL speaker!")