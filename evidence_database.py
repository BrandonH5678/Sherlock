#!/usr/bin/env python3
"""
Evidence Database for Sherlock
SQLite + FTS5 database with evidence cards, claims, and speaker attribution
"""

import json
import sqlite3
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum

# Add current directory to path
sys.path.append(str(Path(__file__).parent))


class EvidenceType(Enum):
    """Types of evidence sources"""
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    TRANSCRIPT = "transcript"
    WEB_ARCHIVE = "web_archive"
    PODCAST = "podcast"
    YOUTUBE = "youtube"


class ClaimType(Enum):
    """Types of claims in evidence cards"""
    FACTUAL = "factual"
    OPINION = "opinion"
    PREDICTION = "prediction"
    CONTRADICTION = "contradiction"
    PROPAGANDA = "propaganda"
    QUESTION = "question"


@dataclass
class Speaker:
    """Speaker information with voice fingerprint"""
    speaker_id: str
    name: Optional[str]
    title: Optional[str]
    organization: Optional[str]
    voice_embedding: Optional[str]  # JSON serialized embedding
    confidence: float
    first_seen: str
    last_seen: str


@dataclass
class EvidenceSource:
    """Source document/media with metadata"""
    source_id: str
    title: str
    url: Optional[str]
    file_path: Optional[str]
    evidence_type: EvidenceType
    duration: Optional[float]  # For audio/video
    page_count: Optional[int]  # For documents
    created_at: str
    ingested_at: str
    metadata: Dict


@dataclass
class EvidenceClaim:
    """Atomic claim extracted from evidence"""
    claim_id: str
    source_id: str
    speaker_id: Optional[str]
    claim_type: ClaimType
    text: str
    confidence: float
    start_time: Optional[float]  # Timecode for audio/video
    end_time: Optional[float]
    page_number: Optional[int]  # For documents
    context: str  # Surrounding context
    entities: List[str]  # Named entities
    tags: List[str]
    created_at: str


@dataclass
class EvidenceRelationship:
    """Relationships between claims, sources, and entities"""
    relationship_id: str
    subject_type: str  # "claim", "source", "speaker", "entity"
    subject_id: str
    relationship_type: str  # "contradicts", "supports", "references", "mentions"
    object_type: str
    object_id: str
    confidence: float
    evidence: str  # Supporting evidence for relationship
    created_at: str


class EvidenceDatabase:
    """SQLite database with FTS5 for evidence storage and search"""

    def __init__(self, db_path: str = "evidence.db"):
        self.db_path = Path(db_path)
        self.connection = None
        self._init_database()

    def _init_database(self):
        """Initialize database with all tables and indexes"""
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row

        # Enable FTS5 and JSON1 extensions
        self.connection.execute("PRAGMA foreign_keys = ON")

        self._create_tables()
        self._create_fts_tables()
        self._create_indexes()

    def _create_tables(self):
        """Create all core tables"""

        # Speakers table
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS speakers (
                speaker_id TEXT PRIMARY KEY,
                name TEXT,
                title TEXT,
                organization TEXT,
                voice_embedding TEXT,  -- JSON serialized embedding
                confidence REAL NOT NULL,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Evidence sources table
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS evidence_sources (
                source_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT,
                file_path TEXT,
                evidence_type TEXT NOT NULL,
                duration REAL,  -- For audio/video in seconds
                page_count INTEGER,  -- For documents
                created_at TEXT NOT NULL,
                ingested_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT NOT NULL DEFAULT '{}',  -- JSON metadata
                processing_status TEXT NOT NULL DEFAULT 'pending'
            )
        """)

        # Evidence claims table
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS evidence_claims (
                claim_id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                speaker_id TEXT,
                claim_type TEXT NOT NULL,
                text TEXT NOT NULL,
                confidence REAL NOT NULL,
                start_time REAL,  -- Timecode for audio/video
                end_time REAL,
                page_number INTEGER,  -- For documents
                context TEXT NOT NULL DEFAULT '',
                entities TEXT NOT NULL DEFAULT '[]',  -- JSON array
                tags TEXT NOT NULL DEFAULT '[]',  -- JSON array
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES evidence_sources (source_id),
                FOREIGN KEY (speaker_id) REFERENCES speakers (speaker_id)
            )
        """)

        # Evidence relationships table
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS evidence_relationships (
                relationship_id TEXT PRIMARY KEY,
                subject_type TEXT NOT NULL,
                subject_id TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                object_type TEXT NOT NULL,
                object_id TEXT NOT NULL,
                confidence REAL NOT NULL,
                evidence TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Processing log table for audit trail
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS processing_log (
                log_id TEXT PRIMARY KEY,
                operation TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                details TEXT NOT NULL DEFAULT '{}',  -- JSON details
                success BOOLEAN NOT NULL,
                error_message TEXT,
                processing_time REAL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.connection.commit()

    def _create_fts_tables(self):
        """Create FTS5 tables for full-text search"""

        # Full-text search for claims
        self.connection.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS claims_fts USING fts5(
                claim_id UNINDEXED,
                text,
                context,
                entities,
                tags,
                content='evidence_claims',
                content_rowid='rowid'
            )
        """)

        # Full-text search for sources
        self.connection.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS sources_fts USING fts5(
                source_id UNINDEXED,
                title,
                metadata,
                content='evidence_sources',
                content_rowid='rowid'
            )
        """)

        # Triggers to keep FTS in sync with main tables
        self.connection.execute("""
            CREATE TRIGGER IF NOT EXISTS claims_fts_insert AFTER INSERT ON evidence_claims BEGIN
                INSERT INTO claims_fts(claim_id, text, context, entities, tags)
                VALUES (new.claim_id, new.text, new.context, new.entities, new.tags);
            END
        """)

        self.connection.execute("""
            CREATE TRIGGER IF NOT EXISTS claims_fts_delete AFTER DELETE ON evidence_claims BEGIN
                INSERT INTO claims_fts(claims_fts, claim_id, text, context, entities, tags)
                VALUES ('delete', old.claim_id, old.text, old.context, old.entities, old.tags);
            END
        """)

        self.connection.execute("""
            CREATE TRIGGER IF NOT EXISTS claims_fts_update AFTER UPDATE ON evidence_claims BEGIN
                INSERT INTO claims_fts(claims_fts, claim_id, text, context, entities, tags)
                VALUES ('delete', old.claim_id, old.text, old.context, old.entities, old.tags);
                INSERT INTO claims_fts(claim_id, text, context, entities, tags)
                VALUES (new.claim_id, new.text, new.context, new.entities, new.tags);
            END
        """)

        self.connection.commit()

    def _create_indexes(self):
        """Create performance indexes"""

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_claims_source ON evidence_claims(source_id)",
            "CREATE INDEX IF NOT EXISTS idx_claims_speaker ON evidence_claims(speaker_id)",
            "CREATE INDEX IF NOT EXISTS idx_claims_type ON evidence_claims(claim_type)",
            "CREATE INDEX IF NOT EXISTS idx_claims_time ON evidence_claims(start_time, end_time)",
            "CREATE INDEX IF NOT EXISTS idx_relationships_subject ON evidence_relationships(subject_type, subject_id)",
            "CREATE INDEX IF NOT EXISTS idx_relationships_object ON evidence_relationships(object_type, object_id)",
            "CREATE INDEX IF NOT EXISTS idx_sources_type ON evidence_sources(evidence_type)",
            "CREATE INDEX IF NOT EXISTS idx_sources_status ON evidence_sources(processing_status)",
            "CREATE INDEX IF NOT EXISTS idx_log_target ON processing_log(target_type, target_id)"
        ]

        for index_sql in indexes:
            self.connection.execute(index_sql)

        self.connection.commit()

    def add_speaker(self, speaker: Speaker) -> bool:
        """Add speaker to database"""
        try:
            self.connection.execute("""
                INSERT OR REPLACE INTO speakers
                (speaker_id, name, title, organization, voice_embedding, confidence, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                speaker.speaker_id, speaker.name, speaker.title, speaker.organization,
                speaker.voice_embedding, speaker.confidence, speaker.first_seen, speaker.last_seen
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error adding speaker: {e}")
            return False

    def add_evidence_source(self, source: EvidenceSource) -> bool:
        """Add evidence source to database"""
        try:
            self.connection.execute("""
                INSERT OR REPLACE INTO evidence_sources
                (source_id, title, url, file_path, evidence_type, duration, page_count, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                source.source_id, source.title, source.url, source.file_path,
                source.evidence_type.value, source.duration, source.page_count,
                source.created_at, json.dumps(source.metadata)
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error adding evidence source: {e}")
            return False

    def add_evidence_claim(self, claim: EvidenceClaim) -> bool:
        """Add evidence claim to database"""
        try:
            self.connection.execute("""
                INSERT OR REPLACE INTO evidence_claims
                (claim_id, source_id, speaker_id, claim_type, text, confidence,
                 start_time, end_time, page_number, context, entities, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                claim.claim_id, claim.source_id, claim.speaker_id, claim.claim_type.value,
                claim.text, claim.confidence, claim.start_time, claim.end_time,
                claim.page_number, claim.context, json.dumps(claim.entities), json.dumps(claim.tags)
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error adding evidence claim: {e}")
            return False

    def add_relationship(self, relationship: EvidenceRelationship) -> bool:
        """Add relationship to database"""
        try:
            self.connection.execute("""
                INSERT OR REPLACE INTO evidence_relationships
                (relationship_id, subject_type, subject_id, relationship_type,
                 object_type, object_id, confidence, evidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                relationship.relationship_id, relationship.subject_type, relationship.subject_id,
                relationship.relationship_type, relationship.object_type, relationship.object_id,
                relationship.confidence, relationship.evidence
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error adding relationship: {e}")
            return False

    def search_claims(self, query: str, limit: int = 50) -> List[Dict]:
        """Full-text search for claims"""
        try:
            cursor = self.connection.execute("""
                SELECT ec.*, es.title as source_title, s.name as speaker_name
                FROM claims_fts cf
                JOIN evidence_claims ec ON cf.claim_id = ec.claim_id
                JOIN evidence_sources es ON ec.source_id = es.source_id
                LEFT JOIN speakers s ON ec.speaker_id = s.speaker_id
                WHERE claims_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (query, limit))

            results = []
            for row in cursor.fetchall():
                result = dict(row)
                result['entities'] = json.loads(result['entities'])
                result['tags'] = json.loads(result['tags'])
                results.append(result)

            return results
        except Exception as e:
            print(f"Error searching claims: {e}")
            return []

    def get_claims_by_speaker(self, speaker_id: str) -> List[Dict]:
        """Get all claims by a specific speaker"""
        try:
            cursor = self.connection.execute("""
                SELECT ec.*, es.title as source_title
                FROM evidence_claims ec
                JOIN evidence_sources es ON ec.source_id = es.source_id
                WHERE ec.speaker_id = ?
                ORDER BY ec.start_time
            """, (speaker_id,))

            results = []
            for row in cursor.fetchall():
                result = dict(row)
                result['entities'] = json.loads(result['entities'])
                result['tags'] = json.loads(result['tags'])
                results.append(result)

            return results
        except Exception as e:
            print(f"Error getting claims by speaker: {e}")
            return []

    def get_claims_by_source(self, source_id: str) -> List[Dict]:
        """Get all claims from a specific source"""
        try:
            cursor = self.connection.execute("""
                SELECT ec.*, s.name as speaker_name
                FROM evidence_claims ec
                LEFT JOIN speakers s ON ec.speaker_id = s.speaker_id
                WHERE ec.source_id = ?
                ORDER BY ec.start_time, ec.page_number
            """, (source_id,))

            results = []
            for row in cursor.fetchall():
                result = dict(row)
                result['entities'] = json.loads(result['entities'])
                result['tags'] = json.loads(result['tags'])
                results.append(result)

            return results
        except Exception as e:
            print(f"Error getting claims by source: {e}")
            return []

    def find_contradictions(self, claim_id: str) -> List[Dict]:
        """Find claims that contradict the given claim"""
        try:
            cursor = self.connection.execute("""
                SELECT er.*, ec.text as contradicting_text, s.name as speaker_name
                FROM evidence_relationships er
                JOIN evidence_claims ec ON er.object_id = ec.claim_id
                LEFT JOIN speakers s ON ec.speaker_id = s.speaker_id
                WHERE er.subject_id = ? AND er.relationship_type = 'contradicts'
                ORDER BY er.confidence DESC
            """, (claim_id,))

            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error finding contradictions: {e}")
            return []

    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        try:
            stats = {}

            # Count tables
            tables = ['speakers', 'evidence_sources', 'evidence_claims', 'evidence_relationships']
            for table in tables:
                cursor = self.connection.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]

            # Evidence types breakdown
            cursor = self.connection.execute("""
                SELECT evidence_type, COUNT(*)
                FROM evidence_sources
                GROUP BY evidence_type
            """)
            stats['evidence_types'] = dict(cursor.fetchall())

            # Claim types breakdown
            cursor = self.connection.execute("""
                SELECT claim_type, COUNT(*)
                FROM evidence_claims
                GROUP BY claim_type
            """)
            stats['claim_types'] = dict(cursor.fetchall())

            # Processing status
            cursor = self.connection.execute("""
                SELECT processing_status, COUNT(*)
                FROM evidence_sources
                GROUP BY processing_status
            """)
            stats['processing_status'] = dict(cursor.fetchall())

            return stats
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {}

    def log_operation(self, operation: str, target_type: str, target_id: str,
                     success: bool, details: Dict = None, error_message: str = None,
                     processing_time: float = None):
        """Log operation for audit trail"""
        try:
            log_id = f"log_{int(time.time() * 1000)}"
            self.connection.execute("""
                INSERT INTO processing_log
                (log_id, operation, target_type, target_id, details, success, error_message, processing_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log_id, operation, target_type, target_id,
                json.dumps(details or {}), success, error_message, processing_time
            ))
            self.connection.commit()
        except Exception as e:
            print(f"Error logging operation: {e}")

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()


def main():
    """CLI interface for evidence database"""
    if len(sys.argv) < 2:
        print("Evidence Database for Sherlock")
        print("Usage:")
        print("  python evidence_database.py init")
        print("  python evidence_database.py stats")
        print("  python evidence_database.py search <query>")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "init":
        print("🗄️  Initializing Evidence Database...")
        db = EvidenceDatabase()
        stats = db.get_database_stats()

        print("✅ Database initialized with tables:")
        for table, count in stats.items():
            if isinstance(count, int):
                print(f"   {table}: {count} records")

        db.close()

    elif command == "stats":
        db = EvidenceDatabase()
        stats = db.get_database_stats()

        print("📊 Evidence Database Statistics")
        print("=" * 40)
        print(f"Speakers: {stats.get('speakers', 0)}")
        print(f"Evidence Sources: {stats.get('evidence_sources', 0)}")
        print(f"Evidence Claims: {stats.get('evidence_claims', 0)}")
        print(f"Relationships: {stats.get('evidence_relationships', 0)}")

        if stats.get('evidence_types'):
            print("\n📁 Evidence Types:")
            for etype, count in stats['evidence_types'].items():
                print(f"   {etype}: {count}")

        if stats.get('claim_types'):
            print("\n💬 Claim Types:")
            for ctype, count in stats['claim_types'].items():
                print(f"   {ctype}: {count}")

        db.close()

    elif command == "search":
        if len(sys.argv) < 3:
            print("❌ Search query required")
            sys.exit(1)

        query = " ".join(sys.argv[2:])
        db = EvidenceDatabase()
        results = db.search_claims(query)

        print(f"🔍 Search Results for: {query}")
        print("=" * 50)

        if not results:
            print("No results found")
        else:
            for i, result in enumerate(results[:10], 1):
                print(f"\n{i}. {result['text'][:100]}...")
                print(f"   Source: {result['source_title']}")
                if result['speaker_name']:
                    print(f"   Speaker: {result['speaker_name']}")
                if result['start_time']:
                    print(f"   Time: {result['start_time']:.1f}s")

        db.close()

    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()