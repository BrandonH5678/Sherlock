#!/usr/bin/env python3
"""
5-Block Answer Format Synthesis for Sherlock
Structures query results into established/contested/why/flags/next format
"""

import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
from enum import Enum

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from query_system import HybridQuerySystem, QueryResult, SearchQuery, QueryType
from evidence_database import EvidenceDatabase


class FlagType(Enum):
    """Types of analytical flags"""
    CONTRADICTION = "contradiction"
    PROPAGANDA = "propaganda"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    BIAS_DETECTED = "bias_detected"
    TEMPORAL_INCONSISTENCY = "temporal_inconsistency"
    SOURCE_RELIABILITY = "source_reliability"
    MISSING_CONTEXT = "missing_context"


@dataclass
class AnalysisFlag:
    """Individual analytical flag"""
    flag_type: FlagType
    severity: str  # "low", "medium", "high", "critical"
    description: str
    evidence: List[str]
    confidence: float


@dataclass
class SynthesisBlock:
    """Individual block in 5-block answer format"""
    block_type: str  # "established", "contested", "why", "flags", "next"
    title: str
    content: str
    sources: List[Dict]
    confidence: float
    metadata: Dict


@dataclass
class AnswerSynthesis:
    """Complete 5-block structured answer"""
    query: str
    query_type: str
    generated_at: str
    processing_time: float

    # The 5 blocks
    established: SynthesisBlock
    contested: SynthesisBlock
    why: SynthesisBlock
    flags: SynthesisBlock
    next_steps: SynthesisBlock

    # Metadata
    total_sources: int
    total_claims: int
    overall_confidence: float
    synthesis_notes: str


class AnswerSynthesizer:
    """Synthesizes query results into structured 5-block format"""

    def __init__(self, db_path: str = "evidence.db"):
        self.db = EvidenceDatabase(db_path)
        self.query_system = HybridQuerySystem(db_path)

    def synthesize_answer(self, query: SearchQuery) -> AnswerSynthesis:
        """Generate 5-block structured answer for query"""

        print(f"🧠 Synthesizing answer for: '{query.query_text}'")
        start_time = time.time()

        try:
            # Execute query to get raw results
            results = self.query_system.execute_query(query)

            if not results:
                return self._create_no_results_synthesis(query, start_time)

            # Analyze results for synthesis
            analysis = self._analyze_results(results, query)

            # Generate each block
            established_block = self._generate_established_block(analysis)
            contested_block = self._generate_contested_block(analysis)
            why_block = self._generate_why_block(analysis)
            flags_block = self._generate_flags_block(analysis)
            next_steps_block = self._generate_next_steps_block(analysis)

            # Calculate overall metrics
            overall_confidence = self._calculate_overall_confidence(analysis)

            processing_time = time.time() - start_time

            synthesis = AnswerSynthesis(
                query=query.query_text,
                query_type=query.query_type.value,
                generated_at=datetime.now().isoformat(),
                processing_time=processing_time,
                established=established_block,
                contested=contested_block,
                why=why_block,
                flags=flags_block,
                next_steps=next_steps_block,
                total_sources=len(set(r.source_info.get('source_id') for r in results)),
                total_claims=len(results),
                overall_confidence=overall_confidence,
                synthesis_notes=f"Generated from {len(results)} results across {len(set(r.source_info.get('source_id') for r in results))} sources"
            )

            print(f"✅ Answer synthesis completed in {processing_time:.2f}s")
            return synthesis

        except Exception as e:
            print(f"❌ Answer synthesis error: {e}")
            return self._create_error_synthesis(query, str(e), start_time)

    def _analyze_results(self, results: List[QueryResult], query: SearchQuery) -> Dict:
        """Analyze query results to prepare for synthesis"""

        analysis = {
            'results': results,
            'query': query,
            'high_confidence_claims': [],
            'low_confidence_claims': [],
            'contradictions': [],
            'propaganda_flags': [],
            'sources': {},
            'speakers': {},
            'entities': set(),
            'temporal_patterns': [],
            'bias_indicators': [],
            'missing_evidence_gaps': []
        }

        # Categorize results by confidence
        for result in results:
            if result.confidence >= 0.7:
                analysis['high_confidence_claims'].append(result)
            elif result.confidence < 0.4:
                analysis['low_confidence_claims'].append(result)

            # Track sources and speakers
            source_id = result.source_info.get('source_id')
            if source_id:
                if source_id not in analysis['sources']:
                    analysis['sources'][source_id] = {
                        'source_id': source_id,
                        'title': result.source_info.get('source_title'),
                        'claims': [],
                        'reliability_score': 0.0
                    }
                analysis['sources'][source_id]['claims'].append(result)

            speaker_name = result.source_info.get('speaker_name')
            if speaker_name:
                if speaker_name not in analysis['speakers']:
                    analysis['speakers'][speaker_name] = {
                        'name': speaker_name,
                        'claims': [],
                        'consistency_score': 0.0
                    }
                analysis['speakers'][speaker_name]['claims'].append(result)

            # Collect entities
            analysis['entities'].update(result.metadata.get('entities', []))

            # Identify special result types
            if result.result_type == 'contradiction':
                analysis['contradictions'].append(result)
            elif result.result_type == 'propaganda':
                analysis['propaganda_flags'].append(result)

        # Calculate source reliability scores
        for source_id, source_data in analysis['sources'].items():
            claims = source_data['claims']
            if claims:
                avg_confidence = sum(c.confidence for c in claims) / len(claims)
                source_data['reliability_score'] = avg_confidence

        # Calculate speaker consistency scores
        for speaker_name, speaker_data in analysis['speakers'].items():
            claims = speaker_data['claims']
            if claims:
                # Simple consistency measure based on confidence variance
                confidences = [c.confidence for c in claims]
                avg_confidence = sum(confidences) / len(confidences)
                variance = sum((c - avg_confidence) ** 2 for c in confidences) / len(confidences)
                consistency_score = max(0.0, avg_confidence - variance)
                speaker_data['consistency_score'] = consistency_score

        return analysis

    def _generate_established_block(self, analysis: Dict) -> SynthesisBlock:
        """Generate ESTABLISHED block - well-supported claims"""

        high_conf_claims = analysis['high_confidence_claims']

        if not high_conf_claims:
            content = "No claims meet the threshold for established facts based on current evidence."
            sources = []
            confidence = 0.0
        else:
            # Group by similar content/themes
            content_lines = []
            sources = []
            confidence_scores = []

            for claim in high_conf_claims[:5]:  # Top 5 established facts
                content_lines.append(f"• {claim.content[:200]}...")
                if claim.source_info.get('source_title'):
                    sources.append({
                        'title': claim.source_info['source_title'],
                        'confidence': claim.confidence,
                        'timecode': claim.timecode
                    })
                confidence_scores.append(claim.confidence)

            content = "\n".join(content_lines)
            confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

        return SynthesisBlock(
            block_type="established",
            title="ESTABLISHED FACTS",
            content=content,
            sources=sources,
            confidence=confidence,
            metadata={
                'claim_count': len(high_conf_claims),
                'avg_confidence': confidence,
                'threshold': 0.7
            }
        )

    def _generate_contested_block(self, analysis: Dict) -> SynthesisBlock:
        """Generate CONTESTED block - contradictory or disputed claims"""

        contradictions = analysis['contradictions']
        low_conf_claims = analysis['low_confidence_claims']

        content_lines = []
        sources = []
        confidence_scores = []

        # Include direct contradictions
        for contradiction in contradictions[:3]:
            content_lines.append(f"⚠️ CONTRADICTION: {contradiction.content[:150]}...")
            if contradiction.source_info:
                sources.append({
                    'title': contradiction.source_info.get('source1_title', 'Unknown'),
                    'confidence': contradiction.confidence,
                    'type': 'contradiction'
                })
            confidence_scores.append(contradiction.confidence)

        # Include low-confidence claims that might be disputed
        for claim in low_conf_claims[:3]:
            content_lines.append(f"❓ DISPUTED: {claim.content[:150]}... (Low confidence: {claim.confidence:.1%})")
            if claim.source_info.get('source_title'):
                sources.append({
                    'title': claim.source_info['source_title'],
                    'confidence': claim.confidence,
                    'type': 'low_confidence'
                })
            confidence_scores.append(claim.confidence)

        if not content_lines:
            content = "No significant contradictions or disputed claims identified in current evidence set."
            confidence = 1.0  # High confidence in the absence of disputes
        else:
            content = "\n".join(content_lines)
            confidence = 1.0 - (sum(confidence_scores) / len(confidence_scores)) if confidence_scores else 0.5

        return SynthesisBlock(
            block_type="contested",
            title="CONTESTED/DISPUTED",
            content=content,
            sources=sources,
            confidence=confidence,
            metadata={
                'contradiction_count': len(contradictions),
                'low_confidence_count': len(low_conf_claims),
                'dispute_indicators': len(content_lines)
            }
        )

    def _generate_why_block(self, analysis: Dict) -> SynthesisBlock:
        """Generate WHY block - analytical reasoning and context"""

        results = analysis['results']
        sources = analysis['sources']
        speakers = analysis['speakers']

        content_lines = []

        # Source diversity analysis
        source_count = len(sources)
        content_lines.append(f"📊 EVIDENCE BASE: {source_count} sources analyzed, {len(results)} total claims extracted.")

        # Source reliability analysis
        if sources:
            reliable_sources = [s for s in sources.values() if s['reliability_score'] >= 0.7]
            content_lines.append(f"📈 SOURCE RELIABILITY: {len(reliable_sources)}/{source_count} sources show high reliability (≥70% confidence).")

        # Speaker consistency analysis
        if speakers:
            consistent_speakers = [s for s in speakers.values() if s['consistency_score'] >= 0.6]
            content_lines.append(f"🎤 SPEAKER ANALYSIS: {len(consistent_speakers)}/{len(speakers)} speakers show consistent messaging.")

        # Temporal patterns
        time_sensitive_claims = [r for r in results if r.timecode is not None]
        if time_sensitive_claims:
            content_lines.append(f"⏱️ TEMPORAL COVERAGE: Claims span across {len(time_sensitive_claims)} timestamped segments.")

        # Entity coverage
        entity_count = len(analysis['entities'])
        if entity_count > 0:
            content_lines.append(f"🏷️ ENTITY COVERAGE: {entity_count} distinct entities identified in evidence.")

        # Confidence distribution
        high_conf = len(analysis['high_confidence_claims'])
        low_conf = len(analysis['low_confidence_claims'])
        content_lines.append(f"📊 CONFIDENCE DISTRIBUTION: {high_conf} high-confidence, {low_conf} low-confidence claims.")

        content = "\n".join(content_lines)

        # Calculate analytical confidence based on evidence quality
        analytical_confidence = min(1.0, (
            (source_count / 10.0) * 0.3 +  # Source diversity
            (len(reliable_sources) / source_count if sources else 0) * 0.4 +  # Source reliability
            (high_conf / len(results) if results else 0) * 0.3  # Claim confidence
        ))

        return SynthesisBlock(
            block_type="why",
            title="ANALYTICAL REASONING",
            content=content,
            sources=[],  # No specific sources for meta-analysis
            confidence=analytical_confidence,
            metadata={
                'source_count': source_count,
                'speaker_count': len(speakers),
                'entity_count': entity_count,
                'high_confidence_ratio': high_conf / len(results) if results else 0
            }
        )

    def _generate_flags_block(self, analysis: Dict) -> SynthesisBlock:
        """Generate FLAGS block - warnings and analytical concerns"""

        flags = []

        # Propaganda flags
        propaganda_count = len(analysis['propaganda_flags'])
        if propaganda_count > 0:
            flags.append(AnalysisFlag(
                flag_type=FlagType.PROPAGANDA,
                severity="high",
                description=f"Propaganda techniques detected in {propaganda_count} claims",
                evidence=[f.content[:100] for f in analysis['propaganda_flags'][:3]],
                confidence=0.8
            ))

        # Contradiction flags
        contradiction_count = len(analysis['contradictions'])
        if contradiction_count > 0:
            flags.append(AnalysisFlag(
                flag_type=FlagType.CONTRADICTION,
                severity="medium",
                description=f"Internal contradictions found between {contradiction_count} claim pairs",
                evidence=[f.content[:100] for f in analysis['contradictions'][:3]],
                confidence=0.7
            ))

        # Source reliability flags
        unreliable_sources = [s for s in analysis['sources'].values() if s['reliability_score'] < 0.4]
        if unreliable_sources:
            flags.append(AnalysisFlag(
                flag_type=FlagType.SOURCE_RELIABILITY,
                severity="medium",
                description=f"Low reliability detected in {len(unreliable_sources)} sources",
                evidence=[s['title'] for s in unreliable_sources[:3]],
                confidence=0.6
            ))

        # Insufficient evidence flags
        if len(analysis['results']) < 3:
            flags.append(AnalysisFlag(
                flag_type=FlagType.INSUFFICIENT_EVIDENCE,
                severity="high",
                description="Insufficient evidence for comprehensive analysis",
                evidence=[f"Only {len(analysis['results'])} claims available"],
                confidence=0.9
            ))

        # Generate content
        if not flags:
            content = "🟢 No significant analytical flags identified. Evidence appears consistent and reliable."
        else:
            content_lines = []
            for flag in flags:
                severity_emoji = {"low": "🟡", "medium": "🟠", "high": "🔴", "critical": "⚫"}
                emoji = severity_emoji.get(flag.severity, "⚪")
                content_lines.append(f"{emoji} {flag.flag_type.value.upper()}: {flag.description}")
                if flag.evidence:
                    content_lines.append(f"   Evidence: {', '.join(flag.evidence[:2])}...")
            content = "\n".join(content_lines)

        flag_confidence = 1.0 - (len(flags) * 0.2) if flags else 1.0

        return SynthesisBlock(
            block_type="flags",
            title="ANALYTICAL FLAGS",
            content=content,
            sources=[],
            confidence=max(0.0, flag_confidence),
            metadata={
                'flag_count': len(flags),
                'severity_breakdown': {
                    severity: len([f for f in flags if f.severity == severity])
                    for severity in ['low', 'medium', 'high', 'critical']
                }
            }
        )

    def _generate_next_steps_block(self, analysis: Dict) -> SynthesisBlock:
        """Generate NEXT STEPS block - recommended follow-up actions"""

        results = analysis['results']
        sources = analysis['sources']

        recommendations = []

        # Source expansion recommendations
        if len(sources) < 5:
            recommendations.append("🔍 EXPAND SOURCES: Gather additional sources to strengthen evidence base")

        # Temporal gap analysis
        time_claims = [r for r in results if r.timecode is not None]
        if time_claims and len(time_claims) < len(results) * 0.5:
            recommendations.append("⏱️ TEMPORAL VERIFICATION: Seek timestamped evidence for better temporal analysis")

        # Contradiction resolution
        if analysis['contradictions']:
            recommendations.append("⚖️ RESOLVE CONTRADICTIONS: Investigate and clarify conflicting claims")

        # Low confidence investigation
        low_conf_count = len(analysis['low_confidence_claims'])
        if low_conf_count > len(results) * 0.3:
            recommendations.append("🔬 VERIFY LOW-CONFIDENCE CLAIMS: Seek additional evidence for disputed statements")

        # Entity deep-dive
        if len(analysis['entities']) > 5:
            recommendations.append("🏷️ ENTITY ANALYSIS: Conduct focused analysis on key entities identified")

        # Cross-reference opportunities
        if len(sources) >= 3:
            recommendations.append("🔗 CROSS-REFERENCE: Compare claims across sources for consistency patterns")

        # Default recommendation if none identified
        if not recommendations:
            recommendations.append("✅ ANALYSIS COMPLETE: Current evidence set provides comprehensive coverage")

        content = "\n".join(recommendations)

        # Calculate actionability confidence
        actionability_confidence = min(1.0, len(recommendations) / 5.0)

        return SynthesisBlock(
            block_type="next_steps",
            title="RECOMMENDED NEXT STEPS",
            content=content,
            sources=[],
            confidence=actionability_confidence,
            metadata={
                'recommendation_count': len(recommendations),
                'priority_actions': recommendations[:3]
            }
        )

    def _calculate_overall_confidence(self, analysis: Dict) -> float:
        """Calculate overall confidence in the synthesis"""

        results = analysis['results']
        if not results:
            return 0.0

        # Factors affecting confidence
        source_diversity = min(1.0, len(analysis['sources']) / 5.0)  # 5+ sources = full confidence
        claim_confidence = sum(r.confidence for r in results) / len(results)
        contradiction_penalty = len(analysis['contradictions']) * 0.1
        propaganda_penalty = len(analysis['propaganda_flags']) * 0.1

        overall = (source_diversity * 0.3 + claim_confidence * 0.7) - contradiction_penalty - propaganda_penalty
        return max(0.0, min(1.0, overall))

    def _create_no_results_synthesis(self, query: SearchQuery, start_time: float) -> AnswerSynthesis:
        """Create synthesis for queries with no results"""

        processing_time = time.time() - start_time
        empty_block = SynthesisBlock(
            block_type="empty",
            title="NO RESULTS",
            content="No evidence found matching the query criteria.",
            sources=[],
            confidence=0.0,
            metadata={}
        )

        return AnswerSynthesis(
            query=query.query_text,
            query_type=query.query_type.value,
            generated_at=datetime.now().isoformat(),
            processing_time=processing_time,
            established=empty_block,
            contested=empty_block,
            why=empty_block,
            flags=empty_block,
            next_steps=SynthesisBlock(
                block_type="next_steps",
                title="RECOMMENDED NEXT STEPS",
                content="🔍 EXPAND SEARCH: Try broader search terms or alternative query types",
                sources=[],
                confidence=1.0,
                metadata={}
            ),
            total_sources=0,
            total_claims=0,
            overall_confidence=0.0,
            synthesis_notes="No results found for query"
        )

    def _create_error_synthesis(self, query: SearchQuery, error: str, start_time: float) -> AnswerSynthesis:
        """Create synthesis for error cases"""

        processing_time = time.time() - start_time
        error_block = SynthesisBlock(
            block_type="error",
            title="ERROR",
            content=f"Synthesis failed: {error}",
            sources=[],
            confidence=0.0,
            metadata={'error': error}
        )

        return AnswerSynthesis(
            query=query.query_text,
            query_type=query.query_type.value,
            generated_at=datetime.now().isoformat(),
            processing_time=processing_time,
            established=error_block,
            contested=error_block,
            why=error_block,
            flags=error_block,
            next_steps=error_block,
            total_sources=0,
            total_claims=0,
            overall_confidence=0.0,
            synthesis_notes=f"Error during synthesis: {error}"
        )

    def close(self):
        """Close database connections"""
        self.db.close()
        self.query_system.close()


def main():
    """CLI interface for answer synthesis"""
    if len(sys.argv) < 2:
        print("5-Block Answer Synthesis for Sherlock")
        print("Usage:")
        print("  python answer_synthesis.py synthesize '<query_text>' [query_type]")
        sys.exit(1)

    command = sys.argv[1].lower()
    synthesizer = AnswerSynthesizer()

    try:
        if command == "synthesize":
            query_text = sys.argv[2] if len(sys.argv) > 2 else ""
            query_type = QueryType(sys.argv[3]) if len(sys.argv) > 3 else QueryType.FULL_TEXT

            query = SearchQuery(
                query_text=query_text,
                query_type=query_type,
                filters={},
                date_range=None,
                speaker_filter=None,
                source_filter=None,
                entity_filter=None,
                limit=20,
                sort_by="relevance",
                include_context=True
            )

            synthesis = synthesizer.synthesize_answer(query)

            print(f"\n🧠 5-BLOCK ANSWER SYNTHESIS")
            print("=" * 60)
            print(f"Query: {synthesis.query}")
            print(f"Type: {synthesis.query_type}")
            print(f"Generated: {synthesis.generated_at}")
            print(f"Processing Time: {synthesis.processing_time:.2f}s")
            print(f"Overall Confidence: {synthesis.overall_confidence:.1%}")
            print("=" * 60)

            blocks = [
                synthesis.established,
                synthesis.contested,
                synthesis.why,
                synthesis.flags,
                synthesis.next_steps
            ]

            for block in blocks:
                print(f"\n📋 {block.title}")
                print(f"Confidence: {block.confidence:.1%}")
                print(f"{block.content}")
                if block.sources:
                    print(f"Sources: {len(block.sources)} referenced")

        else:
            print(f"❌ Unknown command: {command}")

    finally:
        synthesizer.close()


if __name__ == "__main__":
    main()