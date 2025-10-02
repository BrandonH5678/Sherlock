#!/usr/bin/env python3
"""
Sherlock Targeting CLI

Command-line interface for Targeting Officer and package management.

Commands:
    # Targets
    python3 sherlock_targeting_cli.py target list
    python3 sherlock_targeting_cli.py target show <id>

    # Packages
    python3 sherlock_targeting_cli.py pkg list [--status STATUS]
    python3 sherlock_targeting_cli.py pkg show <id>
    python3 sherlock_targeting_cli.py pkg create --target <id>

    # Targeting Officer
    python3 sherlock_targeting_cli.py officer run
    python3 sherlock_targeting_cli.py officer status
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from sherlock_targeting_officer import TargetingOfficer, Package, PackageType, PackageStatus, ValidationLevel


def format_table(headers, rows):
    """Simple table formatting"""
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    # Print header
    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    print(header_line)
    print("-" * len(header_line))

    # Print rows
    for row in rows:
        print(" | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)))


def target_list(db_path):
    """List all targets"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT target_id, name, target_type, priority, status
        FROM targets
        ORDER BY priority ASC, name ASC
    ''')

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No targets found.")
        return

    headers = ["ID", "Name", "Type", "Priority", "Status"]
    format_table(headers, rows)
    print(f"\nTotal: {len(rows)} targets")


def target_show(db_path, target_id):
    """Show target details"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT target_id, name, target_type, priority, status, created_at, updated_at, metadata
        FROM targets
        WHERE target_id = ?
    ''', (target_id,))

    row = cursor.fetchone()

    if not row:
        print(f"Target {target_id} not found")
        conn.close()
        return

    print(f"\nTarget Details:")
    print(f"  ID: {row[0]}")
    print(f"  Name: {row[1]}")
    print(f"  Type: {row[2]}")
    print(f"  Priority: {row[3]}")
    print(f"  Status: {row[4]}")
    print(f"  Created: {row[5]}")
    print(f"  Updated: {row[6]}")

    metadata = json.loads(row[7]) if row[7] else {}
    if metadata:
        print(f"\n  Metadata:")
        for key, value in metadata.items():
            print(f"    {key}: {value}")

    # Get packages
    cursor.execute('''
        SELECT package_id, version, package_type, status, created_at
        FROM targeting_packages
        WHERE target_id = ?
        ORDER BY version DESC
    ''', (target_id,))

    packages = cursor.fetchall()
    conn.close()

    if packages:
        print(f"\nPackages ({len(packages)}):")
        headers = ["ID", "Ver", "Type", "Status", "Created"]
        format_table(headers, packages)


def pkg_list(db_path, status=None):
    """List packages"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = '''
        SELECT p.package_id, t.name, p.package_type, p.status, p.created_at
        FROM targeting_packages p
        JOIN targets t ON p.target_id = t.target_id
        WHERE 1=1
    '''
    params = []

    if status:
        query += " AND p.status = ?"
        params.append(status)

    query += " ORDER BY p.created_at DESC LIMIT 50"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No packages found.")
        return

    headers = ["ID", "Target", "Type", "Status", "Created"]
    format_table(headers, rows)
    print(f"\nTotal: {len(rows)} packages")


def pkg_show(db_path, package_id):
    """Show package details"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT p.*, t.name
        FROM targeting_packages p
        JOIN targets t ON p.target_id = t.target_id
        WHERE p.package_id = ?
    ''', (package_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        print(f"Package {package_id} not found")
        return

    print(f"\nPackage Details:")
    print(f"  Package ID: {row[0]}")
    print(f"  Target: {row[11]} (ID: {row[1]})")
    print(f"  Version: {row[2]}")
    print(f"  Type: {row[3]}")
    print(f"  Status: {row[4]}")
    print(f"  Validation Level: {row[7]}")
    print(f"  Created: {row[8]}")

    collection_urls = json.loads(row[5])
    print(f"\n  Collection URLs ({len(collection_urls)}):")
    for i, url in enumerate(collection_urls, 1):
        print(f"    {i}. {url}")

    expected_outputs = json.loads(row[6])
    print(f"\n  Expected Outputs ({len(expected_outputs)}):")
    for i, output in enumerate(expected_outputs, 1):
        print(f"    {i}. {output}")


def pkg_create(db_path, target_id):
    """Create package for target"""
    officer = TargetingOfficer(db_path=db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT name, target_type, priority, metadata
        FROM targets
        WHERE target_id = ?
    ''', (target_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        print(f"Target {target_id} not found")
        return

    name, target_type, priority, metadata_json = row
    metadata = json.loads(metadata_json) if metadata_json else {}

    print(f"Creating package for: {name}")

    # Create package
    package = officer.create_package(
        target_id=target_id,
        target_name=name,
        target_type=target_type,
        priority=priority,
        metadata=metadata
    )

    # Save package
    package_id = officer.save_package(package)

    print(f"\n✅ Package created:")
    print(f"   Package ID: {package_id}")
    print(f"   Type: {package.package_type.value}")
    print(f"   Status: {package.status.value}")
    print(f"   URLs: {len(package.collection_urls)}")
    print(f"   Outputs: {len(package.expected_outputs)}")


def officer_run(db_path):
    """Run Targeting Officer sweep"""
    officer = TargetingOfficer(db_path=db_path)

    print("Running Targeting Officer sweep...")
    print("=" * 70)

    report = officer.run_daily_sweep()

    print(f"\nSweep completed: {report.sweep_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nResults:")
    print(f"  Targets scanned: {report.targets_scanned}")
    print(f"  Targets needing packages: {report.targets_needing_packages}")
    print(f"  Packages created: {report.packages_created}")
    print(f"  Packages validated: {report.packages_validated}")
    print(f"  Packages submitted to J5A: {report.packages_submitted_to_j5a}")

    if report.errors:
        print(f"\nErrors:")
        for error in report.errors:
            print(f"  ⚠️  {error}")

    if report.created_packages:
        print(f"\nCreated Packages ({len(report.created_packages)}):")
        for pkg in report.created_packages[:20]:
            print(f"  [{pkg['package_id']}] {pkg['target_name']} ({pkg['package_type']}) - {pkg['status']}")


def officer_status(db_path):
    """Show Targeting Officer status"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\nTargeting Officer Status")
    print("=" * 70)

    # Targets by status
    cursor.execute('''
        SELECT status, COUNT(*)
        FROM targets
        GROUP BY status
    ''')
    target_stats = cursor.fetchall()

    print("\nTargets by Status:")
    if target_stats:
        format_table(["Status", "Count"], target_stats)

    # Packages by status
    cursor.execute('''
        SELECT status, COUNT(*)
        FROM targeting_packages
        GROUP BY status
    ''')
    package_stats = cursor.fetchall()

    print("\nPackages by Status:")
    if package_stats:
        format_table(["Status", "Count"], package_stats)

    conn.close()


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    db_path = "sherlock.db"
    command = sys.argv[1]

    if command == "target":
        if len(sys.argv) < 3:
            print("Usage: sherlock_targeting_cli.py target <list|show>")
            sys.exit(1)

        subcommand = sys.argv[2]

        if subcommand == "list":
            target_list(db_path)
        elif subcommand == "show":
            if len(sys.argv) < 4:
                print("Usage: sherlock_targeting_cli.py target show <id>")
                sys.exit(1)
            target_show(db_path, int(sys.argv[3]))

    elif command == "pkg":
        if len(sys.argv) < 3:
            print("Usage: sherlock_targeting_cli.py pkg <list|show|create>")
            sys.exit(1)

        subcommand = sys.argv[2]

        if subcommand == "list":
            status = None
            if "--status" in sys.argv:
                status = sys.argv[sys.argv.index("--status") + 1]
            pkg_list(db_path, status=status)

        elif subcommand == "show":
            if len(sys.argv) < 4:
                print("Usage: sherlock_targeting_cli.py pkg show <id>")
                sys.exit(1)
            pkg_show(db_path, int(sys.argv[3]))

        elif subcommand == "create":
            if "--target" not in sys.argv:
                print("Usage: sherlock_targeting_cli.py pkg create --target <id>")
                sys.exit(1)
            pkg_create(db_path, int(sys.argv[sys.argv.index("--target") + 1]))

    elif command == "officer":
        if len(sys.argv) < 3:
            print("Usage: sherlock_targeting_cli.py officer <run|status>")
            sys.exit(1)

        subcommand = sys.argv[2]

        if subcommand == "run":
            officer_run(db_path)
        elif subcommand == "status":
            officer_status(db_path)

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
