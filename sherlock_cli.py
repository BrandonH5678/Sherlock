#!/usr/bin/env python3
"""
Enhanced CLI Interface for Sherlock Phase 4
Unified command-line interface integrating all Phase 4 capabilities
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from query_system import HybridQuerySystem, SearchQuery, QueryType
from answer_synthesis import AnswerSynthesizer
from export_system import ExportSystem, ExportFormat
from audit_system import AuditSystem, AuditEventType, AuditLevel
from evidence_database import EvidenceDatabase


class SherlockCLI:
    """Enhanced CLI for Sherlock Phase 4 capabilities"""

    def __init__(self, db_path: str = "evidence.db", verbose: bool = False):
        self.db_path = db_path
        self.verbose = verbose

        # Initialize systems
        self.audit_system = AuditSystem(db_path)
        self.query_system = HybridQuerySystem(db_path)
        self.synthesizer = AnswerSynthesizer(db_path)
        self.export_system = ExportSystem(db_path)
        self.db = EvidenceDatabase(db_path)

        # Log CLI startup
        self.audit_system.log_event(
            AuditEventType.SYSTEM_STARTED,
            AuditLevel.INFO,
            "sherlock_cli",
            "initialize",
            metadata={'verbose': verbose, 'database': db_path}
        )

    def execute_search(self, query_text: str, query_type: str = "full_text",
                      limit: int = 10, sort_by: str = "relevance",
                      output_format: str = None, output_path: str = None) -> Dict:
        """Execute search query with optional export"""

        start_time = time.time()

        try:
            # Parse query type
            try:
                qt = QueryType(query_type.lower())
            except ValueError:
                available_types = [t.value for t in QueryType]
                raise ValueError(f"Invalid query type '{query_type}'. Available: {', '.join(available_types)}")

            # Create search query
            query = SearchQuery(
                query_text=query_text,
                query_type=qt,
                filters={},
                date_range=None,
                speaker_filter=None,
                source_filter=None,
                entity_filter=None,
                limit=limit,
                sort_by=sort_by,
                include_context=True
            )

            if self.verbose:
                print(f"🔍 Executing {query_type} search: '{query_text}'")

            # Execute query
            results = self.query_system.execute_query(query)
            processing_time = time.time() - start_time

            # Log query execution
            self.audit_system.log_event(
                AuditEventType.QUERY_EXECUTED,
                AuditLevel.INFO,
                "sherlock_cli",
                "execute_search",
                input_data={
                    'query_text': query_text,
                    'query_type': query_type,
                    'limit': limit,
                    'sort_by': sort_by
                },
                output_data={
                    'result_count': len(results),
                    'processing_time': processing_time
                },
                processing_time=processing_time
            )

            # Export if requested
            if output_format and output_path:
                try:
                    export_format = ExportFormat(output_format.lower())
                    success = self.export_system.export_query_results(results, query, export_format, output_path)
                    if success and self.verbose:
                        print(f"📄 Results exported to: {output_path}")
                except ValueError:
                    print(f"❌ Invalid export format: {output_format}")

            return {
                'status': 'success',
                'results': results,
                'metadata': {
                    'result_count': len(results),
                    'processing_time': processing_time,
                    'query_type': query_type
                }
            }

        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = str(e)

            # Log error
            self.audit_system.log_event(
                AuditEventType.ERROR_OCCURRED,
                AuditLevel.ERROR,
                "sherlock_cli",
                "execute_search",
                input_data={'query_text': query_text},
                processing_time=processing_time,
                error_message=error_msg
            )

            return {
                'status': 'error',
                'error': error_msg,
                'metadata': {
                    'processing_time': processing_time
                }
            }

    def execute_synthesis(self, query_text: str, query_type: str = "full_text",
                         output_format: str = None, output_path: str = None) -> Dict:
        """Execute 5-block answer synthesis"""

        start_time = time.time()

        try:
            # Parse query type
            try:
                qt = QueryType(query_type.lower())
            except ValueError:
                available_types = [t.value for t in QueryType]
                raise ValueError(f"Invalid query type '{query_type}'. Available: {', '.join(available_types)}")

            # Create search query
            query = SearchQuery(
                query_text=query_text,
                query_type=qt,
                filters={},
                date_range=None,
                speaker_filter=None,
                source_filter=None,
                entity_filter=None,
                limit=20,  # More results for better synthesis
                sort_by="relevance",
                include_context=True
            )

            if self.verbose:
                print(f"🧠 Generating synthesis for: '{query_text}'")

            # Generate synthesis
            synthesis = self.synthesizer.synthesize_answer(query)
            processing_time = time.time() - start_time

            # Create reproducibility profile
            profile_id = self.audit_system.create_reproducibility_profile(
                query={'text': query_text, 'type': query_type},
                result={'synthesis_id': synthesis.generated_at, 'confidence': synthesis.overall_confidence},
                processing_steps=['query_execution', '5_block_synthesis', 'confidence_calculation']
            )

            # Log synthesis generation
            self.audit_system.log_event(
                AuditEventType.SYNTHESIS_GENERATED,
                AuditLevel.INFO,
                "sherlock_cli",
                "execute_synthesis",
                input_data={
                    'query_text': query_text,
                    'query_type': query_type
                },
                output_data={
                    'overall_confidence': synthesis.overall_confidence,
                    'total_sources': synthesis.total_sources,
                    'total_claims': synthesis.total_claims,
                    'profile_id': profile_id
                },
                processing_time=processing_time
            )

            # Export if requested
            if output_format and output_path:
                try:
                    export_format = ExportFormat(output_format.lower())
                    success = self.export_system.export_synthesis(synthesis, export_format, output_path)
                    if success and self.verbose:
                        print(f"📄 Synthesis exported to: {output_path}")
                except ValueError:
                    print(f"❌ Invalid export format: {output_format}")

            return {
                'status': 'success',
                'synthesis': synthesis,
                'profile_id': profile_id,
                'metadata': {
                    'processing_time': processing_time,
                    'overall_confidence': synthesis.overall_confidence
                }
            }

        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = str(e)

            # Log error
            self.audit_system.log_event(
                AuditEventType.ERROR_OCCURRED,
                AuditLevel.ERROR,
                "sherlock_cli",
                "execute_synthesis",
                input_data={'query_text': query_text},
                processing_time=processing_time,
                error_message=error_msg
            )

            return {
                'status': 'error',
                'error': error_msg,
                'metadata': {
                    'processing_time': processing_time
                }
            }

    def show_database_status(self) -> Dict:
        """Show database and system status"""

        try:
            # Get database statistics
            cursor = self.db.connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            stats = {}
            for table in tables:
                if not table.startswith('sqlite_'):
                    cursor = self.db.connection.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    stats[table] = count

            # Get recent audit events
            recent_events = self.audit_system.get_audit_trail(limit=5)

            # Run integrity check
            integrity = self.audit_system.run_integrity_check()

            status = {
                'database_path': self.db_path,
                'table_statistics': stats,
                'recent_activity': len(recent_events),
                'integrity_status': integrity['overall_status'],
                'system_operational': True
            }

            # Log status check
            self.audit_system.log_event(
                AuditEventType.SYSTEM_STARTED,
                AuditLevel.INFO,
                "sherlock_cli",
                "show_database_status",
                output_data=status
            )

            return {'status': 'success', 'data': status}

        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def show_audit_trail(self, limit: int = 20, session_id: str = None) -> Dict:
        """Show audit trail"""

        try:
            events = self.audit_system.get_audit_trail(
                session_id=session_id,
                limit=limit
            )

            return {
                'status': 'success',
                'events': events,
                'metadata': {
                    'event_count': len(events),
                    'session_filter': session_id
                }
            }

        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def export_data(self, data_type: str, output_path: str, format_type: str = "json") -> Dict:
        """Export various types of data"""

        try:
            if data_type == "audit":
                success = self.audit_system.export_audit_data(output_path, format_type)
            else:
                raise ValueError(f"Unknown data type: {data_type}")

            if success:
                return {
                    'status': 'success',
                    'message': f"Data exported to {output_path}",
                    'output_path': output_path
                }
            else:
                return {
                    'status': 'error',
                    'error': 'Export failed'
                }

        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def close(self):
        """Close all systems"""
        self.audit_system.log_event(
            AuditEventType.SYSTEM_STOPPED,
            AuditLevel.INFO,
            "sherlock_cli",
            "shutdown"
        )

        self.audit_system.close()
        self.query_system.close()
        self.synthesizer.close()
        self.export_system.close()
        self.db.close()


def create_parser():
    """Create command-line argument parser"""

    parser = argparse.ArgumentParser(
        description="Sherlock Evidence Analysis System - Phase 4 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic search
  python sherlock_cli.py search "government surveillance"

  # Advanced search with export
  python sherlock_cli.py search "propaganda techniques" --type semantic --limit 20 --export markdown results.md

  # Generate synthesis
  python sherlock_cli.py synthesize "NSA activities" --export html analysis.html

  # Show system status
  python sherlock_cli.py status

  # Export audit trail
  python sherlock_cli.py export audit audit_trail.json

  # View recent activity
  python sherlock_cli.py audit --limit 50
        """)

    parser.add_argument('--database', '-d', default='evidence.db',
                       help='Path to evidence database (default: evidence.db)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Search command
    search_parser = subparsers.add_parser('search', help='Execute search query')
    search_parser.add_argument('query', help='Search query text')
    search_parser.add_argument('--type', '-t', default='full_text',
                              choices=[t.value for t in QueryType],
                              help='Query type (default: full_text)')
    search_parser.add_argument('--limit', '-l', type=int, default=10,
                              help='Maximum results (default: 10)')
    search_parser.add_argument('--sort', '-s', default='relevance',
                              choices=['relevance', 'confidence', 'date'],
                              help='Sort results by (default: relevance)')
    search_parser.add_argument('--export', '-e',
                              help='Export format (markdown, json, csv, html)')
    search_parser.add_argument('--output', '-o',
                              help='Output file path for export')

    # Synthesis command
    synth_parser = subparsers.add_parser('synthesize', help='Generate 5-block analysis')
    synth_parser.add_argument('query', help='Analysis query text')
    synth_parser.add_argument('--type', '-t', default='full_text',
                             choices=[t.value for t in QueryType],
                             help='Query type (default: full_text)')
    synth_parser.add_argument('--export', '-e',
                             help='Export format (markdown, json, mermaid, html)')
    synth_parser.add_argument('--output', '-o',
                             help='Output file path for export')

    # Status command
    subparsers.add_parser('status', help='Show system status')

    # Audit command
    audit_parser = subparsers.add_parser('audit', help='Show audit trail')
    audit_parser.add_argument('--limit', '-l', type=int, default=20,
                             help='Number of events to show (default: 20)')
    audit_parser.add_argument('--session', '-s',
                             help='Filter by session ID')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export system data')
    export_parser.add_argument('data_type', choices=['audit'],
                              help='Type of data to export')
    export_parser.add_argument('output_path', help='Output file path')
    export_parser.add_argument('--format', '-f', default='json',
                              help='Export format (default: json)')

    return parser


def format_search_results(results: List, metadata: Dict):
    """Format search results for display"""

    print(f"\n🔍 SEARCH RESULTS ({metadata['result_count']} found)")
    print(f"Processing time: {metadata['processing_time']:.2f}s")
    print("=" * 60)

    if not results:
        print("No results found.")
        return

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.title}")
        print(f"   Type: {result.result_type.upper()} | Confidence: {result.confidence:.1%} | Relevance: {result.relevance_score:.1%}")
        print(f"   Content: {result.content[:150]}...")

        if result.timecode:
            print(f"   Timecode: {result.timecode:.1f}s")

        if result.source_info.get('source_title'):
            print(f"   Source: {result.source_info['source_title']}")


def format_synthesis(synthesis, metadata: Dict):
    """Format synthesis results for display"""

    print(f"\n🧠 5-BLOCK ANALYSIS SYNTHESIS")
    print(f"Query: {synthesis.query}")
    print(f"Generated: {synthesis.generated_at}")
    print(f"Processing time: {metadata['processing_time']:.2f}s")
    print(f"Overall confidence: {synthesis.overall_confidence:.1%}")
    print("=" * 60)

    # Display each block
    blocks = [
        ("🏛️ ESTABLISHED FACTS", synthesis.established),
        ("⚖️ CONTESTED/DISPUTED", synthesis.contested),
        ("🧠 ANALYTICAL REASONING", synthesis.why),
        ("🚩 ANALYTICAL FLAGS", synthesis.flags),
        ("➡️ NEXT STEPS", synthesis.next_steps)
    ]

    for title, block in blocks:
        print(f"\n{title}")
        print(f"Confidence: {block.confidence:.1%}")
        print(f"{block.content}")

        if block.sources:
            print(f"Sources: {len(block.sources)} referenced")


def format_status(status_data: Dict):
    """Format system status for display"""

    print(f"\n🔧 SHERLOCK SYSTEM STATUS")
    print("=" * 40)
    print(f"Database: {status_data['database_path']}")
    print(f"Operational: {'✅ YES' if status_data['system_operational'] else '❌ NO'}")
    print(f"Integrity: {'✅ PASS' if status_data['integrity_status'] == 'pass' else '❌ FAIL'}")
    print(f"Recent Activity: {status_data['recent_activity']} events")

    print("\nTable Statistics:")
    for table, count in status_data['table_statistics'].items():
        print(f"  {table}: {count} records")


def format_audit_trail(events: List, metadata: Dict):
    """Format audit trail for display"""

    print(f"\n📋 AUDIT TRAIL ({metadata['event_count']} events)")
    if metadata.get('session_filter'):
        print(f"Session filter: {metadata['session_filter']}")
    print("=" * 60)

    for event in events:
        timestamp = event['timestamp'][:19].replace('T', ' ')
        print(f"\n[{timestamp}] {event['event_type'].upper()}")
        print(f"  Component: {event['component']} | Operation: {event['operation']}")
        print(f"  Level: {event['level']} | Processing: {event['processing_time']:.2f}s")

        if event['error_message']:
            print(f"  Error: {event['error_message']}")


def main():
    """Main CLI entry point"""

    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize CLI
    cli = SherlockCLI(db_path=args.database, verbose=args.verbose)

    try:
        if args.command == 'search':
            result = cli.execute_search(
                query_text=args.query,
                query_type=args.type,
                limit=args.limit,
                sort_by=args.sort,
                output_format=args.export,
                output_path=args.output
            )

            if result['status'] == 'success':
                format_search_results(result['results'], result['metadata'])
            else:
                print(f"❌ Search failed: {result['error']}")

        elif args.command == 'synthesize':
            result = cli.execute_synthesis(
                query_text=args.query,
                query_type=args.type,
                output_format=args.export,
                output_path=args.output
            )

            if result['status'] == 'success':
                format_synthesis(result['synthesis'], result['metadata'])
                if args.verbose:
                    print(f"\nReproducibility Profile ID: {result['profile_id']}")
            else:
                print(f"❌ Synthesis failed: {result['error']}")

        elif args.command == 'status':
            result = cli.show_database_status()

            if result['status'] == 'success':
                format_status(result['data'])
            else:
                print(f"❌ Status check failed: {result['error']}")

        elif args.command == 'audit':
            result = cli.show_audit_trail(
                limit=args.limit,
                session_id=getattr(args, 'session', None)
            )

            if result['status'] == 'success':
                format_audit_trail(result['events'], result['metadata'])
            else:
                print(f"❌ Audit trail failed: {result['error']}")

        elif args.command == 'export':
            result = cli.export_data(
                data_type=args.data_type,
                output_path=args.output_path,
                format_type=getattr(args, 'format', 'json')
            )

            if result['status'] == 'success':
                print(f"✅ {result['message']}")
            else:
                print(f"❌ Export failed: {result['error']}")

    except KeyboardInterrupt:
        print("\n🛑 Operation interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
    finally:
        cli.close()


if __name__ == "__main__":
    main()