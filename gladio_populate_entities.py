#!/usr/bin/env python3
"""
Operation Gladio Database Population
Loads entity dossiers into gladio_intelligence.db

Design: Populate people and organizations tables from dossier JSON
Memory: <200MB
Pattern: Atomic inserts with duplicate detection
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class GladioEntityPopulator:
    """Populate gladio_intelligence.db with entities from dossiers"""

    def __init__(self, db_path: Path, dossiers_path: Path):
        self.db_path = Path(db_path)
        self.dossiers_path = Path(dossiers_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()

    def load_dossiers(self) -> Dict:
        """Load dossiers from JSON file"""
        with open(self.dossiers_path) as f:
            data = json.load(f)
        return data

    def add_person(self, person_data: Dict) -> bool:
        """Add person to database"""
        try:
            # Create JSON blob
            person_json = json.dumps({
                'name': person_data['name'],
                'aliases': person_data.get('aliases', []),
                'mention_count': person_data.get('mention_count', 0),
                'first_appearance_line': person_data.get('first_appearance_line', 0),
                'roles': person_data.get('roles', []),
                'affiliations': person_data.get('affiliations', []),
                'contexts': person_data.get('contexts', [])[:5],  # Keep top 5
                'confidence': person_data.get('confidence', 0.8)
            })

            # Generate ID from name (lowercase, no spaces)
            person_id = person_data['name'].lower().replace(' ', '_').replace('.', '')

            # Insert or replace
            self.cursor.execute('''
                INSERT OR REPLACE INTO people (person_id, dossier_json, created, last_updated)
                VALUES (?, ?, ?, ?)
            ''', (
                person_id,
                person_json,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))

            return True

        except Exception as e:
            print(f"ERROR adding person {person_data.get('name', 'UNKNOWN')}: {e}")
            return False

    def add_organization(self, org_data: Dict) -> bool:
        """Add organization to database"""
        try:
            # Create JSON blob
            org_json = json.dumps({
                'name': org_data['name'],
                'aliases': org_data.get('aliases', []),
                'mention_count': org_data.get('mention_count', 0),
                'first_appearance_line': org_data.get('first_appearance_line', 0),
                'affiliations': org_data.get('affiliations', []),
                'contexts': org_data.get('contexts', [])[:5],  # Keep top 5
                'confidence': org_data.get('confidence', 0.8)
            })

            # Generate ID from name
            org_id = org_data['name'].lower().replace(' ', '_').replace('.', '')

            # Insert or replace
            self.cursor.execute('''
                INSERT OR REPLACE INTO organizations (organization_id, organization_json, created, last_updated)
                VALUES (?, ?, ?, ?)
            ''', (
                org_id,
                org_json,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))

            return True

        except Exception as e:
            print(f"ERROR adding organization {org_data.get('name', 'UNKNOWN')}: {e}")
            return False

    def populate(self) -> Dict[str, int]:
        """Populate database from dossiers"""

        print(f"Loading dossiers from {self.dossiers_path}...")
        data = self.load_dossiers()

        dossiers = data['dossiers']
        metadata = data['metadata']

        print(f"  Total entities: {metadata['total_entities']}")
        print(f"  People: {metadata['people']}")
        print(f"  Organizations: {metadata['organizations']}")

        people_inserted = 0
        orgs_inserted = 0
        errors = 0

        print("\nPopulating database...")

        for name, dossier in dossiers.items():
            if dossier['entity_type'] == 'person':
                if self.add_person(dossier):
                    people_inserted += 1
                else:
                    errors += 1

            elif dossier['entity_type'] == 'organization':
                if self.add_organization(dossier):
                    orgs_inserted += 1
                else:
                    errors += 1

        # Commit transaction
        self.conn.commit()

        print(f"\nPopulation complete!")
        print(f"  People inserted: {people_inserted}")
        print(f"  Organizations inserted: {orgs_inserted}")
        print(f"  Errors: {errors}")

        return {
            'people_inserted': people_inserted,
            'orgs_inserted': orgs_inserted,
            'errors': errors
        }

    def verify_population(self) -> Dict[str, int]:
        """Verify database was populated correctly"""

        # Count people
        self.cursor.execute("SELECT COUNT(*) FROM people")
        people_count = self.cursor.fetchone()[0]

        # Count organizations
        self.cursor.execute("SELECT COUNT(*) FROM organizations")
        orgs_count = self.cursor.fetchone()[0]

        print("\n" + "="*60)
        print("DATABASE VERIFICATION:")
        print("="*60)
        print(f"People in database: {people_count}")
        print(f"Organizations in database: {orgs_count}")

        # Show sample people
        print("\nSample people:")
        self.cursor.execute("SELECT person_id, dossier_json FROM people LIMIT 5")
        for person_id, json_data in self.cursor.fetchall():
            data = json.loads(json_data)
            print(f"  {data['name']} (mentions: {data.get('mention_count', 0)})")

        # Show sample organizations
        print("\nSample organizations:")
        self.cursor.execute("SELECT organization_id, organization_json FROM organizations LIMIT 5")
        for org_id, json_data in self.cursor.fetchall():
            data = json.loads(json_data)
            print(f"  {data['name']} (mentions: {data.get('mention_count', 0)})")

        return {
            'people_count': people_count,
            'orgs_count': orgs_count
        }

    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    """Populate gladio_intelligence.db with entities"""

    db_path = Path("/home/johnny5/Sherlock/gladio_intelligence.db")
    dossiers_path = Path("/home/johnny5/Sherlock/audiobooks/operation_gladio/entity_dossiers.json")

    if not dossiers_path.exists():
        print(f"ERROR: Dossiers file not found: {dossiers_path}")
        return

    if not db_path.exists():
        print(f"ERROR: Database not found: {db_path}")
        print("Please create database schema first.")
        return

    populator = GladioEntityPopulator(db_path, dossiers_path)

    # Populate
    stats = populator.populate()

    # Verify
    verification = populator.verify_population()

    # Close
    populator.close()

    print("\n" + "="*60)
    print("POPULATION SUMMARY:")
    print("="*60)
    print(f"✅ {stats['people_inserted']} people inserted")
    print(f"✅ {stats['orgs_inserted']} organizations inserted")
    print(f"✅ {verification['people_count']} total people in database")
    print(f"✅ {verification['orgs_count']} total organizations in database")

    if stats['errors'] > 0:
        print(f"⚠️  {stats['errors']} errors encountered")


if __name__ == "__main__":
    main()
