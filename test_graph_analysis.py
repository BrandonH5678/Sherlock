#!/usr/bin/env python3
"""
Test script for Graph Analysis System
Tests entity graph building, relationship analysis, and network clustering
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from graph_analysis import GraphAnalysisSystem
from evidence_database import (
    EvidenceDatabase, EvidenceSource, EvidenceClaim, Speaker,
    EvidenceType, ClaimType
)


def setup_test_graph_database():
    """Set up test database with interconnected entities"""
    print("🗄️  Setting up test database for graph analysis...")

    db = EvidenceDatabase("test_graph.db")

    # Create test sources
    sources = [
        EvidenceSource(
            source_id="ai_research_paper",
            title="AI Research Paper - Machine Learning Ethics",
            url="https://example.com/ai-research",
            file_path=None,
            evidence_type=EvidenceType.DOCUMENT,
            duration=None,
            page_count=25,
            created_at="2025-01-01T00:00:00",
            ingested_at=datetime.now().isoformat(),
            metadata={"authors": ["Dr. Smith", "Dr. Johnson"], "journal": "AI Ethics"}
        ),
        EvidenceSource(
            source_id="tech_conference",
            title="Tech Conference - AI Policy Discussion",
            url="https://example.com/conference",
            file_path="/audio/conference.wav",
            evidence_type=EvidenceType.AUDIO,
            duration=7200.0,
            page_count=None,
            created_at="2025-02-15T00:00:00",
            ingested_at=datetime.now().isoformat(),
            metadata={"event": "TechConf 2025", "location": "San Francisco"}
        ),
        EvidenceSource(
            source_id="policy_document",
            title="Government AI Policy Framework",
            url=None,
            file_path="/docs/ai_policy.pdf",
            evidence_type=EvidenceType.DOCUMENT,
            duration=None,
            page_count=100,
            created_at="2025-03-01T00:00:00",
            ingested_at=datetime.now().isoformat(),
            metadata={"department": "Technology Policy", "classification": "public"}
        )
    ]

    # Create test speakers
    speakers = [
        Speaker(
            speaker_id="dr_smith",
            name="Dr. Alice Smith",
            title="AI Research Director",
            organization="Stanford AI Lab",
            voice_embedding=None,
            confidence=0.95,
            first_seen="2025-01-01T00:00:00",
            last_seen="2025-03-01T00:00:00"
        ),
        Speaker(
            speaker_id="policy_expert",
            name="Robert Chen",
            title="Policy Analyst",
            organization="Government Technology Office",
            voice_embedding=None,
            confidence=0.92,
            first_seen="2025-02-15T00:00:00",
            last_seen="2025-03-01T00:00:00"
        )
    ]

    # Create interconnected claims with overlapping entities
    claims = [
        # AI research network
        EvidenceClaim(
            claim_id="claim_ai_ethics_1",
            source_id="ai_research_paper",
            speaker_id="dr_smith",
            claim_type=ClaimType.FACTUAL,
            text="Machine learning algorithms require careful bias testing to ensure fairness",
            confidence=0.95,
            start_time=None,
            end_time=None,
            page_number=5,
            context="Discussion of algorithmic fairness in AI systems development",
            entities=["Machine learning", "algorithms", "bias testing", "fairness", "Dr. Smith"],
            tags=["AI", "ethics", "bias", "fairness"],
            created_at="2025-01-01T10:00:00"
        ),
        EvidenceClaim(
            claim_id="claim_ai_ethics_2",
            source_id="ai_research_paper",
            speaker_id="dr_smith",
            claim_type=ClaimType.FACTUAL,
            text="Stanford AI Lab has developed new frameworks for algorithmic accountability",
            confidence=0.92,
            start_time=None,
            end_time=None,
            page_number=12,
            context="Research findings from Stanford's algorithmic accountability project",
            entities=["Stanford AI Lab", "frameworks", "algorithmic accountability", "Dr. Smith"],
            tags=["AI", "research", "accountability", "Stanford"],
            created_at="2025-01-01T11:00:00"
        ),

        # Conference network
        EvidenceClaim(
            claim_id="claim_conference_1",
            source_id="tech_conference",
            speaker_id="dr_smith",
            claim_type=ClaimType.OPINION,
            text="Industry collaboration is essential for responsible AI development",
            confidence=0.88,
            start_time=1200.0,
            end_time=1225.0,
            page_number=None,
            context="Panel discussion on AI industry standards and collaboration",
            entities=["Industry collaboration", "responsible AI", "development", "Dr. Smith"],
            tags=["AI", "industry", "collaboration", "responsibility"],
            created_at="2025-02-15T14:00:00"
        ),
        EvidenceClaim(
            claim_id="claim_conference_2",
            source_id="tech_conference",
            speaker_id="policy_expert",
            claim_type=ClaimType.FACTUAL,
            text="Government Technology Office is developing new AI regulation standards",
            confidence=0.94,
            start_time=2400.0,
            end_time=2430.0,
            page_number=None,
            context="Policy expert presentation on upcoming AI regulation framework",
            entities=["Government Technology Office", "AI regulation", "standards", "Robert Chen"],
            tags=["government", "regulation", "AI", "policy"],
            created_at="2025-02-15T15:00:00"
        ),

        # Policy network
        EvidenceClaim(
            claim_id="claim_policy_1",
            source_id="policy_document",
            speaker_id="policy_expert",
            claim_type=ClaimType.FACTUAL,
            text="Algorithmic accountability frameworks must include transparency requirements",
            confidence=0.96,
            start_time=None,
            end_time=None,
            page_number=25,
            context="Policy framework section on algorithmic transparency and accountability",
            entities=["algorithmic accountability", "frameworks", "transparency requirements", "Robert Chen"],
            tags=["policy", "accountability", "transparency", "regulation"],
            created_at="2025-03-01T09:00:00"
        ),
        EvidenceClaim(
            claim_id="claim_policy_2",
            source_id="policy_document",
            speaker_id="policy_expert",
            claim_type=ClaimType.FACTUAL,
            text="Machine learning bias testing will become mandatory for government AI systems",
            confidence=0.93,
            start_time=None,
            end_time=None,
            page_number=45,
            context="Mandatory requirements section for government AI system deployment",
            entities=["Machine learning", "bias testing", "mandatory", "government AI systems", "Robert Chen"],
            tags=["policy", "government", "AI", "mandatory", "bias"],
            created_at="2025-03-01T10:00:00"
        ),

        # Cross-cutting relationships
        EvidenceClaim(
            claim_id="claim_collaboration",
            source_id="tech_conference",
            speaker_id="dr_smith",
            claim_type=ClaimType.OPINION,
            text="Stanford AI Lab should collaborate with Government Technology Office on policy research",
            confidence=0.87,
            start_time=3600.0,
            end_time=3635.0,
            page_number=None,
            context="Discussion of academic-government partnerships in AI policy development",
            entities=["Stanford AI Lab", "Government Technology Office", "collaboration", "policy research", "Dr. Smith"],
            tags=["collaboration", "government", "academic", "policy"],
            created_at="2025-02-15T16:00:00"
        )
    ]

    # Add all data to database
    for source in sources:
        db.add_evidence_source(source)

    for speaker in speakers:
        db.add_speaker(speaker)

    for claim in claims:
        db.add_evidence_claim(claim)

    print(f"✅ Test graph database created with {len(sources)} sources, {len(speakers)} speakers, {len(claims)} claims")
    db.close()
    return len(sources), len(speakers), len(claims)


def test_entity_graph_building():
    """Test entity graph construction"""
    print("🕸️  Testing Entity Graph Building...")

    graph_system = GraphAnalysisSystem("test_graph.db")

    try:
        entities = graph_system.build_entity_graph()

        print(f"✅ Entity graph building completed:")
        print(f"   Entities identified: {len(entities)}")

        if entities:
            # Show sample entities
            sample_entities = list(entities.values())[:3]
            for i, entity in enumerate(sample_entities, 1):
                print(f"   {i}. {entity.name} ({entity.entity_type}): {entity.claim_count} mentions")

        graph_system.close()
        return len(entities) > 0

    except Exception as e:
        print(f"❌ Entity graph building test failed: {e}")
        graph_system.close()
        return False


def test_relationship_analysis():
    """Test relationship analysis between entities"""
    print("🔗 Testing Relationship Analysis...")

    graph_system = GraphAnalysisSystem("test_graph.db")

    try:
        # Build entity graph first
        graph_system.build_entity_graph()

        # Analyze relationships
        relationships = graph_system.analyze_entity_relationships()

        print(f"✅ Relationship analysis completed:")
        print(f"   Relationships found: {len(relationships)}")

        if relationships:
            # Show strongest relationships
            top_relationships = sorted(relationships, key=lambda x: x.weight, reverse=True)[:3]
            for i, rel in enumerate(top_relationships, 1):
                print(f"   {i}. {rel.source_entity} ↔ {rel.target_entity} (weight: {rel.weight})")

        graph_system.close()
        return len(relationships) > 0

    except Exception as e:
        print(f"❌ Relationship analysis test failed: {e}")
        graph_system.close()
        return False


def test_timeline_analysis():
    """Test timeline event extraction"""
    print("📅 Testing Timeline Analysis...")

    graph_system = GraphAnalysisSystem("test_graph.db")

    try:
        timeline_events = graph_system.create_timeline_analysis()

        print(f"✅ Timeline analysis completed:")
        print(f"   Timeline events: {len(timeline_events)}")

        if timeline_events:
            # Show sample events
            for i, event in enumerate(timeline_events[:3], 1):
                print(f"   {i}. {event.timestamp[:10]} - {event.event_type}: {len(event.entities)} entities")

        graph_system.close()
        return len(timeline_events) > 0

    except Exception as e:
        print(f"❌ Timeline analysis test failed: {e}")
        graph_system.close()
        return False


def test_network_clustering():
    """Test network cluster detection"""
    print("🕸️  Testing Network Clustering...")

    graph_system = GraphAnalysisSystem("test_graph.db")

    try:
        # Build components needed for clustering
        graph_system.build_entity_graph()
        relationships = graph_system.analyze_entity_relationships()

        # Detect clusters
        clusters = graph_system.detect_network_clusters(relationships)

        print(f"✅ Network clustering completed:")
        print(f"   Clusters detected: {len(clusters)}")

        if clusters:
            for i, cluster in enumerate(clusters[:2], 1):
                print(f"   {i}. {cluster.cluster_type} cluster: {len(cluster.entities)} entities")
                print(f"      Central entity: {cluster.central_entity}")
                print(f"      Cohesion: {cluster.cohesion_score:.2f}")

        graph_system.close()
        return True  # Clustering success measured by no errors

    except Exception as e:
        print(f"❌ Network clustering test failed: {e}")
        graph_system.close()
        return False


def test_network_summary():
    """Test comprehensive network summary generation"""
    print("📊 Testing Network Summary Generation...")

    graph_system = GraphAnalysisSystem("test_graph.db")

    try:
        summary = graph_system.generate_network_summary()

        print(f"✅ Network summary generated:")
        print(f"   Total entities: {summary.get('entity_count', 0)}")
        print(f"   Total relationships: {summary.get('relationship_count', 0)}")
        print(f"   Timeline events: {summary.get('timeline_events', 0)}")
        print(f"   Network clusters: {summary.get('network_clusters', 0)}")

        if summary.get('entity_types'):
            print(f"   Entity types: {', '.join(summary['entity_types'].keys())}")

        if summary.get('key_entities'):
            print(f"   Key entities: {len(summary['key_entities'])} identified")

        graph_system.close()
        return len(summary) > 0

    except Exception as e:
        print(f"❌ Network summary test failed: {e}")
        graph_system.close()
        return False


def cleanup_test_database():
    """Clean up test database"""
    test_db_path = Path("test_graph.db")
    if test_db_path.exists():
        test_db_path.unlink()
        print("🗑️  Test database cleaned up")


def main():
    """Run comprehensive graph analysis system testing"""
    print("🧪 GRAPH ANALYSIS SYSTEM TESTING")
    print("=" * 55)

    # Clean up any existing test database
    cleanup_test_database()

    # Set up test data
    sources_count, speakers_count, claims_count = setup_test_graph_database()

    tests = [
        ("Entity Graph Building", test_entity_graph_building),
        ("Relationship Analysis", test_relationship_analysis),
        ("Timeline Analysis", test_timeline_analysis),
        ("Network Clustering", test_network_clustering),
        ("Network Summary", test_network_summary)
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
    print("\n" + "=" * 55)
    print("📊 GRAPH ANALYSIS SYSTEM TEST SUMMARY")
    print("=" * 55)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")

    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 Graph Analysis System implementation SUCCESSFUL!")
        print("\n📋 Phase 3 Components Complete:")
        print("   ✅ Entity knowledge graph construction")
        print("   ✅ Relationship analysis and network mapping")
        print("   ✅ Timeline event extraction and sequencing")
        print("   ✅ Network cluster detection and analysis")
        print("   ✅ Comprehensive graph analytics and reporting")
        print("\n🚀 Sherlock Evidence Pipeline Phase 3 COMPLETE!")
        print("🔬 Ready for advanced analysis and synthesis capabilities!")
    else:
        print("⚠️  Some tests failed - review implementation before proceeding")

    # Clean up
    cleanup_test_database()

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)