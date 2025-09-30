#!/usr/bin/env python3
"""
Dual-Engine Voice Processing System
Supports both Squirt (fast/accurate modes) and Sherlock (auto-anchor detection)
Enhanced with Intelligent Model Selection for constraint-aware processing
"""

import asyncio
import json
import logging
import time
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import threading
import queue

# Core dependencies
import numpy as np
import torch
from pydub import AudioSegment
import webrtcvad

# Intelligent model selection
from intelligent_model_selector import IntelligentModelSelector, QualityPreference

# Engine imports (to be loaded lazily)
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False

try:
    import whisper
    OPENAI_WHISPER_AVAILABLE = True
except ImportError:
    OPENAI_WHISPER_AVAILABLE = False

try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    RESEMBLYZER_AVAILABLE = True
except ImportError:
    RESEMBLYZER_AVAILABLE = False


class TranscriptionMode(Enum):
    FAST = "fast"           # faster-whisper tiny for speed
    ACCURATE = "accurate"   # whisper large-v3 for accuracy
    AUTO = "auto"          # system chooses based on content


class ProcessingPriority(Enum):
    IMMEDIATE = "immediate"  # Squirt voice memos - preempt everything
    SCHEDULED = "scheduled"  # Sherlock research - scheduled processing
    BACKGROUND = "background" # Batch processing when system idle


@dataclass
class VoiceProcessingRequest:
    """Request for voice processing"""
    audio_path: str
    mode: TranscriptionMode
    priority: ProcessingPriority
    system: str  # "squirt" or "sherlock"
    metadata: Dict = None
    callback: Optional[callable] = None


@dataclass
class TranscriptionResult:
    """Result from voice transcription"""
    text: str
    segments: List[Dict]
    processing_time: float
    model_used: str
    confidence: float
    metadata: Dict = None


@dataclass
class SpeakerTurn:
    """Speaker diarization turn"""
    speaker: str
    start: float
    end: float
    confidence: float
    text: Optional[str] = None


@dataclass
class DiarizationResult:
    """Result from speaker diarization"""
    turns: List[SpeakerTurn]
    speakers: List[str]
    processing_time: float
    method: str
    confidence: float
    anchors_used: Optional[List[str]] = None
    auto_anchors: Optional[Dict] = None


class VoiceEngineManager:
    """
    Central manager for dual-engine voice processing
    Handles both Squirt and Sherlock use cases with intelligent resource management
    """

    def __init__(self, max_ram_gb: float = 12.0, enable_intelligent_selection: bool = True):
        self.max_ram_gb = max_ram_gb
        self.models = {}
        self.processing_queue = queue.PriorityQueue()
        self.current_processing = None
        self.stats = {
            "requests_processed": 0,
            "fast_mode_count": 0,
            "accurate_mode_count": 0,
            "average_processing_time": 0.0
        }

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Intelligent model selection
        self.enable_intelligent_selection = enable_intelligent_selection
        if enable_intelligent_selection:
            self.model_selector = IntelligentModelSelector()
            self.logger.info("🤖 Intelligent model selection ENABLED")
        else:
            self.model_selector = None
            self.logger.info("⚠️ Intelligent model selection DISABLED (using manual mode)")

        # Threading for queue processing
        self.processing_thread = None
        self.shutdown_event = threading.Event()

    def start(self):
        """Start the voice processing service"""
        self.logger.info("Starting Voice Engine Manager")
        self.processing_thread = threading.Thread(target=self._process_queue)
        self.processing_thread.daemon = True
        self.processing_thread.start()

    def stop(self):
        """Stop the voice processing service"""
        self.logger.info("Stopping Voice Engine Manager")
        self.shutdown_event.set()
        if self.processing_thread:
            self.processing_thread.join()

    def _load_model(self, mode: TranscriptionMode) -> bool:
        """Lazy load transcription models based on mode"""
        if mode == TranscriptionMode.FAST:
            if "faster_whisper_tiny" not in self.models:
                if not FASTER_WHISPER_AVAILABLE:
                    self.logger.error("faster-whisper not available")
                    return False

                self.logger.info("Loading faster-whisper tiny model")
                try:
                    self.models["faster_whisper_tiny"] = WhisperModel(
                        "tiny",
                        device="cpu",
                        compute_type="int8"
                    )
                    self.logger.info("faster-whisper tiny model loaded successfully")
                    return True
                except Exception as e:
                    self.logger.error(f"Failed to load faster-whisper tiny: {e}")
                    return False
            return True

        elif mode == TranscriptionMode.ACCURATE:
            if "whisper_large_v3" not in self.models:
                if not OPENAI_WHISPER_AVAILABLE:
                    self.logger.error("openai-whisper not available")
                    return False

                self.logger.info("Loading Whisper Large-v3 model")
                try:
                    self.models["whisper_large_v3"] = whisper.load_model(
                        "large-v3",
                        device="cpu"
                    )
                    self.logger.info("Whisper Large-v3 model loaded successfully")
                    return True
                except Exception as e:
                    self.logger.error(f"Failed to load Whisper Large-v3: {e}")
                    return False
            return True

        return False

    def _process_queue(self):
        """Background thread to process voice requests"""
        while not self.shutdown_event.is_set():
            try:
                # Get request with timeout
                priority, timestamp, request = self.processing_queue.get(timeout=1.0)

                self.current_processing = request
                self.logger.info(f"Processing {request.system} request: {request.audio_path}")

                # Route to appropriate processor
                if request.system == "squirt":
                    result = self._process_squirt_request(request)
                elif request.system == "sherlock":
                    result = self._process_sherlock_request(request)
                else:
                    self.logger.error(f"Unknown system: {request.system}")
                    continue

                # Execute callback if provided
                if request.callback:
                    request.callback(result)

                self.stats["requests_processed"] += 1
                self.current_processing = None

            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing request: {e}")
                self.current_processing = None

    def transcribe_squirt(self,
                         audio_path: str,
                         mode: TranscriptionMode = TranscriptionMode.FAST,
                         priority: ProcessingPriority = ProcessingPriority.IMMEDIATE,
                         callback: Optional[callable] = None) -> Optional[TranscriptionResult]:
        """
        Submit Squirt transcription request
        """
        request = VoiceProcessingRequest(
            audio_path=audio_path,
            mode=mode,
            priority=priority,
            system="squirt",
            callback=callback
        )

        # Priority: 0=immediate, 1=scheduled, 2=background
        priority_value = priority.value
        timestamp = time.time()

        self.processing_queue.put((priority_value, timestamp, request))
        self.logger.info(f"Queued Squirt transcription: {audio_path} (mode: {mode.value})")

        return None  # Async processing, result via callback

    def transcribe_sherlock(self,
                           audio_path: str,
                           quality_preference: QualityPreference = QualityPreference.BALANCED,
                           priority: ProcessingPriority = ProcessingPriority.SCHEDULED,
                           callback: Optional[callable] = None) -> Optional[TranscriptionResult]:
        """
        Submit Sherlock transcription request with intelligent model selection

        Args:
            audio_path: Path to audio file
            quality_preference: Desired quality level (MINIMUM, BALANCED, HIGH, MAXIMUM)
            priority: Processing priority
            callback: Optional callback for async processing

        Returns:
            None (async) or TranscriptionResult (if called synchronously)
        """

        # Use intelligent model selection if enabled
        if self.enable_intelligent_selection and self.model_selector:
            selection = self.model_selector.select_model(
                audio_path=audio_path,
                quality_preference=quality_preference
            )

            self.model_selector.log_selection(selection)

            # Validate selection is safe
            if not self.model_selector.validate_selection(selection):
                self.logger.error("❌ Selected model exceeds RAM constraints - aborting")
                return None

            # Map selection to TranscriptionMode
            if selection.engine == "faster-whisper":
                mode = TranscriptionMode.FAST
            elif selection.model_size == "large-v3":
                mode = TranscriptionMode.ACCURATE
            else:
                mode = TranscriptionMode.FAST

            self.logger.info(f"🤖 Intelligent selection: {selection.engine} {selection.model_size} -> {mode.value} mode")
        else:
            # Fallback to manual mode selection
            mode = TranscriptionMode.ACCURATE
            self.logger.warning("⚠️ Intelligent selection disabled - using ACCURATE mode (may cause OOM!)")

        request = VoiceProcessingRequest(
            audio_path=audio_path,
            mode=mode,
            priority=priority,
            system="sherlock",
            callback=callback
        )

        priority_value = {"immediate": 0, "scheduled": 1, "background": 2}[priority.value]
        timestamp = time.time()

        self.processing_queue.put((priority_value, timestamp, request))
        self.logger.info(f"Queued Sherlock transcription: {audio_path} (mode: {mode.value})")

        return None  # Async processing, result via callback

    def diarize_sherlock(self,
                        audio_path: str,
                        auto_anchors: bool = True,
                        manual_anchors: Optional[Dict[str, str]] = None,
                        priority: ProcessingPriority = ProcessingPriority.SCHEDULED,
                        callback: Optional[callable] = None) -> Optional[DiarizationResult]:
        """
        Submit Sherlock diarization request with auto-anchor detection
        """
        metadata = {
            "auto_anchors": auto_anchors,
            "manual_anchors": manual_anchors or {}
        }

        request = VoiceProcessingRequest(
            audio_path=audio_path,
            mode=TranscriptionMode.ACCURATE,  # Sherlock always uses accurate
            priority=priority,
            system="sherlock",
            metadata=metadata,
            callback=callback
        )

        priority_value = {"immediate": 0, "scheduled": 1, "background": 2}[priority.value]
        timestamp = time.time()

        self.processing_queue.put((priority_value, timestamp, request))
        self.logger.info(f"Queued Sherlock diarization: {audio_path} (auto_anchors: {auto_anchors})")

        return None  # Async processing, result via callback

    def _process_squirt_request(self, request: VoiceProcessingRequest) -> TranscriptionResult:
        """Process Squirt voice memo transcription"""
        start_time = time.time()

        # Load appropriate model
        if not self._load_model(request.mode):
            raise Exception(f"Failed to load model for mode: {request.mode}")

        # Ensure audio is in correct format
        processed_audio_path = self._ensure_wav_format(request.audio_path)

        # Transcribe based on mode
        if request.mode == TranscriptionMode.FAST:
            result = self._transcribe_fast(processed_audio_path)
        elif request.mode == TranscriptionMode.ACCURATE:
            result = self._transcribe_accurate(processed_audio_path)
        else:
            raise Exception(f"Unsupported mode: {request.mode}")

        processing_time = time.time() - start_time

        # Update stats
        if request.mode == TranscriptionMode.FAST:
            self.stats["fast_mode_count"] += 1
        else:
            self.stats["accurate_mode_count"] += 1

        return TranscriptionResult(
            text=result["text"],
            segments=result.get("segments", []),
            processing_time=processing_time,
            model_used=result["model"],
            confidence=result.get("confidence", 0.0),
            metadata={"mode": request.mode.value, "system": "squirt"}
        )

    def _process_sherlock_request(self, request: VoiceProcessingRequest) -> DiarizationResult:
        """Process Sherlock research content with diarization"""
        start_time = time.time()

        # Always use accurate mode for Sherlock
        if not self._load_model(TranscriptionMode.ACCURATE):
            raise Exception("Failed to load accurate model for Sherlock")

        metadata = request.metadata or {}
        auto_anchors = metadata.get("auto_anchors", True)
        manual_anchors = metadata.get("manual_anchors", {})

        # Step 1: Transcribe audio
        processed_audio_path = self._ensure_wav_format(request.audio_path)
        transcription = self._transcribe_accurate(processed_audio_path)

        # Step 2: Speaker diarization
        if auto_anchors and not manual_anchors:
            # Auto-anchor detection mode
            diarization = self._auto_anchor_diarization(request.audio_path, transcription)
        elif manual_anchors:
            # Manual anchor mode
            diarization = self._manual_anchor_diarization(request.audio_path, manual_anchors, transcription)
        else:
            # Fallback to unsupervised clustering
            diarization = self._unsupervised_diarization(request.audio_path, transcription)

        processing_time = time.time() - start_time

        return DiarizationResult(
            turns=diarization["turns"],
            speakers=diarization["speakers"],
            processing_time=processing_time,
            method=diarization["method"],
            confidence=diarization["confidence"],
            anchors_used=diarization.get("anchors_used"),
            auto_anchors=diarization.get("auto_anchors")
        )

    def _ensure_wav_format(self, audio_path: str) -> str:
        """Ensure audio is in WAV format at 16kHz mono for processing"""
        import tempfile
        import os

        path = Path(audio_path)

        # If already a WAV file, check if it needs conversion
        if path.suffix.lower() == '.wav':
            try:
                audio = AudioSegment.from_wav(audio_path)
                if audio.frame_rate == 16000 and audio.channels == 1:
                    return audio_path  # Already in correct format
            except:
                pass

        # Convert to proper format
        try:
            audio = AudioSegment.from_file(audio_path)
            audio = audio.set_frame_rate(16000).set_channels(1)

            # Create temp file or use standardized name
            temp_dir = Path(audio_path).parent / "temp_audio"
            temp_dir.mkdir(exist_ok=True)

            output_path = temp_dir / f"{path.stem}_16k_mono.wav"
            audio.export(str(output_path), format="wav")

            self.logger.info(f"Converted {audio_path} to {output_path}")
            return str(output_path)

        except Exception as e:
            self.logger.error(f"Audio conversion failed for {audio_path}: {e}")
            raise Exception(f"Could not convert audio file: {e}")

    def _preprocess_audio(self, audio_path: str) -> np.ndarray:
        """Convert audio to numpy array for legacy processing"""
        # Convert to 16kHz mono WAV
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_frame_rate(16000).set_channels(1)

        # Convert to numpy array
        audio_data = np.array(audio.get_array_of_samples(), dtype=np.float32)
        audio_data = audio_data / 32768.0  # Normalize to [-1, 1]

        return audio_data

    def _transcribe_fast(self, audio_path: str) -> Dict:
        """Fast transcription using faster-whisper tiny"""
        model = self.models["faster_whisper_tiny"]

        try:
            segments, info = model.transcribe(audio_path, beam_size=1)
            segments_list = list(segments)  # Convert generator to list

            text = " ".join([segment.text for segment in segments_list])

            return {
                "text": text.strip(),
                "segments": [{"start": s.start, "end": s.end, "text": s.text} for s in segments_list],
                "model": "faster-whisper-tiny",
                "confidence": float(info.language_probability),
                "language": info.language,
                "duration": info.duration
            }
        except Exception as e:
            self.logger.error(f"Fast transcription failed: {e}")
            return {
                "text": "",
                "segments": [],
                "model": "faster-whisper-tiny",
                "confidence": 0.0,
                "error": str(e)
            }

    def _transcribe_accurate(self, audio_path: str) -> Dict:
        """Accurate transcription using Whisper Large-v3"""
        model = self.models["whisper_large_v3"]

        try:
            result = model.transcribe(audio_path)

            # Calculate average confidence from segments
            segments = result.get("segments", [])
            avg_confidence = 0.95  # Default high confidence for large model
            if segments:
                confidences = [seg.get("no_speech_prob", 0.0) for seg in segments]
                avg_confidence = 1.0 - (sum(confidences) / len(confidences))

            return {
                "text": result["text"].strip(),
                "segments": [{"start": s["start"], "end": s["end"], "text": s["text"]} for s in segments],
                "model": "whisper-large-v3",
                "confidence": avg_confidence,
                "language": result.get("language", "unknown")
            }
        except Exception as e:
            self.logger.error(f"Accurate transcription failed: {e}")
            return {
                "text": "",
                "segments": [],
                "model": "whisper-large-v3",
                "confidence": 0.0,
                "error": str(e)
            }

    def _auto_anchor_diarization(self, audio_path: str, transcription: Dict) -> Dict:
        """Automatic anchor detection and diarization"""
        # Placeholder for auto-anchor detection
        # This will be implemented in Phase 3
        return {
            "turns": [],
            "speakers": ["AUTO_SPEAKER_1", "AUTO_SPEAKER_2"],
            "method": "auto_anchor_detection",
            "confidence": 0.0,
            "auto_anchors": {}
        }

    def _manual_anchor_diarization(self, audio_path: str, anchors: Dict, transcription: Dict) -> Dict:
        """Manual anchor-based diarization"""
        # Placeholder for manual anchor processing
        # This will leverage existing Sherlock supervised diarization
        return {
            "turns": [],
            "speakers": list(anchors.keys()),
            "method": "manual_anchors",
            "confidence": 0.0,
            "anchors_used": list(anchors.keys())
        }

    def _unsupervised_diarization(self, audio_path: str, transcription: Dict) -> Dict:
        """Fallback unsupervised clustering"""
        # Placeholder for unsupervised clustering
        # This will leverage existing Sherlock clustering methods
        return {
            "turns": [],
            "speakers": ["SPEAKER_1", "SPEAKER_2"],
            "method": "unsupervised_clustering",
            "confidence": 0.0
        }

    def get_status(self) -> Dict:
        """Get current system status"""
        return {
            "queue_size": self.processing_queue.qsize(),
            "current_processing": asdict(self.current_processing) if self.current_processing else None,
            "models_loaded": list(self.models.keys()),
            "stats": self.stats,
            "available_engines": {
                "faster_whisper": FASTER_WHISPER_AVAILABLE,
                "openai_whisper": OPENAI_WHISPER_AVAILABLE,
                "resemblyzer": RESEMBLYZER_AVAILABLE
            }
        }


# Global engine instance
voice_engine = VoiceEngineManager()


def main():
    """Test the voice engine manager"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python voice_engine.py <audio_file>")
        sys.exit(1)

    audio_file = sys.argv[1]

    # Test callback
    def on_result(result):
        print(f"Result: {result}")

    # Start engine
    voice_engine.start()

    try:
        # Test Squirt fast mode
        print("Testing Squirt fast transcription...")
        voice_engine.transcribe_squirt(
            audio_file,
            mode=TranscriptionMode.FAST,
            callback=on_result
        )

        # Wait a bit
        time.sleep(2)

        # Check status
        status = voice_engine.get_status()
        print(f"Status: {json.dumps(status, indent=2)}")

        # Keep running for a bit
        time.sleep(10)

    finally:
        voice_engine.stop()


if __name__ == "__main__":
    main()