#!/usr/bin/env python3
"""
Quick stereo channel diarization for Sherlock
Runs VAD on L/R channels separately and tags speakers as L/R
"""
import subprocess
import json
import time
import sys

def run_vad_on_channel(audio_file, channel_name):
    """Run the existing diarize_light.py on a single channel"""
    output_file = f"bench/{channel_name}_turns.json"

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
    print("[*] Running stereo channel separation for Sherlock...", file=sys.stderr)
    start_time = time.time()

    # Process both channels
    left_data, left_error = run_vad_on_channel('build/yt2_L.wav', 'LEFT')
    right_data, right_error = run_vad_on_channel('build/yt2_R.wav', 'RIGHT')

    if left_error or right_error:
        print(f"Errors: L={left_error}, R={right_error}")
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

    # Create combined result
    result = {
        "wall_sec": total_time,
        "turns": all_turns,
        "method": "stereo_channel_separation",
        "left_processing": left_data.get('wall_sec', 0),
        "right_processing": right_data.get('wall_sec', 0)
    }

    # Save combined result
    with open('bench/stereo_turns.json', 'w') as f:
        json.dump(result, f, indent=2)

    # Print summary (matching original format)
    print(json.dumps({
        "wall_sec": total_time,
        "n_turns": len(all_turns),
        "left_turns": len(left_data.get('turns', [])),
        "right_turns": len(right_data.get('turns', []))
    }))

if __name__ == "__main__":
    main()