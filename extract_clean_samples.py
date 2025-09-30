#!/usr/bin/env python3
"""
Extract cleaner single-speaker samples
Focus on shorter segments more likely to contain only one speaker
"""
import json
import subprocess

def main():
    print("[*] Extracting cleaner single-speaker samples...")

    # Load enhanced clustering results
    with open('bench/enhanced_voice_turns.json', 'r') as f:
        data = json.load(f)

    # Group by cluster and find shorter, cleaner segments
    clusters = {}
    for turn in data['turns']:
        cluster_id = turn.get('voice_cluster', -1)
        if cluster_id == -1:  # Skip segments too short for analysis
            continue

        if cluster_id not in clusters:
            clusters[cluster_id] = []

        duration = turn['end'] - turn['start']
        # Look for medium-length segments (5-20 seconds) - more likely single speaker
        if 5.0 <= duration <= 20.0:
            clusters[cluster_id].append(turn)

    print(f"[*] Found cleaner segments:")
    for cluster_id in sorted(clusters.keys()):
        segments = clusters[cluster_id]
        print(f"  Cluster {cluster_id}: {len(segments)} clean segments (5-20s each)")

    # Extract one clean sample per cluster
    audio_file = 'build/yt2_full_stereo.wav'
    samples_dir = 'build/clean_samples'
    subprocess.run(['mkdir', '-p', samples_dir], capture_output=True)

    for cluster_id in sorted(clusters.keys()):
        segments = clusters[cluster_id]
        if not segments:
            continue

        # Sort by duration and pick a medium-length one
        segments.sort(key=lambda x: x['end'] - x['start'])
        mid_idx = len(segments) // 2
        selected = segments[mid_idx]

        start_sec = selected['start']
        end_sec = selected['end']
        duration = end_sec - start_sec

        output_file = f"{samples_dir}/clean_speaker_{cluster_id}_{duration:.1f}s.wav"

        print(f"[*] Extracting clean sample {cluster_id}: {start_sec:.1f}s - {end_sec:.1f}s ({duration:.1f}s)")

        cmd = [
            'ffmpeg', '-y',
            '-i', audio_file,
            '-ss', str(start_sec),
            '-t', str(duration),
            '-acodec', 'pcm_s16le',
            output_file
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  Saved: {output_file}")
        else:
            print(f"  Failed: {result.stderr}")

    print(f"[*] Clean samples extracted to: {samples_dir}/")

if __name__ == "__main__":
    main()