#!/usr/bin/env python3
"""
Evidence Schema for Operation Gladio Analysis
Comprehensive fact library structure for intelligence analysis
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class EvidenceType(Enum):
    """Types of evidence supporting or contradicting claims"""
    DOCUMENT = "document"
    TESTIMONY = "testimony"
    PHOTOGRAPH = "photograph"
    OFFICIAL_RECORD = "official_record"
    DECLASSIFIED_FILE = "declassified_file"
    NEWSPAPER = "newspaper"
    BOOK = "book"
    INTERVIEW = "interview"
    COURT_RECORD = "court_record"
    CORRELATION = "correlation"
    PATTERN = "pattern"


class ConfidenceLevel(Enum):
    """Confidence levels for claims and evidence"""
    CONFIRMED = "confirmed"        # Multiple independent sources
    PROBABLE = "probable"          # Strong evidence, minor gaps
    POSSIBLE = "possible"          # Some evidence, significant gaps
    DISPUTED = "disputed"          # Contradictory evidence exists
    UNVERIFIED = "unverified"      # Single source, no corroboration
    DISPROVEN = "disproven"        # Evidence contradicts claim


@dataclass
class TimeReference:
    """Precise temporal reference with uncertainty bounds"""
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    hour: Optional[int] = None
    minute: Optional[int] = None

    # Uncertainty bounds
    earliest_possible: Optional[str] = None
    latest_possible: Optional[str] = None

    # Context
    time_description: Optional[str] = None  # "early 1960s", "winter of 1963"
    source_description: Optional[str] = None  # How date was determined
    confidence: ConfidenceLevel = ConfidenceLevel.POSSIBLE


@dataclass
class LocationReference:
    """Geographic reference with precision levels"""
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None  # lat, lon

    # Context
    location_description: Optional[str] = None
    source_description: Optional[str] = None
    confidence: ConfidenceLevel = ConfidenceLevel.POSSIBLE


@dataclass
class Evidence:
    """Individual piece of evidence supporting or contradicting a claim"""
    evidence_id: str
    evidence_type: EvidenceType
    description: str
    source: str
    page_reference: Optional[str] = None

    # Temporal context
    evidence_date: Optional[TimeReference] = None

    # Quality assessment
    confidence: ConfidenceLevel = ConfidenceLevel.POSSIBLE
    reliability_notes: Optional[str] = None

    # Cross-references
    related_evidence: List[str] = None  # Other evidence IDs
    contradicted_by: List[str] = None   # Evidence that disputes this


@dataclass
class Claim:
    """Factual claim with supporting and contradicting evidence"""
    claim_id: str
    statement: str
    category: str  # "biographical", "operational", "organizational", etc.

    # Evidence
    supporting_evidence: List[Evidence] = None
    contradicting_evidence: List[Evidence] = None

    # Assessment
    overall_confidence: ConfidenceLevel = ConfidenceLevel.POSSIBLE
    assessment_notes: Optional[str] = None

    # Temporal and spatial context
    time_reference: Optional[TimeReference] = None
    location_reference: Optional[LocationReference] = None


@dataclass
class PersonDossier:
    """Comprehensive person dossier with temporal granularity"""
    person_id: str

    # Basic identification
    first_name: Optional[str] = None
    middle_names: List[str] = None
    last_name: Optional[str] = None
    aliases: List[str] = None

    # Life events with temporal precision
    birth_date: Optional[TimeReference] = None
    death_date: Optional[TimeReference] = None
    birth_location: Optional[LocationReference] = None

    # Background with timeline
    childhood_events: List[Claim] = None
    education_timeline: List[Claim] = None
    training_timeline: List[Claim] = None
    employment_timeline: List[Claim] = None
    military_service: List[Claim] = None

    # Affiliations and memberships with dates
    organization_memberships: List[Claim] = None
    political_affiliations: List[Claim] = None
    political_positions: List[Claim] = None

    # Operations and activities
    operation_participation: List[Claim] = None
    significant_activities: List[Claim] = None

    # Impact assessment
    political_impact: List[Claim] = None
    economic_impact: List[Claim] = None
    technological_impact: List[Claim] = None
    cultural_impact: List[Claim] = None
    emotional_impact: List[Claim] = None
    spiritual_impact: List[Claim] = None

    # Relationships
    personal_relationships: List[str] = None  # Person IDs
    professional_relationships: List[str] = None

    # Meta information
    dossier_created: str = None
    last_updated: str = None
    created_by: str = None


@dataclass
class Organization:
    """Organization with membership and operations tracking"""
    organization_id: str
    name: str
    aliases: List[str] = None

    # Organizational timeline
    founding_date: Optional[TimeReference] = None
    dissolution_date: Optional[TimeReference] = None
    significant_events: List[Claim] = None

    # Structure and membership
    organizational_structure: List[Claim] = None
    leadership_timeline: List[Claim] = None
    membership_timeline: List[Claim] = None

    # Activities and operations
    declared_purpose: List[Claim] = None
    actual_activities: List[Claim] = None
    operations: List[Claim] = None

    # Resources and funding
    funding_sources: List[Claim] = None
    resource_flows: List[Claim] = None
    budget_information: List[Claim] = None

    # Relationships
    parent_organizations: List[str] = None  # Organization IDs
    subsidiary_organizations: List[str] = None
    partner_organizations: List[str] = None
    rival_organizations: List[str] = None

    # Geographic presence
    headquarters: Optional[LocationReference] = None
    operational_locations: List[LocationReference] = None

    # Meta information
    created: str = None
    last_updated: str = None


@dataclass
class ResourceFlow:
    """Financial or material resource movement"""
    flow_id: str

    # Parties involved
    source_entity: str  # Person or Organization ID
    recipient_entity: str

    # Resource details
    resource_type: str  # "money", "weapons", "information", "personnel"
    amount: Optional[str] = None
    description: str = None

    # Temporal context
    flow_date: Optional[TimeReference] = None
    duration: Optional[str] = None

    # Purpose and context
    stated_purpose: Optional[str] = None
    actual_purpose: Optional[str] = None
    operational_context: Optional[str] = None

    # Evidence
    evidence: List[Evidence] = None
    confidence: ConfidenceLevel = ConfidenceLevel.POSSIBLE


@dataclass
class Relationship:
    """Relationship between entities with evidence tracking"""
    relationship_id: str

    # Entities
    entity_1: str  # Person or Organization ID
    entity_2: str
    entity_1_type: str  # "person" or "organization"
    entity_2_type: str

    # Relationship details
    relationship_type: str  # "member", "leader", "funder", "operational", "personal"
    relationship_description: str

    # Temporal context
    relationship_start: Optional[TimeReference] = None
    relationship_end: Optional[TimeReference] = None

    # Evidence
    supporting_evidence: List[Evidence] = None
    contradicting_evidence: List[Evidence] = None
    confidence: ConfidenceLevel = ConfidenceLevel.POSSIBLE

    # Obscuration indicators
    publicly_acknowledged: bool = False
    deliberately_hidden: bool = False
    cover_story: Optional[str] = None

    # Impact assessment
    significance: str = None  # "high", "medium", "low"
    implications: List[str] = None


class GladioEvidenceDatabase:
    """Database for managing Operation Gladio evidence"""

    def __init__(self, db_path: str = "gladio_evidence.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # People table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS people (
                person_id TEXT PRIMARY KEY,
                dossier_json TEXT,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Organizations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS organizations (
                organization_id TEXT PRIMARY KEY,
                organization_json TEXT,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Resource flows table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resource_flows (
                flow_id TEXT PRIMARY KEY,
                flow_json TEXT,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Relationships table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                relationship_id TEXT PRIMARY KEY,
                relationship_json TEXT,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Evidence table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evidence (
                evidence_id TEXT PRIMARY KEY,
                evidence_json TEXT,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Timeline table for chronological analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS timeline (
                event_id TEXT PRIMARY KEY,
                event_date TEXT,
                event_type TEXT,
                entity_id TEXT,
                entity_type TEXT,
                description TEXT,
                confidence TEXT,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def add_person(self, person: PersonDossier) -> bool:
        """Add person to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            person.dossier_created = datetime.now().isoformat()
            person.last_updated = datetime.now().isoformat()

            def json_serializer(obj):
                if isinstance(obj, Enum):
                    return obj.value
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

            cursor.execute('''
                INSERT OR REPLACE INTO people (person_id, dossier_json, last_updated)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (person.person_id, json.dumps(asdict(person), indent=2, default=json_serializer)))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding person {person.person_id}: {e}")
            return False

    def add_organization(self, org: Organization) -> bool:
        """Add organization to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            org.created = datetime.now().isoformat()
            org.last_updated = datetime.now().isoformat()

            def json_serializer(obj):
                if isinstance(obj, Enum):
                    return obj.value
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

            cursor.execute('''
                INSERT OR REPLACE INTO organizations (organization_id, organization_json, last_updated)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (org.organization_id, json.dumps(asdict(org), indent=2, default=json_serializer)))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding organization {org.organization_id}: {e}")
            return False

    def add_relationship(self, rel: Relationship) -> bool:
        """Add relationship to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            def json_serializer(obj):
                if isinstance(obj, Enum):
                    return obj.value
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

            cursor.execute('''
                INSERT OR REPLACE INTO relationships (relationship_id, relationship_json)
                VALUES (?, ?)
            ''', (rel.relationship_id, json.dumps(asdict(rel), indent=2, default=json_serializer)))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding relationship {rel.relationship_id}: {e}")
            return False

    def search_people(self, query: str) -> List[PersonDossier]:
        """Search people by name or alias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT dossier_json FROM people
            WHERE dossier_json LIKE ?
        ''', (f'%{query}%',))

        results = []
        for row in cursor.fetchall():
            person_data = json.loads(row[0])
            # Convert dict data back to PersonDossier (simplified for demo)
            results.append(person_data)

        conn.close()
        return results

    def get_timeline(self, start_year: int = None, end_year: int = None) -> List[Dict]:
        """Get chronological timeline of events"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if start_year and end_year:
            cursor.execute('''
                SELECT * FROM timeline
                WHERE event_date BETWEEN ? AND ?
                ORDER BY event_date
            ''', (f'{start_year}-01-01', f'{end_year}-12-31'))
        else:
            cursor.execute('''
                SELECT * FROM timeline
                ORDER BY event_date
            ''')

        results = []
        for row in cursor.fetchall():
            results.append({
                'event_id': row[0],
                'event_date': row[1],
                'event_type': row[2],
                'entity_id': row[3],
                'entity_type': row[4],
                'description': row[5],
                'confidence': row[6]
            })

        conn.close()
        return results

    def analyze_relationships(self, entity_id: str) -> Dict[str, List]:
        """Analyze all relationships for an entity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT relationship_json FROM relationships
            WHERE relationship_json LIKE ? OR relationship_json LIKE ?
        ''', (f'%"entity_1": "{entity_id}"%', f'%"entity_2": "{entity_id}"%'))

        relationships = []
        for row in cursor.fetchall():
            rel_data = json.loads(row[0])
            relationships.append(Relationship(**rel_data))

        conn.close()

        # Organize by relationship type
        analysis = {
            'direct_relationships': relationships,
            'network_analysis': self._analyze_network(entity_id, relationships),
            'obscured_relationships': [r for r in relationships if r.deliberately_hidden],
            'high_significance': [r for r in relationships if r.significance == "high"]
        }

        return analysis

    def _analyze_network(self, entity_id: str, relationships: List[Relationship]) -> Dict:
        """Analyze network connections and patterns"""
        # This would implement network analysis algorithms
        # For now, return basic connection counts
        return {
            'total_connections': len(relationships),
            'connection_types': {},  # Count by relationship type
            'temporal_patterns': {},  # Patterns over time
            'potential_hidden_connections': []  # Inferred relationships
        }


def create_sample_dossier():
    """Create a sample person dossier for testing"""

    # Sample evidence
    evidence1 = Evidence(
        evidence_id="EV001",
        evidence_type=EvidenceType.DECLASSIFIED_FILE,
        description="NATO document mentioning recruitment",
        source="Operation Gladio by Paul L. Williams",
        page_reference="Page 45",
        confidence=ConfidenceLevel.PROBABLE
    )

    # Sample claim
    claim1 = Claim(
        claim_id="CL001",
        statement="Served in military intelligence unit",
        category="military_service",
        supporting_evidence=[evidence1],
        overall_confidence=ConfidenceLevel.PROBABLE,
        time_reference=TimeReference(
            year=1955,
            earliest_possible="1954-01-01",
            latest_possible="1956-12-31",
            time_description="mid-1950s",
            confidence=ConfidenceLevel.POSSIBLE
        )
    )

    # Sample person
    person = PersonDossier(
        person_id="PERS001",
        first_name="John",
        last_name="Doe",
        aliases=["Agent X", "Il Biondo"],
        birth_date=TimeReference(
            year=1925,
            month=3,
            day=15,
            confidence=ConfidenceLevel.CONFIRMED
        ),
        military_service=[claim1],
        created_by="evidence_analyst"
    )

    return person


def main():
    """Test the evidence database system"""
    print("🔍 Initializing Gladio Evidence Database...")

    db = GladioEvidenceDatabase("test_gladio.db")

    # Create sample data
    sample_person = create_sample_dossier()

    # Test database operations
    print(f"Adding sample person: {sample_person.first_name} {sample_person.last_name}")
    success = db.add_person(sample_person)
    print(f"✅ Person added successfully: {success}")

    # Test search
    results = db.search_people("John")
    print(f"🔍 Search results for 'John': {len(results)} found")

    print("\n📊 Database structure ready for Operation Gladio analysis")
    print("Ready to process:")
    print("- Person dossiers with temporal granularity")
    print("- Organization structure and operations")
    print("- Resource flow tracking")
    print("- Relationship mapping with evidence")
    print("- Cross-referenced claims with supporting/contradicting evidence")


if __name__ == "__main__":
    main()