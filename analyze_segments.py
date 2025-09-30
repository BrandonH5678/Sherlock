#!/usr/bin/env python3
import json

# Load the analysis results
with open('bench/diarize_embed_full.json', 'r') as f:
    data = json.load(f)

# Group segments by speaker and find longest ones
speakers = {}
for turn in data['turns']:
    speaker = turn['speaker']
    if speaker not in speakers:
        speakers[speaker] = []
    speakers[speaker].append({
        'duration': turn['duration'],
        'start': turn['start'],
        'end': turn['end']
    })

# Sort by duration and get top 3 for each speaker
print("🎤 LONGEST SEGMENTS BY SPEAKER:")
print("=" * 50)

for speaker in sorted(speakers.keys()):
    segments = sorted(speakers[speaker], key=lambda x: x['duration'], reverse=True)
    top_3 = segments[:3]

    print(f"\n{speaker}:")
    for i, seg in enumerate(top_3, 1):
        minutes = int(seg['duration'] // 60)
        seconds = seg['duration'] % 60
        start_min = int(seg['start'] // 60)
        start_sec = seg['start'] % 60
        end_min = int(seg['end'] // 60)
        end_sec = seg['end'] % 60

        print(f"  {i}. {minutes:02d}:{seconds:05.2f} ({seg['start']:.1f}s - {seg['end']:.1f}s)")
        print(f"     [{start_min:02d}:{start_sec:05.2f} - {end_min:02d}:{end_sec:05.2f}]")