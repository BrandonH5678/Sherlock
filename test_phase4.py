#!/usr/bin/env python3
"""
Comprehensive Phase 4 Testing Suite for Sherlock
Tests all Phase 4 components: synthesis, export, audit, and CLI
"""

import json
import os
import sqlite3
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from query_system import HybridQuerySystem, SearchQuery, QueryType
from answer_synthesis import AnswerSynthesizer, AnswerSynthesis
from export_system import ExportSystem, ExportFormat
from audit_system import AuditSystem, AuditEventType, AuditLevel
from sherlock_cli import SherlockCLI
from evidence_database import EvidenceDatabase, EvidenceType, ClaimType


class TestPhase4Components(unittest.TestCase):
    """Test suite for Phase 4 components"""

    def setUp(self):
        """Set up test environment"""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        self.temp_db.close()

        # Create temporary files for exports
        self.temp_dir = tempfile.mkdtemp()

        # Initialize test database with sample data
        self._setup_test_database()

    def tearDown(self):
        """Clean up test environment"""
        # Clean up temporary files
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

        # Clean up temp directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _setup_test_database(self):
        """Initialize test database with sample data"""

        db = EvidenceDatabase(self.db_path)

        # Add test sources
        from evidence_database import EvidenceSource
        test_source = EvidenceSource(
            source_id='test_source_1',
            title='Test Document: Government Surveillance',
            url='https://example.com/test',
            file_path=None,
            evidence_type=EvidenceType.DOCUMENT,
            duration=None,
            page_count=10,
            created_at='2024-01-01T00:00:00Z',
            ingested_at='2024-01-01T00:00:00Z',
            metadata={'test': True}
        )
        db.add_evidence_source(test_source)

        # Add test claims
        from evidence_database import EvidenceClaim
        test_claims = [
            EvidenceClaim(
                claim_id='claim_1',
                source_id='test_source_1',
                speaker_id=None,
                claim_type=ClaimType.FACTUAL,
                text='Government surveillance programs monitor citizens without warrants',
                confidence=0.85,
                start_time=None,
                end_time=None,
                page_number=1,
                context='Discussion of surveillance overreach',
                entities=['Government', 'Surveillance', 'Citizens'],
                tags=['privacy', 'surveillance'],
                created_at='2024-01-01T00:00:00Z'
            ),
            EvidenceClaim(
                claim_id='claim_2',
                source_id='test_source_1',
                speaker_id=None,
                claim_type=ClaimType.OPINION,
                text='These surveillance programs are necessary for national security',
                confidence=0.60,
                start_time=None,
                end_time=None,
                page_number=2,
                context='Counterargument presented',
                entities=['Surveillance', 'National Security'],
                tags=['security', 'surveillance'],
                created_at='2024-01-01T00:00:00Z'
            ),
            EvidenceClaim(
                claim_id='claim_3',
                source_id='test_source_1',
                speaker_id=None,
                claim_type=ClaimType.CONTRADICTION,
                text='No surveillance programs exist that monitor citizens',
                confidence=0.30,
                start_time=None,
                end_time=None,
                page_number=3,
                context='Denial of surveillance activities',
                entities=['Surveillance', 'Citizens'],
                tags=['denial', 'surveillance'],
                created_at='2024-01-01T00:00:00Z'
            )
        ]

        for claim in test_claims:
            db.add_evidence_claim(claim)

        db.close()

    def test_query_system_integration(self):
        """Test hybrid query system functionality"""

        query_system = HybridQuerySystem(self.db_path)

        # Test full-text search
        query = SearchQuery(
            query_text="surveillance",
            query_type=QueryType.FULL_TEXT,
            filters={},
            date_range=None,
            speaker_filter=None,
            source_filter=None,
            entity_filter=None,
            limit=10,
            sort_by="relevance",
            include_context=True
        )

        results = query_system.execute_query(query)

        self.assertGreater(len(results), 0, "Should find surveillance-related claims")
        self.assertTrue(any("surveillance" in r.content.lower() for r in results))

        # Test entity search
        entity_query = SearchQuery(
            query_text="Government",
            query_type=QueryType.ENTITY,
            filters={},
            date_range=None,
            speaker_filter=None,
            source_filter=None,
            entity_filter=None,
            limit=10,
            sort_by="relevance",
            include_context=True
        )

        entity_results = query_system.execute_query(entity_query)
        self.assertGreater(len(entity_results), 0, "Should find government-related claims")

        query_system.close()

    def test_answer_synthesis(self):
        """Test 5-block answer synthesis system"""

        synthesizer = AnswerSynthesizer(self.db_path)

        query = SearchQuery(
            query_text="government surveillance",
            query_type=QueryType.FULL_TEXT,
            filters={},
            date_range=None,
            speaker_filter=None,
            source_filter=None,
            entity_filter=None,
            limit=20,
            sort_by="relevance",
            include_context=True
        )

        # Generate synthesis
        synthesis = synthesizer.synthesize_answer(query)

        # Validate synthesis structure
        self.assertIsInstance(synthesis, AnswerSynthesis)
        self.assertEqual(synthesis.query, "government surveillance")
        self.assertGreater(synthesis.processing_time, 0)

        # Validate blocks
        self.assertIsNotNone(synthesis.established)
        self.assertIsNotNone(synthesis.contested)
        self.assertIsNotNone(synthesis.why)
        self.assertIsNotNone(synthesis.flags)
        self.assertIsNotNone(synthesis.next_steps)

        # Validate confidence scores
        self.assertGreaterEqual(synthesis.overall_confidence, 0.0)
        self.assertLessEqual(synthesis.overall_confidence, 1.0)

        # Validate metadata
        self.assertGreaterEqual(synthesis.total_sources, 0)
        self.assertGreaterEqual(synthesis.total_claims, 0)

        synthesizer.close()

    def test_export_system(self):
        """Test multi-format export capabilities"""

        export_system = ExportSystem(self.db_path)

        # First, generate a synthesis to export
        synthesizer = AnswerSynthesizer(self.db_path)
        query = SearchQuery(
            query_text="surveillance",
            query_type=QueryType.FULL_TEXT,
            filters={},
            date_range=None,
            speaker_filter=None,
            source_filter=None,
            entity_filter=None,
            limit=10,
            sort_by="relevance",
            include_context=True
        )

        synthesis = synthesizer.synthesize_answer(query)

        # Test Markdown export
        md_path = os.path.join(self.temp_dir, "test_synthesis.md")
        success = export_system.export_synthesis(synthesis, ExportFormat.MARKDOWN, md_path)
        self.assertTrue(success, "Markdown export should succeed")
        self.assertTrue(os.path.exists(md_path), "Markdown file should be created")

        with open(md_path, 'r') as f:
            md_content = f.read()
            self.assertIn("ESTABLISHED FACTS", md_content)
            self.assertIn("CONTESTED/DISPUTED", md_content)

        # Test JSON export
        json_path = os.path.join(self.temp_dir, "test_synthesis.json")
        success = export_system.export_synthesis(synthesis, ExportFormat.JSON, json_path)
        self.assertTrue(success, "JSON export should succeed")
        self.assertTrue(os.path.exists(json_path), "JSON file should be created")

        with open(json_path, 'r') as f:
            json_data = json.load(f)
            self.assertIn("query", json_data)
            self.assertIn("established", json_data)

        # Test Mermaid export
        mermaid_path = os.path.join(self.temp_dir, "test_synthesis.mmd")
        success = export_system.export_synthesis(synthesis, ExportFormat.MERMAID, mermaid_path)
        self.assertTrue(success, "Mermaid export should succeed")
        self.assertTrue(os.path.exists(mermaid_path), "Mermaid file should be created")

        with open(mermaid_path, 'r') as f:
            mermaid_content = f.read()
            self.assertIn("graph TD", mermaid_content)
            self.assertIn("ESTABLISHED", mermaid_content)

        # Test HTML export
        html_path = os.path.join(self.temp_dir, "test_synthesis.html")
        success = export_system.export_synthesis(synthesis, ExportFormat.HTML, html_path)
        self.assertTrue(success, "HTML export should succeed")
        self.assertTrue(os.path.exists(html_path), "HTML file should be created")

        with open(html_path, 'r') as f:
            html_content = f.read()
            self.assertIn("<html", html_content)
            self.assertIn("ESTABLISHED FACTS", html_content)

        export_system.close()
        synthesizer.close()

    def test_audit_system(self):
        """Test audit and reproducibility system"""

        audit_system = AuditSystem(self.db_path)

        # Test event logging
        event_id = audit_system.log_event(
            AuditEventType.QUERY_EXECUTED,
            AuditLevel.INFO,
            "test_component",
            "test_operation",
            input_data={"query": "test"},
            output_data={"results": 5},
            processing_time=1.5
        )

        self.assertIsNotNone(event_id)

        # Test audit trail retrieval
        events = audit_system.get_audit_trail(limit=10)
        self.assertGreater(len(events), 0, "Should have audit events")

        # Find our test event
        test_event = next((e for e in events if e['event_id'] == event_id), None)
        self.assertIsNotNone(test_event, "Should find the logged event")
        self.assertEqual(test_event['event_type'], 'query_executed')

        # Test reproducibility profile creation
        test_query = {"text": "test query", "type": "full_text"}
        test_result = {"confidence": 0.8, "claims": 3}
        test_steps = ["step1", "step2", "step3"]

        profile_id = audit_system.create_reproducibility_profile(
            test_query, test_result, test_steps
        )
        self.assertIsNotNone(profile_id)

        # Test reproducibility verification
        verification = audit_system.verify_reproducibility(
            profile_id, test_query, test_result
        )
        self.assertEqual(verification['status'], 'success')
        self.assertTrue(verification['reproducible'])

        # Test integrity check
        integrity_results = audit_system.run_integrity_check()
        self.assertIn('overall_status', integrity_results)
        self.assertIn('checks', integrity_results)

        # Test audit data export
        audit_export_path = os.path.join(self.temp_dir, "audit_export.json")
        success = audit_system.export_audit_data(audit_export_path)
        self.assertTrue(success, "Audit export should succeed")
        self.assertTrue(os.path.exists(audit_export_path), "Audit export file should be created")

        audit_system.close()

    def test_cli_integration(self):
        """Test CLI interface integration"""

        cli = SherlockCLI(self.db_path, verbose=False)

        # Test search command
        search_result = cli.execute_search(
            query_text="surveillance",
            query_type="full_text",
            limit=5
        )

        self.assertEqual(search_result['status'], 'success')
        self.assertIn('results', search_result)
        self.assertIn('metadata', search_result)

        # Test synthesis command
        synthesis_result = cli.execute_synthesis(
            query_text="government surveillance",
            query_type="full_text"
        )

        self.assertEqual(synthesis_result['status'], 'success')
        self.assertIn('synthesis', synthesis_result)
        self.assertIn('profile_id', synthesis_result)

        # Test status command
        status_result = cli.show_database_status()
        self.assertEqual(status_result['status'], 'success')
        self.assertIn('data', status_result)

        # Test audit trail
        audit_result = cli.show_audit_trail(limit=10)
        self.assertEqual(audit_result['status'], 'success')
        self.assertIn('events', audit_result)

        # Test export
        export_path = os.path.join(self.temp_dir, "cli_export.json")
        export_result = cli.export_data("audit", export_path)
        self.assertEqual(export_result['status'], 'success')
        self.assertTrue(os.path.exists(export_path))

        cli.close()

    def test_error_handling(self):
        """Test error handling across components"""

        # Test invalid query type
        query_system = HybridQuerySystem(self.db_path)

        with self.assertRaises(ValueError):
            # This should raise a ValueError when creating the enum
            invalid_type = QueryType("invalid_type")

        # Test invalid export format
        export_system = ExportSystem(self.db_path)
        with self.assertRaises(ValueError):
            invalid_format = ExportFormat("invalid_format")

        # Test audit system with invalid data
        audit_system = AuditSystem(self.db_path)

        # This should still work but handle the error gracefully
        event_id = audit_system.log_event(
            AuditEventType.ERROR_OCCURRED,
            AuditLevel.ERROR,
            "test_component",
            "test_error",
            error_message="Test error message"
        )
        self.assertIsNotNone(event_id)

        query_system.close()
        export_system.close()
        audit_system.close()

    def test_performance_benchmarks(self):
        """Test performance benchmarks for Phase 4 components"""

        # Test query performance
        query_system = HybridQuerySystem(self.db_path)

        start_time = time.time()
        query = SearchQuery(
            query_text="surveillance",
            query_type=QueryType.FULL_TEXT,
            filters={},
            date_range=None,
            speaker_filter=None,
            source_filter=None,
            entity_filter=None,
            limit=10,
            sort_by="relevance",
            include_context=True
        )
        results = query_system.execute_query(query)
        query_time = time.time() - start_time

        # Should complete in under 5 seconds for small test database
        self.assertLess(query_time, 5.0, "Query should complete quickly")

        # Test synthesis performance
        synthesizer = AnswerSynthesizer(self.db_path)

        start_time = time.time()
        synthesis = synthesizer.synthesize_answer(query)
        synthesis_time = time.time() - start_time

        # Should complete in under 10 seconds for small test database
        self.assertLess(synthesis_time, 10.0, "Synthesis should complete quickly")

        # Test export performance
        export_system = ExportSystem(self.db_path)

        start_time = time.time()
        export_path = os.path.join(self.temp_dir, "perf_test.json")
        success = export_system.export_synthesis(synthesis, ExportFormat.JSON, export_path)
        export_time = time.time() - start_time

        self.assertTrue(success)
        self.assertLess(export_time, 2.0, "Export should complete quickly")

        query_system.close()
        synthesizer.close()
        export_system.close()

    def test_data_integrity(self):
        """Test data integrity across components"""

        # Test that synthesis results are consistent
        synthesizer = AnswerSynthesizer(self.db_path)

        query = SearchQuery(
            query_text="surveillance",
            query_type=QueryType.FULL_TEXT,
            filters={},
            date_range=None,
            speaker_filter=None,
            source_filter=None,
            entity_filter=None,
            limit=10,
            sort_by="relevance",
            include_context=True
        )

        # Generate synthesis twice
        synthesis1 = synthesizer.synthesize_answer(query)
        synthesis2 = synthesizer.synthesize_answer(query)

        # Should have same query
        self.assertEqual(synthesis1.query, synthesis2.query)

        # Should have consistent source counts (assuming no database changes)
        self.assertEqual(synthesis1.total_sources, synthesis2.total_sources)
        self.assertEqual(synthesis1.total_claims, synthesis2.total_claims)

        # Test audit consistency
        audit_system = AuditSystem(self.db_path)

        # Log identical events
        event1_id = audit_system.log_event(
            AuditEventType.QUERY_EXECUTED,
            AuditLevel.INFO,
            "test",
            "consistency_test",
            input_data={"test": "data"},
            processing_time=1.0
        )

        event2_id = audit_system.log_event(
            AuditEventType.QUERY_EXECUTED,
            AuditLevel.INFO,
            "test",
            "consistency_test",
            input_data={"test": "data"},
            processing_time=1.0
        )

        # Should have different IDs but same content structure
        self.assertNotEqual(event1_id, event2_id)

        events = audit_system.get_audit_trail(limit=5)
        test_events = [e for e in events if e['operation'] == 'consistency_test']
        self.assertEqual(len(test_events), 2)

        synthesizer.close()
        audit_system.close()


def run_phase4_tests():
    """Run comprehensive Phase 4 test suite"""

    print("🧪 Starting Sherlock Phase 4 Test Suite")
    print("=" * 50)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhase4Components)

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")

    if result.errors:
        print("\n🔥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")

    # Overall result
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED - Phase 4 is ready for production!")
        return True
    else:
        print("\n❌ SOME TESTS FAILED - Phase 4 needs attention")
        return False


if __name__ == "__main__":
    success = run_phase4_tests()
    sys.exit(0 if success else 1)