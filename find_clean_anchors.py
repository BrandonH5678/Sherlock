#!/usr/bin/env python3
import json

# Load the high-resolution analysis
with open('bench/diarize_embed_full.json', 'r') as f:
    data = json.load(f)

turns = data['turns']

# Find clean solo segments for each speaker (no overlaps, good duration)
def find_clean_segments(speaker_name, min_duration=10, max_duration=60):
    segments = []

    for i, turn in enumerate(turns):
        if turn['speaker'] == speaker_name and turn['duration'] >= min_duration:
            # Check for overlaps with adjacent turns
            start_time = turn['start']
            end_time = turn['end']

            # Look for gaps before/after to ensure clean isolation
            clean_before = True
            clean_after = True

            # Check previous turn
            if i > 0:
                prev_turn = turns[i-1]
                if prev_turn['end'] > start_time - 1.0:  # Less than 1s gap
                    clean_before = False

            # Check next turn
            if i < len(turns) - 1:
                next_turn = turns[i+1]
                if next_turn['start'] < end_time + 1.0:  # Less than 1s gap
                    clean_after = False

            if clean_before and clean_after:
                segments.append({
                    'start': start_time,
                    'duration': min(turn['duration'], max_duration),
                    'original_duration': turn['duration'],
                    'quality_score': turn['duration'] * (2 if clean_before and clean_after else 1)
                })

    # Sort by quality score
    return sorted(segments, key=lambda x: x['quality_score'], reverse=True)

print("🎯 FINDING CLEAN ANCHOR SEGMENTS")
print("=" * 50)

# Find best segments for each speaker
speakers = ['Speaker_0', 'Speaker_1', 'Speaker_2']
anchor_segments = {}

for speaker in speakers:
    clean_segs = find_clean_segments(speaker)
    if clean_segs:
        best = clean_segs[0]
        anchor_segments[speaker] = best

        start_min = int(best['start'] // 60)
        start_sec = best['start'] % 60

        print(f"\n{speaker}:")
        print(f"  Start: {start_min:02d}:{start_sec:05.2f}")
        print(f"  Duration: {best['duration']:.0f}s")
        print(f"  Quality: {best['quality_score']:.1f}")
        print(f"  Original segment: {best['original_duration']:.1f}s")

print("\n" + "=" * 50)
print("FFMPEG COMMANDS:")
print("=" * 50)

anchor_names = ['A', 'B', 'C']
for i, speaker in enumerate(speakers):
    if speaker in anchor_segments:
        seg = anchor_segments[speaker]
        start_time = seg['start']
        duration = int(seg['duration'])

        start_min = int(start_time // 60)
        start_sec = int(start_time % 60)

        print(f"ffmpeg -ss {start_min:02d}:{start_sec:02d}:{int((start_time % 1) * 100):02d} -t {duration} -i build/yt2_full_stereo.wav -ac 1 -ar 16000 anchors/{anchor_names[i]}.wav")
    else:
        print(f"# No clean segment found for {speaker}")