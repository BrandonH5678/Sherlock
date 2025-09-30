#!/usr/bin/env python3
"""
Enhanced speaker diarization using voice embeddings
Uses Resemblyzer + scikit-learn clustering to detect 3+ speakers beyond L/R channels
"""
import subprocess
import json
import time
import sys
import os
import numpy as np
from pathlib import Path

# Voice clustering imports
try:
    from resemblyzer import preprocess_wav, VoiceEncoder
    from sklearn.cluster import AgglomerativeClustering
    from sklearn.metrics import silhouette_score
    import librosa
    VOICE_CLUSTERING_AVAILABLE = True
except ImportError as e:
    print(f"[!] Voice clustering libraries not available: {e}", file=sys.stderr)
    VOICE_CLUSTERING_AVAILABLE = False

def extract_voice_segments(audio_file, turns_data):
    """Extract audio segments for each speaker turn"""
    if not VOICE_CLUSTERING_AVAILABLE:
        return None, "Voice clustering libraries not available"

    try:
        # Load audio
        print(f"[*] Loading audio: {audio_file}", file=sys.stderr)
        wav = preprocess_wav(audio_file)

        # Initialize voice encoder
        encoder = VoiceEncoder()

        # Extract embeddings for each turn
        embeddings = []
        segments_info = []

        for i, turn in enumerate(turns_data.get('turns', [])):
            start_sec = turn['start']
            end_sec = turn['end']
            duration = end_sec - start_sec

            # Skip very short segments (less than 0.5 seconds)
            if duration < 0.5:
                continue

            # Extract segment (convert seconds to samples)
            sample_rate = 16000  # Resemblyzer uses 16kHz
            start_sample = int(start_sec * sample_rate)
            end_sample = int(end_sec * sample_rate)

            # Ensure we don't exceed audio bounds
            end_sample = min(end_sample, len(wav))
            if start_sample >= len(wav):
                continue

            segment = wav[start_sample:end_sample]

            # Skip if segment is too short after extraction
            if len(segment) < sample_rate * 0.5:  # Minimum 0.5 seconds
                continue

            # Generate embedding
            try:
                embedding = encoder.embed_utterance(segment)
                embeddings.append(embedding)
                segments_info.append({
                    'turn_index': i,
                    'start': start_sec,
                    'end': end_sec,
                    'duration': duration,
                    'original_speaker': turn.get('speaker', 'unknown'),
                    'channel': turn.get('channel', 'mono')
                })
            except Exception as e:
                print(f"[!] Failed to process segment {i} ({start_sec:.1f}s-{end_sec:.1f}s): {e}", file=sys.stderr)
                continue

        print(f"[*] Extracted {len(embeddings)} voice embeddings from {len(turns_data.get('turns', []))} turns", file=sys.stderr)
        return embeddings, segments_info

    except Exception as e:
        return None, f"Voice embedding extraction failed: {e}"

def cluster_voices(embeddings, segments_info, min_clusters=2, max_clusters=6):
    """Cluster voice embeddings to identify unique speakers"""
    if not embeddings:
        return None, "No embeddings to cluster"

    embeddings_array = np.array(embeddings)
    print(f"[*] Clustering {len(embeddings)} embeddings...", file=sys.stderr)

    best_score = -1
    best_clustering = None
    best_n_clusters = min_clusters

    # Try different numbers of clusters
    for n_clusters in range(min_clusters, min(max_clusters + 1, len(embeddings))):
        try:
            clustering = AgglomerativeClustering(
                n_clusters=n_clusters,
                linkage='ward'
            )
            labels = clustering.fit_predict(embeddings_array)

            # Calculate silhouette score (higher is better)
            if len(set(labels)) > 1:  # Need at least 2 clusters for silhouette score
                score = silhouette_score(embeddings_array, labels)
                print(f"[*] {n_clusters} clusters: silhouette score {score:.3f}", file=sys.stderr)

                if score > best_score:
                    best_score = score
                    best_clustering = labels
                    best_n_clusters = n_clusters
        except Exception as e:
            print(f"[!] Clustering with {n_clusters} clusters failed: {e}", file=sys.stderr)
            continue

    if best_clustering is None:
        return None, "Clustering failed for all attempted cluster counts"

    # Assign cluster labels to segments
    clustered_segments = []
    for i, (segment_info, cluster_id) in enumerate(zip(segments_info, best_clustering)):
        segment_info['voice_cluster'] = int(cluster_id)
        segment_info['embedding_index'] = i
        clustered_segments.append(segment_info)

    print(f"[*] Best clustering: {best_n_clusters} speakers (silhouette score: {best_score:.3f})", file=sys.stderr)

    # Print cluster statistics
    cluster_counts = {}
    for segment in clustered_segments:
        cluster_id = segment['voice_cluster']
        cluster_counts[cluster_id] = cluster_counts.get(cluster_id, 0) + 1

    for cluster_id, count in sorted(cluster_counts.items()):
        total_duration = sum(s['duration'] for s in clustered_segments if s['voice_cluster'] == cluster_id)
        print(f"[*] Voice cluster {cluster_id}: {count} segments, {total_duration:.1f}s total", file=sys.stderr)

    return clustered_segments, best_n_clusters

def main():
    print("[*] Enhanced Sherlock Speaker Diarization with Voice Clustering", file=sys.stderr)
    start_time = time.time()

    if not VOICE_CLUSTERING_AVAILABLE:
        print("[!] Voice clustering libraries not available. Install resemblyzer and scikit-learn.", file=sys.stderr)
        return

    # Check if we have the stereo analysis results
    stereo_results_file = 'bench/full_stereo_turns.json'
    if not os.path.exists(stereo_results_file):
        print(f"[!] Stereo analysis results not found: {stereo_results_file}", file=sys.stderr)
        print("[*] Please run stereo_diarize_full.py first", file=sys.stderr)
        return

    # Load existing stereo analysis
    try:
        with open(stereo_results_file, 'r') as f:
            stereo_data = json.load(f)
    except Exception as e:
        print(f"[!] Failed to load stereo results: {e}", file=sys.stderr)
        return

    print(f"[*] Loaded stereo analysis: {len(stereo_data['turns'])} turns", file=sys.stderr)

    # Use the full stereo audio for voice analysis
    audio_file = 'build/yt2_full_stereo.wav'
    if not os.path.exists(audio_file):
        print(f"[!] Audio file not found: {audio_file}", file=sys.stderr)
        return

    # Extract voice embeddings from all speaker turns
    embeddings, segments_info = extract_voice_segments(audio_file, stereo_data)
    if embeddings is None:
        print(f"[!] Voice embedding extraction failed: {segments_info}", file=sys.stderr)
        return

    # Cluster voices to identify unique speakers
    clustered_segments, n_voice_clusters = cluster_voices(embeddings, segments_info)
    if clustered_segments is None:
        print(f"[!] Voice clustering failed: {n_voice_clusters}", file=sys.stderr)
        return

    # Create enhanced turns with voice cluster information
    enhanced_turns = []
    segment_lookup = {seg['turn_index']: seg for seg in clustered_segments}

    for i, turn in enumerate(stereo_data['turns']):
        enhanced_turn = turn.copy()

        if i in segment_lookup:
            seg_info = segment_lookup[i]
            enhanced_turn['voice_cluster'] = seg_info['voice_cluster']
            enhanced_turn['speaker_id'] = f"Speaker_{seg_info['voice_cluster']}"
            # Keep original channel info but add voice-based speaker ID
            enhanced_turn['channel_speaker'] = turn.get('speaker', 'unknown')
        else:
            # Turn was too short for voice analysis
            enhanced_turn['voice_cluster'] = -1
            enhanced_turn['speaker_id'] = f"Channel_{turn.get('speaker', 'unknown')}"
            enhanced_turn['channel_speaker'] = turn.get('speaker', 'unknown')

        enhanced_turns.append(enhanced_turn)

    total_time = time.time() - start_time

    # Create enhanced result
    result = {
        "wall_sec": total_time,
        "audio_duration": stereo_data['audio_duration'],
        "turns": enhanced_turns,
        "method": "enhanced_voice_clustering",
        "stereo_analysis_time": stereo_data.get('wall_sec', 0),
        "voice_analysis_time": total_time - stereo_data.get('wall_sec', 0),
        "total_turns": len(enhanced_turns),
        "voice_clusters_detected": n_voice_clusters,
        "segments_analyzed": len(clustered_segments),
        "segments_skipped": len(stereo_data['turns']) - len(clustered_segments)
    }

    # Save enhanced result
    output_file = 'bench/enhanced_voice_turns.json'
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"[*] Enhanced analysis complete!", file=sys.stderr)
    print(f"[*] Audio duration: {result['audio_duration']/60:.1f} minutes", file=sys.stderr)
    print(f"[*] Total turns: {result['total_turns']}", file=sys.stderr)
    print(f"[*] Voice clusters detected: {result['voice_clusters_detected']}", file=sys.stderr)
    print(f"[*] Results saved to: {output_file}", file=sys.stderr)

    # Print comparison with stereo-only analysis
    print("\n[*] COMPARISON:", file=sys.stderr)
    print(f"[*] Stereo-only speakers: 2 (L/R channels)", file=sys.stderr)
    print(f"[*] Voice-detected speakers: {n_voice_clusters}", file=sys.stderr)

    if n_voice_clusters > 2:
        print(f"[*] SUCCESS: Detected {n_voice_clusters - 2} additional speakers beyond L/R channels!", file=sys.stderr)
    else:
        print(f"[*] Voice analysis confirms 2-speaker conversation", file=sys.stderr)

    # Print summary in original format
    print(json.dumps({
        "wall_sec": total_time,
        "audio_duration": result['audio_duration'],
        "n_turns": len(enhanced_turns),
        "voice_clusters": n_voice_clusters,
        "method": "enhanced_voice_clustering"
    }))

if __name__ == "__main__":
    main()