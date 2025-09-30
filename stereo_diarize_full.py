#!/usr/bin/env python3
"""
Full-length stereo channel diarization for Sherlock
Processes entire audio file to detect all speakers across full conversation
"""
import subprocess
import json
import time
import sys

def run_vad_on_channel(audio_file, channel_name):
    """Run the existing diarize_light.py on a single channel"""
    output_file = f"bench/{channel_name}_full_turns.json"

    print(f"[*] Processing {channel_name} channel...", file=sys.stderr)

    # Run existing VAD script
    result = subprocess.run([
        'python3', 'diarize_light.py',
        '--audio', audio_file,
        '--out', output_file,
        '--agg_gap', '30'
    ], capture_output=True, text=True)

    if result.returncode != 0:
        return None, f"VAD failed for {channel_name}: {result.stderr}"

    # Load results
    try:
        with open(output_file, 'r') as f:
            data = json.load(f)
        return data, None
    except Exception as e:
        return None, f"Failed to load {channel_name} results: {e}"

def main():
    print("[*] Running FULL stereo channel separation for Sherlock...", file=sys.stderr)
    start_time = time.time()

    # Process both channels of full audio
    left_data, left_error = run_vad_on_channel('build/yt2_full_L.wav', 'LEFT')
    right_data, right_error = run_vad_on_channel('build/yt2_full_R.wav', 'RIGHT')

    if left_error or right_error:
        print(f"Errors: L={left_error}, R={right_error}", file=sys.stderr)
        return

    # Combine results
    all_turns = []

    # Add left channel turns
    for turn in left_data.get('turns', []):
        turn['speaker'] = 'L'
        turn['channel'] = 'left'
        all_turns.append(turn)

    # Add right channel turns
    for turn in right_data.get('turns', []):
        turn['speaker'] = 'R'
        turn['channel'] = 'right'
        all_turns.append(turn)

    # Sort by start time
    all_turns.sort(key=lambda x: x['start'])

    total_time = time.time() - start_time

    # Calculate audio duration from first result
    audio_duration = max(
        max([t['end'] for t in left_data.get('turns', [])], default=0),
        max([t['end'] for t in right_data.get('turns', [])], default=0)
    )

    # Create combined result
    result = {
        "wall_sec": total_time,
        "audio_duration": audio_duration,
        "turns": all_turns,
        "method": "full_stereo_channel_separation",
        "left_processing": left_data.get('wall_sec', 0),
        "right_processing": right_data.get('wall_sec', 0),
        "total_turns": len(all_turns),
        "left_turns": len(left_data.get('turns', [])),
        "right_turns": len(right_data.get('turns', []))
    }

    # Save combined result
    with open('bench/full_stereo_turns.json', 'w') as f:
        json.dump(result, f, indent=2)

    print(f"[*] Full analysis complete: {audio_duration/60:.1f} minutes processed", file=sys.stderr)
    print(f"[*] Left channel: {result['left_turns']} turns", file=sys.stderr)
    print(f"[*] Right channel: {result['right_turns']} turns", file=sys.stderr)

    # Print summary (matching original format)
    print(json.dumps({
        "wall_sec": total_time,
        "audio_duration": audio_duration,
        "n_turns": len(all_turns),
        "left_turns": len(left_data.get('turns', [])),
        "right_turns": len(right_data.get('turns', []))
    }))

if __name__ == "__main__":
    main()