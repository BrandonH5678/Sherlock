#!/usr/bin/env python3
"""
Test script for Analysis Engine
Tests contradiction detection, propaganda flagging, and bias analysis
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from analysis_engine import AnalysisEngine
from evidence_database import (
    EvidenceDatabase, EvidenceSource, EvidenceClaim, Speaker,
    EvidenceType, ClaimType
)


def setup_test_database():
    """Set up test database with sample data"""
    print("🗄️  Setting up test database with sample evidence...")

    db = EvidenceDatabase("test_analysis.db")

    # Create test sources
    sources = [
        EvidenceSource(
            source_id="source_study_a",
            title="Medical Study A - Drug Effectiveness",
            url="https://example.com/study-a",
            file_path=None,
            evidence_type=EvidenceType.DOCUMENT,
            duration=None,
            page_count=50,
            created_at="2025-01-15T00:00:00",
            ingested_at=datetime.now().isoformat(),
            metadata={"study_type": "clinical_trial", "participants": 1000}
        ),
        EvidenceSource(
            source_id="source_study_b",
            title="Medical Study B - Drug Safety Analysis",
            url="https://example.com/study-b",
            file_path=None,
            evidence_type=EvidenceType.DOCUMENT,
            duration=None,
            page_count=75,
            created_at="2025-02-20T00:00:00",
            ingested_at=datetime.now().isoformat(),
            metadata={"study_type": "safety_analysis", "participants": 500}
        ),
        EvidenceSource(
            source_id="source_podcast",
            title="Political Discussion Podcast",
            url="https://example.com/podcast",
            file_path="/audio/political_podcast.wav",
            evidence_type=EvidenceType.PODCAST,
            duration=3600.0,
            page_count=None,
            created_at="2025-03-01T00:00:00",
            ingested_at=datetime.now().isoformat(),
            metadata={"episode": 42, "host": "Political Commentator"}
        )
    ]

    # Create test speakers
    speakers = [
        Speaker(
            speaker_id="dr_smith",
            name="Dr. Sarah Smith",
            title="Chief Researcher",
            organization="Medical Institute",
            voice_embedding=None,
            confidence=0.95,
            first_seen="2025-03-01T10:00:00",
            last_seen="2025-03-01T11:00:00"
        ),
        Speaker(
            speaker_id="commentator_jones",
            name="Mike Jones",
            title="Political Commentator",
            organization="News Network",
            voice_embedding=None,
            confidence=0.88,
            first_seen="2025-03-01T15:00:00",
            last_seen="2025-03-01T16:00:00"
        )
    ]

    # Create contradictory claims for testing
    claims = [
        # Contradictory medical claims
        EvidenceClaim(
            claim_id="claim_drug_effective",
            source_id="source_study_a",
            speaker_id="dr_smith",
            claim_type=ClaimType.FACTUAL,
            text="Drug X is effective in treating condition Y with 85% success rate",
            confidence=0.92,
            start_time=None,
            end_time=None,
            page_number=15,
            context="Clinical trial results showing significant improvement in patient outcomes",
            entities=["Drug X", "condition Y", "clinical trial"],
            tags=["medicine", "treatment", "effectiveness"],
            created_at=datetime.now().isoformat()
        ),
        EvidenceClaim(
            claim_id="claim_drug_ineffective",
            source_id="source_study_b",
            speaker_id="dr_smith",
            claim_type=ClaimType.FACTUAL,
            text="Drug X is ineffective for condition Y showing only 15% improvement",
            confidence=0.89,
            start_time=None,
            end_time=None,
            page_number=23,
            context="Safety analysis revealing limited therapeutic benefit and potential side effects",
            entities=["Drug X", "condition Y", "safety analysis"],
            tags=["medicine", "treatment", "safety"],
            created_at=datetime.now().isoformat()
        ),

        # Propaganda-style claims
        EvidenceClaim(
            claim_id="claim_fear_appeal",
            source_id="source_podcast",
            speaker_id="commentator_jones",
            claim_type=ClaimType.OPINION,
            text="This crisis threatens our entire way of life and we must act now or face disaster",
            confidence=0.75,
            start_time=1200.0,
            end_time=1215.0,
            page_number=None,
            context="Discussion about policy changes with emotional language and urgency",
            entities=["crisis", "way of life", "disaster"],
            tags=["politics", "policy", "emotional"],
            created_at=datetime.now().isoformat()
        ),
        EvidenceClaim(
            claim_id="claim_false_dichotomy",
            source_id="source_podcast",
            speaker_id="commentator_jones",
            claim_type=ClaimType.OPINION,
            text="We must choose between complete freedom or total government control - there are only two options",
            confidence=0.78,
            start_time=1800.0,
            end_time=1820.0,
            page_number=None,
            context="Political debate presenting oversimplified choices to listeners",
            entities=["freedom", "government control", "options"],
            tags=["politics", "freedom", "government"],
            created_at=datetime.now().isoformat()
        ),

        # Numeric contradiction
        EvidenceClaim(
            claim_id="claim_stats_high",
            source_id="source_study_a",
            speaker_id="dr_smith",
            claim_type=ClaimType.FACTUAL,
            text="Patient satisfaction increased by 73% after treatment implementation",
            confidence=0.94,
            start_time=None,
            end_time=None,
            page_number=42,
            context="Patient survey results showing significant satisfaction improvements",
            entities=["patient satisfaction", "treatment"],
            tags=["medicine", "satisfaction", "statistics"],
            created_at=datetime.now().isoformat()
        ),
        EvidenceClaim(
            claim_id="claim_stats_low",
            source_id="source_study_b",
            speaker_id="dr_smith",
            claim_type=ClaimType.FACTUAL,
            text="Patient satisfaction increased by only 12% following treatment protocol",
            confidence=0.91,
            start_time=None,
            end_time=None,
            page_number=38,
            context="Independent assessment revealing modest satisfaction gains",
            entities=["patient satisfaction", "treatment protocol"],
            tags=["medicine", "satisfaction", "statistics"],
            created_at=datetime.now().isoformat()
        )
    ]

    # Add all data to database
    for source in sources:
        db.add_evidence_source(source)

    for speaker in speakers:
        db.add_speaker(speaker)

    for claim in claims:
        db.add_evidence_claim(claim)

    print(f"✅ Test database created with {len(sources)} sources, {len(speakers)} speakers, {len(claims)} claims")
    db.close()
    return len(sources), len(speakers), len(claims)


def test_contradiction_detection():
    """Test contradiction detection engine"""
    print("🔍 Testing Contradiction Detection...")

    engine = AnalysisEngine("test_analysis.db")

    try:
        contradictions = engine.analyze_contradictions()

        print(f"✅ Contradiction detection completed:")
        print(f"   Contradictions found: {len(contradictions)}")

        if contradictions:
            for i, contradiction in enumerate(contradictions[:3], 1):
                print(f"   {i}. {contradiction.contradiction_type} ({contradiction.confidence:.1%})")
                print(f"      Claim 1: {contradiction.claim_1_text[:60]}...")
                print(f"      Claim 2: {contradiction.claim_2_text[:60]}...")

        engine.close()
        return len(contradictions) > 0

    except Exception as e:
        print(f"❌ Contradiction detection test failed: {e}")
        engine.close()
        return False


def test_propaganda_detection():
    """Test propaganda detection engine"""
    print("🎭 Testing Propaganda Detection...")

    engine = AnalysisEngine("test_analysis.db")

    try:
        propaganda_flags = engine.analyze_propaganda()

        print(f"✅ Propaganda detection completed:")
        print(f"   Propaganda flags: {len(propaganda_flags)}")

        if propaganda_flags:
            for i, flag in enumerate(propaganda_flags[:3], 1):
                print(f"   {i}. {flag.propaganda_type} ({flag.confidence:.1%})")
                print(f"      Techniques: {', '.join(flag.techniques)}")

        engine.close()
        return len(propaganda_flags) > 0

    except Exception as e:
        print(f"❌ Propaganda detection test failed: {e}")
        engine.close()
        return False


def test_bias_analysis():
    """Test bias analysis engine"""
    print("⚖️  Testing Bias Analysis...")

    engine = AnalysisEngine("test_analysis.db")

    try:
        bias_analysis = engine.analyze_bias_patterns()

        print(f"✅ Bias analysis completed:")
        print(f"   Sources analyzed: {len(bias_analysis.get('source_bias', {}))}")
        print(f"   Speakers analyzed: {len(bias_analysis.get('speaker_bias', {}))}")

        if bias_analysis.get('source_bias'):
            print("   Top biased sources:")
            for source_id, data in list(bias_analysis['source_bias'].items())[:2]:
                print(f"      {data['title']}: {data['bias_score']:.1f}% bias")

        engine.close()
        # Bias analysis is successful if it runs without error and analyzes speakers
        return len(bias_analysis.get('speaker_bias', {})) > 0

    except Exception as e:
        print(f"❌ Bias analysis test failed: {e}")
        engine.close()
        return False


def test_analysis_summary():
    """Test analysis summary functionality"""
    print("📊 Testing Analysis Summary...")

    engine = AnalysisEngine("test_analysis.db")

    try:
        summary = engine.get_analysis_summary()

        print(f"✅ Analysis summary generated:")
        print(f"   Total contradictions: {summary.get('contradictions', 0)}")
        print(f"   Total propaganda flags: {summary.get('propaganda_flags', 0)}")
        print(f"   Total relationships: {summary.get('total_relationships', 0)}")
        print(f"   Analysis coverage: {summary.get('analysis_coverage', 0):.1%}")

        engine.close()
        return isinstance(summary, dict) and len(summary) > 0

    except Exception as e:
        print(f"❌ Analysis summary test failed: {e}")
        engine.close()
        return False


def cleanup_test_database():
    """Clean up test database"""
    test_db_path = Path("test_analysis.db")
    if test_db_path.exists():
        test_db_path.unlink()
        print("🗑️  Test database cleaned up")


def main():
    """Run comprehensive analysis engine testing"""
    print("🧪 ANALYSIS ENGINE TESTING")
    print("=" * 50)

    # Clean up any existing test database
    cleanup_test_database()

    # Set up test data
    sources_count, speakers_count, claims_count = setup_test_database()

    tests = [
        ("Contradiction Detection", test_contradiction_detection),
        ("Propaganda Detection", test_propaganda_detection),
        ("Bias Analysis", test_bias_analysis),
        ("Analysis Summary", test_analysis_summary)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
        except Exception as e:
            results.append((test_name, False))
            print(f"❌ FAILED: {test_name} - {e}")

    # Summary
    print("\n" + "=" * 50)
    print("📊 ANALYSIS ENGINE TEST SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")

    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 Analysis Engine implementation SUCCESSFUL!")
        print("\n📋 Components Ready:")
        print("   ✅ Contradiction detection with pattern matching")
        print("   ✅ Propaganda technique identification")
        print("   ✅ Bias analysis across sources and speakers")
        print("   ✅ Relationship tracking and database integration")
        print("   ✅ Comprehensive analysis reporting")
        print("\n🚀 Ready for graph and relationship analysis system!")
    else:
        print("⚠️  Some tests failed - review implementation before proceeding")

    # Clean up
    cleanup_test_database()

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)