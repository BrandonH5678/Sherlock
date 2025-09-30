#!/usr/bin/env python3
"""
Auto-Anchor Detection Engine for Sherlock
Automatically identifies high-quality speaker anchor segments using voice characteristics
"""

import json
import logging
import numpy as np
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import webrtcvad
from pydub import AudioSegment

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from voice_engine import VoiceEngineManager

# Try to import resemblyzer for voice embeddings
try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    RESEMBLYZER_AVAILABLE = True
except ImportError:
    RESEMBLYZER_AVAILABLE = False
    print("Warning: resemblyzer not available. Install with: pip install resemblyzer")


@dataclass
class AnchorCandidate:
    """Potential anchor segment"""
    speaker_id: str
    start_time: float
    end_time: float
    duration: float
    quality_score: float
    snr_db: float
    voice_consistency: float
    isolation_score: float
    embedding: Optional[np.ndarray] = None
    confidence: float = 0.0


@dataclass
class AutoAnchorResult:
    """Result from auto-anchor detection"""
    success: bool
    confidence: float
    processing_time: float
    anchor_candidates: List[AnchorCandidate]
    selected_anchors: Dict[str, str]  # speaker_id -> anchor_file_path
    quality_metrics: Dict
    fallback_reason: Optional[str] = None


class AutoAnchorDetector:
    """Automatically detects high-quality speaker anchor segments"""

    def __init__(self):
        self.voice_encoder = None
        self.vad = webrtcvad.Vad(2)  # Aggressive VAD
        self.logger = logging.getLogger(__name__)

        # Quality thresholds
        self.min_anchor_duration = 8.0  # seconds
        self.max_anchor_duration = 15.0  # seconds
        self.min_snr_db = 15.0  # minimum signal-to-noise ratio
        self.min_isolation_score = 0.7  # minimum speaker isolation
        self.confidence_threshold = 0.85  # minimum confidence to proceed

        # Initialize voice encoder if available
        if RESEMBLYZER_AVAILABLE:
            try:
                self.voice_encoder = VoiceEncoder()
                self.logger.info("Voice encoder loaded successfully")
            except Exception as e:
                self.logger.warning(f"Could not load voice encoder: {e}")
                self.voice_encoder = None

    def detect_anchors(self,
                      audio_file: str,
                      target_speakers: int = 3,
                      analysis_duration: int = 900) -> AutoAnchorResult:  # 15 minutes
        """
        Detect anchor segments automatically

        Args:
            audio_file: Path to audio file
            target_speakers: Expected number of speakers (2-5)
            analysis_duration: How many seconds to analyze (default: 15 minutes)

        Returns:
            AutoAnchorResult with detected anchors or fallback recommendation
        """

        start_time = time.time()

        try:
            self.logger.info(f"Starting auto-anchor detection on {audio_file}")
            self.logger.info(f"Target speakers: {target_speakers}, Analysis duration: {analysis_duration}s")

            # Step 1: Preprocess audio
            processed_audio = self._preprocess_audio(audio_file)
            analysis_segment = self._extract_analysis_segment(processed_audio, analysis_duration)

            # Step 2: Voice Activity Detection
            speech_segments = self._detect_speech_segments(analysis_segment)
            self.logger.info(f"Found {len(speech_segments)} speech segments")

            if len(speech_segments) < 5:
                return AutoAnchorResult(
                    success=False,
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    anchor_candidates=[],
                    selected_anchors={},
                    quality_metrics={},
                    fallback_reason="Insufficient speech segments detected"
                )

            # Step 3: Voice embedding analysis (if available)
            if self.voice_encoder:
                anchor_candidates = self._embedding_based_detection(analysis_segment, speech_segments, target_speakers)
            else:
                anchor_candidates = self._fallback_detection(analysis_segment, speech_segments, target_speakers)

            # Step 4: Quality assessment and filtering
            quality_candidates = self._assess_anchor_quality(anchor_candidates, analysis_segment)

            # Step 5: Select best anchors per speaker
            selected_anchors = self._select_best_anchors(quality_candidates, target_speakers)

            # Step 6: Extract anchor audio files
            anchor_files = self._extract_anchor_files(audio_file, selected_anchors)

            # Calculate overall confidence
            overall_confidence = self._calculate_confidence(selected_anchors, quality_candidates)

            processing_time = time.time() - start_time

            result = AutoAnchorResult(
                success=overall_confidence >= self.confidence_threshold,
                confidence=overall_confidence,
                processing_time=processing_time,
                anchor_candidates=quality_candidates,
                selected_anchors=anchor_files,
                quality_metrics=self._generate_quality_metrics(quality_candidates, selected_anchors)
            )

            if not result.success:
                result.fallback_reason = f"Confidence {overall_confidence:.1%} below threshold {self.confidence_threshold:.1%}"

            self.logger.info(f"Auto-anchor detection completed: {result.success}, confidence: {result.confidence:.1%}")

            return result

        except Exception as e:
            self.logger.error(f"Auto-anchor detection failed: {e}")
            return AutoAnchorResult(
                success=False,
                confidence=0.0,
                processing_time=time.time() - start_time,
                anchor_candidates=[],
                selected_anchors={},
                quality_metrics={},
                fallback_reason=f"Processing error: {str(e)}"
            )

    def _preprocess_audio(self, audio_file: str) -> AudioSegment:
        """Preprocess audio to standard format"""
        audio = AudioSegment.from_file(audio_file)

        # Convert to mono 16kHz for analysis
        audio = audio.set_channels(1).set_frame_rate(16000)

        # Normalize volume
        audio = audio.normalize()

        self.logger.info(f"Audio preprocessed: {len(audio)/1000:.1f}s duration")
        return audio

    def _extract_analysis_segment(self, audio: AudioSegment, duration: int) -> AudioSegment:
        """Extract segment for analysis (usually first N minutes)"""
        max_duration_ms = duration * 1000

        if len(audio) <= max_duration_ms:
            return audio

        # Extract first N minutes for analysis
        analysis_segment = audio[:max_duration_ms]
        self.logger.info(f"Using analysis segment: {len(analysis_segment)/1000:.1f}s")

        return analysis_segment

    def _detect_speech_segments(self, audio: AudioSegment) -> List[Tuple[float, float]]:
        """Detect speech segments using VAD"""

        # Convert to bytes for VAD
        frame_duration_ms = 30
        frame_size = int(16000 * frame_duration_ms / 1000)

        segments = []
        current_segment_start = None

        for i in range(0, len(audio), frame_duration_ms):
            frame = audio[i:i + frame_duration_ms]

            if len(frame) < frame_duration_ms:
                break

            frame_bytes = frame.raw_data

            # Pad or truncate to exact frame size
            expected_bytes = frame_size * 2  # 16-bit samples
            if len(frame_bytes) < expected_bytes:
                frame_bytes += b'\x00' * (expected_bytes - len(frame_bytes))
            elif len(frame_bytes) > expected_bytes:
                frame_bytes = frame_bytes[:expected_bytes]

            try:
                is_speech = self.vad.is_speech(frame_bytes, 16000)

                frame_time = i / 1000.0

                if is_speech and current_segment_start is None:
                    current_segment_start = frame_time
                elif not is_speech and current_segment_start is not None:
                    # End of speech segment
                    segments.append((current_segment_start, frame_time))
                    current_segment_start = None

            except Exception as e:
                self.logger.warning(f"VAD error at frame {i}: {e}")
                continue

        # Handle segment that ends at audio end
        if current_segment_start is not None:
            segments.append((current_segment_start, len(audio) / 1000.0))

        # Filter segments by minimum duration
        min_duration = 2.0  # seconds
        filtered_segments = [(start, end) for start, end in segments if (end - start) >= min_duration]

        self.logger.info(f"Speech segments: {len(filtered_segments)} (after filtering)")
        return filtered_segments

    def _embedding_based_detection(self, audio: AudioSegment, speech_segments: List[Tuple[float, float]], target_speakers: int) -> List[AnchorCandidate]:
        """Use voice embeddings to detect speaker-specific anchor candidates"""

        candidates = []

        self.logger.info("Performing embedding-based speaker detection")

        # Extract embeddings for each speech segment
        segment_embeddings = []

        for i, (start, end) in enumerate(speech_segments):
            try:
                # Extract audio segment
                start_ms = int(start * 1000)
                end_ms = int(end * 1000)
                segment_audio = audio[start_ms:end_ms]

                # Convert to numpy array for resemblyzer
                audio_array = np.array(segment_audio.get_array_of_samples(), dtype=np.float32)
                audio_array = audio_array / np.max(np.abs(audio_array))  # Normalize

                # Get voice embedding
                embedding = self.voice_encoder.embed_utterance(audio_array)

                segment_embeddings.append({
                    'start': start,
                    'end': end,
                    'duration': end - start,
                    'embedding': embedding,
                    'segment_id': i
                })

            except Exception as e:
                self.logger.warning(f"Failed to process segment {i}: {e}")
                continue

        if len(segment_embeddings) < target_speakers:
            self.logger.warning(f"Only {len(segment_embeddings)} segments processed, need {target_speakers}")
            return candidates

        # Cluster embeddings to identify speakers
        speaker_clusters = self._cluster_voice_embeddings(segment_embeddings, target_speakers)

        # Create anchor candidates for each speaker cluster
        for speaker_id, cluster_segments in speaker_clusters.items():
            # Find best segment in each cluster
            best_segment = self._find_best_segment_in_cluster(cluster_segments, audio)

            if best_segment:
                candidate = AnchorCandidate(
                    speaker_id=speaker_id,
                    start_time=best_segment['start'],
                    end_time=best_segment['end'],
                    duration=best_segment['duration'],
                    quality_score=0.0,  # Will be calculated later
                    snr_db=0.0,  # Will be calculated later
                    voice_consistency=best_segment.get('consistency', 0.8),
                    isolation_score=0.0,  # Will be calculated later
                    embedding=best_segment['embedding']
                )
                candidates.append(candidate)

        self.logger.info(f"Generated {len(candidates)} embedding-based candidates")
        return candidates

    def _fallback_detection(self, audio: AudioSegment, speech_segments: List[Tuple[float, float]], target_speakers: int) -> List[AnchorCandidate]:
        """Fallback detection without voice embeddings"""

        self.logger.info("Using fallback detection (no voice embeddings)")

        candidates = []

        # Simple approach: select well-spaced segments of good duration
        suitable_segments = [
            (start, end) for start, end in speech_segments
            if self.min_anchor_duration <= (end - start) <= self.max_anchor_duration
        ]

        # Sort by duration (prefer longer segments)
        suitable_segments.sort(key=lambda x: x[1] - x[0], reverse=True)

        # Select spaced segments
        selected_segments = []
        min_gap = 60.0  # 1 minute minimum gap

        for start, end in suitable_segments:
            if len(selected_segments) >= target_speakers:
                break

            # Check if this segment is far enough from selected ones
            too_close = any(
                abs(start - sel_start) < min_gap or abs(end - sel_end) < min_gap
                for sel_start, sel_end in selected_segments
            )

            if not too_close:
                selected_segments.append((start, end))

                candidate = AnchorCandidate(
                    speaker_id=f"FALLBACK_SPEAKER_{len(selected_segments)}",
                    start_time=start,
                    end_time=end,
                    duration=end - start,
                    quality_score=0.6,  # Medium quality for fallback
                    snr_db=0.0,  # Will be calculated later
                    voice_consistency=0.6,  # Assume medium consistency
                    isolation_score=0.0  # Will be calculated later
                )
                candidates.append(candidate)

        self.logger.info(f"Generated {len(candidates)} fallback candidates")
        return candidates

    def _cluster_voice_embeddings(self, segment_embeddings: List[Dict], target_speakers: int) -> Dict[str, List[Dict]]:
        """Cluster voice embeddings to identify speakers"""

        if not segment_embeddings:
            return {}

        try:
            from sklearn.cluster import AgglomerativeClustering
            import numpy as np

            # Extract embeddings matrix
            embeddings_matrix = np.array([seg['embedding'] for seg in segment_embeddings])

            # Perform clustering
            clustering = AgglomerativeClustering(
                n_clusters=min(target_speakers, len(segment_embeddings)),
                linkage='average',
                metric='cosine'
            )

            cluster_labels = clustering.fit_predict(embeddings_matrix)

            # Group segments by cluster
            clusters = {}
            for i, label in enumerate(cluster_labels):
                speaker_id = f"SPEAKER_{label + 1}"
                if speaker_id not in clusters:
                    clusters[speaker_id] = []
                clusters[speaker_id].append(segment_embeddings[i])

            self.logger.info(f"Clustered into {len(clusters)} speakers")
            return clusters

        except ImportError:
            self.logger.warning("sklearn not available, using fallback clustering")

            # Simple fallback: assign speakers based on temporal order
            clusters = {}
            segments_per_speaker = len(segment_embeddings) // target_speakers

            for i, segment in enumerate(segment_embeddings):
                speaker_num = min(i // max(1, segments_per_speaker), target_speakers - 1)
                speaker_id = f"SPEAKER_{speaker_num + 1}"

                if speaker_id not in clusters:
                    clusters[speaker_id] = []
                clusters[speaker_id].append(segment)

            return clusters

    def _find_best_segment_in_cluster(self, cluster_segments: List[Dict], audio: AudioSegment) -> Optional[Dict]:
        """Find the best anchor segment within a speaker cluster"""

        if not cluster_segments:
            return None

        # Score segments by duration preference and position
        scored_segments = []

        for segment in cluster_segments:
            duration = segment['duration']

            # Prefer segments close to optimal duration
            optimal_duration = (self.min_anchor_duration + self.max_anchor_duration) / 2
            duration_score = 1.0 - abs(duration - optimal_duration) / optimal_duration

            # Prefer segments not at the very beginning (intro/outro issues)
            position_score = 1.0 if segment['start'] > 30 else 0.7

            total_score = duration_score * 0.7 + position_score * 0.3

            scored_segments.append((total_score, segment))

        # Return highest scoring segment
        scored_segments.sort(key=lambda x: x[0], reverse=True)
        return scored_segments[0][1]

    def _assess_anchor_quality(self, candidates: List[AnchorCandidate], audio: AudioSegment) -> List[AnchorCandidate]:
        """Assess quality metrics for anchor candidates"""

        for candidate in candidates:
            try:
                # Extract candidate segment
                start_ms = int(candidate.start_time * 1000)
                end_ms = int(candidate.end_time * 1000)
                segment = audio[start_ms:end_ms]

                # Calculate SNR
                candidate.snr_db = self._calculate_snr(segment)

                # Calculate isolation score (simplified)
                candidate.isolation_score = self._calculate_isolation_score(segment)

                # Calculate overall quality score
                candidate.quality_score = self._calculate_quality_score(candidate)

                # Calculate confidence
                candidate.confidence = min(candidate.quality_score, 1.0)

            except Exception as e:
                self.logger.warning(f"Quality assessment failed for candidate: {e}")
                candidate.quality_score = 0.0
                candidate.confidence = 0.0

        # Filter by minimum quality
        quality_candidates = [c for c in candidates if c.quality_score >= 0.5]

        self.logger.info(f"Quality assessment: {len(quality_candidates)}/{len(candidates)} candidates passed")
        return quality_candidates

    def _calculate_snr(self, audio_segment: AudioSegment) -> float:
        """Calculate signal-to-noise ratio"""

        try:
            # Convert to numpy array
            audio_array = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)

            # Simple SNR estimation: assume noise is the quietest 10% of samples
            sorted_samples = np.sort(np.abs(audio_array))
            noise_threshold = int(len(sorted_samples) * 0.1)

            if noise_threshold > 0:
                noise_level = np.mean(sorted_samples[:noise_threshold])
                signal_level = np.mean(sorted_samples[noise_threshold:])

                if noise_level > 0:
                    snr_db = 20 * np.log10(signal_level / noise_level)
                    return float(snr_db)

            return 20.0  # Default reasonable SNR

        except Exception as e:
            self.logger.warning(f"SNR calculation failed: {e}")
            return 15.0  # Default

    def _calculate_isolation_score(self, audio_segment: AudioSegment) -> float:
        """Calculate how isolated/clean the speech is"""

        try:
            # Simple approach: check volume consistency
            # More consistent volume = better isolation
            audio_array = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)

            # Calculate RMS in overlapping windows
            window_size = int(16000 * 0.1)  # 100ms windows
            hop_size = window_size // 2

            rms_values = []
            for i in range(0, len(audio_array) - window_size, hop_size):
                window = audio_array[i:i + window_size]
                rms = np.sqrt(np.mean(window ** 2))
                rms_values.append(rms)

            if len(rms_values) > 1:
                # Lower variance in RMS = better isolation
                rms_std = np.std(rms_values)
                rms_mean = np.mean(rms_values)

                if rms_mean > 0:
                    isolation_score = 1.0 - min(rms_std / rms_mean, 1.0)
                    return float(isolation_score)

            return 0.7  # Default reasonable isolation

        except Exception as e:
            self.logger.warning(f"Isolation score calculation failed: {e}")
            return 0.6  # Default

    def _calculate_quality_score(self, candidate: AnchorCandidate) -> float:
        """Calculate overall quality score for candidate"""

        # Duration score (prefer optimal length)
        optimal_duration = (self.min_anchor_duration + self.max_anchor_duration) / 2
        duration_score = 1.0 - abs(candidate.duration - optimal_duration) / optimal_duration
        duration_score = max(0.0, duration_score)

        # SNR score
        snr_score = min(candidate.snr_db / 25.0, 1.0)  # Normalize to 25dB max

        # Isolation score
        isolation_score = candidate.isolation_score

        # Voice consistency score
        consistency_score = candidate.voice_consistency

        # Weighted combination
        quality_score = (
            duration_score * 0.25 +
            snr_score * 0.3 +
            isolation_score * 0.25 +
            consistency_score * 0.2
        )

        return quality_score

    def _select_best_anchors(self, candidates: List[AnchorCandidate], target_speakers: int) -> List[AnchorCandidate]:
        """Select the best anchor for each speaker"""

        # Group by speaker
        speaker_candidates = {}
        for candidate in candidates:
            speaker_id = candidate.speaker_id
            if speaker_id not in speaker_candidates:
                speaker_candidates[speaker_id] = []
            speaker_candidates[speaker_id].append(candidate)

        # Select best candidate per speaker
        selected = []
        for speaker_id, speaker_cands in speaker_candidates.items():
            if speaker_cands:
                # Sort by quality score
                speaker_cands.sort(key=lambda x: x.quality_score, reverse=True)
                selected.append(speaker_cands[0])

        # Sort by quality and limit to target number
        selected.sort(key=lambda x: x.quality_score, reverse=True)
        return selected[:target_speakers]

    def _extract_anchor_files(self, original_audio_file: str, selected_anchors: List[AnchorCandidate]) -> Dict[str, str]:
        """Extract anchor audio files from original audio"""

        anchor_files = {}

        # Create anchor output directory
        output_dir = Path("auto_anchors")
        output_dir.mkdir(exist_ok=True)

        # Load original audio
        audio = AudioSegment.from_file(original_audio_file)

        for candidate in selected_anchors:
            try:
                # Extract segment
                start_ms = int(candidate.start_time * 1000)
                end_ms = int(candidate.end_time * 1000)
                anchor_segment = audio[start_ms:end_ms]

                # Generate filename
                timestamp = int(candidate.start_time)
                filename = f"{candidate.speaker_id}_{timestamp}s.wav"
                file_path = output_dir / filename

                # Export as WAV
                anchor_segment.export(str(file_path), format="wav")

                anchor_files[candidate.speaker_id] = str(file_path)

                self.logger.info(f"Extracted anchor: {candidate.speaker_id} -> {file_path}")

            except Exception as e:
                self.logger.error(f"Failed to extract anchor for {candidate.speaker_id}: {e}")

        return anchor_files

    def _calculate_confidence(self, selected_anchors: List[AnchorCandidate], all_candidates: List[AnchorCandidate]) -> float:
        """Calculate overall confidence in auto-detected anchors"""

        if not selected_anchors:
            return 0.0

        # Average quality of selected anchors
        avg_quality = sum(anchor.quality_score for anchor in selected_anchors) / len(selected_anchors)

        # Penalty for having fewer anchors than expected
        target_count = 3  # Default target
        count_penalty = len(selected_anchors) / target_count if len(selected_anchors) < target_count else 1.0

        # Bonus for having good alternatives (indicates robust detection)
        alternative_bonus = 1.0
        if len(all_candidates) > len(selected_anchors):
            alternative_qualities = [c.quality_score for c in all_candidates if c not in selected_anchors]
            if alternative_qualities:
                avg_alternative_quality = sum(alternative_qualities) / len(alternative_qualities)
                alternative_bonus = 1.0 + (avg_alternative_quality * 0.1)

        confidence = avg_quality * count_penalty * alternative_bonus
        return min(confidence, 1.0)

    def _generate_quality_metrics(self, candidates: List[AnchorCandidate], selected: List[AnchorCandidate]) -> Dict:
        """Generate quality metrics for reporting"""

        metrics = {
            "total_candidates": len(candidates),
            "selected_anchors": len(selected),
            "avg_quality_all": sum(c.quality_score for c in candidates) / len(candidates) if candidates else 0.0,
            "avg_quality_selected": sum(c.quality_score for c in selected) / len(selected) if selected else 0.0,
            "avg_snr_db": sum(c.snr_db for c in selected) / len(selected) if selected else 0.0,
            "avg_isolation": sum(c.isolation_score for c in selected) / len(selected) if selected else 0.0,
            "speakers_detected": len(set(c.speaker_id for c in candidates))
        }

        return metrics


def main():
    """CLI interface for auto-anchor detection"""

    if len(sys.argv) < 2:
        print("Auto-Anchor Detection for Sherlock")
        print("Usage: python auto_anchor_detector.py <audio_file> [target_speakers] [analysis_duration]")
        print("Example: python auto_anchor_detector.py build/yt2_full_stereo.wav 3 900")
        sys.exit(1)

    audio_file = sys.argv[1]
    target_speakers = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    analysis_duration = int(sys.argv[3]) if len(sys.argv) > 3 else 900  # 15 minutes

    if not Path(audio_file).exists():
        print(f"❌ Audio file not found: {audio_file}")
        sys.exit(1)

    print("🔍 Auto-Anchor Detection for Sherlock")
    print("=" * 40)
    print(f"Audio file: {audio_file}")
    print(f"Target speakers: {target_speakers}")
    print(f"Analysis duration: {analysis_duration}s ({analysis_duration/60:.1f} minutes)")

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Run detection
    detector = AutoAnchorDetector()

    print("\n🚀 Starting auto-anchor detection...")
    result = detector.detect_anchors(audio_file, target_speakers, analysis_duration)

    # Display results
    print("\n" + "=" * 50)
    print("📊 AUTO-ANCHOR DETECTION RESULTS")
    print("=" * 50)

    print(f"Success: {'✅ YES' if result.success else '❌ NO'}")
    print(f"Confidence: {result.confidence:.1%}")
    print(f"Processing time: {result.processing_time:.1f}s")

    if result.selected_anchors:
        print(f"\n🎯 Selected Anchors:")
        for speaker_id, file_path in result.selected_anchors.items():
            print(f"  {speaker_id}: {file_path}")

    if result.quality_metrics:
        metrics = result.quality_metrics
        print(f"\n📈 Quality Metrics:")
        print(f"  Candidates found: {metrics['total_candidates']}")
        print(f"  Anchors selected: {metrics['selected_anchors']}")
        print(f"  Average quality: {metrics['avg_quality_selected']:.2f}")
        print(f"  Average SNR: {metrics['avg_snr_db']:.1f} dB")
        print(f"  Average isolation: {metrics['avg_isolation']:.2f}")

    if result.fallback_reason:
        print(f"\n⚠️ Fallback reason: {result.fallback_reason}")

    # Save results
    output_file = f"auto_anchor_result_{int(time.time())}.json"

    # Convert result to JSON-serializable format
    result_dict = {
        "success": result.success,
        "confidence": result.confidence,
        "processing_time": result.processing_time,
        "selected_anchors": result.selected_anchors,
        "quality_metrics": result.quality_metrics,
        "fallback_reason": result.fallback_reason,
        "candidates": [
            {
                "speaker_id": c.speaker_id,
                "start_time": c.start_time,
                "end_time": c.end_time,
                "duration": c.duration,
                "quality_score": c.quality_score,
                "snr_db": c.snr_db,
                "confidence": c.confidence
            }
            for c in result.anchor_candidates
        ]
    }

    with open(output_file, 'w') as f:
        json.dump(result_dict, f, indent=2)

    print(f"\n💾 Results saved: {output_file}")

    if result.success:
        print("\n✅ Auto-anchor detection successful!")
        print("   You can now use these anchors for supervised diarization.")
    else:
        print("\n⚠️ Auto-anchor detection needs manual review or fallback to unsupervised mode.")


if __name__ == "__main__":
    main()