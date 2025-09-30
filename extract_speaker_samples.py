#!/usr/bin/env python3
"""
Extract audio samples from each detected speaker cluster
Creates short clips to verify speaker separation quality
"""
import json
import subprocess
import sys

def extract_audio_segment(input_file, output_file, start_sec, end_sec):
    """Extract audio segment using ffmpeg"""
    duration = end_sec - start_sec
    cmd = [
        'ffmpeg', '-y',  # -y to overwrite existing files
        '-i', input_file,
        '-ss', str(start_sec),
        '-t', str(duration),
        '-acodec', 'pcm_s16le',
        output_file
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stderr

def main():
    print("[*] Extracting speaker samples from enhanced clustering results...")

    # Load enhanced clustering results
    try:
        with open('bench/enhanced_voice_turns.json', 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"[!] Failed to load results: {e}")
        return

    # Group turns by voice cluster
    clusters = {}
    for turn in data['turns']:
        cluster_id = turn.get('voice_cluster', -1)
        if cluster_id not in clusters:
            clusters[cluster_id] = []
        clusters[cluster_id].append(turn)

    print(f"[*] Found {len(clusters)} voice clusters")

    # Extract samples from each cluster (avoiding cluster -1 which are too-short segments)
    audio_file = 'build/yt2_full_stereo.wav'
    samples_dir = 'build/speaker_samples'

    # Create samples directory
    subprocess.run(['mkdir', '-p', samples_dir], capture_output=True)

    for cluster_id in sorted(clusters.keys()):
        if cluster_id == -1:  # Skip segments too short for voice analysis
            continue

        turns = clusters[cluster_id]
        print(f"\n[*] Processing Speaker {cluster_id}: {len(turns)} segments")

        # Find some good representative segments (longer ones for better quality)
        good_segments = [t for t in turns if (t['end'] - t['start']) > 3.0]  # At least 3 seconds
        good_segments.sort(key=lambda x: x['end'] - x['start'], reverse=True)  # Longest first

        # Extract up to 3 samples per speaker
        samples_extracted = 0
        for i, turn in enumerate(good_segments[:3]):
            start_sec = turn['start']
            end_sec = turn['end']
            duration = end_sec - start_sec

            output_file = f"{samples_dir}/speaker_{cluster_id}_sample_{samples_extracted + 1}_{duration:.1f}s.wav"

            print(f"  [*] Extracting sample {samples_extracted + 1}: {start_sec:.1f}s - {end_sec:.1f}s ({duration:.1f}s)")

            success, error = extract_audio_segment(audio_file, output_file, start_sec, end_sec)
            if success:
                print(f"      Saved: {output_file}")
                samples_extracted += 1
            else:
                print(f"      Failed: {error}")

        print(f"  [*] Extracted {samples_extracted} samples for Speaker {cluster_id}")

    print(f"\n[*] Sample extraction complete!")
    print(f"[*] Samples saved in: {samples_dir}/")
    print(f"[*] Play samples with: play {samples_dir}/speaker_X_sample_Y_Zs.wav")

if __name__ == "__main__":
    main()