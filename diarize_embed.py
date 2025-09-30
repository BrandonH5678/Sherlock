#!/usr/bin/env python3
"""
Advanced speaker diarization with configurable parameters
Tunable voice embedding clustering with VAD and windowing controls
"""
import argparse
import json
import time
import sys
import os
import numpy as np
from pathlib import Path

try:
    from resemblyzer import preprocess_wav, VoiceEncoder
    from sklearn.cluster import AgglomerativeClustering
    from sklearn.metrics import silhouette_score
    import webrtcvad
    import librosa
    LIBS_AVAILABLE = True
except ImportError as e:
    print(f"[!] Required libraries not available: {e}", file=sys.stderr)
    LIBS_AVAILABLE = False

def apply_vad(audio, sample_rate, level=2, frame_ms=30):
    """Apply Voice Activity Detection with configurable sensitivity"""
    vad = webrtcvad.Vad(level)
    frame_length = int(sample_rate * frame_ms / 1000)

    frames = []
    voiced_frames = []

    for i in range(0, len(audio) - frame_length, frame_length):
        frame = audio[i:i + frame_length]
        # Convert to 16-bit PCM for webrtcvad
        frame_16bit = (frame * 32767).astype(np.int16).tobytes()
        is_voiced = vad.is_speech(frame_16bit, sample_rate)
        frames.append(frame)
        voiced_frames.append(is_voiced)

    return frames, voiced_frames

def extract_embeddings_windowed(audio_file, win_sec=0.9, hop_sec=0.3, vad_level=2, min_gap=0.30):
    """Extract voice embeddings using sliding window with VAD"""
    if not LIBS_AVAILABLE:
        return None, "Required libraries not available"

    try:
        print(f"[*] Loading audio: {audio_file}", file=sys.stderr)
        wav = preprocess_wav(audio_file)
        sample_rate = 16000

        print(f"[*] Applying VAD (level {vad_level})", file=sys.stderr)
        frames, voiced_frames = apply_vad(wav, sample_rate, vad_level)

        encoder = VoiceEncoder()
        embeddings = []
        segments_info = []

        win_samples = int(win_sec * sample_rate)
        hop_samples = int(hop_sec * sample_rate)

        print(f"[*] Extracting embeddings (win={win_sec}s, hop={hop_sec}s)", file=sys.stderr)

        for start_sample in range(0, len(wav) - win_samples, hop_samples):
            end_sample = start_sample + win_samples
            segment = wav[start_sample:end_sample]

            start_sec = start_sample / sample_rate
            end_sec = end_sample / sample_rate

            # Check VAD for this window
            start_frame_idx = start_sample // (sample_rate * 30 // 1000)
            end_frame_idx = min(end_sample // (sample_rate * 30 // 1000), len(voiced_frames))

            if end_frame_idx > start_frame_idx:
                voiced_ratio = sum(voiced_frames[start_frame_idx:end_frame_idx]) / (end_frame_idx - start_frame_idx)

                # Require at least 40% voiced content
                if voiced_ratio < 0.4:
                    continue

            try:
                embedding = encoder.embed_utterance(segment)
                embeddings.append(embedding)
                segments_info.append({
                    'start': start_sec,
                    'end': end_sec,
                    'duration': win_sec,
                    'voiced_ratio': voiced_ratio if end_frame_idx > start_frame_idx else 0.0
                })
            except Exception as e:
                print(f"[!] Failed to process segment {start_sec:.1f}s-{end_sec:.1f}s: {e}", file=sys.stderr)
                continue

        print(f"[*] Extracted {len(embeddings)} embeddings", file=sys.stderr)
        return embeddings, segments_info

    except Exception as e:
        return None, f"Embedding extraction failed: {e}"

def cluster_speakers(embeddings, segments_info, n_speakers=3):
    """Cluster embeddings into specified number of speakers"""
    if not embeddings:
        return None, "No embeddings to cluster"

    embeddings_array = np.array(embeddings)
    print(f"[*] Clustering into {n_speakers} speakers", file=sys.stderr)

    try:
        clustering = AgglomerativeClustering(
            n_clusters=n_speakers,
            linkage='ward'
        )
        labels = clustering.fit_predict(embeddings_array)

        # Calculate quality score
        score = silhouette_score(embeddings_array, labels) if len(set(labels)) > 1 else 0
        print(f"[*] Clustering score: {score:.3f}", file=sys.stderr)

        # Assign clusters to segments
        clustered_segments = []
        for i, (segment_info, cluster_id) in enumerate(zip(segments_info, labels)):
            segment_info['speaker'] = int(cluster_id)
            segment_info['embedding_index'] = i
            clustered_segments.append(segment_info)

        # Print statistics
        cluster_stats = {}
        for segment in clustered_segments:
            speaker = segment['speaker']
            if speaker not in cluster_stats:
                cluster_stats[speaker] = {'count': 0, 'duration': 0}
            cluster_stats[speaker]['count'] += 1
            cluster_stats[speaker]['duration'] += segment['duration']

        for speaker in sorted(cluster_stats.keys()):
            stats = cluster_stats[speaker]
            print(f"[*] Speaker {speaker}: {stats['count']} segments, {stats['duration']:.1f}s total", file=sys.stderr)

        return clustered_segments, score

    except Exception as e:
        return None, f"Clustering failed: {e}"

def create_turns_with_gaps(segments, min_gap=0.30):
    """Convert windowed segments to speaker turns with gap handling"""
    if not segments:
        return []

    # Sort by start time
    segments.sort(key=lambda x: x['start'])

    turns = []
    current_speaker = segments[0]['speaker']
    turn_start = segments[0]['start']
    last_end = segments[0]['end']

    for segment in segments[1:]:
        gap = segment['start'] - last_end

        # If speaker changes or gap is too large, end current turn
        if segment['speaker'] != current_speaker or gap > min_gap:
            turns.append({
                'start': turn_start,
                'end': last_end,
                'speaker': f"Speaker_{current_speaker}",
                'duration': last_end - turn_start
            })

            # Start new turn
            current_speaker = segment['speaker']
            turn_start = segment['start']

        last_end = segment['end']

    # Add final turn
    turns.append({
        'start': turn_start,
        'end': last_end,
        'speaker': f"Speaker_{current_speaker}",
        'duration': last_end - turn_start
    })

    return turns

def main():
    parser = argparse.ArgumentParser(description='Advanced speaker diarization with embeddings')
    parser.add_argument('--audio', required=True, help='Input audio file')
    parser.add_argument('--out', required=True, help='Output JSON file')
    parser.add_argument('--speakers', type=int, default=3, help='Number of speakers')
    parser.add_argument('--win', type=float, default=0.9, help='Window size in seconds')
    parser.add_argument('--hop', type=float, default=0.3, help='Hop size in seconds')
    parser.add_argument('--min_gap', type=float, default=0.30, help='Minimum gap between turns')
    parser.add_argument('--vad_level', type=int, default=2, help='VAD sensitivity (0-3)')

    args = parser.parse_args()

    if not LIBS_AVAILABLE:
        print("[!] Required libraries not installed", file=sys.stderr)
        return 1

    if not os.path.exists(args.audio):
        print(f"[!] Audio file not found: {args.audio}", file=sys.stderr)
        return 1

    start_time = time.time()

    print(f"[*] Advanced diarization: {args.speakers} speakers", file=sys.stderr)
    print(f"[*] Parameters: win={args.win}s, hop={args.hop}s, gap={args.min_gap}s, vad={args.vad_level}", file=sys.stderr)

    # Extract embeddings
    embeddings, segments_info = extract_embeddings_windowed(
        args.audio, args.win, args.hop, args.vad_level, args.min_gap
    )

    if embeddings is None:
        print(f"[!] Embedding extraction failed: {segments_info}", file=sys.stderr)
        return 1

    # Cluster speakers
    clustered_segments, score = cluster_speakers(embeddings, segments_info, args.speakers)
    if clustered_segments is None:
        print(f"[!] Clustering failed: {score}", file=sys.stderr)
        return 1

    # Create speaker turns
    turns = create_turns_with_gaps(clustered_segments, args.min_gap)

    # Get audio duration
    try:
        import librosa
        y, sr = librosa.load(args.audio, sr=None)
        audio_duration = len(y) / sr
    except:
        audio_duration = max(segment['end'] for segment in clustered_segments) if clustered_segments else 0

    wall_time = time.time() - start_time

    # Create result
    result = {
        "wall_sec": wall_time,
        "audio_duration": audio_duration,
        "turns": turns,
        "method": "advanced_embedding_clustering",
        "parameters": {
            "speakers": args.speakers,
            "window_sec": args.win,
            "hop_sec": args.hop,
            "min_gap_sec": args.min_gap,
            "vad_level": args.vad_level
        },
        "n_turns": len(turns),
        "clustering_score": score,
        "segments_processed": len(clustered_segments)
    }

    # Save result
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"[*] Analysis complete! {len(turns)} turns detected", file=sys.stderr)
    print(f"[*] Processing time: {wall_time:.1f}s", file=sys.stderr)
    print(f"[*] Results saved to: {args.out}", file=sys.stderr)

    # Print summary in expected format
    print(json.dumps({
        "wall_sec": wall_time,
        "audio_duration": audio_duration,
        "n_turns": len(turns),
        "method": "advanced_embedding_clustering"
    }))

    return 0

if __name__ == "__main__":
    sys.exit(main())