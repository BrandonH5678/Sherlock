#!/usr/bin/env python3
"""
Audit and Reproducibility System for Sherlock
Append-only logging, version tracking, and analysis reproducibility
"""

import hashlib
import json
import sys
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from enum import Enum

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from evidence_database import EvidenceDatabase


class AuditEventType(Enum):
    """Types of audit events"""
    QUERY_EXECUTED = "query_executed"
    SYNTHESIS_GENERATED = "synthesis_generated"
    EXPORT_CREATED = "export_created"
    EVIDENCE_INGESTED = "evidence_ingested"
    ANALYSIS_COMPLETED = "analysis_completed"
    DATABASE_MODIFIED = "database_modified"
    SYSTEM_STARTED = "system_started"
    SYSTEM_STOPPED = "system_stopped"
    ERROR_OCCURRED = "error_occurred"
    CONFIGURATION_CHANGED = "configuration_changed"


class AuditLevel(Enum):
    """Audit logging levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Individual audit event record"""
    event_id: str
    timestamp: str
    event_type: AuditEventType
    level: AuditLevel
    component: str  # Which system component generated this event
    operation: str  # Specific operation performed
    user_id: Optional[str]
    session_id: str

    # Event data
    input_data: Dict  # Input parameters/query/etc
    output_data: Dict  # Results/response/etc
    metadata: Dict  # Additional context

    # Reproducibility data
    system_version: str
    database_hash: str
    configuration_hash: str
    processing_time: float

    # Error information (if applicable)
    error_message: Optional[str]
    stack_trace: Optional[str]


@dataclass
class ReproducibilityProfile:
    """Profile for reproducing analysis results"""
    profile_id: str
    created_at: str
    query_hash: str
    database_state_hash: str
    system_configuration: Dict
    dependency_versions: Dict
    processing_steps: List[str]
    result_hash: str

    # Validation data
    validation_checksum: str
    verification_timestamp: Optional[str]


class AuditSystem:
    """Comprehensive audit and reproducibility tracking system"""

    def __init__(self, db_path: str = "evidence.db", audit_db_path: str = "audit.db"):
        self.db_path = db_path
        self.audit_db_path = audit_db_path
        self.session_id = str(uuid.uuid4())

        # Initialize audit database
        self._init_audit_database()

        # System configuration tracking
        self.system_version = "1.0.0"  # Should be from config
        self._current_config_hash = None
        self._update_configuration_hash()

    def _init_audit_database(self):
        """Initialize audit database with required tables"""

        import sqlite3
        self.audit_connection = sqlite3.connect(self.audit_db_path)

        # Create audit events table
        self.audit_connection.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                level TEXT NOT NULL,
                component TEXT NOT NULL,
                operation TEXT NOT NULL,
                user_id TEXT,
                session_id TEXT NOT NULL,
                input_data TEXT,
                output_data TEXT,
                metadata TEXT,
                system_version TEXT NOT NULL,
                database_hash TEXT NOT NULL,
                configuration_hash TEXT NOT NULL,
                processing_time REAL NOT NULL,
                error_message TEXT,
                stack_trace TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create reproducibility profiles table
        self.audit_connection.execute("""
            CREATE TABLE IF NOT EXISTS reproducibility_profiles (
                profile_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                query_hash TEXT NOT NULL,
                database_state_hash TEXT NOT NULL,
                system_configuration TEXT NOT NULL,
                dependency_versions TEXT NOT NULL,
                processing_steps TEXT NOT NULL,
                result_hash TEXT NOT NULL,
                validation_checksum TEXT NOT NULL,
                verification_timestamp TEXT
            )
        """)

        # Create integrity verification table
        self.audit_connection.execute("""
            CREATE TABLE IF NOT EXISTS integrity_checks (
                check_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                check_type TEXT NOT NULL,
                target_hash TEXT NOT NULL,
                current_hash TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT
            )
        """)

        # Create indexes for performance
        self.audit_connection.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_events(timestamp)")
        self.audit_connection.execute("CREATE INDEX IF NOT EXISTS idx_audit_session ON audit_events(session_id)")
        self.audit_connection.execute("CREATE INDEX IF NOT EXISTS idx_audit_type ON audit_events(event_type)")

        self.audit_connection.commit()

    def log_event(self, event_type: AuditEventType, level: AuditLevel, component: str,
                  operation: str, input_data: Dict = None, output_data: Dict = None,
                  metadata: Dict = None, user_id: str = None, processing_time: float = 0.0,
                  error_message: str = None, stack_trace: str = None) -> str:
        """Log an audit event"""

        event_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # Calculate current database hash
        db_hash = self._calculate_database_hash()

        # Create audit event
        event = AuditEvent(
            event_id=event_id,
            timestamp=timestamp,
            event_type=event_type,
            level=level,
            component=component,
            operation=operation,
            user_id=user_id,
            session_id=self.session_id,
            input_data=input_data or {},
            output_data=output_data or {},
            metadata=metadata or {},
            system_version=self.system_version,
            database_hash=db_hash,
            configuration_hash=self._current_config_hash,
            processing_time=processing_time,
            error_message=error_message,
            stack_trace=stack_trace
        )

        # Insert into audit database
        self.audit_connection.execute("""
            INSERT INTO audit_events (
                event_id, timestamp, event_type, level, component, operation,
                user_id, session_id, input_data, output_data, metadata,
                system_version, database_hash, configuration_hash,
                processing_time, error_message, stack_trace
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.event_id, event.timestamp, event.event_type.value, event.level.value,
            event.component, event.operation, event.user_id, event.session_id,
            json.dumps(event.input_data), json.dumps(event.output_data),
            json.dumps(event.metadata), event.system_version, event.database_hash,
            event.configuration_hash, event.processing_time, event.error_message,
            event.stack_trace
        ))
        self.audit_connection.commit()

        return event_id

    def create_reproducibility_profile(self, query: Dict, result: Dict, processing_steps: List[str]) -> str:
        """Create a reproducibility profile for an analysis"""

        profile_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # Calculate hashes
        query_hash = self._calculate_hash(json.dumps(query, sort_keys=True))
        db_state_hash = self._calculate_database_hash()
        result_hash = self._calculate_hash(json.dumps(result, sort_keys=True, default=str))

        # Get system configuration
        system_config = self._get_system_configuration()
        dependency_versions = self._get_dependency_versions()

        # Create validation checksum
        validation_data = {
            'query_hash': query_hash,
            'database_state_hash': db_state_hash,
            'result_hash': result_hash,
            'system_config': system_config,
            'processing_steps': processing_steps
        }
        validation_checksum = self._calculate_hash(json.dumps(validation_data, sort_keys=True))

        profile = ReproducibilityProfile(
            profile_id=profile_id,
            created_at=timestamp,
            query_hash=query_hash,
            database_state_hash=db_state_hash,
            system_configuration=system_config,
            dependency_versions=dependency_versions,
            processing_steps=processing_steps,
            result_hash=result_hash,
            validation_checksum=validation_checksum,
            verification_timestamp=None
        )

        # Insert into database
        self.audit_connection.execute("""
            INSERT INTO reproducibility_profiles (
                profile_id, created_at, query_hash, database_state_hash,
                system_configuration, dependency_versions, processing_steps,
                result_hash, validation_checksum
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile.profile_id, profile.created_at, profile.query_hash,
            profile.database_state_hash, json.dumps(profile.system_configuration),
            json.dumps(profile.dependency_versions), json.dumps(profile.processing_steps),
            profile.result_hash, profile.validation_checksum
        ))
        self.audit_connection.commit()

        # Log the profile creation
        self.log_event(
            AuditEventType.ANALYSIS_COMPLETED,
            AuditLevel.INFO,
            "audit_system",
            "create_reproducibility_profile",
            input_data={'query_hash': query_hash},
            output_data={'profile_id': profile_id, 'validation_checksum': validation_checksum},
            metadata={'processing_steps_count': len(processing_steps)}
        )

        return profile_id

    def verify_reproducibility(self, profile_id: str, current_query: Dict, current_result: Dict) -> Dict:
        """Verify if analysis can be reproduced with given profile"""

        # Get stored profile
        cursor = self.audit_connection.execute("""
            SELECT * FROM reproducibility_profiles WHERE profile_id = ?
        """, (profile_id,))

        row = cursor.fetchone()
        if not row:
            return {
                'status': 'failed',
                'reason': 'Profile not found',
                'reproducible': False
            }

        # Parse stored profile
        stored_profile = row

        # Calculate current hashes
        current_query_hash = self._calculate_hash(json.dumps(current_query, sort_keys=True))
        current_db_hash = self._calculate_database_hash()
        current_result_hash = self._calculate_hash(json.dumps(current_result, sort_keys=True, default=str))

        # Verification results
        verification = {
            'profile_id': profile_id,
            'verification_timestamp': datetime.now().isoformat(),
            'query_match': stored_profile[2] == current_query_hash,
            'database_match': stored_profile[3] == current_db_hash,
            'result_match': stored_profile[7] == current_result_hash,
            'stored_query_hash': stored_profile[2],
            'current_query_hash': current_query_hash,
            'stored_db_hash': stored_profile[3],
            'current_db_hash': current_db_hash,
            'stored_result_hash': stored_profile[7],
            'current_result_hash': current_result_hash
        }

        # Determine reproducibility status
        verification['reproducible'] = (
            verification['query_match'] and
            verification['database_match'] and
            verification['result_match']
        )

        if verification['reproducible']:
            verification['status'] = 'success'
            verification['reason'] = 'Analysis fully reproduced'
        else:
            verification['status'] = 'partial'
            mismatches = []
            if not verification['query_match']:
                mismatches.append('query')
            if not verification['database_match']:
                mismatches.append('database')
            if not verification['result_match']:
                mismatches.append('result')
            verification['reason'] = f"Mismatches in: {', '.join(mismatches)}"

        # Update verification timestamp
        self.audit_connection.execute("""
            UPDATE reproducibility_profiles
            SET verification_timestamp = ?
            WHERE profile_id = ?
        """, (verification['verification_timestamp'], profile_id))
        self.audit_connection.commit()

        # Log verification
        self.log_event(
            AuditEventType.ANALYSIS_COMPLETED,
            AuditLevel.INFO,
            "audit_system",
            "verify_reproducibility",
            input_data={'profile_id': profile_id},
            output_data=verification,
            metadata={'reproducible': verification['reproducible']}
        )

        return verification

    def get_audit_trail(self, session_id: str = None, event_type: AuditEventType = None,
                       start_time: str = None, end_time: str = None, limit: int = 100) -> List[Dict]:
        """Retrieve audit trail with optional filtering"""

        query = "SELECT * FROM audit_events WHERE 1=1"
        params = []

        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)

        if event_type:
            query += " AND event_type = ?"
            params.append(event_type.value)

        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)

        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor = self.audit_connection.execute(query, params)

        events = []
        for row in cursor.fetchall():
            event = {
                'event_id': row[0],
                'timestamp': row[1],
                'event_type': row[2],
                'level': row[3],
                'component': row[4],
                'operation': row[5],
                'user_id': row[6],
                'session_id': row[7],
                'input_data': json.loads(row[8]) if row[8] else {},
                'output_data': json.loads(row[9]) if row[9] else {},
                'metadata': json.loads(row[10]) if row[10] else {},
                'system_version': row[11],
                'database_hash': row[12],
                'configuration_hash': row[13],
                'processing_time': row[14],
                'error_message': row[15],
                'stack_trace': row[16]
            }
            events.append(event)

        return events

    def run_integrity_check(self) -> Dict:
        """Run comprehensive integrity check on audit system"""

        check_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # Check 1: Audit database integrity
        try:
            cursor = self.audit_connection.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()[0]
            audit_db_ok = integrity_result == "ok"
        except Exception as e:
            audit_db_ok = False
            integrity_result = str(e)

        # Check 2: Evidence database integrity
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("PRAGMA integrity_check")
                evidence_integrity = cursor.fetchone()[0]
                evidence_db_ok = evidence_integrity == "ok"
        except Exception as e:
            evidence_db_ok = False
            evidence_integrity = str(e)

        # Check 3: Configuration consistency
        current_config_hash = self._calculate_configuration_hash()
        config_consistent = current_config_hash == self._current_config_hash

        # Check 4: Recent events validation
        recent_events = self.get_audit_trail(limit=50)
        events_valid = True
        invalid_events = []

        for event in recent_events:
            # Validate event structure
            required_fields = ['event_id', 'timestamp', 'event_type', 'component']
            if not all(field in event for field in required_fields):
                events_valid = False
                invalid_events.append(event['event_id'])

        # Compile results
        check_results = {
            'check_id': check_id,
            'timestamp': timestamp,
            'overall_status': 'pass' if all([audit_db_ok, evidence_db_ok, config_consistent, events_valid]) else 'fail',
            'checks': {
                'audit_database': {
                    'status': 'pass' if audit_db_ok else 'fail',
                    'details': integrity_result
                },
                'evidence_database': {
                    'status': 'pass' if evidence_db_ok else 'fail',
                    'details': evidence_integrity
                },
                'configuration': {
                    'status': 'pass' if config_consistent else 'fail',
                    'details': f"Current: {current_config_hash}, Expected: {self._current_config_hash}"
                },
                'events_validation': {
                    'status': 'pass' if events_valid else 'fail',
                    'details': f"Invalid events: {invalid_events}" if invalid_events else "All events valid"
                }
            }
        }

        # Store integrity check result
        self.audit_connection.execute("""
            INSERT INTO integrity_checks (
                check_id, timestamp, check_type, target_hash, current_hash, status, details
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            check_id, timestamp, "comprehensive", self._current_config_hash,
            current_config_hash, check_results['overall_status'], json.dumps(check_results)
        ))
        self.audit_connection.commit()

        return check_results

    def export_audit_data(self, output_path: str, format_type: str = "json") -> bool:
        """Export audit data for external analysis"""

        try:
            # Get all audit events
            events = self.get_audit_trail(limit=10000)

            # Get all reproducibility profiles
            cursor = self.audit_connection.execute("SELECT * FROM reproducibility_profiles")
            profiles = []
            for row in cursor.fetchall():
                profile = {
                    'profile_id': row[0],
                    'created_at': row[1],
                    'query_hash': row[2],
                    'database_state_hash': row[3],
                    'system_configuration': json.loads(row[4]),
                    'dependency_versions': json.loads(row[5]),
                    'processing_steps': json.loads(row[6]),
                    'result_hash': row[7],
                    'validation_checksum': row[8],
                    'verification_timestamp': row[9]
                }
                profiles.append(profile)

            # Get integrity checks
            cursor = self.audit_connection.execute("SELECT * FROM integrity_checks ORDER BY timestamp DESC LIMIT 100")
            integrity_checks = []
            for row in cursor.fetchall():
                check = {
                    'check_id': row[0],
                    'timestamp': row[1],
                    'check_type': row[2],
                    'target_hash': row[3],
                    'current_hash': row[4],
                    'status': row[5],
                    'details': json.loads(row[6]) if row[6] else {}
                }
                integrity_checks.append(check)

            # Compile export data
            export_data = {
                'export_metadata': {
                    'exported_at': datetime.now().isoformat(),
                    'system_version': self.system_version,
                    'session_id': self.session_id,
                    'format': format_type
                },
                'audit_events': events,
                'reproducibility_profiles': profiles,
                'integrity_checks': integrity_checks,
                'statistics': {
                    'total_events': len(events),
                    'total_profiles': len(profiles),
                    'total_integrity_checks': len(integrity_checks)
                }
            }

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                if format_type.lower() == 'json':
                    json.dump(export_data, f, indent=2, default=str)
                else:
                    # Default to JSON for unsupported formats
                    json.dump(export_data, f, indent=2, default=str)

            # Log export
            self.log_event(
                AuditEventType.EXPORT_CREATED,
                AuditLevel.INFO,
                "audit_system",
                "export_audit_data",
                input_data={'format': format_type, 'output_path': output_path},
                output_data={'events_count': len(events), 'profiles_count': len(profiles)},
                metadata={'file_size': Path(output_path).stat().st_size}
            )

            return True

        except Exception as e:
            self.log_event(
                AuditEventType.ERROR_OCCURRED,
                AuditLevel.ERROR,
                "audit_system",
                "export_audit_data",
                input_data={'format': format_type, 'output_path': output_path},
                error_message=str(e)
            )
            return False

    def _calculate_database_hash(self) -> str:
        """Calculate hash of current database state"""

        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get all table names
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]

                # Calculate hash based on table schemas and row counts
                hash_data = []
                for table in tables:
                    if not table.startswith('sqlite_'):
                        # Get schema
                        cursor = conn.execute(f"SELECT sql FROM sqlite_master WHERE name='{table}'")
                        schema = cursor.fetchone()
                        if schema:
                            hash_data.append(f"schema:{table}:{schema[0]}")

                        # Get row count
                        cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        hash_data.append(f"count:{table}:{count}")

                return self._calculate_hash('\n'.join(sorted(hash_data)))

        except Exception as e:
            return f"error:{str(e)}"

    def _calculate_configuration_hash(self) -> str:
        """Calculate hash of current system configuration"""

        config_data = self._get_system_configuration()
        return self._calculate_hash(json.dumps(config_data, sort_keys=True))

    def _update_configuration_hash(self):
        """Update stored configuration hash"""
        self._current_config_hash = self._calculate_configuration_hash()

    def _get_system_configuration(self) -> Dict:
        """Get current system configuration"""

        return {
            'system_version': self.system_version,
            'database_path': self.db_path,
            'audit_database_path': self.audit_db_path,
            'python_version': sys.version,
            'platform': sys.platform
        }

    def _get_dependency_versions(self) -> Dict:
        """Get versions of key dependencies"""

        dependencies = {}

        try:
            import sqlite3
            dependencies['sqlite3'] = sqlite3.sqlite_version
        except:
            pass

        try:
            import json
            dependencies['json'] = 'builtin'
        except:
            pass

        return dependencies

    def _calculate_hash(self, data: str) -> str:
        """Calculate SHA-256 hash of data"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def close(self):
        """Close audit database connection"""
        if hasattr(self, 'audit_connection'):
            self.audit_connection.close()


def main():
    """CLI interface for audit system"""
    if len(sys.argv) < 2:
        print("Audit and Reproducibility System for Sherlock")
        print("Usage:")
        print("  python audit_system.py trail [session_id] [limit]")
        print("  python audit_system.py integrity")
        print("  python audit_system.py export <output_path> [format]")
        print("  python audit_system.py profiles [limit]")
        sys.exit(1)

    command = sys.argv[1].lower()
    audit_system = AuditSystem()

    try:
        if command == "trail":
            session_id = sys.argv[2] if len(sys.argv) > 2 else None
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 50

            events = audit_system.get_audit_trail(session_id=session_id, limit=limit)

            print(f"\n📋 AUDIT TRAIL ({len(events)} events)")
            print("=" * 60)

            for event in events:
                print(f"\n[{event['timestamp']}] {event['event_type'].upper()}")
                print(f"Component: {event['component']} | Operation: {event['operation']}")
                print(f"Level: {event['level']} | Session: {event['session_id'][:8]}...")
                if event['error_message']:
                    print(f"Error: {event['error_message']}")

        elif command == "integrity":
            print("🔍 Running integrity check...")
            results = audit_system.run_integrity_check()

            print(f"\n🛡️ INTEGRITY CHECK RESULTS")
            print("=" * 40)
            print(f"Overall Status: {results['overall_status'].upper()}")
            print(f"Check ID: {results['check_id']}")
            print(f"Timestamp: {results['timestamp']}")

            for check_name, check_result in results['checks'].items():
                status_emoji = "✅" if check_result['status'] == 'pass' else "❌"
                print(f"\n{status_emoji} {check_name.replace('_', ' ').title()}: {check_result['status']}")
                print(f"   Details: {check_result['details']}")

        elif command == "export":
            output_path = sys.argv[2] if len(sys.argv) > 2 else "audit_export.json"
            format_type = sys.argv[3] if len(sys.argv) > 3 else "json"

            success = audit_system.export_audit_data(output_path, format_type)
            if success:
                print(f"✅ Audit data exported to: {output_path}")
            else:
                print(f"❌ Failed to export audit data")

        elif command == "profiles":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10

            cursor = audit_system.audit_connection.execute("""
                SELECT profile_id, created_at, query_hash, result_hash, validation_checksum
                FROM reproducibility_profiles
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))

            profiles = cursor.fetchall()

            print(f"\n🔬 REPRODUCIBILITY PROFILES ({len(profiles)} found)")
            print("=" * 60)

            for profile in profiles:
                print(f"\nProfile ID: {profile[0]}")
                print(f"Created: {profile[1]}")
                print(f"Query Hash: {profile[2][:16]}...")
                print(f"Result Hash: {profile[3][:16]}...")
                print(f"Validation: {profile[4][:16]}...")

        else:
            print(f"❌ Unknown command: {command}")

    finally:
        audit_system.close()


if __name__ == "__main__":
    main()