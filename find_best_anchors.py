#!/usr/bin/env python3
import json

# Load the high-resolution analysis
with open('bench/diarize_embed_full.json', 'r') as f:
    data = json.load(f)

turns = data['turns']

# Find best segments for each speaker (relaxed criteria)
def find_best_segments(speaker_name, min_duration=8):
    segments = []

    for turn in turns:
        if turn['speaker'] == speaker_name and turn['duration'] >= min_duration:
            segments.append({
                'start': turn['start'],
                'duration': turn['duration'],
                'end': turn['end']
            })

    # Sort by duration (longer = better quality typically)
    return sorted(segments, key=lambda x: x['duration'], reverse=True)

print("🎯 BEST ANCHOR SEGMENTS (Top 3 per speaker)")
print("=" * 60)

speakers = ['Speaker_0', 'Speaker_1', 'Speaker_2']
selected_anchors = {}

for speaker in speakers:
    segments = find_best_segments(speaker)
    print(f"\n{speaker} - Top 3 longest segments:")

    for i, seg in enumerate(segments[:3], 1):
        start_min = int(seg['start'] // 60)
        start_sec = seg['start'] % 60
        duration = seg['duration']

        print(f"  {i}. {duration:5.1f}s @ {start_min:02d}:{start_sec:05.2f}")

    # Select the first (longest) for anchor
    if segments:
        selected_anchors[speaker] = segments[0]

print("\n" + "=" * 60)
print("RECOMMENDED FFMPEG COMMANDS:")
print("=" * 60)

anchor_names = ['A', 'B', 'C']
for i, speaker in enumerate(speakers):
    if speaker in selected_anchors:
        seg = selected_anchors[speaker]
        start_time = seg['start']

        # Use reasonable duration (cap at 45 seconds for quality)
        duration = min(int(seg['duration']), 45)

        start_min = int(start_time // 60)
        start_sec = int(start_time % 60)
        start_ms = int((start_time % 1) * 100)

        print(f"ffmpeg -ss {start_min:02d}:{start_sec:02d}:{start_ms:02d} -t {duration} -i build/yt2_full_stereo.wav -ac 1 -ar 16000 anchors/{anchor_names[i]}.wav")

print(f"\n# Create anchors directory first:")
print(f"mkdir -p anchors")