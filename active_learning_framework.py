#!/usr/bin/env python3
"""
Active Learning Framework for Sherlock Phase 6
Enables continuous model improvement through intelligent sample selection and cross-system learning
"""

import json
import numpy as np
import os
import sqlite3
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import logging
from abc import ABC, abstractmethod

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from evidence_database import EvidenceDatabase
from audit_system import AuditSystem

# Optional imports for ML components
try:
    import numpy as np
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import torch
    import torch.nn as nn
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False


class LearningStrategy(Enum):
    """Active learning strategies for sample selection"""
    UNCERTAINTY_SAMPLING = "uncertainty_sampling"
    DIVERSITY_SAMPLING = "diversity_sampling"
    QUERY_BY_COMMITTEE = "query_by_committee"
    EXPECTED_MODEL_CHANGE = "expected_model_change"
    DENSITY_WEIGHTED = "density_weighted"
    HYBRID = "hybrid"


class FeedbackType(Enum):
    """Types of feedback for learning"""
    CORRECTION = "correction"         # Correcting wrong predictions
    CONFIRMATION = "confirmation"     # Confirming correct predictions
    ANNOTATION = "annotation"         # Adding new labels/information
    VALIDATION = "validation"         # Validating uncertain predictions
    IMPROVEMENT = "improvement"       # General improvement suggestions


class ModelType(Enum):
    """Types of models that can be improved"""
    SPEAKER_DIARIZATION = "speaker_diarization"
    EMOTION_DETECTION = "emotion_detection"
    OVERLAP_DETECTION = "overlap_detection"
    DOCUMENT_EXTRACTION = "document_extraction"
    VISUAL_SPEAKER_ID = "visual_speaker_id"
    CONTRADICTION_DETECTION = "contradiction_detection"
    PROPAGANDA_DETECTION = "propaganda_detection"


@dataclass
class LearningCandidate:
    """A candidate sample for active learning"""
    candidate_id: str
    model_type: ModelType
    source_id: str
    timestamp: Optional[float]
    features: Dict
    current_prediction: Dict
    uncertainty_score: float
    diversity_score: float
    importance_score: float
    metadata: Dict
    created_at: str


@dataclass
class HumanFeedback:
    """Human feedback on model predictions"""
    feedback_id: str
    candidate_id: str
    feedback_type: FeedbackType
    original_prediction: Dict
    corrected_prediction: Dict
    confidence: float
    explanation: Optional[str]
    reviewer_id: str
    timestamp: str
    metadata: Dict = None


@dataclass
class ModelUpdateRecord:
    """Record of a model update from active learning"""
    update_id: str
    model_type: ModelType
    update_type: str  # "retrain", "fine_tune", "parameter_adjust"
    samples_used: int
    performance_before: Dict
    performance_after: Dict
    timestamp: str
    metadata: Dict


@dataclass
class LearningSession:
    """A session of active learning"""
    session_id: str
    model_type: ModelType
    strategy: LearningStrategy
    candidates_selected: int
    feedback_received: int
    improvements_made: List[str]
    start_time: str
    end_time: Optional[str]
    metadata: Dict = None


class UncertaintyCalculator(ABC):
    """Abstract base class for uncertainty calculation"""

    @abstractmethod
    def calculate_uncertainty(self, prediction: Dict, features: Dict) -> float:
        """Calculate uncertainty score for a prediction"""
        pass


class DiversityCalculator(ABC):
    """Abstract base class for diversity calculation"""

    @abstractmethod
    def calculate_diversity(self, candidate_features: Dict, existing_samples: List[Dict]) -> float:
        """Calculate diversity score for a candidate relative to existing samples"""
        pass


class BasicUncertaintyCalculator(UncertaintyCalculator):
    """Basic uncertainty calculation based on prediction confidence"""

    def calculate_uncertainty(self, prediction: Dict, features: Dict) -> float:
        """Calculate uncertainty based on prediction confidence"""
        confidence = prediction.get('confidence', 0.5)

        # Higher uncertainty for predictions closer to 0.5 confidence
        if isinstance(confidence, (list, tuple)):
            # For multi-class predictions, use entropy
            probs = np.array(confidence)
            probs = probs / np.sum(probs)  # Normalize
            entropy = -np.sum(probs * np.log(probs + 1e-10))
            uncertainty = entropy / np.log(len(probs))  # Normalize by max entropy
        else:
            # For binary predictions, distance from 0.5
            uncertainty = 1.0 - abs(confidence - 0.5) * 2

        return max(0.0, min(1.0, uncertainty))


class BasicDiversityCalculator(DiversityCalculator):
    """Basic diversity calculation using feature distance"""

    def __init__(self):
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None

    def calculate_diversity(self, candidate_features: Dict, existing_samples: List[Dict]) -> float:
        """Calculate diversity based on feature distance from existing samples"""
        if not existing_samples or not SKLEARN_AVAILABLE:
            return 1.0  # Maximum diversity if no existing samples

        try:
            # Convert features to vectors
            candidate_vector = self._features_to_vector(candidate_features)
            existing_vectors = [self._features_to_vector(sample) for sample in existing_samples]

            if not existing_vectors or len(candidate_vector) == 0:
                return 1.0

            # Calculate minimum distance to existing samples
            min_distance = float('inf')
            for existing_vector in existing_vectors:
                if len(existing_vector) == len(candidate_vector):
                    distance = np.linalg.norm(np.array(candidate_vector) - np.array(existing_vector))
                    min_distance = min(min_distance, distance)

            # Normalize distance to [0, 1] range
            if min_distance == float('inf'):
                return 1.0

            # Simple normalization (could be improved with domain knowledge)
            max_possible_distance = np.sqrt(len(candidate_vector))
            diversity = min(1.0, min_distance / max_possible_distance)

            return diversity

        except Exception as e:
            logging.warning(f"Diversity calculation error: {e}")
            return 0.5  # Default diversity

    def _features_to_vector(self, features: Dict) -> List[float]:
        """Convert feature dictionary to vector"""
        vector = []
        for key in sorted(features.keys()):
            value = features[key]
            if isinstance(value, (int, float)):
                vector.append(float(value))
            elif isinstance(value, bool):
                vector.append(1.0 if value else 0.0)
        return vector


class ActiveLearningDatabase:
    """Database for storing active learning data"""

    def __init__(self, db_path: str = "active_learning.db"):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self._init_database()

    def _init_database(self):
        """Initialize database tables"""
        cursor = self.connection.cursor()

        # Learning candidates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_candidates (
                candidate_id TEXT PRIMARY KEY,
                model_type TEXT NOT NULL,
                source_id TEXT NOT NULL,
                timestamp REAL,
                features TEXT,  -- JSON
                current_prediction TEXT,  -- JSON
                uncertainty_score REAL,
                diversity_score REAL,
                importance_score REAL,
                metadata TEXT,  -- JSON
                created_at TEXT,
                selected_for_review BOOLEAN DEFAULT FALSE,
                review_completed BOOLEAN DEFAULT FALSE
            )
        """)

        # Human feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS human_feedback (
                feedback_id TEXT PRIMARY KEY,
                candidate_id TEXT,
                feedback_type TEXT,
                original_prediction TEXT,  -- JSON
                corrected_prediction TEXT,  -- JSON
                confidence REAL,
                explanation TEXT,
                reviewer_id TEXT,
                timestamp TEXT,
                metadata TEXT,  -- JSON
                FOREIGN KEY (candidate_id) REFERENCES learning_candidates (candidate_id)
            )
        """)

        # Model updates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_updates (
                update_id TEXT PRIMARY KEY,
                model_type TEXT,
                update_type TEXT,
                samples_used INTEGER,
                performance_before TEXT,  -- JSON
                performance_after TEXT,  -- JSON
                timestamp TEXT,
                metadata TEXT  -- JSON
            )
        """)

        # Learning sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_sessions (
                session_id TEXT PRIMARY KEY,
                model_type TEXT,
                strategy TEXT,
                candidates_selected INTEGER,
                feedback_received INTEGER,
                improvements_made TEXT,  -- JSON
                start_time TEXT,
                end_time TEXT,
                metadata TEXT  -- JSON
            )
        """)

        self.connection.commit()

    def store_candidate(self, candidate: LearningCandidate):
        """Store a learning candidate"""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO learning_candidates
            (candidate_id, model_type, source_id, timestamp, features, current_prediction,
             uncertainty_score, diversity_score, importance_score, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            candidate.candidate_id,
            candidate.model_type.value,
            candidate.source_id,
            candidate.timestamp,
            json.dumps(candidate.features),
            json.dumps(candidate.current_prediction),
            candidate.uncertainty_score,
            candidate.diversity_score,
            candidate.importance_score,
            json.dumps(candidate.metadata),
            candidate.created_at
        ))
        self.connection.commit()

    def store_feedback(self, feedback: HumanFeedback):
        """Store human feedback"""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO human_feedback
            (feedback_id, candidate_id, feedback_type, original_prediction, corrected_prediction,
             confidence, explanation, reviewer_id, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            feedback.feedback_id,
            feedback.candidate_id,
            feedback.feedback_type.value,
            json.dumps(feedback.original_prediction),
            json.dumps(feedback.corrected_prediction),
            feedback.confidence,
            feedback.explanation,
            feedback.reviewer_id,
            feedback.timestamp,
            json.dumps(feedback.metadata or {})
        ))
        self.connection.commit()

    def get_candidates_for_review(self, model_type: ModelType, limit: int = 10) -> List[LearningCandidate]:
        """Get top candidates for human review"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM learning_candidates
            WHERE model_type = ? AND selected_for_review = FALSE
            ORDER BY importance_score DESC, uncertainty_score DESC
            LIMIT ?
        """, (model_type.value, limit))

        candidates = []
        for row in cursor.fetchall():
            candidates.append(self._row_to_candidate(row))

        return candidates

    def _row_to_candidate(self, row: Tuple) -> LearningCandidate:
        """Convert database row to LearningCandidate"""
        return LearningCandidate(
            candidate_id=row[0],
            model_type=ModelType(row[1]),
            source_id=row[2],
            timestamp=row[3],
            features=json.loads(row[4]),
            current_prediction=json.loads(row[5]),
            uncertainty_score=row[6],
            diversity_score=row[7],
            importance_score=row[8],
            metadata=json.loads(row[9]),
            created_at=row[10]
        )


class ActiveLearningEngine:
    """Main active learning engine"""

    def __init__(self, evidence_db_path: str = "evidence.db",
                 learning_db_path: str = "active_learning.db"):
        self.evidence_db = EvidenceDatabase(evidence_db_path)
        self.learning_db = ActiveLearningDatabase(learning_db_path)
        self.audit_system = AuditSystem()

        self.uncertainty_calculator = BasicUncertaintyCalculator()
        self.diversity_calculator = BasicDiversityCalculator()

        # Strategy weights for hybrid approach
        self.strategy_weights = {
            'uncertainty': 0.4,
            'diversity': 0.3,
            'importance': 0.3
        }

    def add_learning_candidate(self, model_type: ModelType, source_id: str,
                              prediction: Dict, features: Dict,
                              timestamp: Optional[float] = None,
                              metadata: Optional[Dict] = None) -> str:
        """Add a new candidate for active learning"""

        candidate_id = self._generate_candidate_id(model_type, source_id, timestamp)

        # Calculate uncertainty score
        uncertainty_score = self.uncertainty_calculator.calculate_uncertainty(prediction, features)

        # Calculate diversity score
        existing_samples = self._get_existing_samples(model_type)
        diversity_score = self.diversity_calculator.calculate_diversity(features, existing_samples)

        # Calculate importance score (hybrid of uncertainty and diversity)
        importance_score = (
            self.strategy_weights['uncertainty'] * uncertainty_score +
            self.strategy_weights['diversity'] * diversity_score +
            self.strategy_weights['importance'] * self._calculate_domain_importance(
                model_type, prediction, features
            )
        )

        candidate = LearningCandidate(
            candidate_id=candidate_id,
            model_type=model_type,
            source_id=source_id,
            timestamp=timestamp,
            features=features,
            current_prediction=prediction,
            uncertainty_score=uncertainty_score,
            diversity_score=diversity_score,
            importance_score=importance_score,
            metadata=metadata or {},
            created_at=datetime.now().isoformat()
        )

        self.learning_db.store_candidate(candidate)

        # Log to audit system
        self.audit_system.log_event("active_learning", "candidate_added", {
            'candidate_id': candidate_id,
            'model_type': model_type.value,
            'uncertainty_score': uncertainty_score,
            'diversity_score': diversity_score,
            'importance_score': importance_score
        })

        return candidate_id

    def start_learning_session(self, model_type: ModelType,
                              strategy: LearningStrategy = LearningStrategy.HYBRID,
                              max_candidates: int = 10) -> str:
        """Start an active learning session"""

        session_id = f"session_{model_type.value}_{int(time.time())}"

        # Select candidates based on strategy
        candidates = self._select_candidates(model_type, strategy, max_candidates)

        # Mark candidates as selected for review
        for candidate in candidates:
            self._mark_candidate_selected(candidate.candidate_id)

        session = LearningSession(
            session_id=session_id,
            model_type=model_type,
            strategy=strategy,
            candidates_selected=len(candidates),
            feedback_received=0,
            improvements_made=[],
            start_time=datetime.now().isoformat(),
            end_time=None,
            metadata={
                'candidate_ids': [c.candidate_id for c in candidates]
            }
        )

        self._store_learning_session(session)

        return session_id

    def submit_feedback(self, candidate_id: str, feedback_type: FeedbackType,
                       corrected_prediction: Dict, confidence: float,
                       explanation: Optional[str] = None,
                       reviewer_id: str = "human_reviewer") -> str:
        """Submit human feedback for a candidate"""

        # Get original candidate
        candidate = self._get_candidate(candidate_id)
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")

        feedback_id = f"feedback_{candidate_id}_{int(time.time())}"

        feedback = HumanFeedback(
            feedback_id=feedback_id,
            candidate_id=candidate_id,
            feedback_type=feedback_type,
            original_prediction=candidate.current_prediction,
            corrected_prediction=corrected_prediction,
            confidence=confidence,
            explanation=explanation,
            reviewer_id=reviewer_id,
            timestamp=datetime.now().isoformat()
        )

        self.learning_db.store_feedback(feedback)

        # Mark candidate as reviewed
        self._mark_candidate_reviewed(candidate_id)

        # Log to audit system
        self.audit_system.log_event("active_learning", "feedback_received", {
            'feedback_id': feedback_id,
            'candidate_id': candidate_id,
            'feedback_type': feedback_type.value,
            'confidence': confidence
        })

        return feedback_id

    def get_pending_reviews(self, model_type: ModelType, limit: int = 10) -> List[LearningCandidate]:
        """Get candidates pending human review"""
        return self.learning_db.get_candidates_for_review(model_type, limit)

    def analyze_feedback_patterns(self, model_type: ModelType,
                                 days_back: int = 30) -> Dict:
        """Analyze patterns in human feedback to improve model"""

        # Get recent feedback
        since_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        feedback_data = self._get_feedback_since(model_type, since_date)

        if not feedback_data:
            return {'status': 'no_feedback', 'recommendations': []}

        patterns = {
            'total_feedback': len(feedback_data),
            'feedback_types': {},
            'accuracy_trends': [],
            'common_errors': [],
            'improvement_recommendations': []
        }

        # Analyze feedback types
        for feedback in feedback_data:
            feedback_type = feedback['feedback_type']
            patterns['feedback_types'][feedback_type] = patterns['feedback_types'].get(feedback_type, 0) + 1

        # Identify common error patterns
        corrections = [f for f in feedback_data if f['feedback_type'] == 'correction']
        if corrections:
            error_patterns = self._analyze_correction_patterns(corrections)
            patterns['common_errors'] = error_patterns

        # Generate recommendations
        recommendations = self._generate_improvement_recommendations(patterns)
        patterns['improvement_recommendations'] = recommendations

        return patterns

    def _generate_candidate_id(self, model_type: ModelType, source_id: str,
                              timestamp: Optional[float]) -> str:
        """Generate unique candidate ID"""
        base_string = f"{model_type.value}_{source_id}_{timestamp or time.time()}"
        return hashlib.md5(base_string.encode()).hexdigest()[:16]

    def _get_existing_samples(self, model_type: ModelType) -> List[Dict]:
        """Get existing samples for diversity calculation"""
        cursor = self.learning_db.connection.cursor()
        cursor.execute("""
            SELECT features FROM learning_candidates
            WHERE model_type = ?
            ORDER BY created_at DESC
            LIMIT 100
        """, (model_type.value,))

        samples = []
        for row in cursor.fetchall():
            try:
                features = json.loads(row[0])
                samples.append(features)
            except:
                continue

        return samples

    def _calculate_domain_importance(self, model_type: ModelType,
                                   prediction: Dict, features: Dict) -> float:
        """Calculate domain-specific importance score"""
        # Domain-specific logic for different model types

        if model_type == ModelType.SPEAKER_DIARIZATION:
            # Higher importance for segments with multiple speakers or low confidence
            confidence = prediction.get('confidence', 0.5)
            speaker_count = prediction.get('speaker_count', 1)
            return (1.0 - confidence) * min(1.0, speaker_count / 3.0)

        elif model_type == ModelType.EMOTION_DETECTION:
            # Higher importance for neutral emotions (often misclassified)
            emotion = prediction.get('emotion', 'neutral')
            emotion_confidence = prediction.get('confidence', 0.5)
            neutrality_weight = 1.2 if emotion == 'neutral' else 1.0
            return (1.0 - emotion_confidence) * neutrality_weight

        elif model_type == ModelType.CONTRADICTION_DETECTION:
            # Higher importance for borderline contradiction cases
            contradiction_score = prediction.get('contradiction_score', 0.5)
            return 1.0 - abs(contradiction_score - 0.5) * 2

        else:
            # Default importance based on confidence
            confidence = prediction.get('confidence', 0.5)
            return 1.0 - confidence

    def _select_candidates(self, model_type: ModelType, strategy: LearningStrategy,
                          max_candidates: int) -> List[LearningCandidate]:
        """Select candidates based on strategy"""
        all_candidates = self.learning_db.get_candidates_for_review(model_type, max_candidates * 2)

        if strategy == LearningStrategy.UNCERTAINTY_SAMPLING:
            # Sort by uncertainty score
            candidates = sorted(all_candidates, key=lambda x: x.uncertainty_score, reverse=True)

        elif strategy == LearningStrategy.DIVERSITY_SAMPLING:
            # Sort by diversity score
            candidates = sorted(all_candidates, key=lambda x: x.diversity_score, reverse=True)

        elif strategy == LearningStrategy.HYBRID:
            # Sort by importance score (already hybrid)
            candidates = sorted(all_candidates, key=lambda x: x.importance_score, reverse=True)

        else:
            # Default to importance score
            candidates = sorted(all_candidates, key=lambda x: x.importance_score, reverse=True)

        return candidates[:max_candidates]

    def _mark_candidate_selected(self, candidate_id: str):
        """Mark candidate as selected for review"""
        cursor = self.learning_db.connection.cursor()
        cursor.execute("""
            UPDATE learning_candidates
            SET selected_for_review = TRUE
            WHERE candidate_id = ?
        """, (candidate_id,))
        self.learning_db.connection.commit()

    def _mark_candidate_reviewed(self, candidate_id: str):
        """Mark candidate as reviewed"""
        cursor = self.learning_db.connection.cursor()
        cursor.execute("""
            UPDATE learning_candidates
            SET review_completed = TRUE
            WHERE candidate_id = ?
        """, (candidate_id,))
        self.learning_db.connection.commit()

    def _get_candidate(self, candidate_id: str) -> Optional[LearningCandidate]:
        """Get candidate by ID"""
        cursor = self.learning_db.connection.cursor()
        cursor.execute("""
            SELECT * FROM learning_candidates
            WHERE candidate_id = ?
        """, (candidate_id,))

        row = cursor.fetchone()
        if row:
            return self.learning_db._row_to_candidate(row)
        return None

    def _store_learning_session(self, session: LearningSession):
        """Store learning session"""
        cursor = self.learning_db.connection.cursor()
        cursor.execute("""
            INSERT INTO learning_sessions
            (session_id, model_type, strategy, candidates_selected, feedback_received,
             improvements_made, start_time, end_time, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session.session_id,
            session.model_type.value,
            session.strategy.value,
            session.candidates_selected,
            session.feedback_received,
            json.dumps(session.improvements_made),
            session.start_time,
            session.end_time,
            json.dumps(session.metadata or {})
        ))
        self.learning_db.connection.commit()

    def _get_feedback_since(self, model_type: ModelType, since_date: str) -> List[Dict]:
        """Get feedback since a certain date"""
        cursor = self.learning_db.connection.cursor()
        cursor.execute("""
            SELECT hf.* FROM human_feedback hf
            JOIN learning_candidates lc ON hf.candidate_id = lc.candidate_id
            WHERE lc.model_type = ? AND hf.timestamp >= ?
            ORDER BY hf.timestamp DESC
        """, (model_type.value, since_date))

        feedback_list = []
        for row in cursor.fetchall():
            feedback_list.append({
                'feedback_id': row[0],
                'candidate_id': row[1],
                'feedback_type': row[2],
                'original_prediction': json.loads(row[3]),
                'corrected_prediction': json.loads(row[4]),
                'confidence': row[5],
                'explanation': row[6],
                'reviewer_id': row[7],
                'timestamp': row[8],
                'metadata': json.loads(row[9] or '{}')
            })

        return feedback_list

    def _analyze_correction_patterns(self, corrections: List[Dict]) -> List[str]:
        """Analyze patterns in correction feedback"""
        patterns = []

        # Simple pattern analysis
        correction_types = {}
        for correction in corrections:
            original = correction['original_prediction']
            corrected = correction['corrected_prediction']

            # Analyze what changed
            if 'confidence' in original and 'confidence' in corrected:
                conf_diff = corrected['confidence'] - original['confidence']
                if conf_diff > 0.3:
                    correction_types['low_confidence'] = correction_types.get('low_confidence', 0) + 1
                elif conf_diff < -0.3:
                    correction_types['overconfident'] = correction_types.get('overconfident', 0) + 1

        # Convert to patterns
        for pattern_type, count in correction_types.items():
            if count >= 3:  # Pattern threshold
                patterns.append(f"{pattern_type}: {count} occurrences")

        return patterns

    def _generate_improvement_recommendations(self, patterns: Dict) -> List[str]:
        """Generate improvement recommendations based on feedback patterns"""
        recommendations = []

        feedback_types = patterns.get('feedback_types', {})
        common_errors = patterns.get('common_errors', [])

        # Analyze feedback types
        total_feedback = patterns.get('total_feedback', 0)
        if total_feedback > 0:
            correction_ratio = feedback_types.get('correction', 0) / total_feedback

            if correction_ratio > 0.5:
                recommendations.append("High correction rate - consider model retraining")
            elif correction_ratio > 0.3:
                recommendations.append("Moderate correction rate - consider parameter tuning")

        # Analyze error patterns
        for error in common_errors:
            if 'low_confidence' in error:
                recommendations.append("Improve confidence calibration for uncertain predictions")
            elif 'overconfident' in error:
                recommendations.append("Reduce overconfidence in model predictions")

        if not recommendations:
            recommendations.append("Performance appears stable - continue monitoring")

        return recommendations


def main():
    """Demo of active learning framework"""
    print("🧠 Active Learning Framework - Phase 6")
    print("=" * 50)

    engine = ActiveLearningEngine()

    print("✅ Active learning engine initialized")
    print("🎯 Sample selection strategies: Uncertainty, diversity, hybrid")
    print("👤 Human feedback integration: Corrections, confirmations, annotations")
    print("📊 Pattern analysis: Error detection and improvement recommendations")
    print("🔄 Continuous improvement: Model updates based on feedback")
    print("\nReady for integration with all Sherlock models")

    # Example usage:
    # candidate_id = engine.add_learning_candidate(
    #     ModelType.SPEAKER_DIARIZATION,
    #     "source_123",
    #     {"speaker": "Speaker_1", "confidence": 0.6},
    #     {"mfcc_features": [...], "energy": 0.5}
    # )
    #
    # session_id = engine.start_learning_session(ModelType.SPEAKER_DIARIZATION)
    # candidates = engine.get_pending_reviews(ModelType.SPEAKER_DIARIZATION)
    #
    # feedback_id = engine.submit_feedback(
    #     candidate_id,
    #     FeedbackType.CORRECTION,
    #     {"speaker": "Speaker_2", "confidence": 0.9},
    #     0.95
    # )


if __name__ == "__main__":
    main()