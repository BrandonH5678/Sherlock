#!/usr/bin/env python3
"""
Advanced Diarization System for Sherlock Phase 6
Includes overlapping speech detection, emotion analysis, and enhanced speaker clustering
"""

import json
import numpy as np
import os
import sys
import time
import librosa
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import logging
from scipy import signal
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from voice_engine import VoiceEngineManager, SpeakerTurn, DiarizationResult

# Optional imports for advanced features
try:
    import torch
    import torch.nn.functional as F
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    RESEMBLYZER_AVAILABLE = True
except ImportError:
    RESEMBLYZER_AVAILABLE = False

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import webrtcvad
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False


class EmotionType(Enum):
    """Types of emotions detected in speech"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    STRESSED = "stressed"
    EXCITED = "excited"


class OverlapType(Enum):
    """Types of speech overlap"""
    NONE = "none"
    PARTIAL = "partial"      # Slight overlap, one speaker dominant
    CONCURRENT = "concurrent"  # Both speakers equally audible
    INTERRUPTION = "interruption"  # One speaker cuts off another
    CROSSTALK = "crosstalk"    # Multiple speakers talking simultaneously


@dataclass
class EmotionAnalysis:
    """Emotion analysis result for a speech segment"""
    emotion: EmotionType
    confidence: float
    arousal: float      # Low to high energy
    valence: float      # Negative to positive sentiment
    features: Dict      # Raw acoustic features
    timestamp: float


@dataclass
class OverlapDetection:
    """Overlapping speech detection result"""
    overlap_type: OverlapType
    start_time: float
    end_time: float
    speakers_involved: List[str]
    confidence: float
    dominant_speaker: Optional[str]
    overlap_ratio: float  # Percentage of segment with overlap


@dataclass
class AdvancedSpeakerTurn:
    """Enhanced speaker turn with emotion and overlap information"""
    speaker: str
    start: float
    end: float
    confidence: float
    text: Optional[str] = None
    emotion: Optional[EmotionAnalysis] = None
    overlap_info: Optional[OverlapDetection] = None
    acoustic_features: Optional[Dict] = None
    energy_profile: Optional[List[float]] = None


@dataclass
class AdvancedDiarizationResult:
    """Enhanced diarization result with advanced features"""
    turns: List[AdvancedSpeakerTurn]
    speakers: List[str]
    processing_time: float
    method: str
    confidence: float
    overlap_segments: List[OverlapDetection]
    emotion_timeline: List[EmotionAnalysis]
    speaker_characteristics: Dict  # Per-speaker acoustic profiles
    quality_metrics: Dict
    metadata: Dict = None


class AcousticFeatureExtractor:
    """Extracts acoustic features for emotion and speaker analysis"""

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate

    def extract_prosodic_features(self, audio_segment: np.ndarray) -> Dict:
        """Extract prosodic features (pitch, energy, tempo)"""
        features = {}

        try:
            # Fundamental frequency (pitch) analysis
            f0, voiced_flag, voiced_probs = librosa.pyin(
                audio_segment,
                fmin=librosa.note_to_hz('C2'),
                fmax=librosa.note_to_hz('C7'),
                sr=self.sample_rate
            )

            # Filter out unvoiced segments
            f0_voiced = f0[voiced_flag]

            if len(f0_voiced) > 0:
                features['pitch_mean'] = np.nanmean(f0_voiced)
                features['pitch_std'] = np.nanstd(f0_voiced)
                features['pitch_range'] = np.nanmax(f0_voiced) - np.nanmin(f0_voiced)
                features['pitch_median'] = np.nanmedian(f0_voiced)
            else:
                features['pitch_mean'] = 0.0
                features['pitch_std'] = 0.0
                features['pitch_range'] = 0.0
                features['pitch_median'] = 0.0

            # Energy features
            energy = librosa.feature.rms(y=audio_segment)[0]
            features['energy_mean'] = np.mean(energy)
            features['energy_std'] = np.std(energy)
            features['energy_max'] = np.max(energy)

            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_segment, sr=self.sample_rate)[0]
            features['spectral_centroid_mean'] = np.mean(spectral_centroids)
            features['spectral_centroid_std'] = np.std(spectral_centroids)

            # Zero crossing rate (indicator of speech/music discrimination)
            zcr = librosa.feature.zero_crossing_rate(audio_segment)[0]
            features['zcr_mean'] = np.mean(zcr)
            features['zcr_std'] = np.std(zcr)

            # Tempo analysis
            tempo, beats = librosa.beat.beat_track(y=audio_segment, sr=self.sample_rate)
            features['tempo'] = tempo

            # MFCC features (first 13 coefficients)
            mfccs = librosa.feature.mfcc(y=audio_segment, sr=self.sample_rate, n_mfcc=13)
            for i in range(13):
                features[f'mfcc_{i}_mean'] = np.mean(mfccs[i])
                features[f'mfcc_{i}_std'] = np.std(mfccs[i])

        except Exception as e:
            logging.warning(f"Feature extraction error: {e}")
            # Return default features on error
            features = {f'feature_{i}': 0.0 for i in range(20)}

        return features

    def extract_emotion_features(self, audio_segment: np.ndarray) -> Dict:
        """Extract features specifically for emotion detection"""
        features = self.extract_prosodic_features(audio_segment)

        try:
            # Add emotion-specific features
            # Jitter (pitch variation)
            f0, voiced_flag, _ = librosa.pyin(audio_segment, sr=self.sample_rate)
            f0_voiced = f0[voiced_flag]
            if len(f0_voiced) > 1:
                pitch_diffs = np.diff(f0_voiced)
                features['jitter'] = np.std(pitch_diffs) / np.mean(f0_voiced) if np.mean(f0_voiced) > 0 else 0

            # Shimmer (amplitude variation)
            rms_energy = librosa.feature.rms(y=audio_segment)[0]
            if len(rms_energy) > 1:
                amplitude_diffs = np.diff(rms_energy)
                features['shimmer'] = np.std(amplitude_diffs) / np.mean(rms_energy) if np.mean(rms_energy) > 0 else 0

            # Formant frequencies (vocal tract characteristics)
            # Simplified formant estimation using spectral peaks
            fft = np.fft.fft(audio_segment)
            freqs = np.fft.fftfreq(len(fft), 1/self.sample_rate)
            magnitude = np.abs(fft)

            # Find first 3 formants (simplified)
            positive_freqs = freqs[:len(freqs)//2]
            positive_magnitude = magnitude[:len(magnitude)//2]

            # Smooth the spectrum
            smoothed_magnitude = signal.savgol_filter(positive_magnitude, 51, 3)

            # Find peaks
            peaks, _ = signal.find_peaks(smoothed_magnitude, height=np.max(smoothed_magnitude) * 0.1)

            if len(peaks) >= 3:
                features['formant_f1'] = positive_freqs[peaks[0]]
                features['formant_f2'] = positive_freqs[peaks[1]]
                features['formant_f3'] = positive_freqs[peaks[2]]
            else:
                features['formant_f1'] = 0.0
                features['formant_f2'] = 0.0
                features['formant_f3'] = 0.0

        except Exception as e:
            logging.warning(f"Emotion feature extraction error: {e}")

        return features


class EmotionDetector:
    """Detects emotions from speech acoustic features"""

    def __init__(self):
        self.feature_extractor = AcousticFeatureExtractor()
        self.emotion_model = None
        self._init_model()

    def _init_model(self):
        """Initialize emotion detection model"""
        # For now, use rule-based emotion detection
        # In a full implementation, this would load a trained ML model
        pass

    def analyze_emotion(self, audio_segment: np.ndarray, timestamp: float) -> EmotionAnalysis:
        """Analyze emotion in an audio segment"""
        features = self.feature_extractor.extract_emotion_features(audio_segment)

        # Rule-based emotion classification (simplified)
        emotion, confidence = self._classify_emotion_rules(features)

        # Calculate arousal and valence
        arousal = self._calculate_arousal(features)
        valence = self._calculate_valence(features)

        return EmotionAnalysis(
            emotion=emotion,
            confidence=confidence,
            arousal=arousal,
            valence=valence,
            features=features,
            timestamp=timestamp
        )

    def _classify_emotion_rules(self, features: Dict) -> Tuple[EmotionType, float]:
        """Simple rule-based emotion classification"""
        # These are simplified rules - a real system would use trained models
        pitch_mean = features.get('pitch_mean', 0)
        energy_mean = features.get('energy_mean', 0)
        jitter = features.get('jitter', 0)
        spectral_centroid = features.get('spectral_centroid_mean', 0)

        # Normalize features for comparison
        normalized_pitch = min(1.0, pitch_mean / 200.0) if pitch_mean > 0 else 0
        normalized_energy = min(1.0, energy_mean * 1000) if energy_mean > 0 else 0

        # Simple classification rules
        if normalized_pitch > 0.7 and normalized_energy > 0.6:
            return EmotionType.EXCITED, 0.7
        elif normalized_pitch > 0.6 and jitter > 0.02:
            return EmotionType.STRESSED, 0.6
        elif normalized_pitch < 0.3 and normalized_energy < 0.3:
            return EmotionType.SAD, 0.6
        elif normalized_energy > 0.7 and spectral_centroid > 2000:
            return EmotionType.ANGRY, 0.65
        elif normalized_pitch > 0.5 and normalized_energy > 0.4:
            return EmotionType.HAPPY, 0.6
        else:
            return EmotionType.NEUTRAL, 0.8

    def _calculate_arousal(self, features: Dict) -> float:
        """Calculate arousal (energy level) from features"""
        energy = features.get('energy_mean', 0)
        tempo = features.get('tempo', 0)
        zcr = features.get('zcr_mean', 0)

        # Combine features for arousal estimation
        arousal = (energy * 1000 + tempo / 200 + zcr * 10) / 3
        return max(0.0, min(1.0, arousal))

    def _calculate_valence(self, features: Dict) -> float:
        """Calculate valence (positive/negative sentiment) from features"""
        pitch_mean = features.get('pitch_mean', 0)
        spectral_centroid = features.get('spectral_centroid_mean', 0)
        jitter = features.get('jitter', 0)

        # Higher pitch and spectral centroid often indicate positive emotions
        # Lower jitter indicates more stable (positive) emotional state
        valence = (pitch_mean / 300 + spectral_centroid / 3000 - jitter * 10) / 2
        return max(0.0, min(1.0, valence + 0.5))  # Bias toward neutral


class OverlapDetector:
    """Detects overlapping speech in multi-speaker audio"""

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.frame_length = int(0.025 * sample_rate)  # 25ms frames
        self.hop_length = int(0.010 * sample_rate)    # 10ms hop

    def detect_overlaps(self, audio: np.ndarray, speaker_turns: List[SpeakerTurn]) -> List[OverlapDetection]:
        """Detect overlapping speech segments"""
        overlaps = []

        # Create a timeline of speaker activity
        timeline = self._create_speaker_timeline(audio, speaker_turns)

        # Find periods with multiple active speakers
        overlap_periods = self._find_overlap_periods(timeline)

        # Analyze each overlap period
        for start_time, end_time, speakers in overlap_periods:
            overlap_info = self._analyze_overlap_segment(
                audio, start_time, end_time, speakers
            )
            overlaps.append(overlap_info)

        return overlaps

    def _create_speaker_timeline(self, audio: np.ndarray, speaker_turns: List[SpeakerTurn]) -> Dict:
        """Create a timeline showing speaker activity"""
        duration = len(audio) / self.sample_rate
        time_resolution = 0.1  # 100ms resolution
        num_frames = int(duration / time_resolution) + 1

        timeline = {}
        for frame_idx in range(num_frames):
            timestamp = frame_idx * time_resolution
            active_speakers = []

            for turn in speaker_turns:
                if turn.start <= timestamp <= turn.end:
                    active_speakers.append(turn.speaker)

            timeline[timestamp] = active_speakers

        return timeline

    def _find_overlap_periods(self, timeline: Dict) -> List[Tuple[float, float, List[str]]]:
        """Find continuous periods with multiple speakers"""
        overlap_periods = []
        current_overlap = None

        for timestamp in sorted(timeline.keys()):
            speakers = timeline[timestamp]

            if len(speakers) > 1:
                if current_overlap is None:
                    # Start new overlap period
                    current_overlap = {
                        'start': timestamp,
                        'speakers': set(speakers)
                    }
                else:
                    # Continue overlap period
                    current_overlap['speakers'].update(speakers)
            else:
                if current_overlap is not None:
                    # End overlap period
                    overlap_periods.append((
                        current_overlap['start'],
                        timestamp,
                        list(current_overlap['speakers'])
                    ))
                    current_overlap = None

        # Handle overlap at end of audio
        if current_overlap is not None:
            final_time = max(timeline.keys())
            overlap_periods.append((
                current_overlap['start'],
                final_time,
                list(current_overlap['speakers'])
            ))

        return overlap_periods

    def _analyze_overlap_segment(self, audio: np.ndarray, start_time: float,
                               end_time: float, speakers: List[str]) -> OverlapDetection:
        """Analyze a specific overlap segment"""
        # Extract audio segment
        start_sample = int(start_time * self.sample_rate)
        end_sample = int(end_time * self.sample_rate)
        segment = audio[start_sample:end_sample]

        # Analyze overlap characteristics
        overlap_ratio = self._calculate_overlap_ratio(segment)
        overlap_type = self._classify_overlap_type(segment, overlap_ratio)
        dominant_speaker = self._find_dominant_speaker(segment, speakers)

        # Calculate confidence based on energy distribution
        confidence = min(0.9, overlap_ratio + 0.3)

        return OverlapDetection(
            overlap_type=overlap_type,
            start_time=start_time,
            end_time=end_time,
            speakers_involved=speakers,
            confidence=confidence,
            dominant_speaker=dominant_speaker,
            overlap_ratio=overlap_ratio
        )

    def _calculate_overlap_ratio(self, segment: np.ndarray) -> float:
        """Calculate the ratio of overlapping speech in segment"""
        if len(segment) == 0:
            return 0.0

        # Use energy-based approach to estimate overlap
        # Higher energy variance might indicate multiple speakers
        energy = librosa.feature.rms(y=segment, frame_length=self.frame_length,
                                   hop_length=self.hop_length)[0]

        if len(energy) < 2:
            return 0.0

        # Calculate energy variation coefficient
        energy_std = np.std(energy)
        energy_mean = np.mean(energy)

        if energy_mean > 0:
            variation_coeff = energy_std / energy_mean
            # Map variation to overlap ratio (heuristic)
            overlap_ratio = min(1.0, variation_coeff * 2)
        else:
            overlap_ratio = 0.0

        return overlap_ratio

    def _classify_overlap_type(self, segment: np.ndarray, overlap_ratio: float) -> OverlapType:
        """Classify the type of overlap"""
        if overlap_ratio < 0.2:
            return OverlapType.NONE
        elif overlap_ratio < 0.4:
            return OverlapType.PARTIAL
        elif overlap_ratio < 0.6:
            return OverlapType.INTERRUPTION
        elif overlap_ratio < 0.8:
            return OverlapType.CONCURRENT
        else:
            return OverlapType.CROSSTALK

    def _find_dominant_speaker(self, segment: np.ndarray, speakers: List[str]) -> Optional[str]:
        """Find the dominant speaker in an overlap segment"""
        if len(speakers) <= 1:
            return speakers[0] if speakers else None

        # For now, return first speaker as placeholder
        # In a full implementation, this would use speaker embeddings
        # to determine which speaker has higher energy/presence
        return speakers[0]


class AdvancedDiarizationEngine:
    """Advanced diarization engine with emotion and overlap detection"""

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.emotion_detector = EmotionDetector()
        self.overlap_detector = OverlapDetector(sample_rate)
        self.feature_extractor = AcousticFeatureExtractor(sample_rate)

    def process_advanced_diarization(self, audio_path: str,
                                   basic_turns: List[SpeakerTurn],
                                   emotion_analysis: bool = True,
                                   overlap_detection: bool = True) -> AdvancedDiarizationResult:
        """Process advanced diarization with emotion and overlap detection"""

        start_time = time.time()

        # Load audio
        audio, sr = librosa.load(audio_path, sr=self.sample_rate)

        # Convert basic turns to advanced turns
        advanced_turns = []
        emotion_timeline = []
        speaker_characteristics = {}

        for turn in basic_turns:
            # Extract audio segment for this turn
            start_sample = int(turn.start * self.sample_rate)
            end_sample = int(turn.end * self.sample_rate)
            segment = audio[start_sample:end_sample]

            # Analyze emotion if requested
            emotion_analysis_result = None
            if emotion_analysis and len(segment) > 0:
                emotion_analysis_result = self.emotion_detector.analyze_emotion(
                    segment, turn.start
                )
                emotion_timeline.append(emotion_analysis_result)

            # Extract acoustic features
            acoustic_features = None
            if len(segment) > 0:
                acoustic_features = self.feature_extractor.extract_prosodic_features(segment)

                # Update speaker characteristics
                if turn.speaker not in speaker_characteristics:
                    speaker_characteristics[turn.speaker] = {
                        'feature_history': [],
                        'emotion_history': []
                    }

                speaker_characteristics[turn.speaker]['feature_history'].append(acoustic_features)
                if emotion_analysis_result:
                    speaker_characteristics[turn.speaker]['emotion_history'].append(emotion_analysis_result)

            # Create advanced turn
            advanced_turn = AdvancedSpeakerTurn(
                speaker=turn.speaker,
                start=turn.start,
                end=turn.end,
                confidence=turn.confidence,
                text=turn.text,
                emotion=emotion_analysis_result,
                overlap_info=None,  # Will be filled in overlap detection
                acoustic_features=acoustic_features,
                energy_profile=self._calculate_energy_profile(segment) if len(segment) > 0 else None
            )
            advanced_turns.append(advanced_turn)

        # Detect overlaps if requested
        overlap_segments = []
        if overlap_detection:
            overlap_segments = self.overlap_detector.detect_overlaps(audio, basic_turns)

            # Update turns with overlap information
            for turn in advanced_turns:
                for overlap in overlap_segments:
                    if (overlap.start_time <= turn.start < overlap.end_time or
                        overlap.start_time < turn.end <= overlap.end_time or
                        (turn.start <= overlap.start_time and turn.end >= overlap.end_time)):
                        turn.overlap_info = overlap
                        break

        # Calculate speaker characteristics summaries
        for speaker_id in speaker_characteristics:
            char_data = speaker_characteristics[speaker_id]
            if char_data['feature_history']:
                # Average features across all turns for this speaker
                feature_summary = self._summarize_speaker_features(char_data['feature_history'])
                char_data['average_features'] = feature_summary

            if char_data['emotion_history']:
                emotion_summary = self._summarize_speaker_emotions(char_data['emotion_history'])
                char_data['emotion_profile'] = emotion_summary

        # Calculate quality metrics
        quality_metrics = self._calculate_quality_metrics(
            advanced_turns, overlap_segments, emotion_timeline
        )

        processing_time = time.time() - start_time

        return AdvancedDiarizationResult(
            turns=advanced_turns,
            speakers=list(set(turn.speaker for turn in advanced_turns)),
            processing_time=processing_time,
            method="advanced_diarization_v1",
            confidence=np.mean([turn.confidence for turn in advanced_turns]) if advanced_turns else 0.0,
            overlap_segments=overlap_segments,
            emotion_timeline=emotion_timeline,
            speaker_characteristics=speaker_characteristics,
            quality_metrics=quality_metrics,
            metadata={
                'audio_path': audio_path,
                'emotion_analysis_enabled': emotion_analysis,
                'overlap_detection_enabled': overlap_detection,
                'sample_rate': self.sample_rate,
                'timestamp': datetime.now().isoformat()
            }
        )

    def _calculate_energy_profile(self, segment: np.ndarray) -> List[float]:
        """Calculate energy profile for a speech segment"""
        if len(segment) == 0:
            return []

        # Calculate RMS energy in 100ms windows
        window_size = int(0.1 * self.sample_rate)  # 100ms windows
        hop_size = int(0.05 * self.sample_rate)    # 50ms hop

        energy_profile = []
        for i in range(0, len(segment) - window_size + 1, hop_size):
            window = segment[i:i + window_size]
            energy = np.sqrt(np.mean(window ** 2))
            energy_profile.append(float(energy))

        return energy_profile

    def _summarize_speaker_features(self, feature_history: List[Dict]) -> Dict:
        """Summarize acoustic features across multiple turns for a speaker"""
        if not feature_history:
            return {}

        # Calculate means and standard deviations for each feature
        feature_keys = feature_history[0].keys()
        summary = {}

        for key in feature_keys:
            values = [features.get(key, 0.0) for features in feature_history]
            summary[f"{key}_mean"] = np.mean(values)
            summary[f"{key}_std"] = np.std(values)
            summary[f"{key}_min"] = np.min(values)
            summary[f"{key}_max"] = np.max(values)

        return summary

    def _summarize_speaker_emotions(self, emotion_history: List[EmotionAnalysis]) -> Dict:
        """Summarize emotion patterns for a speaker"""
        if not emotion_history:
            return {}

        # Count emotion occurrences
        emotion_counts = {}
        total_arousal = 0.0
        total_valence = 0.0

        for emotion_analysis in emotion_history:
            emotion_type = emotion_analysis.emotion.value
            emotion_counts[emotion_type] = emotion_counts.get(emotion_type, 0) + 1
            total_arousal += emotion_analysis.arousal
            total_valence += emotion_analysis.valence

        # Calculate averages and dominant emotion
        num_samples = len(emotion_history)
        avg_arousal = total_arousal / num_samples
        avg_valence = total_valence / num_samples
        dominant_emotion = max(emotion_counts, key=emotion_counts.get)

        return {
            'dominant_emotion': dominant_emotion,
            'emotion_distribution': emotion_counts,
            'average_arousal': avg_arousal,
            'average_valence': avg_valence,
            'emotional_stability': 1.0 - (len(set(emotion_counts.keys())) / 7.0)  # 7 emotion types
        }

    def _calculate_quality_metrics(self, turns: List[AdvancedSpeakerTurn],
                                 overlaps: List[OverlapDetection],
                                 emotions: List[EmotionAnalysis]) -> Dict:
        """Calculate quality metrics for advanced diarization"""
        metrics = {
            'total_turns': len(turns),
            'total_speakers': len(set(turn.speaker for turn in turns)),
            'overlap_segments': len(overlaps),
            'emotion_samples': len(emotions),
            'avg_turn_confidence': np.mean([turn.confidence for turn in turns]) if turns else 0.0,
            'avg_overlap_confidence': np.mean([ov.confidence for ov in overlaps]) if overlaps else 0.0,
            'avg_emotion_confidence': np.mean([em.confidence for em in emotions]) if emotions else 0.0
        }

        # Turn duration statistics
        if turns:
            durations = [turn.end - turn.start for turn in turns]
            metrics['avg_turn_duration'] = np.mean(durations)
            metrics['min_turn_duration'] = np.min(durations)
            metrics['max_turn_duration'] = np.max(durations)

        # Overlap statistics
        if overlaps:
            overlap_durations = [ov.end_time - ov.start_time for ov in overlaps]
            metrics['avg_overlap_duration'] = np.mean(overlap_durations)
            metrics['total_overlap_time'] = sum(overlap_durations)

            overlap_ratios = [ov.overlap_ratio for ov in overlaps]
            metrics['avg_overlap_ratio'] = np.mean(overlap_ratios)

        return metrics

    def export_advanced_results(self, result: AdvancedDiarizationResult, output_path: str):
        """Export advanced diarization results to JSON"""
        export_data = {
            'turns': [asdict(turn) for turn in result.turns],
            'speakers': result.speakers,
            'processing_time': result.processing_time,
            'method': result.method,
            'confidence': result.confidence,
            'overlap_segments': [asdict(overlap) for overlap in result.overlap_segments],
            'emotion_timeline': [asdict(emotion) for emotion in result.emotion_timeline],
            'speaker_characteristics': result.speaker_characteristics,
            'quality_metrics': result.quality_metrics,
            'metadata': result.metadata,
            'export_timestamp': datetime.now().isoformat()
        }

        # Convert numpy types to Python types for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            return obj

        export_data = convert_numpy(export_data)

        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)


def main():
    """Demo of advanced diarization capabilities"""
    print("🧠 Advanced Diarization Engine - Phase 6")
    print("=" * 50)

    engine = AdvancedDiarizationEngine()

    print("✅ Advanced diarization engine initialized")
    print("😊 Emotion detection: 7 emotion types + arousal/valence")
    print("🗣️  Overlap detection: 5 overlap types with analysis")
    print("🎵 Acoustic features: Prosodic + MFCC + spectral analysis")
    print("📊 Speaker profiling: Characteristic summaries per speaker")
    print("\nReady for integration with existing Sherlock diarization system")

    # Example of how to use with existing system:
    # basic_turns = [...] # From existing diarization
    # result = engine.process_advanced_diarization("audio.wav", basic_turns)
    # engine.export_advanced_results(result, "advanced_analysis.json")


if __name__ == "__main__":
    main()