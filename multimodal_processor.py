#!/usr/bin/env python3
"""
Multi-Modal Processing Pipeline for Sherlock Phase 6
Handles video, visual speaker identification, document references, and cross-modal correlation
"""

import cv2
import json
import numpy as np
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from evidence_database import EvidenceDatabase, EvidenceSource, EvidenceClaim, EvidenceType
from voice_engine import VoiceEngineManager, DiarizationResult, SpeakerTurn

# Optional imports for advanced features
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False


class ModalityType(Enum):
    """Types of modalities for processing"""
    AUDIO = "audio"
    VIDEO = "video"
    VISUAL_SPEAKER = "visual_speaker"
    DOCUMENT = "document"
    IMAGE = "image"
    TEXT = "text"


class ProcessingQuality(Enum):
    """Quality levels for processing trade-offs"""
    FAST = "fast"        # Basic processing for real-time
    BALANCED = "balanced"  # Good quality/speed balance
    HIGH = "high"        # Maximum quality, slower
    RESEARCH = "research"  # Full analysis for evidence


@dataclass
class VisualSpeakerFrame:
    """Visual speaker identification for a video frame"""
    timestamp: float
    frame_number: int
    detected_faces: List[Dict]
    speaker_assignments: Dict[str, float]  # speaker_id -> confidence
    face_embeddings: Optional[List] = None
    landmarks: Optional[List] = None


@dataclass
class DocumentReference:
    """Reference to external document found in content"""
    reference_id: str
    document_type: str  # "url", "doi", "citation", "title"
    reference_text: str
    confidence: float
    context: str
    timestamp: Optional[float] = None
    verified: bool = False
    metadata: Dict = None


@dataclass
class CrossModalCorrelation:
    """Correlation between different modalities"""
    correlation_id: str
    modality_1: ModalityType
    modality_2: ModalityType
    correlation_type: str  # "speaker_visual", "document_audio", "emotion_visual"
    confidence: float
    timestamp_range: Tuple[float, float]
    evidence: Dict
    metadata: Dict = None


@dataclass
class MultiModalResult:
    """Result from multi-modal processing"""
    source_id: str
    modalities_processed: List[ModalityType]
    processing_time: float
    visual_speakers: List[VisualSpeakerFrame]
    document_references: List[DocumentReference]
    cross_modal_correlations: List[CrossModalCorrelation]
    quality_metrics: Dict
    errors: List[str]
    metadata: Dict = None


class VisualSpeakerProcessor:
    """Handles visual speaker identification from video"""

    def __init__(self, quality: ProcessingQuality = ProcessingQuality.BALANCED):
        self.quality = quality
        self.face_detector = None
        self.face_recognizer = None
        self.mediapipe_face = None
        self._init_processors()

    def _init_processors(self):
        """Initialize face detection and recognition processors"""
        if MEDIAPIPE_AVAILABLE:
            self.mediapipe_face = mp.solutions.face_detection.FaceDetection(
                model_selection=1,  # Full range model
                min_detection_confidence=0.5
            )

        # Initialize OpenCV face detector as fallback
        try:
            self.face_detector = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
        except Exception as e:
            print(f"Warning: OpenCV face detector not available: {e}")

    def process_video_frames(self, video_path: str, sample_rate: float = 1.0) -> List[VisualSpeakerFrame]:
        """Process video frames for visual speaker identification"""
        frames = []

        if not os.path.exists(video_path):
            return frames

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return frames

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = max(1, int(fps / sample_rate))
        frame_number = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_number % frame_interval == 0:
                    timestamp = frame_number / fps
                    visual_frame = self._analyze_frame(frame, timestamp, frame_number)
                    if visual_frame:
                        frames.append(visual_frame)

                frame_number += 1

        finally:
            cap.release()

        return frames

    def _analyze_frame(self, frame: np.ndarray, timestamp: float, frame_number: int) -> Optional[VisualSpeakerFrame]:
        """Analyze a single frame for faces and speakers"""
        detected_faces = []
        speaker_assignments = {}

        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Use MediaPipe if available
        if self.mediapipe_face and MEDIAPIPE_AVAILABLE:
            results = self.mediapipe_face.process(rgb_frame)

            if results.detections:
                for i, detection in enumerate(results.detections):
                    bbox = detection.location_data.relative_bounding_box
                    h, w, _ = frame.shape

                    face_info = {
                        'id': f'face_{i}',
                        'bbox': {
                            'x': int(bbox.xmin * w),
                            'y': int(bbox.ymin * h),
                            'width': int(bbox.width * w),
                            'height': int(bbox.height * h)
                        },
                        'confidence': detection.score[0] if detection.score else 0.0
                    }
                    detected_faces.append(face_info)

                    # Assign to speaker (placeholder logic)
                    speaker_id = f"visual_speaker_{i}"
                    speaker_assignments[speaker_id] = face_info['confidence']

        # Fallback to OpenCV
        elif self.face_detector is not None:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_detector.detectMultiScale(gray, 1.1, 4)

            for i, (x, y, w, h) in enumerate(faces):
                face_info = {
                    'id': f'face_{i}',
                    'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                    'confidence': 0.8  # Default confidence for OpenCV
                }
                detected_faces.append(face_info)

                speaker_id = f"visual_speaker_{i}"
                speaker_assignments[speaker_id] = 0.8

        if detected_faces:
            return VisualSpeakerFrame(
                timestamp=timestamp,
                frame_number=frame_number,
                detected_faces=detected_faces,
                speaker_assignments=speaker_assignments
            )

        return None


class DocumentReferenceExtractor:
    """Extracts and validates document references from transcripts"""

    def __init__(self):
        self.url_pattern = re.compile(
            r'https?://[^\s<>"{}|\\^`\[\]]+',
            re.IGNORECASE
        )
        self.doi_pattern = re.compile(
            r'\b10\.\d{4,}/[^\s]+',
            re.IGNORECASE
        )
        self.citation_pattern = re.compile(
            r'\b[A-Z][a-z]+(?:\s+et\s+al\.?)?\s+\(\d{4}\)',
            re.IGNORECASE
        )

    def extract_references(self, text: str, timestamp: Optional[float] = None) -> List[DocumentReference]:
        """Extract document references from text"""
        references = []

        # Extract URLs
        for match in self.url_pattern.finditer(text):
            ref = DocumentReference(
                reference_id=f"url_{len(references)}",
                document_type="url",
                reference_text=match.group(),
                confidence=0.9,
                context=self._get_context(text, match.start(), match.end()),
                timestamp=timestamp
            )
            references.append(ref)

        # Extract DOIs
        for match in self.doi_pattern.finditer(text):
            ref = DocumentReference(
                reference_id=f"doi_{len(references)}",
                document_type="doi",
                reference_text=match.group(),
                confidence=0.95,
                context=self._get_context(text, match.start(), match.end()),
                timestamp=timestamp
            )
            references.append(ref)

        # Extract citations
        for match in self.citation_pattern.finditer(text):
            ref = DocumentReference(
                reference_id=f"citation_{len(references)}",
                document_type="citation",
                reference_text=match.group(),
                confidence=0.7,
                context=self._get_context(text, match.start(), match.end()),
                timestamp=timestamp
            )
            references.append(ref)

        return references

    def _get_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Get context around a matched reference"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end].strip()


class CrossModalCorrelationEngine:
    """Correlates information across different modalities"""

    def __init__(self):
        self.correlation_threshold = 0.6

    def correlate_speaker_visual(self, audio_speakers: List[SpeakerTurn],
                               visual_frames: List[VisualSpeakerFrame]) -> List[CrossModalCorrelation]:
        """Correlate audio speakers with visual speaker identification"""
        correlations = []

        for speaker_turn in audio_speakers:
            # Find visual frames during this speaker turn
            relevant_frames = [
                frame for frame in visual_frames
                if speaker_turn.start <= frame.timestamp <= speaker_turn.end
            ]

            if relevant_frames:
                # Calculate confidence based on visual consistency
                visual_confidence = self._calculate_visual_consistency(relevant_frames)

                if visual_confidence > self.correlation_threshold:
                    correlation = CrossModalCorrelation(
                        correlation_id=f"speaker_visual_{speaker_turn.speaker}_{len(correlations)}",
                        modality_1=ModalityType.AUDIO,
                        modality_2=ModalityType.VISUAL_SPEAKER,
                        correlation_type="speaker_visual",
                        confidence=visual_confidence,
                        timestamp_range=(speaker_turn.start, speaker_turn.end),
                        evidence={
                            'audio_speaker': speaker_turn.speaker,
                            'visual_frames': len(relevant_frames),
                            'face_detections': sum(len(f.detected_faces) for f in relevant_frames)
                        }
                    )
                    correlations.append(correlation)

        return correlations

    def correlate_document_audio(self, audio_speakers: List[SpeakerTurn],
                               document_refs: List[DocumentReference]) -> List[CrossModalCorrelation]:
        """Correlate document references with speaker turns"""
        correlations = []

        for doc_ref in document_refs:
            if doc_ref.timestamp is None:
                continue

            # Find the speaker turn containing this reference
            for speaker_turn in audio_speakers:
                if (speaker_turn.start <= doc_ref.timestamp <= speaker_turn.end and
                    speaker_turn.text and doc_ref.reference_text.lower() in speaker_turn.text.lower()):

                    correlation = CrossModalCorrelation(
                        correlation_id=f"doc_audio_{doc_ref.reference_id}_{len(correlations)}",
                        modality_1=ModalityType.DOCUMENT,
                        modality_2=ModalityType.AUDIO,
                        correlation_type="document_audio",
                        confidence=doc_ref.confidence * speaker_turn.confidence,
                        timestamp_range=(speaker_turn.start, speaker_turn.end),
                        evidence={
                            'document_reference': doc_ref.reference_text,
                            'speaker': speaker_turn.speaker,
                            'reference_type': doc_ref.document_type
                        }
                    )
                    correlations.append(correlation)

        return correlations

    def _calculate_visual_consistency(self, frames: List[VisualSpeakerFrame]) -> float:
        """Calculate consistency of visual speaker identification across frames"""
        if not frames:
            return 0.0

        # Simple consistency metric based on number of faces detected
        face_counts = [len(frame.detected_faces) for frame in frames]
        if not face_counts:
            return 0.0

        # Consistency based on stable face count and detection confidence
        avg_faces = sum(face_counts) / len(face_counts)
        face_variance = sum((count - avg_faces) ** 2 for count in face_counts) / len(face_counts)

        # Average confidence across all detections
        total_confidence = 0.0
        total_detections = 0
        for frame in frames:
            for face in frame.detected_faces:
                total_confidence += face.get('confidence', 0.0)
                total_detections += 1

        avg_confidence = total_confidence / max(1, total_detections)

        # Combine variance (lower is better) and confidence (higher is better)
        consistency = avg_confidence * (1.0 - min(face_variance / max(1, avg_faces), 1.0))

        return max(0.0, min(1.0, consistency))


class MultiModalProcessor:
    """Main multi-modal processing pipeline for Phase 6"""

    def __init__(self, db_path: str = "evidence.db"):
        self.db = EvidenceDatabase(db_path)
        self.voice_engine = VoiceEngineManager()
        self.visual_processor = VisualSpeakerProcessor()
        self.document_extractor = DocumentReferenceExtractor()
        self.correlation_engine = CrossModalCorrelationEngine()

    def process_multimodal_content(self, source_path: str, source_type: str,
                                 quality: ProcessingQuality = ProcessingQuality.BALANCED) -> MultiModalResult:
        """Process multi-modal content (video with audio, documents with references)"""

        start_time = time.time()
        modalities_processed = []
        visual_speakers = []
        document_references = []
        cross_modal_correlations = []
        errors = []

        source_id = f"multimodal_{int(time.time())}"

        try:
            # Process video if available
            if source_type in ["video", "mp4", "avi", "mov", "mkv"]:
                modalities_processed.append(ModalityType.VIDEO)
                modalities_processed.append(ModalityType.VISUAL_SPEAKER)

                try:
                    visual_speakers = self.visual_processor.process_video_frames(source_path, sample_rate=1.0)
                except Exception as e:
                    errors.append(f"Visual processing error: {str(e)}")

            # Process audio for speaker diarization
            audio_speakers = []
            if source_type in ["video", "audio", "mp4", "avi", "mov", "mkv", "wav", "mp3", "m4a"]:
                modalities_processed.append(ModalityType.AUDIO)

                try:
                    # Use existing voice engine for diarization
                    # This would integrate with the existing diarization system
                    # For now, we'll create a placeholder result
                    audio_speakers = self._get_audio_speakers(source_path)
                except Exception as e:
                    errors.append(f"Audio processing error: {str(e)}")

            # Extract document references from transcript
            if audio_speakers:
                modalities_processed.append(ModalityType.DOCUMENT)

                for speaker_turn in audio_speakers:
                    if speaker_turn.text:
                        try:
                            refs = self.document_extractor.extract_references(
                                speaker_turn.text,
                                speaker_turn.start
                            )
                            document_references.extend(refs)
                        except Exception as e:
                            errors.append(f"Document extraction error: {str(e)}")

            # Perform cross-modal correlations
            if len(modalities_processed) > 1:
                try:
                    # Speaker-visual correlation
                    if audio_speakers and visual_speakers:
                        speaker_visual_corr = self.correlation_engine.correlate_speaker_visual(
                            audio_speakers, visual_speakers
                        )
                        cross_modal_correlations.extend(speaker_visual_corr)

                    # Document-audio correlation
                    if audio_speakers and document_references:
                        doc_audio_corr = self.correlation_engine.correlate_document_audio(
                            audio_speakers, document_references
                        )
                        cross_modal_correlations.extend(doc_audio_corr)

                except Exception as e:
                    errors.append(f"Cross-modal correlation error: {str(e)}")

            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(
                visual_speakers, document_references, cross_modal_correlations
            )

            processing_time = time.time() - start_time

            return MultiModalResult(
                source_id=source_id,
                modalities_processed=modalities_processed,
                processing_time=processing_time,
                visual_speakers=visual_speakers,
                document_references=document_references,
                cross_modal_correlations=cross_modal_correlations,
                quality_metrics=quality_metrics,
                errors=errors,
                metadata={
                    'source_path': source_path,
                    'source_type': source_type,
                    'quality_setting': quality.value,
                    'timestamp': datetime.now().isoformat()
                }
            )

        except Exception as e:
            errors.append(f"Critical processing error: {str(e)}")
            return MultiModalResult(
                source_id=source_id,
                modalities_processed=modalities_processed,
                processing_time=time.time() - start_time,
                visual_speakers=[],
                document_references=[],
                cross_modal_correlations=[],
                quality_metrics={},
                errors=errors
            )

    def _get_audio_speakers(self, source_path: str) -> List[SpeakerTurn]:
        """Get speaker turns from audio (placeholder for integration)"""
        # This would integrate with the existing voice engine and diarization system
        # For now, return a simple placeholder
        return [
            SpeakerTurn(
                speaker="Speaker_0",
                start=0.0,
                end=10.0,
                confidence=0.8,
                text="Sample transcript text for testing document extraction"
            )
        ]

    def _calculate_quality_metrics(self, visual_speakers: List[VisualSpeakerFrame],
                                 document_refs: List[DocumentReference],
                                 correlations: List[CrossModalCorrelation]) -> Dict:
        """Calculate quality metrics for multi-modal processing"""
        return {
            'visual_frames_processed': len(visual_speakers),
            'faces_detected': sum(len(vs.detected_faces) for vs in visual_speakers),
            'document_references_found': len(document_refs),
            'cross_modal_correlations': len(correlations),
            'avg_visual_confidence': np.mean([
                face['confidence']
                for vs in visual_speakers
                for face in vs.detected_faces
            ]) if visual_speakers else 0.0,
            'avg_document_confidence': np.mean([
                ref.confidence for ref in document_refs
            ]) if document_refs else 0.0,
            'avg_correlation_confidence': np.mean([
                corr.confidence for corr in correlations
            ]) if correlations else 0.0
        }

    def export_multimodal_results(self, result: MultiModalResult, output_path: str):
        """Export multi-modal processing results"""
        export_data = {
            'source_id': result.source_id,
            'modalities_processed': [m.value for m in result.modalities_processed],
            'processing_time': result.processing_time,
            'visual_speakers': [asdict(vs) for vs in result.visual_speakers],
            'document_references': [asdict(dr) for dr in result.document_references],
            'cross_modal_correlations': [asdict(cc) for cc in result.cross_modal_correlations],
            'quality_metrics': result.quality_metrics,
            'errors': result.errors,
            'metadata': result.metadata,
            'generated_at': datetime.now().isoformat()
        }

        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)


def main():
    """Demo of multi-modal processing capabilities"""
    processor = MultiModalProcessor()

    # Example usage
    print("🎬 Multi-Modal Processing Pipeline - Phase 6")
    print("=" * 50)

    # This would process a real video file
    # result = processor.process_multimodal_content("sample_video.mp4", "video")
    # processor.export_multimodal_results(result, "multimodal_analysis.json")

    print("✅ Multi-modal processor initialized")
    print("📹 Video processing: Face detection and visual speaker ID")
    print("📄 Document reference extraction from transcripts")
    print("🔗 Cross-modal correlation analysis")
    print("\nReady for integration with existing Sherlock system")


if __name__ == "__main__":
    main()