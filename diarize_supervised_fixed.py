#!/usr/bin/env python3
"""
Fixed Supervised Speaker Diarization
Uses manually selected anchor segments to identify speakers in full audio
Optimized for Sherlock system architecture
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
    from sklearn.metrics.pairwise import cosine_similarity
    import webrtcvad
    import librosa
    LIBS_AVAILABLE = True
except ImportError as e:
    print(f"[!] Required libraries not available: {e}", file=sys.stderr)
    LIBS_AVAILABLE = False

def apply_vad(audio, sample_rate, level=2, frame_ms=30):
    """Apply Voice Activity Detection - optimized version from working scripts"""
    vad = webrtcvad.Vad(level)
    frame_length = int(sample_rate * frame_ms / 1000)

    voiced_segments = []
    current_start = None

    for i in range(0, len(audio) - frame_length, frame_length):
        frame = audio[i:i + frame_length]
        # Convert to 16-bit PCM for webrtcvad
        frame_16bit = (frame * 32767).astype(np.int16).tobytes()
        is_voiced = vad.is_speech(frame_16bit, sample_rate)

        timestamp = i / sample_rate

        if is_voiced:
            if current_start is None:
                current_start = timestamp
        else:
            if current_start is not None:
                voiced_segments.append((current_start, timestamp))
                current_start = None

    # Close any remaining segment
    if current_start is not None:
        voiced_segments.append((current_start, len(audio) / sample_rate))

    return voiced_segments

def load_and_validate_anchors(anchor_paths, encoder):
    """Load anchor files and extract embeddings with validation"""
    print("[*] Loading anchor embeddings...", file=sys.stderr)

    anchors = {}
    for label, path in anchor_paths.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Anchor file not found: {path}")

        print(f"  Loading {label}: {path}", file=sys.stderr)
        try:
            wav = preprocess_wav(path)
            embedding = encoder.embed_utterance(wav)
            anchors[label] = embedding
            duration = len(wav) / 16000
            print(f"  ✅ {label}: {embedding.shape} ({duration:.1f}s)", file=sys.stderr)
        except Exception as e:
            print(f"  ❌ {label} failed: {e}", file=sys.stderr)
            raise

    return anchors

def extract_windowed_embeddings(audio_file, voiced_segments, encoder, win_sec=0.9, hop_sec=0.3):
    """Extract embeddings using sliding window over voiced segments"""
    print(f"[*] Loading audio: {audio_file}", file=sys.stderr)
    wav = preprocess_wav(audio_file)
    sample_rate = 16000

    print(f"[*] Extracting embeddings (win={win_sec}s, hop={hop_sec}s)", file=sys.stderr)

    embeddings_data = []
    win_samples = int(win_sec * sample_rate)
    hop_samples = int(hop_sec * sample_rate)

    total_segments = len(voiced_segments)
    processed_segments = 0

    for start_sec, end_sec in voiced_segments:
        processed_segments += 1
        if processed_segments % 10 == 0:
            print(f"  Processed {processed_segments}/{total_segments} voiced segments", file=sys.stderr)

        start_sample = int(start_sec * sample_rate)
        end_sample = int(end_sec * sample_rate)

        # Slide window over this voiced segment
        for win_start in range(start_sample, end_sample - win_samples, hop_samples):
            win_end = win_start + win_samples

            if win_end > len(wav):
                break

            segment = wav[win_start:win_end]
            win_start_sec = win_start / sample_rate
            win_end_sec = win_end / sample_rate

            try:
                embedding = encoder.embed_utterance(segment)
                embeddings_data.append({
                    'start': win_start_sec,
                    'end': win_end_sec,
                    'embedding': embedding
                })
            except Exception as e:
                print(f"  Warning: Failed to extract embedding at {win_start_sec:.1f}s: {e}", file=sys.stderr)
                continue

    print(f"[*] Extracted {len(embeddings_data)} embeddings", file=sys.stderr)
    return embeddings_data

def classify_embeddings(embeddings_data, anchors, switch_margin=0.08):
    """Classify each embedding against anchor embeddings"""
    print("[*] Classifying embeddings against anchors...", file=sys.stderr)

    # Prepare anchor data
    anchor_labels = list(anchors.keys())
    anchor_embeddings = np.stack([anchors[label] for label in anchor_labels])

    classified_segments = []

    for i, data in enumerate(embeddings_data):
        if i % 1000 == 0:
            print(f"  Classified {i}/{len(embeddings_data)} embeddings", file=sys.stderr)

        embedding = data['embedding'].reshape(1, -1)
        similarities = cosine_similarity(embedding, anchor_embeddings)[0]

        best_idx = np.argmax(similarities)
        best_label = anchor_labels[best_idx]
        best_similarity = similarities[best_idx]

        classified_segments.append({
            'start': data['start'],
            'end': data['end'],
            'speaker': best_label,
            'similarity': best_similarity,
            'all_similarities': {anchor_labels[j]: similarities[j] for j in range(len(anchor_labels))}
        })

    return classified_segments

def merge_segments(classified_segments, switch_margin=0.08, merge_gap=0.25, min_turn=1.0):
    """Merge segments into speaker turns with hysteresis and gap filling"""
    print("[*] Merging segments into speaker turns...", file=sys.stderr)

    if not classified_segments:
        return []

    # Sort by start time
    segments = sorted(classified_segments, key=lambda x: x['start'])

    turns = []
    current_turn = None

    for segment in segments:
        if current_turn is None:
            # Start first turn
            current_turn = {
                'speaker': segment['speaker'],
                'start': segment['start'],
                'end': segment['end'],
                'last_similarity': segment['similarity']
            }
            continue

        # Check if we should continue current turn or start new one
        prev_speaker = current_turn['speaker']
        new_speaker = segment['speaker']

        # Apply hysteresis: only switch if new speaker has significantly better similarity
        if new_speaker != prev_speaker:
            prev_sim = current_turn['last_similarity']
            new_sim = segment['similarity']

            # Check if gap is small enough to merge
            gap = segment['start'] - current_turn['end']

            if gap <= merge_gap and (new_sim - prev_sim) < switch_margin:
                # Continue current turn (ignore speaker change due to insufficient margin)
                current_turn['end'] = segment['end']
                continue

        # Check for small gap - merge if same speaker or gap is tiny
        gap = segment['start'] - current_turn['end']
        if gap <= merge_gap and new_speaker == prev_speaker:
            # Extend current turn
            current_turn['end'] = segment['end']
            current_turn['last_similarity'] = max(current_turn['last_similarity'], segment['similarity'])
        else:
            # End current turn and start new one
            if current_turn['end'] - current_turn['start'] >= min_turn:
                turns.append({
                    'speaker': current_turn['speaker'],
                    'start': current_turn['start'],
                    'end': current_turn['end'],
                    'duration': current_turn['end'] - current_turn['start']
                })

            current_turn = {
                'speaker': new_speaker,
                'start': segment['start'],
                'end': segment['end'],
                'last_similarity': segment['similarity']
            }

    # Don't forget the last turn
    if current_turn and (current_turn['end'] - current_turn['start']) >= min_turn:
        turns.append({
            'speaker': current_turn['speaker'],
            'start': current_turn['start'],
            'end': current_turn['end'],
            'duration': current_turn['end'] - current_turn['start']
        })

    print(f"[*] Created {len(turns)} speaker turns", file=sys.stderr)
    return turns

def main():
    if not LIBS_AVAILABLE:
        print("[!] Required libraries not installed", file=sys.stderr)
        return 1

    parser = argparse.ArgumentParser(description="Supervised speaker diarization with anchor embeddings")
    parser.add_argument("--audio", required=True, help="Input audio file")
    parser.add_argument("--A", required=True, help="Anchor A audio file")
    parser.add_argument("--B", required=True, help="Anchor B audio file")
    parser.add_argument("--C", required=True, help="Anchor C audio file")
    parser.add_argument("--out", default="bench/turns_supervised.json", help="Output JSON file")
    parser.add_argument("--win", type=float, default=0.9, help="Window size in seconds")
    parser.add_argument("--hop", type=float, default=0.3, help="Hop size in seconds")
    parser.add_argument("--vad_level", type=int, default=2, help="VAD sensitivity (0-3)")
    parser.add_argument("--switch_margin", type=float, default=0.08, help="Minimum similarity margin to switch speakers")
    parser.add_argument("--merge_gap", type=float, default=0.25, help="Maximum gap to merge segments (seconds)")
    parser.add_argument("--min_turn", type=float, default=1.0, help="Minimum turn duration (seconds)")

    args = parser.parse_args()

    # Validate inputs
    if not os.path.exists(args.audio):
        print(f"[!] Audio file not found: {args.audio}", file=sys.stderr)
        return 1

    start_time = time.time()

    print(f"[*] Supervised diarization with anchors", file=sys.stderr)
    print(f"[*] Parameters: win={args.win}s, hop={args.hop}s, vad={args.vad_level}", file=sys.stderr)
    print(f"[*] Thresholds: switch_margin={args.switch_margin}, merge_gap={args.merge_gap}s", file=sys.stderr)

    # Initialize voice encoder
    print("[*] Loading voice encoder...", file=sys.stderr)
    encoder = VoiceEncoder()

    # Load anchor embeddings
    anchor_paths = {"A": args.A, "B": args.B, "C": args.C}
    try:
        anchors = load_and_validate_anchors(anchor_paths, encoder)
    except Exception as e:
        print(f"[!] Failed to load anchors: {e}", file=sys.stderr)
        return 1

    # Apply VAD to find voiced segments
    print("[*] Applying Voice Activity Detection...", file=sys.stderr)
    wav = preprocess_wav(args.audio)
    voiced_segments = apply_vad(wav, 16000, args.vad_level)

    total_voiced_time = sum(end - start for start, end in voiced_segments)
    print(f"[*] Found {len(voiced_segments)} voiced segments ({total_voiced_time:.1f}s total)", file=sys.stderr)

    # Extract embeddings from voiced segments
    embeddings_data = extract_windowed_embeddings(
        args.audio, voiced_segments, encoder, args.win, args.hop
    )

    # Classify embeddings against anchors
    classified_segments = classify_embeddings(embeddings_data, anchors, args.switch_margin)

    # Merge into speaker turns
    turns = merge_segments(classified_segments, args.switch_margin, args.merge_gap, args.min_turn)

    # Calculate statistics
    wall_time = time.time() - start_time

    # Get audio duration
    try:
        y, sr = librosa.load(args.audio, sr=None)
        audio_duration = len(y) / sr
    except:
        audio_duration = max(turn['end'] for turn in turns) if turns else 0

    # Calculate speaker statistics
    speaker_stats = {}
    for turn in turns:
        speaker = turn['speaker']
        if speaker not in speaker_stats:
            speaker_stats[speaker] = {'turns': 0, 'duration': 0.0}
        speaker_stats[speaker]['turns'] += 1
        speaker_stats[speaker]['duration'] += turn['duration']

    # Create result
    result = {
        "method": "supervised_anchor_classification",
        "wall_sec": wall_time,
        "audio_duration": audio_duration,
        "n_turns": len(turns),
        "anchors": {
            "A": args.A,
            "B": args.B,
            "C": args.C
        },
        "parameters": {
            "window_sec": args.win,
            "hop_sec": args.hop,
            "vad_level": args.vad_level,
            "switch_margin": args.switch_margin,
            "merge_gap": args.merge_gap,
            "min_turn": args.min_turn
        },
        "speaker_stats": speaker_stats,
        "turns": turns
    }

    # Save result
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w') as f:
        json.dump(result, f, indent=2)

    # Print summary
    print(f"[*] Analysis complete! {len(turns)} turns detected", file=sys.stderr)
    print(f"[*] Processing time: {wall_time:.1f}s", file=sys.stderr)
    print(f"[*] Results saved to: {args.out}", file=sys.stderr)

    # Output summary JSON
    summary = {
        "wall_sec": wall_time,
        "audio_duration": audio_duration,
        "n_turns": len(turns),
        "method": "supervised_anchor_classification"
    }

    print(json.dumps(summary, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())