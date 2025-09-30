#!/usr/bin/env python3
"""
Summarize speaker turn analysis results
Provides detailed statistics and comparison across different parameter sets
"""
import argparse
import json
import sys
import os
from pathlib import Path

def analyze_turns(data):
    """Analyze turn data and extract key statistics"""
    turns = data.get('turns', [])
    if not turns:
        return None

    # Basic stats
    stats = {
        'total_turns': len(turns),
        'total_duration': sum(turn.get('duration', turn['end'] - turn['start']) for turn in turns),
        'avg_turn_duration': 0,
        'min_turn_duration': float('inf'),
        'max_turn_duration': 0,
        'speakers': {},
        'method': data.get('method', 'unknown'),
        'processing_time': data.get('wall_sec', 0),
        'audio_duration': data.get('audio_duration', 0),
        'clustering_score': data.get('clustering_score', 'N/A'),
        'parameters': data.get('parameters', {}),
        'segments_processed': data.get('segments_processed', 0)
    }

    # Per-turn analysis
    durations = []
    for turn in turns:
        duration = turn.get('duration', turn['end'] - turn['start'])
        durations.append(duration)

        speaker = turn.get('speaker', 'unknown')
        if speaker not in stats['speakers']:
            stats['speakers'][speaker] = {'count': 0, 'duration': 0, 'turns': []}

        stats['speakers'][speaker]['count'] += 1
        stats['speakers'][speaker]['duration'] += duration
        stats['speakers'][speaker]['turns'].append(turn)

    # Duration statistics
    if durations:
        stats['avg_turn_duration'] = sum(durations) / len(durations)
        stats['min_turn_duration'] = min(durations)
        stats['max_turn_duration'] = max(durations)
        stats['median_turn_duration'] = sorted(durations)[len(durations)//2]

    # Speaker averages
    for speaker_stats in stats['speakers'].values():
        if speaker_stats['count'] > 0:
            speaker_stats['avg_duration'] = speaker_stats['duration'] / speaker_stats['count']

    return stats

def print_summary(filepath, stats):
    """Print formatted summary of turn analysis"""
    filename = os.path.basename(filepath)
    print(f"\n{'='*60}")
    print(f"SUMMARY: {filename}")
    print(f"{'='*60}")

    if not stats:
        print("No turn data found")
        return

    # Method and parameters
    print(f"Method: {stats['method']}")
    if stats['parameters']:
        print("Parameters:")
        for key, value in stats['parameters'].items():
            print(f"  {key}: {value}")

    # Performance metrics
    print(f"\nProcessing:")
    print(f"  Audio duration: {stats['audio_duration']:.1f}s ({stats['audio_duration']/60:.1f} min)")
    print(f"  Processing time: {stats['processing_time']:.1f}s ({stats['processing_time']/60:.1f} min)")
    if stats['audio_duration'] > 0:
        real_time_factor = stats['processing_time'] / stats['audio_duration']
        print(f"  Real-time factor: {real_time_factor:.2f}x")

    if stats['segments_processed'] > 0:
        print(f"  Segments processed: {stats['segments_processed']}")

    if stats['clustering_score'] != 'N/A':
        print(f"  Clustering score: {stats['clustering_score']:.3f}")

    # Turn statistics
    print(f"\nTurn Analysis:")
    print(f"  Total turns: {stats['total_turns']}")
    print(f"  Total speaking time: {stats['total_duration']:.1f}s ({stats['total_duration']/60:.1f} min)")
    print(f"  Coverage: {stats['total_duration']/stats['audio_duration']*100:.1f}% of audio")
    print(f"  Average turn: {stats['avg_turn_duration']:.1f}s")
    print(f"  Turn range: {stats['min_turn_duration']:.1f}s - {stats['max_turn_duration']:.1f}s")
    print(f"  Median turn: {stats['median_turn_duration']:.1f}s")

    # Speaker breakdown
    print(f"\nSpeaker Breakdown:")
    total_speaker_time = sum(s['duration'] for s in stats['speakers'].values())

    for speaker in sorted(stats['speakers'].keys()):
        speaker_stats = stats['speakers'][speaker]
        percentage = (speaker_stats['duration'] / total_speaker_time * 100) if total_speaker_time > 0 else 0
        print(f"  {speaker}:")
        print(f"    Turns: {speaker_stats['count']} ({speaker_stats['count']/stats['total_turns']*100:.1f}%)")
        print(f"    Duration: {speaker_stats['duration']:.1f}s ({percentage:.1f}%)")
        print(f"    Avg turn: {speaker_stats['avg_duration']:.1f}s")

def compare_results(files_data):
    """Compare results across multiple files"""
    if len(files_data) < 2:
        return

    print(f"\n{'='*80}")
    print("COMPARISON ACROSS PARAMETER SETS")
    print(f"{'='*80}")

    # Table header
    print(f"{'File':<20} {'Turns':<8} {'Score':<8} {'AvgTurn':<10} {'RTF':<8} {'Coverage':<10}")
    print("-" * 80)

    for filepath, stats in files_data:
        if not stats:
            continue

        filename = os.path.basename(filepath).replace('.json', '').replace('turns_', '')
        rtf = stats['processing_time'] / stats['audio_duration'] if stats['audio_duration'] > 0 else 0
        coverage = stats['total_duration'] / stats['audio_duration'] * 100 if stats['audio_duration'] > 0 else 0
        score = f"{stats['clustering_score']:.3f}" if stats['clustering_score'] != 'N/A' else 'N/A'

        print(f"{filename:<20} {stats['total_turns']:<8} {score:<8} {stats['avg_turn_duration']:<10.1f} {rtf:<8.2f} {coverage:<10.1f}%")

def main():
    parser = argparse.ArgumentParser(description='Summarize speaker turn analysis results')
    parser.add_argument('files', nargs='+', help='JSON files to analyze')
    parser.add_argument('--compare', action='store_true', help='Show comparison table')

    args = parser.parse_args()

    files_data = []

    for filepath in args.files:
        if not os.path.exists(filepath):
            print(f"[!] File not found: {filepath}", file=sys.stderr)
            continue

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"[!] Failed to load {filepath}: {e}", file=sys.stderr)
            continue

        stats = analyze_turns(data)
        files_data.append((filepath, stats))
        print_summary(filepath, stats)

    # Show comparison if requested or multiple files
    if args.compare or len(files_data) > 1:
        compare_results(files_data)

if __name__ == "__main__":
    main()