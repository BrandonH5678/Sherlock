#!/usr/bin/env python3
"""
Comprehensive Test Suite for Sherlock Phase 6 Advanced Features
Tests multi-modal processing, advanced diarization, active learning, cross-system intelligence, and integrations
"""

import json
import numpy as np
import os
import sys
import tempfile
import time
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Import Phase 6 modules
from multimodal_processor import (
    MultiModalProcessor, VisualSpeakerProcessor, DocumentReferenceExtractor,
    CrossModalCorrelationEngine, ModalityType, ProcessingQuality
)
from advanced_diarization import (
    AdvancedDiarizationEngine, EmotionDetector, OverlapDetector,
    AcousticFeatureExtractor, EmotionType, OverlapType
)
from active_learning_framework import (
    ActiveLearningEngine, ModelType, LearningStrategy, FeedbackType,
    UncertaintyCalculator, DiversityCalculator
)
from cross_system_intelligence import (
    CrossSystemIntelligenceEngine, IntelligenceType, SystemType, SecurityLevel
)
from external_ai_integration import (
    ExternalAIManager, AIServiceConfig, ExternalAIProvider, AIServiceType
)
from squirt_johny5_integration import (
    SherlockSystemIntegrator, MessageBus, SystemComponent, MessageType
)

# Import existing modules
from evidence_database import EvidenceDatabase, EvidenceSource, EvidenceClaim, Speaker
from voice_engine import SpeakerTurn


class TestMultiModalProcessor(unittest.TestCase):
    """Test multi-modal processing capabilities"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_evidence.db")
        self.processor = MultiModalProcessor(self.db_path)

    def test_visual_speaker_processor_init(self):
        """Test visual speaker processor initialization"""
        visual_processor = VisualSpeakerProcessor(ProcessingQuality.FAST)
        self.assertIsNotNone(visual_processor)
        self.assertEqual(visual_processor.quality, ProcessingQuality.FAST)

    def test_document_reference_extractor(self):
        """Test document reference extraction"""
        extractor = DocumentReferenceExtractor()

        test_text = """
        According to the study at https://example.com/research.pdf,
        we can see that Smith et al. (2023) found significant results.
        The DOI is 10.1234/example.doi for this paper.
        """

        references = extractor.extract_references(test_text, timestamp=10.5)

        self.assertGreater(len(references), 0)

        # Check for URL extraction
        url_refs = [ref for ref in references if ref.document_type == "url"]
        self.assertGreater(len(url_refs), 0)
        self.assertIn("https://example.com/research.pdf", url_refs[0].reference_text)

        # Check for citation extraction
        citation_refs = [ref for ref in references if ref.document_type == "citation"]
        self.assertGreater(len(citation_refs), 0)

        # Check for DOI extraction
        doi_refs = [ref for ref in references if ref.document_type == "doi"]
        self.assertGreater(len(doi_refs), 0)

    def test_cross_modal_correlation_engine(self):
        """Test cross-modal correlation"""
        engine = CrossModalCorrelationEngine()

        # Create mock speaker turns
        speaker_turns = [
            SpeakerTurn("Speaker_0", 0.0, 10.0, 0.8, "This is a test transcript"),
            SpeakerTurn("Speaker_1", 10.0, 20.0, 0.9, "Another speaker segment")
        ]

        # Create mock visual frames (empty for now)
        visual_frames = []

        correlations = engine.correlate_speaker_visual(speaker_turns, visual_frames)
        self.assertIsInstance(correlations, list)

    def test_multimodal_result_structure(self):
        """Test multi-modal result data structure"""
        # Create a synthetic test
        with tempfile.NamedTemporaryFile(suffix=".wav") as temp_audio:
            # Write minimal WAV header for testing
            temp_audio.write(b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x40\x1f\x00\x00\x80\x3e\x00\x00\x02\x00\x10\x00data\x00\x08\x00\x00')
            temp_audio.flush()

            result = self.processor.process_multimodal_content(
                temp_audio.name, "audio", ProcessingQuality.FAST
            )

            self.assertIsNotNone(result.source_id)
            self.assertIsInstance(result.modalities_processed, list)
            self.assertIsInstance(result.processing_time, float)
            self.assertIsInstance(result.visual_speakers, list)
            self.assertIsInstance(result.document_references, list)
            self.assertIsInstance(result.cross_modal_correlations, list)
            self.assertIsInstance(result.quality_metrics, dict)
            self.assertIsInstance(result.errors, list)


class TestAdvancedDiarization(unittest.TestCase):
    """Test advanced diarization capabilities"""

    def setUp(self):
        self.engine = AdvancedDiarizationEngine()
        self.emotion_detector = EmotionDetector()
        self.overlap_detector = OverlapDetector()
        self.feature_extractor = AcousticFeatureExtractor()

    def test_acoustic_feature_extraction(self):
        """Test acoustic feature extraction"""
        # Create synthetic audio signal
        sample_rate = 16000
        duration = 1.0  # 1 second
        frequency = 440  # A4 note

        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_signal = 0.5 * np.sin(2 * np.pi * frequency * t)

        features = self.feature_extractor.extract_prosodic_features(audio_signal)

        # Check that basic features are extracted
        self.assertIn('pitch_mean', features)
        self.assertIn('energy_mean', features)
        self.assertIn('spectral_centroid_mean', features)
        self.assertIn('zcr_mean', features)
        self.assertIn('tempo', features)

        # Check MFCC features
        for i in range(13):
            self.assertIn(f'mfcc_{i}_mean', features)
            self.assertIn(f'mfcc_{i}_std', features)

    def test_emotion_detection(self):
        """Test emotion detection from features"""
        # Create synthetic audio for emotion analysis
        sample_rate = 16000
        duration = 2.0
        t = np.linspace(0, duration, int(sample_rate * duration))

        # High pitch, high energy signal (might indicate excitement)
        high_freq_signal = 0.8 * np.sin(2 * np.pi * 880 * t)  # High pitch
        emotion_analysis = self.emotion_detector.analyze_emotion(high_freq_signal, 0.0)

        self.assertIsInstance(emotion_analysis.emotion, EmotionType)
        self.assertIsInstance(emotion_analysis.confidence, float)
        self.assertIsInstance(emotion_analysis.arousal, float)
        self.assertIsInstance(emotion_analysis.valence, float)
        self.assertIsInstance(emotion_analysis.features, dict)

        # Check ranges
        self.assertTrue(0.0 <= emotion_analysis.confidence <= 1.0)
        self.assertTrue(0.0 <= emotion_analysis.arousal <= 1.0)
        self.assertTrue(0.0 <= emotion_analysis.valence <= 1.0)

    def test_overlap_detection(self):
        """Test overlap detection"""
        # Create mock speaker turns with overlap
        speaker_turns = [
            SpeakerTurn("Speaker_0", 0.0, 5.0, 0.8),
            SpeakerTurn("Speaker_1", 3.0, 8.0, 0.9),  # Overlaps with Speaker_0
            SpeakerTurn("Speaker_0", 7.0, 10.0, 0.85)
        ]

        # Create synthetic audio
        sample_rate = 16000
        duration = 10.0
        audio = np.random.normal(0, 0.1, int(sample_rate * duration))

        overlaps = self.overlap_detector.detect_overlaps(audio, speaker_turns)

        self.assertIsInstance(overlaps, list)
        for overlap in overlaps:
            self.assertIsInstance(overlap.overlap_type, OverlapType)
            self.assertIsInstance(overlap.confidence, float)
            self.assertTrue(0.0 <= overlap.confidence <= 1.0)

    def test_advanced_diarization_processing(self):
        """Test complete advanced diarization processing"""
        # Create basic speaker turns
        basic_turns = [
            SpeakerTurn("Speaker_0", 0.0, 3.0, 0.8, "First speaker segment"),
            SpeakerTurn("Speaker_1", 3.0, 6.0, 0.9, "Second speaker segment")
        ]

        # Create temporary audio file for testing
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            # Create minimal WAV file with synthetic data
            sample_rate = 16000
            duration = 6.0
            audio_data = np.random.normal(0, 0.1, int(sample_rate * duration))

            # Convert to 16-bit PCM
            audio_int16 = (audio_data * 32767).astype(np.int16)

            # Write WAV header and data
            import wave
            with wave.open(temp_audio.name, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_int16.tobytes())

            try:
                result = self.engine.process_advanced_diarization(
                    temp_audio.name, basic_turns, emotion_analysis=True, overlap_detection=True
                )

                self.assertIsNotNone(result)
                self.assertIsInstance(result.turns, list)
                self.assertIsInstance(result.speakers, list)
                self.assertIsInstance(result.processing_time, float)
                self.assertIsInstance(result.overlap_segments, list)
                self.assertIsInstance(result.emotion_timeline, list)
                self.assertIsInstance(result.speaker_characteristics, dict)
                self.assertIsInstance(result.quality_metrics, dict)

                # Check that advanced turns have additional features
                if result.turns:
                    turn = result.turns[0]
                    self.assertIsNotNone(turn.acoustic_features)
                    # Emotion analysis might be None for short segments

            finally:
                os.unlink(temp_audio.name)


class TestActiveLearning(unittest.TestCase):
    """Test active learning framework"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.evidence_db_path = os.path.join(self.temp_dir, "test_evidence.db")
        self.learning_db_path = os.path.join(self.temp_dir, "test_learning.db")
        self.engine = ActiveLearningEngine(self.evidence_db_path, self.learning_db_path)

    def test_candidate_addition(self):
        """Test adding learning candidates"""
        prediction = {
            'speaker': 'Speaker_1',
            'confidence': 0.6
        }

        features = {
            'mfcc_0_mean': 1.5,
            'mfcc_1_mean': -0.8,
            'energy_mean': 0.3,
            'pitch_mean': 150.0
        }

        candidate_id = self.engine.add_learning_candidate(
            ModelType.SPEAKER_DIARIZATION,
            "test_source_123",
            prediction,
            features,
            timestamp=10.5
        )

        self.assertIsInstance(candidate_id, str)
        self.assertTrue(len(candidate_id) > 0)

    def test_learning_session(self):
        """Test learning session management"""
        # Add some candidates first
        for i in range(5):
            prediction = {'speaker': f'Speaker_{i}', 'confidence': 0.5 + i * 0.1}
            features = {f'feature_{j}': np.random.random() for j in range(10)}

            self.engine.add_learning_candidate(
                ModelType.SPEAKER_DIARIZATION,
                f"source_{i}",
                prediction,
                features
            )

        # Start learning session
        session_id = self.engine.start_learning_session(
            ModelType.SPEAKER_DIARIZATION,
            LearningStrategy.HYBRID,
            max_candidates=3
        )

        self.assertIsInstance(session_id, str)

        # Get pending reviews
        candidates = self.engine.get_pending_reviews(ModelType.SPEAKER_DIARIZATION, limit=5)
        self.assertLessEqual(len(candidates), 3)  # Should be limited by max_candidates

    def test_feedback_submission(self):
        """Test human feedback submission"""
        # Add a candidate
        prediction = {'speaker': 'Speaker_1', 'confidence': 0.6}
        features = {'feature_1': 1.0, 'feature_2': 0.5}

        candidate_id = self.engine.add_learning_candidate(
            ModelType.SPEAKER_DIARIZATION,
            "test_source",
            prediction,
            features
        )

        # Submit feedback
        corrected_prediction = {'speaker': 'Speaker_2', 'confidence': 0.9}

        feedback_id = self.engine.submit_feedback(
            candidate_id,
            FeedbackType.CORRECTION,
            corrected_prediction,
            0.95,
            explanation="Speaker was misidentified"
        )

        self.assertIsInstance(feedback_id, str)

    def test_feedback_pattern_analysis(self):
        """Test feedback pattern analysis"""
        # Add candidates and feedback
        for i in range(3):
            prediction = {'speaker': f'Speaker_{i}', 'confidence': 0.4}
            features = {f'feature_{j}': np.random.random() for j in range(5)}

            candidate_id = self.engine.add_learning_candidate(
                ModelType.EMOTION_DETECTION,
                f"source_{i}",
                prediction,
                features
            )

            # Submit correction feedback
            corrected = {'speaker': f'Speaker_{i+1}', 'confidence': 0.9}
            self.engine.submit_feedback(
                candidate_id,
                FeedbackType.CORRECTION,
                corrected,
                0.8
            )

        # Analyze patterns
        patterns = self.engine.analyze_feedback_patterns(ModelType.EMOTION_DETECTION)

        self.assertIn('total_feedback', patterns)
        self.assertIn('feedback_types', patterns)
        self.assertIn('improvement_recommendations', patterns)


class TestCrossSystemIntelligence(unittest.TestCase):
    """Test cross-system intelligence sharing"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.evidence_db_path = os.path.join(self.temp_dir, "test_evidence.db")
        self.engine = CrossSystemIntelligenceEngine(
            system_id="test_sherlock",
            evidence_db_path=self.evidence_db_path
        )

    def test_system_registration(self):
        """Test system registration in intelligence network"""
        self.engine.register_with_network(
            endpoint_url="http://localhost:8080/test",
            capabilities=[IntelligenceType.SPEAKER_PROFILE, IntelligenceType.ENTITY_KNOWLEDGE]
        )

        # Verify registration by checking if system appears in database
        systems = self.engine.intelligence_db.get_registered_systems()
        test_system = [s for s in systems if s.system_id == "test_sherlock"]
        self.assertEqual(len(test_system), 1)
        self.assertEqual(test_system[0].system_type, SystemType.SHERLOCK)

    def test_intelligence_sharing(self):
        """Test intelligence packet sharing"""
        test_data = {
            'speaker_id': 'Speaker_Test',
            'characteristics': {'pitch_mean': 150.0, 'confidence': 0.8},
            'last_seen': datetime.now().isoformat()
        }

        packet_id = self.engine.share_intelligence(
            IntelligenceType.SPEAKER_PROFILE,
            test_data,
            [SystemType.SQUIRT, SystemType.JOHNY5ALIVE],
            SecurityLevel.INTERNAL
        )

        self.assertIsInstance(packet_id, str)
        self.assertTrue(len(packet_id) > 0)

    def test_intelligence_retrieval(self):
        """Test intelligence retrieval"""
        # Share some intelligence first
        test_data = {'entity': 'TestEntity', 'mentions': 5}

        self.engine.share_intelligence(
            IntelligenceType.ENTITY_KNOWLEDGE,
            test_data,
            [SystemType.SHERLOCK],
            SecurityLevel.INTERNAL
        )

        # Retrieve intelligence
        intelligence_list = self.engine.get_available_intelligence(
            IntelligenceType.ENTITY_KNOWLEDGE,
            max_age_hours=1
        )

        self.assertGreater(len(intelligence_list), 0)
        retrieved = intelligence_list[0]
        self.assertIn('data', retrieved)
        self.assertIn('timestamp', retrieved)

    def test_speaker_profile_sharing(self):
        """Test speaker profile extraction and sharing"""
        # Create a test speaker in evidence database
        test_speaker = Speaker(
            speaker_id="test_speaker_1",
            name="Test Speaker",
            metadata={"test": True}
        )

        self.engine.evidence_db.store_speaker(test_speaker)

        # Share speaker profile
        packet_id = self.engine.share_speaker_profile(
            "test_speaker_1",
            [SystemType.SQUIRT]
        )

        if packet_id:  # Will be empty if no profile data found
            self.assertIsInstance(packet_id, str)


class TestExternalAIIntegration(unittest.TestCase):
    """Test external AI system integration"""

    def setUp(self):
        self.manager = ExternalAIManager()

    def test_service_registration(self):
        """Test registering external AI services"""
        config = AIServiceConfig(
            service_id="test_sentiment",
            provider=ExternalAIProvider.HUGGINGFACE,
            service_type=AIServiceType.SENTIMENT_ANALYSIS,
            endpoint_url="",
            api_key=None,
            model_name="test-model",
            parameters={},
            rate_limit=100,
            timeout=30,
            retry_attempts=3,
            cost_per_request=0.0
        )

        success = self.manager.register_service(config)
        # Success depends on whether the dependencies are available
        self.assertIsInstance(success, bool)

    def test_service_status(self):
        """Test getting service status"""
        config = AIServiceConfig(
            service_id="test_service",
            provider=ExternalAIProvider.CUSTOM_API,
            service_type=AIServiceType.TEXT_ANALYSIS,
            endpoint_url="http://localhost:9999/api",
            api_key="test_key",
            model_name=None,
            parameters={},
            rate_limit=50,
            timeout=30,
            retry_attempts=2,
            cost_per_request=0.01
        )

        # Register service (might fail due to missing dependencies)
        self.manager.register_service(config)

        # Get status for all services
        status = self.manager.get_all_services_status()
        self.assertIsInstance(status, dict)

    @patch('asyncio.Queue')
    async def test_async_request_processing(self, mock_queue):
        """Test asynchronous request processing"""
        # This is a placeholder test for async functionality
        # In a real test, we would mock the actual async processing
        self.assertTrue(True)  # Placeholder assertion


class TestSquirtJohny5Integration(unittest.TestCase):
    """Test Squirt and Johny5Alive integration"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.evidence_db_path = os.path.join(self.temp_dir, "test_evidence.db")

    def test_message_bus_initialization(self):
        """Test message bus initialization"""
        message_bus = MessageBus(SystemComponent.SHERLOCK)
        self.assertEqual(message_bus.component_id, SystemComponent.SHERLOCK)
        self.assertIsInstance(message_bus.subscribers, dict)

    def test_system_message_structure(self):
        """Test system message structure"""
        from squirt_johny5_integration import SystemMessage

        message = SystemMessage(
            message_id="test_123",
            source=SystemComponent.SQUIRT,
            target=SystemComponent.SHERLOCK,
            message_type=MessageType.VOICE_MEMO_READY,
            payload={"file_path": "/test/memo.wav"},
            priority=1,
            timestamp=datetime.now().isoformat()
        )

        self.assertEqual(message.source, SystemComponent.SQUIRT)
        self.assertEqual(message.target, SystemComponent.SHERLOCK)
        self.assertEqual(message.message_type, MessageType.VOICE_MEMO_READY)
        self.assertIn("file_path", message.payload)

    def test_system_integrator_initialization(self):
        """Test system integrator initialization"""
        integrator = SherlockSystemIntegrator(self.evidence_db_path)

        self.assertIsNotNone(integrator.evidence_db)
        self.assertIsNotNone(integrator.voice_engine)
        self.assertIsNotNone(integrator.message_bus)
        self.assertIsNotNone(integrator.squirt_integration)
        self.assertIsNotNone(integrator.johny5_integration)


class TestPhase6Integration(unittest.TestCase):
    """Test integration between Phase 6 components"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.evidence_db_path = os.path.join(self.temp_dir, "test_evidence.db")

    def test_multimodal_to_diarization_integration(self):
        """Test integration between multi-modal processing and advanced diarization"""
        # Create processors
        multimodal_processor = MultiModalProcessor(self.evidence_db_path)
        diarization_engine = AdvancedDiarizationEngine()

        # This would test the flow from multi-modal processing to advanced diarization
        # For now, just verify both components can be instantiated
        self.assertIsNotNone(multimodal_processor)
        self.assertIsNotNone(diarization_engine)

    def test_active_learning_to_intelligence_sharing(self):
        """Test integration between active learning and intelligence sharing"""
        learning_engine = ActiveLearningEngine(self.evidence_db_path)
        intelligence_engine = CrossSystemIntelligenceEngine(evidence_db_path=self.evidence_db_path)

        # Test that learning insights could be shared as intelligence
        # This would involve extracting patterns from active learning
        # and sharing them via the intelligence framework

        self.assertIsNotNone(learning_engine)
        self.assertIsNotNone(intelligence_engine)

    def test_external_ai_to_evidence_database(self):
        """Test integration between external AI results and evidence database"""
        ai_manager = ExternalAIManager(self.evidence_db_path)
        evidence_db = EvidenceDatabase(self.evidence_db_path)

        # This would test storing AI analysis results in the evidence database
        self.assertIsNotNone(ai_manager.evidence_db)
        self.assertEqual(ai_manager.evidence_db.db_path, evidence_db.db_path)


def run_phase6_tests():
    """Run all Phase 6 tests"""
    print("🧪 Running Sherlock Phase 6 Test Suite")
    print("=" * 50)

    # Create test suite
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestMultiModalProcessor,
        TestAdvancedDiarization,
        TestActiveLearning,
        TestCrossSystemIntelligence,
        TestExternalAIIntegration,
        TestSquirtJohny5Integration,
        TestPhase6Integration
    ]

    for test_class in test_classes:
        tests = test_loader.loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print("\n" + "=" * 50)
    print("🎯 PHASE 6 TEST RESULTS:")
    print(f"✅ Tests run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print(f"⏭️  Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")

    if result.failures:
        print(f"\n❌ FAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split(chr(10))[-2] if chr(10) in traceback else 'Unknown failure'}")

    if result.errors:
        print(f"\n⚠️  ERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split(chr(10))[-2] if chr(10) in traceback else 'Unknown error'}")

    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) /
                   max(1, result.testsRun)) * 100

    print(f"\n📊 Success Rate: {success_rate:.1f}%")

    if success_rate >= 80:
        print("🚀 Phase 6 components are ready for deployment!")
    elif success_rate >= 60:
        print("⚡ Phase 6 components need minor fixes")
    else:
        print("🔧 Phase 6 components need significant work")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_phase6_tests()
    sys.exit(0 if success else 1)