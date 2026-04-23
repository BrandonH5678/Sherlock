#!/usr/bin/env python3
"""
Merge Mac Mini sherlock.db into J5A sherlock.db
Handles conflicts by preferring newer data
Creates backup before merging

Usage: python3 merge_sherlock_databases.py <mac_mini_db> <j5a_db>
Example: python3 merge_sherlock_databases.py /tmp/mac_mini_sherlock.db /home/johnny5/Sherlock/sherlock.db
"""

import sys
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple

class DatabaseMerger:
    """Merge Sherlock databases with conflict resolution"""

    def __init__(self, mac_mini_db: str, j5a_db: str, backup: bool = True):
        self.mac_mini_db = Path(mac_mini_db)
        self.j5a_db = Path(j5a_db)
        self.backup_enabled = backup
        self.backup_path = None

        # Statistics
        self.stats = {
            "targets_inserted": 0,
            "targets_updated": 0,
            "targets_skipped": 0,
            "packages_inserted": 0,
            "packages_updated": 0,
            "evidence_inserted": 0,
            "errors": []
        }

    def create_backup(self) -> Path:
        """Create backup of J5A database"""
        if not self.j5a_db.exists():
            raise FileNotFoundError(f"J5A database not found: {self.j5a_db}")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_path = self.j5a_db.parent / f"{self.j5a_db.stem}_backup_{timestamp}.db"

        print(f"📦 Creating backup: {self.backup_path}")
        shutil.copy2(self.j5a_db, self.backup_path)
        print(f"✅ Backup created: {self.backup_path.stat().st_size:,} bytes")

        return self.backup_path

    def merge_targets(self, mac_conn: sqlite3.Connection, j5a_conn: sqlite3.Connection):
        """Merge targets table with conflict resolution"""
        print("\n📊 Merging targets table...")

        # Get all targets from Mac Mini
        mac_cursor = mac_conn.cursor()
        mac_targets = mac_cursor.execute("""
            SELECT target_id, name, target_type, priority, status,
                   created_at, updated_at, metadata
            FROM targets
        """).fetchall()

        print(f"   Mac Mini has {len(mac_targets)} targets")

        j5a_cursor = j5a_conn.cursor()

        for target in mac_targets:
            target_id, name, target_type, priority, status, created_at, updated_at, metadata = target

            # Check if target exists in J5A (by name and type, not ID)
            existing = j5a_cursor.execute("""
                SELECT target_id, updated_at, priority, status
                FROM targets
                WHERE name = ? AND target_type = ?
            """, (name, target_type)).fetchone()

            if existing:
                existing_id, existing_updated_at, existing_priority, existing_status = existing

                # Update if Mac Mini version is newer
                if updated_at > existing_updated_at:
                    j5a_cursor.execute("""
                        UPDATE targets
                        SET priority = ?, status = ?, updated_at = ?, metadata = ?
                        WHERE target_id = ?
                    """, (priority, status, updated_at, metadata, existing_id))

                    print(f"   ✏️  Updated: {name} (P{existing_priority} → P{priority}, {existing_status} → {status})")
                    self.stats["targets_updated"] += 1
                else:
                    print(f"   ⏭️  Skipped: {name} (J5A version is newer or same)")
                    self.stats["targets_skipped"] += 1
            else:
                # Insert new target (use Mac Mini's ID)
                j5a_cursor.execute("""
                    INSERT INTO targets
                    (target_id, name, target_type, priority, status,
                     created_at, updated_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (target_id, name, target_type, priority, status,
                      created_at, updated_at, metadata))

                print(f"   ➕ Inserted: {name} (P{priority}, {status})")
                self.stats["targets_inserted"] += 1

        j5a_conn.commit()
        print(f"✅ Targets merged: {self.stats['targets_inserted']} inserted, "
              f"{self.stats['targets_updated']} updated, {self.stats['targets_skipped']} skipped")

    def merge_targeting_packages(self, mac_conn: sqlite3.Connection, j5a_conn: sqlite3.Connection):
        """Merge targeting_packages table"""
        print("\n📦 Merging targeting_packages table...")

        mac_cursor = mac_conn.cursor()

        # Check if targeting_packages table exists
        tables = mac_cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='targeting_packages'
        """).fetchall()

        if not tables:
            print("   ⚠️  No targeting_packages table in Mac Mini database")
            return

        # Get all packages from Mac Mini
        mac_packages = mac_cursor.execute("""
            SELECT * FROM targeting_packages
        """).fetchall()

        if not mac_packages:
            print("   No packages to merge")
            return

        print(f"   Mac Mini has {len(mac_packages)} packages")

        j5a_cursor = j5a_conn.cursor()

        # Get column names
        column_names = [desc[0] for desc in mac_cursor.execute("SELECT * FROM targeting_packages LIMIT 1").description]

        for package in mac_packages:
            package_dict = dict(zip(column_names, package))
            package_id = package_dict.get('package_id')
            target_id = package_dict.get('target_id')
            status = package_dict.get('status')
            updated_at = package_dict.get('updated_at')

            # Check if package exists
            existing = j5a_cursor.execute("""
                SELECT package_id, status, updated_at
                FROM targeting_packages
                WHERE package_id = ?
            """, (package_id,)).fetchone()

            if existing:
                existing_id, existing_status, existing_updated_at = existing

                # Update if Mac Mini version is newer
                if updated_at and existing_updated_at and updated_at > existing_updated_at:
                    placeholders = ', '.join([f"{col} = ?" for col in column_names if col != 'package_id'])
                    values = [package_dict[col] for col in column_names if col != 'package_id']
                    values.append(package_id)

                    j5a_cursor.execute(f"""
                        UPDATE targeting_packages
                        SET {placeholders}
                        WHERE package_id = ?
                    """, values)

                    print(f"   ✏️  Updated package {package_id} for target {target_id}")
                    self.stats["packages_updated"] += 1
            else:
                # Insert new package
                placeholders = ', '.join(['?' for _ in column_names])
                j5a_cursor.execute(f"""
                    INSERT INTO targeting_packages ({', '.join(column_names)})
                    VALUES ({placeholders})
                """, list(package_dict.values()))

                print(f"   ➕ Inserted package {package_id} for target {target_id}")
                self.stats["packages_inserted"] += 1

        j5a_conn.commit()
        print(f"✅ Packages merged: {self.stats['packages_inserted']} inserted, "
              f"{self.stats['packages_updated']} updated")

    def merge_evidence(self, mac_conn: sqlite3.Connection, j5a_conn: sqlite3.Connection):
        """Merge evidence_claims and evidence_sources tables (accumulate, no conflicts)"""
        print("\n🔍 Merging evidence tables...")

        mac_cursor = mac_conn.cursor()
        j5a_cursor = j5a_conn.cursor()

        # Check if evidence tables exist
        evidence_tables = ['evidence_claims', 'evidence_sources']

        for table_name in evidence_tables:
            tables = mac_cursor.execute("""
                SELECT name FROM sqlite_master WHERE type='table' AND name=?
            """, (table_name,)).fetchall()

            if not tables:
                print(f"   ⚠️  No {table_name} table in Mac Mini database")
                continue

            # Get all evidence from Mac Mini
            evidence_rows = mac_cursor.execute(f"SELECT * FROM {table_name}").fetchall()

            if not evidence_rows:
                print(f"   No {table_name} to merge")
                continue

            print(f"   Mac Mini has {len(evidence_rows)} {table_name} records")

            # Get column names
            column_names = [desc[0] for desc in mac_cursor.execute(f"SELECT * FROM {table_name} LIMIT 1").description]

            inserted_count = 0
            for row in evidence_rows:
                row_dict = dict(zip(column_names, row))

                # For evidence, we accumulate rather than check for conflicts
                # Just insert if it doesn't already exist (check by unique constraints)
                try:
                    placeholders = ', '.join(['?' for _ in column_names])
                    j5a_cursor.execute(f"""
                        INSERT OR IGNORE INTO {table_name} ({', '.join(column_names)})
                        VALUES ({placeholders})
                    """, list(row_dict.values()))

                    if j5a_cursor.rowcount > 0:
                        inserted_count += 1
                except Exception as e:
                    self.stats["errors"].append(f"Error inserting {table_name}: {e}")

            j5a_conn.commit()
            print(f"   ✅ {table_name}: {inserted_count} new records inserted")
            self.stats["evidence_inserted"] += inserted_count

        print(f"✅ Evidence merged: {self.stats['evidence_inserted']} total records")

    def verify_merge(self, j5a_conn: sqlite3.Connection):
        """Verify database integrity after merge"""
        print("\n🔍 Verifying merged database...")

        cursor = j5a_conn.cursor()

        # Count targets
        target_count = cursor.execute("SELECT COUNT(*) FROM targets").fetchone()[0]
        print(f"   Total targets: {target_count}")

        # Count packages
        try:
            package_count = cursor.execute("SELECT COUNT(*) FROM targeting_packages").fetchone()[0]
            print(f"   Total packages: {package_count}")
        except:
            print("   targeting_packages table does not exist")

        # Count evidence
        try:
            claims_count = cursor.execute("SELECT COUNT(*) FROM evidence_claims").fetchone()[0]
            print(f"   Total evidence claims: {claims_count}")
        except:
            print("   evidence_claims table does not exist")

        # Check for any obvious corruption
        integrity_check = cursor.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity_check == "ok":
            print(f"   ✅ Database integrity: OK")
        else:
            print(f"   ❌ Database integrity: {integrity_check}")
            self.stats["errors"].append(f"Integrity check failed: {integrity_check}")

    def merge(self) -> Dict[str, Any]:
        """Execute full database merge"""
        print("=" * 80)
        print("SHERLOCK DATABASE MERGER")
        print("=" * 80)
        print(f"Mac Mini DB: {self.mac_mini_db}")
        print(f"J5A DB:      {self.j5a_db}")
        print("=" * 80)

        # Verify source files exist
        if not self.mac_mini_db.exists():
            raise FileNotFoundError(f"Mac Mini database not found: {self.mac_mini_db}")
        if not self.j5a_db.exists():
            raise FileNotFoundError(f"J5A database not found: {self.j5a_db}")

        # Create backup
        if self.backup_enabled:
            self.create_backup()

        # Connect to databases
        print("\n🔌 Connecting to databases...")
        mac_conn = sqlite3.connect(str(self.mac_mini_db))
        j5a_conn = sqlite3.connect(str(self.j5a_db))

        try:
            # Merge tables
            self.merge_targets(mac_conn, j5a_conn)
            self.merge_targeting_packages(mac_conn, j5a_conn)
            self.merge_evidence(mac_conn, j5a_conn)

            # Verify
            self.verify_merge(j5a_conn)

            # Report
            print("\n" + "=" * 80)
            print("MERGE COMPLETE")
            print("=" * 80)
            print(f"Targets:  {self.stats['targets_inserted']} inserted, "
                  f"{self.stats['targets_updated']} updated, {self.stats['targets_skipped']} skipped")
            print(f"Packages: {self.stats['packages_inserted']} inserted, "
                  f"{self.stats['packages_updated']} updated")
            print(f"Evidence: {self.stats['evidence_inserted']} records inserted")

            if self.stats['errors']:
                print(f"\n⚠️  {len(self.stats['errors'])} errors occurred:")
                for error in self.stats['errors']:
                    print(f"   - {error}")
            else:
                print("\n✅ No errors")

            if self.backup_path:
                print(f"\n📦 Backup saved: {self.backup_path}")

            print("=" * 80)

        finally:
            mac_conn.close()
            j5a_conn.close()

        return self.stats


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 merge_sherlock_databases.py <mac_mini_db> <j5a_db>")
        print("\nExample:")
        print("  python3 merge_sherlock_databases.py \\")
        print("    /tmp/mac_mini_sherlock.db \\")
        print("    /home/johnny5/Sherlock/sherlock.db")
        sys.exit(1)

    mac_mini_db = sys.argv[1]
    j5a_db = sys.argv[2]

    merger = DatabaseMerger(mac_mini_db, j5a_db, backup=True)
    stats = merger.merge()

    # Exit with error code if errors occurred
    if stats['errors']:
        sys.exit(1)
    else:
        print("\n✅ Database merge successful!")
        sys.exit(0)


if __name__ == "__main__":
    main()
