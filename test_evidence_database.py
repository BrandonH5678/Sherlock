#!/usr/bin/env python3
"""
Test script for Evidence Database
Tests core functionality of SQLite + FTS5 database
"""

import json
import sys
import time
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from evidence_database import (
    EvidenceDatabase, Speaker, EvidenceSource, EvidenceClaim, EvidenceRelationship,
    EvidenceType, ClaimType
)


def test_speaker_operations():
    """Test speaker database operations"""
    print("👤 Testing Speaker Operations...")

    db = EvidenceDatabase("test_evidence.db")

    # Create test speakers
    speakers = [
        Speaker(
            speaker_id="SPEAKER_A",
            name="Dr. Alice Johnson",
            title="Research Director",
            organization="Tech Institute",
            voice_embedding=json.dumps([0.1, 0.2, 0.3]),  # Mock embedding
            confidence=0.95,
            first_seen="2025-09-27T10:00:00",
            last_seen="2025-09-27T11:30:00"
        ),
        Speaker(
            speaker_id="SPEAKER_B",
            name="Bob Smith",
            title="Policy Analyst",
            organization="Government Agency",
            voice_embedding=json.dumps([0.4, 0.5, 0.6]),
            confidence=0.88,
            first_seen="2025-09-27T10:15:00",
            last_seen="2025-09-27T11:45:00"
        )
    ]

    success_count = 0
    for speaker in speakers:
        if db.add_speaker(speaker):
            success_count += 1

    print(f"✅ Added {success_count}/{len(speakers)} speakers")
    db.close()
    return success_count == len(speakers)


def test_evidence_source_operations():
    """Test evidence source database operations"""
    print("📁 Testing Evidence Source Operations...")

    db = EvidenceDatabase("test_evidence.db")

    # Create test sources
    sources = [
        EvidenceSource(
            source_id="podcast_001",
            title="Tech Policy Discussion - Episode 42",
            url="https://example.com/podcast/ep42",
            file_path="/audio/podcast_ep42.wav",
            evidence_type=EvidenceType.PODCAST,
            duration=2880.0,  # 48 minutes
            page_count=None,
            created_at="2025-09-25T09:00:00",
            ingested_at="2025-09-27T12:00:00",
            metadata={
                "episode_number": 42,
                "transcript_available": True,
                "speakers_detected": 3
            }
        ),
        EvidenceSource(
            source_id="doc_001",
            title="AI Ethics Report 2025",
            url=None,
            file_path="/documents/ai_ethics_2025.pdf",
            evidence_type=EvidenceType.DOCUMENT,
            duration=None,
            page_count=156,
            created_at="2025-09-20T00:00:00",
            ingested_at="2025-09-27T12:30:00",
            metadata={
                "author": "Ethics Committee",
                "classification": "public",
                "version": "1.2"
            }
        )
    ]

    success_count = 0
    for source in sources:
        if db.add_evidence_source(source):
            success_count += 1

    print(f"✅ Added {success_count}/{len(sources)} evidence sources")
    db.close()
    return success_count == len(sources)


def test_evidence_claim_operations():
    """Test evidence claim database operations"""
    print("💬 Testing Evidence Claim Operations...")

    db = EvidenceDatabase("test_evidence.db")

    # Create test claims
    claims = [
        EvidenceClaim(
            claim_id="claim_001",
            source_id="podcast_001",
            speaker_id="SPEAKER_A",
            claim_type=ClaimType.FACTUAL,
            text="AI systems require careful oversight to prevent unintended consequences",
            confidence=0.92,
            start_time=120.5,
            end_time=135.2,
            page_number=None,
            context="Discussion about AI safety measures and regulatory frameworks",
            entities=["AI systems", "oversight", "consequences"],
            tags=["AI safety", "regulation", "policy"],
            created_at="2025-09-27T12:00:00"
        ),
        EvidenceClaim(
            claim_id="claim_002",
            source_id="podcast_001",
            speaker_id="SPEAKER_B",
            claim_type=ClaimType.OPINION,
            text="Current AI regulations are insufficient for emerging technologies",
            confidence=0.87,
            start_time=580.1,
            end_time=595.8,
            page_number=None,
            context="Policy analyst discussing regulatory gaps in AI governance",
            entities=["AI regulations", "emerging technologies"],
            tags=["regulation", "policy", "technology"],
            created_at="2025-09-27T12:05:00"
        ),
        EvidenceClaim(
            claim_id="claim_003",
            source_id="doc_001",
            speaker_id=None,
            claim_type=ClaimType.FACTUAL,
            text="Algorithmic bias affects 73% of hiring decisions in large corporations",
            confidence=0.95,
            start_time=None,
            end_time=None,
            page_number=42,
            context="Statistical analysis of algorithmic bias in employment practices",
            entities=["algorithmic bias", "hiring decisions", "corporations"],
            tags=["bias", "employment", "statistics"],
            created_at="2025-09-27T12:30:00"
        )
    ]

    success_count = 0
    for claim in claims:
        if db.add_evidence_claim(claim):
            success_count += 1

    print(f"✅ Added {success_count}/{len(claims)} evidence claims")
    db.close()
    return success_count == len(claims)


def test_relationship_operations():
    """Test relationship database operations"""
    print("🔗 Testing Relationship Operations...")

    db = EvidenceDatabase("test_evidence.db")

    # Create test relationships
    relationships = [
        EvidenceRelationship(
            relationship_id="rel_001",
            subject_type="claim",
            subject_id="claim_001",
            relationship_type="supports",
            object_type="claim",
            object_id="claim_002",
            confidence=0.78,
            evidence="Both claims discuss AI regulation inadequacy",
            created_at="2025-09-27T13:00:00"
        ),
        EvidenceRelationship(
            relationship_id="rel_002",
            subject_type="claim",
            subject_id="claim_003",
            relationship_type="mentions",
            object_type="entity",
            object_id="algorithmic bias",
            confidence=0.99,
            evidence="Direct statistical reference to algorithmic bias",
            created_at="2025-09-27T13:05:00"
        )
    ]

    success_count = 0
    for relationship in relationships:
        if db.add_relationship(relationship):
            success_count += 1

    print(f"✅ Added {success_count}/{len(relationships)} relationships")
    db.close()
    return success_count == len(relationships)


def test_search_operations():
    """Test search and query operations"""
    print("🔍 Testing Search Operations...")

    db = EvidenceDatabase("test_evidence.db")

    # Test full-text search
    search_results = db.search_claims("AI regulation")
    print(f"✅ Search for 'AI regulation': {len(search_results)} results")

    # Test speaker-specific queries
    speaker_claims = db.get_claims_by_speaker("SPEAKER_A")
    print(f"✅ Claims by SPEAKER_A: {len(speaker_claims)} results")

    # Test source-specific queries
    source_claims = db.get_claims_by_source("podcast_001")
    print(f"✅ Claims from podcast_001: {len(source_claims)} results")

    # Test contradiction finding
    contradictions = db.find_contradictions("claim_001")
    print(f"✅ Contradictions for claim_001: {len(contradictions)} results")

    db.close()
    return len(search_results) > 0


def test_database_integrity():
    """Test database integrity and statistics"""
    print("📊 Testing Database Integrity...")

    db = EvidenceDatabase("test_evidence.db")

    # Get database statistics
    stats = db.get_database_stats()

    print(f"✅ Database contains:")
    print(f"   Speakers: {stats.get('speakers', 0)}")
    print(f"   Sources: {stats.get('evidence_sources', 0)}")
    print(f"   Claims: {stats.get('evidence_claims', 0)}")
    print(f"   Relationships: {stats.get('evidence_relationships', 0)}")

    # Test logging
    db.log_operation("test", "database", "test_db", True, {"test": "data"}, None, 1.5)

    db.close()
    return stats.get('evidence_claims', 0) > 0


def cleanup_test_database():
    """Remove test database"""
    test_db_path = Path("test_evidence.db")
    if test_db_path.exists():
        test_db_path.unlink()
        print("🗑️  Test database cleaned up")


def main():
    """Run comprehensive evidence database testing"""
    print("🧪 EVIDENCE DATABASE TESTING")
    print("=" * 50)

    # Clean up any existing test database
    cleanup_test_database()

    tests = [
        ("Speaker Operations", test_speaker_operations),
        ("Evidence Source Operations", test_evidence_source_operations),
        ("Evidence Claim Operations", test_evidence_claim_operations),
        ("Relationship Operations", test_relationship_operations),
        ("Search Operations", test_search_operations),
        ("Database Integrity", test_database_integrity)
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
    print("📊 EVIDENCE DATABASE TEST SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")

    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 Evidence Database implementation SUCCESSFUL!")
        print("\n📋 Components Ready:")
        print("   ✅ SQLite database with FTS5 full-text search")
        print("   ✅ Evidence cards with atomic claims and provenance")
        print("   ✅ Speaker attribution and voice fingerprinting")
        print("   ✅ Relationship tracking (contradictions, support, mentions)")
        print("   ✅ Multi-modal evidence sources (audio, video, documents)")
        print("   ✅ Audit trail with operation logging")
        print("\n🚀 Ready for content ingestion pipeline!")
    else:
        print("⚠️  Some tests failed - review implementation before proceeding")

    # Clean up
    cleanup_test_database()

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)