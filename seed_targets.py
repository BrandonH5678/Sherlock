#!/usr/bin/env python3
"""
Sherlock Target Seed List Import

Loads initial high-priority targets into the targets table.

Usage:
    python3 seed_targets.py --db sherlock.db
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict

# Target seed data
SEED_TARGETS = [
    # Works / Sources (Books, Programs, Orgs)
    {
        "name": "A People's History of the United States — Howard Zinn",
        "target_type": "book",
        "priority": 3,
        "status": "new",
        "metadata": {"notes": "Baseline historical context", "author": "Howard Zinn"}
    },
    {
        "name": "American Alchemy Interviews with Danny Sheehan",
        "target_type": "interview_series",
        "priority": 2,
        "status": "new",
        "metadata": {"notes": "Podcasts/interviews", "subject": "Danny Sheehan"}
    },
    {
        "name": "American Alchemy with Harald Malmgren",
        "target_type": "interview_series",
        "priority": 2,
        "status": "new",
        "metadata": {"notes": "Requires special processing relying on captions", "subject": "Harald Malmgren"}
    },
    {
        "name": "Danny Sheehan Bibliography",
        "target_type": "book_collection",
        "priority": 2,
        "status": "new",
        "metadata": {"notes": "Collect all books by Danny Sheehan", "author": "Danny Sheehan"}
    },
    {
        "name": "Imminent — Luis Elizondo",
        "target_type": "book",
        "priority": 1,
        "status": "new",
        "metadata": {"author": "Luis Elizondo", "topic": "UAP disclosure"}
    },
    {
        "name": "Weaponized Podcast",
        "target_type": "podcast_series",
        "priority": 1,
        "status": "new",
        "metadata": {"hosts": "Jeremy Corbell & George Knapp", "notes": "All episodes"}
    },
    {
        "name": "The Day After Roswell — Colonel Philip J. Corso",
        "target_type": "book",
        "priority": 2,
        "status": "new",
        "metadata": {"author": "Colonel Philip J. Corso", "topic": "Roswell aftermath"}
    },
    {
        "name": "US Army INSCOM",
        "target_type": "org",
        "priority": 2,
        "status": "new",
        "metadata": {"full_name": "Intelligence & Security Command", "branch": "US Army"}
    },
    {
        "name": "US Naval Intelligence",
        "target_type": "org",
        "priority": 2,
        "status": "new",
        "metadata": {"branch": "US Navy"}
    },
    {
        "name": "Soviet Psychic Program",
        "target_type": "program",
        "priority": 3,
        "status": "new",
        "metadata": {"topic": "ESP/remote viewing", "country": "Soviet Union"}
    },
    {
        "name": "US Radar Lab (Naval Intelligence, 1930s)",
        "target_type": "org_unit",
        "priority": 3,
        "status": "new",
        "metadata": {"notes": "Early radar research", "era": "1930s", "parent_org": "US Naval Intelligence"}
    },
    {
        "name": "S-Force",
        "target_type": "program",
        "priority": 1,
        "status": "new",
        "metadata": {"notes": "Requires disambiguation", "classification": "classified"}
    },
    {
        "name": "MK-Ultra and MK Programs",
        "target_type": "program_cluster",
        "priority": 1,
        "status": "under_research",
        "metadata": {"notes": "All MK programs", "agency": "CIA", "era": "1950s-1970s"}
    },
    {
        "name": "Brown Brothers Harriman",
        "target_type": "org",
        "priority": 2,
        "status": "new",
        "metadata": {"notes": "Bank/finance linkages", "industry": "finance"}
    },
    {
        "name": "Sullivan & Cromwell",
        "target_type": "org",
        "priority": 1,
        "status": "under_research",
        "metadata": {"notes": "Law firm/intel ties", "industry": "law", "operations": "Iran 1953, Guatemala 1954, Chile 1973"}
    },
    {
        "name": "TSMC",
        "target_type": "org",
        "priority": 1,
        "status": "under_research",
        "metadata": {
            "full_name": "Taiwan Semiconductor Manufacturing Company",
            "notes": "Critical tech node",
            "industry": "semiconductors",
            "era": "1987-present"
        }
    },

    # People (Individuals / Entities)
    {
        "name": "Allen Dulles",
        "target_type": "person",
        "priority": 1,
        "status": "new",
        "metadata": {"role": "CIA Director 1953–61", "related_ops": ["Guatemala", "Cuba"]}
    },
    {
        "name": "Thomas Townsend Brown",
        "target_type": "person",
        "priority": 2,
        "status": "new",
        "metadata": {"field": "Electrogravitics"}
    },
    {
        "name": "John Trump",
        "target_type": "person",
        "priority": 2,
        "status": "new",
        "metadata": {"notes": "DJT's uncle, MIT professor, Tesla papers", "affiliation": "MIT"}
    },
    {
        "name": "James Jesus Angleton",
        "target_type": "person",
        "priority": 1,
        "status": "new",
        "metadata": {"role": "CIA counterintelligence"}
    },
    {
        "name": "Curtis LeMay",
        "target_type": "person",
        "priority": 2,
        "status": "new",
        "metadata": {"role": "USAF general"}
    },
    {
        "name": "Harald Malmgren",
        "target_type": "person",
        "priority": 2,
        "status": "new",
        "metadata": {"notes": "Adviser, American Alchemy"}
    },
    {
        "name": "Luis Elizondo",
        "target_type": "person",
        "priority": 1,
        "status": "new",
        "metadata": {"role": "Former AATIP head", "topic": "UAP disclosure"}
    },
    {
        "name": "Dr. James Lacatski",
        "target_type": "person",
        "priority": 1,
        "status": "new",
        "metadata": {"affiliation": "DIA/AATIP"}
    },
    {
        "name": "Bigelow Aerospace",
        "target_type": "org",
        "priority": 1,
        "status": "new",
        "metadata": {"notes": "Contractor (NIDS/BAASS)", "industry": "aerospace/research"}
    },
    {
        "name": "Joseph McMoneagle",
        "target_type": "person",
        "priority": 2,
        "status": "new",
        "metadata": {"role": "Remote viewer, US Army"}
    },
    {
        "name": "Ingo Swann",
        "target_type": "person",
        "priority": 2,
        "status": "new",
        "metadata": {"role": "Remote viewing pioneer"}
    },
    {
        "name": "Pat Price",
        "target_type": "person",
        "priority": 2,
        "status": "new",
        "metadata": {"role": "Remote viewer"}
    },
    {
        "name": "Agnew Bahnson",
        "target_type": "person",
        "priority": 3,
        "status": "new",
        "metadata": {"notes": "Bahnson Labs, antigravity"}
    },
    {
        "name": "Wernher von Braun",
        "target_type": "person",
        "priority": 2,
        "status": "new",
        "metadata": {"role": "Rocket engineer, NASA"}
    },
    {
        "name": "George H. W. Bush",
        "target_type": "person",
        "priority": 1,
        "status": "new",
        "metadata": {"roles": "CIA, US President"}
    },
    {
        "name": "Henry Kissinger",
        "target_type": "person",
        "priority": 1,
        "status": "new",
        "metadata": {"role": "Policy, secrecy networks"}
    },
    {
        "name": "George Joannides",
        "target_type": "person",
        "priority": 2,
        "status": "new",
        "metadata": {"role": "CIA officer (JFK files)"}
    },
    {
        "name": "George Tenet",
        "target_type": "person",
        "priority": 2,
        "status": "new",
        "metadata": {"role": "CIA Director"}
    },
    {
        "name": "Osama bin Laden",
        "target_type": "person",
        "priority": 2,
        "status": "new",
        "metadata": {"role": "AQ leader"}
    },
    {
        "name": "Hal Puthoff",
        "target_type": "person",
        "priority": 1,
        "status": "new",
        "metadata": {"role": "Physicist, remote viewing"}
    },
    {
        "name": "Richard Bissell",
        "target_type": "person",
        "priority": 2,
        "status": "new",
        "metadata": {"role": "CIA planning"}
    },
    {
        "name": "Vladimir Lenin",
        "target_type": "person",
        "priority": 3,
        "status": "new",
        "metadata": {"role": "Soviet state founder"}
    },
    {
        "name": "Albert Stubblebine",
        "target_type": "person",
        "priority": 2,
        "status": "new",
        "metadata": {"role": "US Army Intel/psychic"}
    },
]


def init_database(db_path: str):
    """Initialize targets table if it doesn't exist"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS targets (
            target_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            target_type TEXT NOT NULL,
            priority INTEGER DEFAULT 3,
            status TEXT DEFAULT 'new',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            metadata JSON
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_target_type ON targets(target_type)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_priority ON targets(priority)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_status ON targets(status)
    ''')

    conn.commit()
    conn.close()
    print(f"✅ Database initialized: {db_path}")


def import_targets(db_path: str, targets: List[Dict]) -> int:
    """Import targets into database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    imported = 0
    skipped = 0

    for target in targets:
        # Check if target already exists
        cursor.execute(
            'SELECT target_id FROM targets WHERE name = ?',
            (target['name'],)
        )
        existing = cursor.fetchone()

        if existing:
            print(f"⏭️  Skipped (exists): {target['name']}")
            skipped += 1
            continue

        # Insert new target
        cursor.execute('''
            INSERT INTO targets (name, target_type, priority, status, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            target['name'],
            target['target_type'],
            target['priority'],
            target['status'],
            json.dumps(target['metadata'])
        ))

        imported += 1
        print(f"✅ Imported: {target['name']} ({target['target_type']}, priority {target['priority']})")

    conn.commit()
    conn.close()

    return imported, skipped


def display_summary(db_path: str):
    """Display summary of targets by type and priority"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\n" + "=" * 70)
    print("TARGET LIBRARY SUMMARY")
    print("=" * 70)

    # Total count
    cursor.execute('SELECT COUNT(*) FROM targets')
    total = cursor.fetchone()[0]
    print(f"\nTotal targets: {total}")

    # By type
    print("\nBy Type:")
    cursor.execute('''
        SELECT target_type, COUNT(*) as count
        FROM targets
        GROUP BY target_type
        ORDER BY count DESC
    ''')
    for target_type, count in cursor.fetchall():
        print(f"  {target_type}: {count}")

    # By priority
    print("\nBy Priority:")
    cursor.execute('''
        SELECT priority, COUNT(*) as count
        FROM targets
        GROUP BY priority
        ORDER BY priority ASC
    ''')
    priority_labels = {1: "Critical", 2: "High", 3: "Medium", 4: "Low", 5: "Background"}
    for priority, count in cursor.fetchall():
        label = priority_labels.get(priority, "Unknown")
        print(f"  {priority} ({label}): {count}")

    # By status
    print("\nBy Status:")
    cursor.execute('''
        SELECT status, COUNT(*) as count
        FROM targets
        GROUP BY status
        ORDER BY count DESC
    ''')
    for status, count in cursor.fetchall():
        print(f"  {status}: {count}")

    # Top priority targets
    print("\nTop Priority Targets (Priority 1):")
    cursor.execute('''
        SELECT name, target_type, status
        FROM targets
        WHERE priority = 1
        ORDER BY name
    ''')
    for name, target_type, status in cursor.fetchall():
        print(f"  • {name} ({target_type}) - {status}")

    conn.close()
    print("\n" + "=" * 70)


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Import Sherlock target seed list")
    parser.add_argument(
        '--db',
        default='sherlock.db',
        help='Database path (default: sherlock.db)'
    )
    parser.add_argument(
        '--init-only',
        action='store_true',
        help='Only initialize database, do not import'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Sherlock Target Seed List Import")
    print("=" * 70)
    print()

    # Initialize database
    init_database(args.db)

    if args.init_only:
        print("\n✅ Database initialization complete (--init-only specified)")
        return

    # Import targets
    print(f"\nImporting {len(SEED_TARGETS)} targets...")
    print("-" * 70)

    imported, skipped = import_targets(args.db, SEED_TARGETS)

    print()
    print(f"✅ Import complete: {imported} imported, {skipped} skipped")

    # Display summary
    display_summary(args.db)


if __name__ == "__main__":
    main()
