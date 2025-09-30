#!/usr/bin/env python3
"""
Analysis Engine for Sherlock
Contradiction detection, propaganda flagging, and relationship analysis
"""

import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from evidence_database import (
    EvidenceDatabase, EvidenceRelationship, ClaimType
)


class AnalysisType(Enum):
    """Types of analysis performed on evidence"""
    CONTRADICTION = "contradiction"
    PROPAGANDA = "propaganda"
    BIAS = "bias"
    FACT_CHECK = "fact_check"
    SENTIMENT = "sentiment"
    ENTITY_LINK = "entity_link"


@dataclass
class AnalysisResult:
    """Result of evidence analysis"""
    analysis_id: str
    analysis_type: AnalysisType
    claim_id: str
    confidence: float
    findings: Dict
    flags: List[str]
    evidence: str
    created_at: str


@dataclass
class ContradictionPair:
    """Pair of contradicting claims"""
    claim_1_id: str
    claim_2_id: str
    claim_1_text: str
    claim_2_text: str
    contradiction_type: str
    confidence: float
    explanation: str


@dataclass
class PropagandaFlag:
    """Propaganda detection result"""
    claim_id: str
    propaganda_type: str
    confidence: float
    techniques: List[str]
    explanation: str


class AnalysisEngine:
    """Advanced analysis engine for evidence evaluation"""

    def __init__(self, db_path: str = "evidence.db"):
        self.db = EvidenceDatabase(db_path)
        self.contradiction_patterns = self._load_contradiction_patterns()
        self.propaganda_patterns = self._load_propaganda_patterns()

    def analyze_contradictions(self, batch_size: int = 100) -> List[ContradictionPair]:
        """Detect contradictions between claims"""

        print("🔍 Analyzing contradictions in evidence database...")
        start_time = time.time()

        contradictions = []

        try:
            # Get all factual claims for comparison
            cursor = self.db.connection.execute("""
                SELECT claim_id, text, source_id, speaker_id, entities, context
                FROM evidence_claims
                WHERE claim_type = 'factual'
                ORDER BY claim_id
            """)

            claims = []
            for row in cursor.fetchall():
                claims.append({
                    'claim_id': row[0],
                    'text': row[1],
                    'source_id': row[2],
                    'speaker_id': row[3],
                    'entities': json.loads(row[4]) if row[4] else [],
                    'context': row[5]
                })

            print(f"📊 Analyzing {len(claims)} factual claims for contradictions...")

            # Compare claims pairwise
            for i, claim1 in enumerate(claims):
                for j, claim2 in enumerate(claims[i+1:], i+1):
                    # Skip claims from the same source
                    if claim1['source_id'] == claim2['source_id']:
                        continue

                    contradiction = self._detect_contradiction(claim1, claim2)
                    if contradiction:
                        contradictions.append(contradiction)

                        # Add relationship to database
                        self._add_contradiction_relationship(claim1['claim_id'], claim2['claim_id'], contradiction)

            processing_time = time.time() - start_time
            print(f"✅ Contradiction analysis complete: {len(contradictions)} contradictions found in {processing_time:.1f}s")

            return contradictions

        except Exception as e:
            print(f"❌ Contradiction analysis error: {e}")
            return []

    def analyze_propaganda(self, batch_size: int = 100) -> List[PropagandaFlag]:
        """Detect propaganda techniques in claims"""

        print("🎭 Analyzing propaganda techniques in evidence database...")
        start_time = time.time()

        propaganda_flags = []

        try:
            # Get all claims for analysis
            cursor = self.db.connection.execute("""
                SELECT claim_id, text, claim_type, context, tags
                FROM evidence_claims
                ORDER BY claim_id
            """)

            claims = []
            for row in cursor.fetchall():
                claims.append({
                    'claim_id': row[0],
                    'text': row[1],
                    'claim_type': row[2],
                    'context': row[3],
                    'tags': json.loads(row[4]) if row[4] else []
                })

            print(f"📊 Analyzing {len(claims)} claims for propaganda techniques...")

            for claim in claims:
                propaganda_flag = self._detect_propaganda(claim)
                if propaganda_flag:
                    propaganda_flags.append(propaganda_flag)

                    # Add analysis result to database
                    self._add_propaganda_analysis(claim['claim_id'], propaganda_flag)

            processing_time = time.time() - start_time
            print(f"✅ Propaganda analysis complete: {len(propaganda_flags)} flags identified in {processing_time:.1f}s")

            return propaganda_flags

        except Exception as e:
            print(f"❌ Propaganda analysis error: {e}")
            return []

    def analyze_bias_patterns(self) -> Dict:
        """Analyze bias patterns in evidence sources"""

        print("⚖️  Analyzing bias patterns across sources...")

        try:
            bias_analysis = {
                "source_bias": {},
                "speaker_bias": {},
                "topic_bias": {},
                "overall_patterns": []
            }

            # Analyze source bias
            cursor = self.db.connection.execute("""
                SELECT es.source_id, es.title, COUNT(ec.claim_id) as claim_count,
                       AVG(CASE WHEN ec.claim_type = 'opinion' THEN 1.0 ELSE 0.0 END) as opinion_ratio
                FROM evidence_sources es
                JOIN evidence_claims ec ON es.source_id = ec.source_id
                GROUP BY es.source_id, es.title
                HAVING claim_count > 2
                ORDER BY opinion_ratio DESC
            """)

            for row in cursor.fetchall():
                source_id, title, claim_count, opinion_ratio = row
                bias_analysis["source_bias"][source_id] = {
                    "title": title,
                    "claim_count": claim_count,
                    "opinion_ratio": opinion_ratio,
                    "bias_score": opinion_ratio * 100
                }

            # Analyze speaker bias
            cursor = self.db.connection.execute("""
                SELECT s.speaker_id, s.name, COUNT(ec.claim_id) as claim_count,
                       AVG(CASE WHEN ec.claim_type = 'opinion' THEN 1.0 ELSE 0.0 END) as opinion_ratio,
                       COUNT(DISTINCT ec.source_id) as source_count
                FROM speakers s
                JOIN evidence_claims ec ON s.speaker_id = ec.speaker_id
                GROUP BY s.speaker_id, s.name
                HAVING claim_count > 1
                ORDER BY opinion_ratio DESC
            """)

            for row in cursor.fetchall():
                speaker_id, name, claim_count, opinion_ratio, source_count = row
                bias_analysis["speaker_bias"][speaker_id] = {
                    "name": name or "Unknown",
                    "claim_count": claim_count,
                    "opinion_ratio": opinion_ratio,
                    "source_diversity": source_count,
                    "bias_score": opinion_ratio * (100 / max(source_count, 1))
                }

            print(f"✅ Bias analysis complete:")
            print(f"   Sources analyzed: {len(bias_analysis['source_bias'])}")
            print(f"   Speakers analyzed: {len(bias_analysis['speaker_bias'])}")

            return bias_analysis

        except Exception as e:
            print(f"❌ Bias analysis error: {e}")
            return {}

    def _detect_contradiction(self, claim1: Dict, claim2: Dict) -> Optional[ContradictionPair]:
        """Detect contradiction between two claims"""

        text1 = claim1['text'].lower()
        text2 = claim2['text'].lower()

        # Check for entity overlap (claims must be about similar topics)
        entities1 = set(entity.lower() for entity in claim1['entities'])
        entities2 = set(entity.lower() for entity in claim2['entities'])

        entity_overlap = len(entities1.intersection(entities2))
        if entity_overlap == 0:
            return None  # No topical overlap

        # Check for contradiction patterns
        for pattern_name, pattern in self.contradiction_patterns.items():
            confidence = self._match_contradiction_pattern(text1, text2, pattern)

            if confidence > 0.7:  # Threshold for contradiction detection
                return ContradictionPair(
                    claim_1_id=claim1['claim_id'],
                    claim_2_id=claim2['claim_id'],
                    claim_1_text=claim1['text'],
                    claim_2_text=claim2['text'],
                    contradiction_type=pattern_name,
                    confidence=confidence,
                    explanation=f"Detected {pattern_name} contradiction with {confidence:.1%} confidence"
                )

        return None

    def _detect_propaganda(self, claim: Dict) -> Optional[PropagandaFlag]:
        """Detect propaganda techniques in a claim"""

        text = claim['text'].lower()
        detected_techniques = []
        max_confidence = 0.0

        for technique_name, pattern in self.propaganda_patterns.items():
            confidence = self._match_propaganda_pattern(text, claim['context'].lower(), pattern)

            if confidence > 0.6:  # Threshold for propaganda detection
                detected_techniques.append(technique_name)
                max_confidence = max(max_confidence, confidence)

        if detected_techniques:
            # Determine primary propaganda type
            propaganda_type = detected_techniques[0] if detected_techniques else "general"

            return PropagandaFlag(
                claim_id=claim['claim_id'],
                propaganda_type=propaganda_type,
                confidence=max_confidence,
                techniques=detected_techniques,
                explanation=f"Detected propaganda techniques: {', '.join(detected_techniques)}"
            )

        return None

    def _match_contradiction_pattern(self, text1: str, text2: str, pattern: Dict) -> float:
        """Match contradiction pattern against two texts"""

        confidence = 0.0

        # Check for negation patterns
        if pattern.get("type") == "negation":
            for positive_phrase in pattern.get("positive_phrases", []):
                for negative_phrase in pattern.get("negative_phrases", []):
                    if positive_phrase in text1 and negative_phrase in text2:
                        confidence = max(confidence, 0.8)
                    elif positive_phrase in text2 and negative_phrase in text1:
                        confidence = max(confidence, 0.8)

        # Check for numeric contradictions
        elif pattern.get("type") == "numeric":
            numbers1 = self._extract_numbers(text1)
            numbers2 = self._extract_numbers(text2)

            if numbers1 and numbers2:
                for num1 in numbers1:
                    for num2 in numbers2:
                        # Check for significant numeric differences
                        if abs(num1 - num2) / max(num1, num2, 1) > 0.2:  # 20% difference
                            confidence = max(confidence, 0.7)

        # Check for temporal contradictions
        elif pattern.get("type") == "temporal":
            dates1 = self._extract_dates(text1)
            dates2 = self._extract_dates(text2)

            if dates1 and dates2:
                # Simplified date contradiction detection
                confidence = 0.6

        return confidence

    def _match_propaganda_pattern(self, text: str, context: str, pattern: Dict) -> float:
        """Match propaganda pattern against text"""

        confidence = 0.0
        combined_text = text + " " + context

        # Check for emotional appeals
        if pattern.get("type") == "emotional_appeal":
            emotional_words = pattern.get("keywords", [])
            matches = sum(1 for word in emotional_words if word in combined_text)
            confidence = min(matches / len(emotional_words), 1.0) * 0.8

        # Check for loaded language
        elif pattern.get("type") == "loaded_language":
            loaded_phrases = pattern.get("phrases", [])
            matches = sum(1 for phrase in loaded_phrases if phrase in combined_text)
            confidence = min(matches / max(len(loaded_phrases), 1), 1.0) * 0.9

        # Check for false dichotomy
        elif pattern.get("type") == "false_dichotomy":
            dichotomy_indicators = pattern.get("indicators", [])
            matches = sum(1 for indicator in dichotomy_indicators if indicator in combined_text)
            confidence = min(matches, 1.0) * 0.7

        # Check for appeal to authority
        elif pattern.get("type") == "appeal_to_authority":
            authority_phrases = pattern.get("authority_phrases", [])
            matches = sum(1 for phrase in authority_phrases if phrase in combined_text)
            confidence = min(matches, 1.0) * 0.6

        return confidence

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values from text"""
        # Simple numeric extraction - in production would be more sophisticated
        pattern = r'\b\d+(?:\.\d+)?\b'
        matches = re.findall(pattern, text)
        return [float(match) for match in matches]

    def _extract_dates(self, text: str) -> List[str]:
        """Extract date references from text"""
        # Simple date extraction - in production would use proper date parsing
        date_patterns = [
            r'\b\d{4}\b',  # Years
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
            r'\b\d{1,2}-\d{1,2}-\d{4}\b'   # MM-DD-YYYY
        ]

        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text))

        return dates

    def _add_contradiction_relationship(self, claim1_id: str, claim2_id: str, contradiction: ContradictionPair):
        """Add contradiction relationship to database"""

        relationship = EvidenceRelationship(
            relationship_id=f"contradiction_{claim1_id}_{claim2_id}",
            subject_type="claim",
            subject_id=claim1_id,
            relationship_type="contradicts",
            object_type="claim",
            object_id=claim2_id,
            confidence=contradiction.confidence,
            evidence=contradiction.explanation,
            created_at=datetime.now().isoformat()
        )

        self.db.add_relationship(relationship)

    def _add_propaganda_analysis(self, claim_id: str, propaganda_flag: PropagandaFlag):
        """Add propaganda analysis to database"""

        # Store as a special relationship
        relationship = EvidenceRelationship(
            relationship_id=f"propaganda_{claim_id}_{int(time.time())}",
            subject_type="claim",
            subject_id=claim_id,
            relationship_type="propaganda_flag",
            object_type="analysis",
            object_id=propaganda_flag.propaganda_type,
            confidence=propaganda_flag.confidence,
            evidence=json.dumps({
                "techniques": propaganda_flag.techniques,
                "explanation": propaganda_flag.explanation
            }),
            created_at=datetime.now().isoformat()
        )

        self.db.add_relationship(relationship)

    def _load_contradiction_patterns(self) -> Dict:
        """Load contradiction detection patterns"""

        return {
            "negation": {
                "type": "negation",
                "positive_phrases": [
                    "is effective", "works well", "increases", "improves", "beneficial",
                    "safe", "secure", "reliable", "accurate", "successful"
                ],
                "negative_phrases": [
                    "is ineffective", "doesn't work", "decreases", "worsens", "harmful",
                    "unsafe", "insecure", "unreliable", "inaccurate", "failed"
                ]
            },
            "numeric": {
                "type": "numeric",
                "description": "Contradictory numeric claims"
            },
            "temporal": {
                "type": "temporal",
                "description": "Contradictory temporal claims"
            }
        }

    def _load_propaganda_patterns(self) -> Dict:
        """Load propaganda detection patterns"""

        return {
            "emotional_appeal": {
                "type": "emotional_appeal",
                "keywords": [
                    "fear", "terror", "panic", "crisis", "disaster", "catastrophe",
                    "outrage", "shocking", "incredible", "amazing", "fantastic"
                ]
            },
            "loaded_language": {
                "type": "loaded_language",
                "phrases": [
                    "radical", "extremist", "dangerous", "threatening", "evil",
                    "heroic", "patriotic", "freedom", "liberty", "justice"
                ]
            },
            "false_dichotomy": {
                "type": "false_dichotomy",
                "indicators": [
                    "either", "only two", "must choose", "no other option",
                    "black and white", "all or nothing"
                ]
            },
            "appeal_to_authority": {
                "type": "appeal_to_authority",
                "authority_phrases": [
                    "experts say", "studies show", "research proves", "scientists agree",
                    "according to authorities", "officials confirm"
                ]
            }
        }

    def get_analysis_summary(self) -> Dict:
        """Get comprehensive analysis summary"""

        try:
            summary = {
                "contradictions": 0,
                "propaganda_flags": 0,
                "total_relationships": 0,
                "analysis_coverage": 0.0,
                "top_contradiction_types": [],
                "top_propaganda_techniques": []
            }

            # Count contradictions
            cursor = self.db.connection.execute("""
                SELECT COUNT(*) FROM evidence_relationships
                WHERE relationship_type = 'contradicts'
            """)
            summary["contradictions"] = cursor.fetchone()[0]

            # Count propaganda flags
            cursor = self.db.connection.execute("""
                SELECT COUNT(*) FROM evidence_relationships
                WHERE relationship_type = 'propaganda_flag'
            """)
            summary["propaganda_flags"] = cursor.fetchone()[0]

            # Total relationships
            cursor = self.db.connection.execute("""
                SELECT COUNT(*) FROM evidence_relationships
            """)
            summary["total_relationships"] = cursor.fetchone()[0]

            # Analysis coverage
            cursor = self.db.connection.execute("""
                SELECT
                    COUNT(DISTINCT ec.claim_id) as analyzed_claims,
                    (SELECT COUNT(*) FROM evidence_claims) as total_claims
                FROM evidence_claims ec
                JOIN evidence_relationships er ON ec.claim_id = er.subject_id
                WHERE er.relationship_type IN ('contradicts', 'propaganda_flag')
            """)

            result = cursor.fetchone()
            if result and result[1] > 0:
                summary["analysis_coverage"] = result[0] / result[1]

            return summary

        except Exception as e:
            print(f"Error getting analysis summary: {e}")
            return {}

    def close(self):
        """Close database connection"""
        self.db.close()


def main():
    """CLI interface for analysis engine"""
    if len(sys.argv) < 2:
        print("Analysis Engine for Sherlock")
        print("Usage:")
        print("  python analysis_engine.py contradictions")
        print("  python analysis_engine.py propaganda")
        print("  python analysis_engine.py bias")
        print("  python analysis_engine.py summary")
        sys.exit(1)

    command = sys.argv[1].lower()
    engine = AnalysisEngine()

    try:
        if command == "contradictions":
            contradictions = engine.analyze_contradictions()

            print(f"\n📊 CONTRADICTION ANALYSIS RESULTS")
            print("=" * 40)

            if not contradictions:
                print("No contradictions detected")
            else:
                for i, contradiction in enumerate(contradictions[:10], 1):
                    print(f"\n{i}. {contradiction.contradiction_type.upper()} ({contradiction.confidence:.1%})")
                    print(f"   Claim 1: {contradiction.claim_1_text[:80]}...")
                    print(f"   Claim 2: {contradiction.claim_2_text[:80]}...")
                    print(f"   Explanation: {contradiction.explanation}")

        elif command == "propaganda":
            propaganda_flags = engine.analyze_propaganda()

            print(f"\n🎭 PROPAGANDA ANALYSIS RESULTS")
            print("=" * 40)

            if not propaganda_flags:
                print("No propaganda techniques detected")
            else:
                for i, flag in enumerate(propaganda_flags[:10], 1):
                    print(f"\n{i}. {flag.propaganda_type.upper()} ({flag.confidence:.1%})")
                    print(f"   Techniques: {', '.join(flag.techniques)}")
                    print(f"   Explanation: {flag.explanation}")

        elif command == "bias":
            bias_analysis = engine.analyze_bias_patterns()

            print(f"\n⚖️  BIAS ANALYSIS RESULTS")
            print("=" * 40)

            if bias_analysis.get("source_bias"):
                print("\nTop Biased Sources:")
                for source_id, data in list(bias_analysis["source_bias"].items())[:5]:
                    print(f"   {data['title']}: {data['bias_score']:.1f}% bias score")

            if bias_analysis.get("speaker_bias"):
                print("\nTop Biased Speakers:")
                for speaker_id, data in list(bias_analysis["speaker_bias"].items())[:5]:
                    print(f"   {data['name']}: {data['bias_score']:.1f}% bias score")

        elif command == "summary":
            summary = engine.get_analysis_summary()

            print(f"\n📈 ANALYSIS SUMMARY")
            print("=" * 30)
            print(f"Contradictions detected: {summary.get('contradictions', 0)}")
            print(f"Propaganda flags: {summary.get('propaganda_flags', 0)}")
            print(f"Total relationships: {summary.get('total_relationships', 0)}")
            print(f"Analysis coverage: {summary.get('analysis_coverage', 0):.1%}")

        else:
            print(f"❌ Unknown command: {command}")
            sys.exit(1)

    finally:
        engine.close()


if __name__ == "__main__":
    main()