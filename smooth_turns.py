#!/usr/bin/env python3
"""
Post-process speaker turns with smoothing and merging
Reduces chatter and consolidates speaker segments
"""
import argparse
import json
import sys
import os

def smooth_speaker_turns(turns, min_turn_sec=1.0, merge_gap_sec=0.25):
    """
    Smooth and merge speaker turns
    - Remove turns shorter than min_turn_sec
    - Merge consecutive turns by same speaker if gap < merge_gap_sec
    """
    if not turns:
        return []

    print(f"[*] Smoothing {len(turns)} turns", file=sys.stderr)
    print(f"[*] Parameters: min_turn={min_turn_sec}s, merge_gap={merge_gap_sec}s", file=sys.stderr)

    # Sort by start time
    sorted_turns = sorted(turns, key=lambda x: x['start'])

    # First pass: remove short turns
    filtered_turns = []
    for turn in sorted_turns:
        duration = turn.get('duration', turn['end'] - turn['start'])
        if duration >= min_turn_sec:
            filtered_turns.append(turn)
        else:
            print(f"[*] Removing short turn: {duration:.2f}s < {min_turn_sec}s", file=sys.stderr)

    print(f"[*] After filtering: {len(filtered_turns)} turns", file=sys.stderr)

    # Second pass: merge consecutive same-speaker turns with small gaps
    if not filtered_turns:
        return []

    merged_turns = []
    current_turn = filtered_turns[0].copy()

    for next_turn in filtered_turns[1:]:
        gap = next_turn['start'] - current_turn['end']
        same_speaker = current_turn['speaker'] == next_turn['speaker']

        if same_speaker and gap <= merge_gap_sec:
            # Merge turns
            print(f"[*] Merging turns: gap={gap:.2f}s <= {merge_gap_sec}s", file=sys.stderr)
            current_turn['end'] = next_turn['end']
            current_turn['duration'] = current_turn['end'] - current_turn['start']
        else:
            # Save current turn and start new one
            merged_turns.append(current_turn)
            current_turn = next_turn.copy()

    # Don't forget the last turn
    merged_turns.append(current_turn)

    print(f"[*] After merging: {len(merged_turns)} turns", file=sys.stderr)

    # Recalculate durations to ensure consistency
    for turn in merged_turns:
        turn['duration'] = turn['end'] - turn['start']

    return merged_turns

def print_turn_summary(turns, title="Turn Summary"):
    """Print summary statistics of speaker turns"""
    if not turns:
        print(f"[*] {title}: No turns", file=sys.stderr)
        return

    print(f"\n[*] {title}:", file=sys.stderr)

    # Overall stats
    total_duration = sum(turn.get('duration', turn['end'] - turn['start']) for turn in turns)
    print(f"[*] Total turns: {len(turns)}", file=sys.stderr)
    print(f"[*] Total speaking time: {total_duration:.1f}s", file=sys.stderr)

    # Per-speaker stats
    speaker_stats = {}
    for turn in turns:
        speaker = turn['speaker']
        duration = turn.get('duration', turn['end'] - turn['start'])

        if speaker not in speaker_stats:
            speaker_stats[speaker] = {'count': 0, 'duration': 0, 'avg_duration': 0}

        speaker_stats[speaker]['count'] += 1
        speaker_stats[speaker]['duration'] += duration

    # Calculate averages and print
    for speaker in sorted(speaker_stats.keys()):
        stats = speaker_stats[speaker]
        stats['avg_duration'] = stats['duration'] / stats['count']
        print(f"[*] {speaker}: {stats['count']} turns, {stats['duration']:.1f}s total, {stats['avg_duration']:.1f}s avg", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description='Smooth and merge speaker turns')
    parser.add_argument('--in', dest='input_file', required=True, help='Input JSON file with turns')
    parser.add_argument('--out', required=True, help='Output JSON file')
    parser.add_argument('--min_turn', type=float, default=1.0, help='Minimum turn duration in seconds')
    parser.add_argument('--merge_gap', type=float, default=0.25, help='Maximum gap to merge same speaker')

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"[!] Input file not found: {args.input_file}", file=sys.stderr)
        return 1

    # Load input data
    try:
        with open(args.input_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"[!] Failed to load input file: {e}", file=sys.stderr)
        return 1

    original_turns = data.get('turns', [])
    print_turn_summary(original_turns, "Original Turns")

    # Smooth the turns
    smoothed_turns = smooth_speaker_turns(
        original_turns,
        args.min_turn,
        args.merge_gap
    )

    print_turn_summary(smoothed_turns, "Smoothed Turns")

    # Create output data (preserve original metadata)
    output_data = data.copy()
    output_data['turns'] = smoothed_turns
    output_data['n_turns'] = len(smoothed_turns)
    output_data['smoothing_applied'] = True
    output_data['smoothing_parameters'] = {
        'min_turn_sec': args.min_turn,
        'merge_gap_sec': args.merge_gap,
        'original_turns': len(original_turns),
        'smoothed_turns': len(smoothed_turns),
        'turns_removed': len(original_turns) - len(smoothed_turns)
    }

    # Save output
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n[*] Smoothing complete!", file=sys.stderr)
    print(f"[*] Original turns: {len(original_turns)}", file=sys.stderr)
    print(f"[*] Smoothed turns: {len(smoothed_turns)}", file=sys.stderr)
    print(f"[*] Reduction: {len(original_turns) - len(smoothed_turns)} turns", file=sys.stderr)
    print(f"[*] Results saved to: {args.out}", file=sys.stderr)

    return 0

if __name__ == "__main__":
    sys.exit(main())