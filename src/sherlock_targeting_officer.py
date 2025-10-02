#!/usr/bin/env python3
"""
Sherlock Targeting Officer

Automated system ensuring all research targets have valid packages.

DETERMINISTIC AUTOMATION:
- Nightly scan at 1am via J5A overnight queue
- Create packages for targets without valid research plans
- Validate packages through V0/V1/V2 gates
- Submit ready packages to J5A for execution scheduling

Package Lifecycle:
  draft → ready → submitted → queued → running → completed → validated → closed

Usage:
    from src.sherlock_targeting_officer import TargetingOfficer

    officer = TargetingOfficer(db_path="sherlock.db")
    report = officer.run_daily_sweep()
    print(report)
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class TargetStatus(Enum):
    """Target research status"""
    NEW = "new"
    UNDER_RESEARCH = "under_research"
    VALIDATED = "validated"
    CLOSED = "closed"


class PackageStatus(Enum):
    """Package lifecycle status"""
    DRAFT = "draft"
    READY = "ready"
    SUBMITTED = "submitted"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    VALIDATED = "validated"
    CLOSED = "closed"


class PackageType(Enum):
    """Research package types"""
    YOUTUBE = "youtube"
    DOCUMENT = "document"
    COMPOSITE = "composite"


class ValidationLevel(Enum):
    """Package validation levels"""
    V0 = "v0"  # Schema validation
    V1 = "v1"  # Execution validation
    V2 = "v2"  # Output conformance validation


@dataclass
class Package:
    """Targeting package"""
    package_id: Optional[int]
    target_id: int
    target_name: str
    version: int
    package_type: PackageType
    status: PackageStatus
    collection_urls: List[str]
    expected_outputs: List[str]
    validation_level: ValidationLevel
    created_at: datetime
    updated_at: datetime
    metadata: Dict

    def to_dict(self):
        return {
            'package_id': self.package_id,
            'target_id': self.target_id,
            'target_name': self.target_name,
            'version': self.version,
            'package_type': self.package_type.value,
            'status': self.status.value,
            'collection_urls': self.collection_urls,
            'expected_outputs': self.expected_outputs,
            'validation_level': self.validation_level.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class SweepReport:
    """Daily sweep report"""
    sweep_time: datetime
    targets_scanned: int
    targets_needing_packages: int
    packages_created: int
    packages_validated: int
    packages_submitted_to_j5a: int
    packages_failed_validation: int
    errors: List[str]
    created_packages: List[Dict]

    def to_dict(self):
        return {
            'sweep_time': self.sweep_time.isoformat(),
            'targets_scanned': self.targets_scanned,
            'targets_needing_packages': self.targets_needing_packages,
            'packages_created': self.packages_created,
            'packages_validated': self.packages_validated,
            'packages_submitted_to_j5a': self.packages_submitted_to_j5a,
            'packages_failed_validation': self.packages_failed_validation,
            'errors': self.errors,
            'created_packages': self.created_packages
        }


class TargetingOfficer:
    """
    Automated targeting officer for Sherlock.

    DETERMINISTIC RULES:
    1. Scan all targets daily
    2. Create packages for targets without valid plans
    3. Validate packages (V0 → V1 → V2)
    4. Submit ready packages to J5A queue
    """

    # Package creation heuristics
    YOUTUBE_KEYWORDS = ['podcast', 'interview', 'series', 'channel', 'video']
    DOCUMENT_KEYWORDS = ['book', 'document', 'report', 'paper', 'declassified']
    COMPOSITE_KEYWORDS = ['person', 'org', 'operation', 'event', 'program']

    def __init__(self, db_path: str = "sherlock.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Targets table (should already exist from seed_targets.py)
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

        # Targeting packages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS targeting_packages (
                package_id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id INTEGER NOT NULL,
                version INTEGER DEFAULT 1,
                package_type TEXT NOT NULL,
                status TEXT DEFAULT 'draft',
                collection_urls JSON,
                expected_outputs JSON,
                validation_level TEXT DEFAULT 'v0',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata JSON,
                FOREIGN KEY (target_id) REFERENCES targets(target_id)
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_package_target ON targeting_packages(target_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_package_status ON targeting_packages(status)
        ''')

        conn.commit()
        conn.close()

    def _determine_package_type(self, target_name: str, target_type: str, metadata: Dict) -> PackageType:
        """
        Deterministic package type selection.

        Rules:
        1. If target_type contains youtube keywords → YOUTUBE
        2. If target_type contains document keywords → DOCUMENT
        3. Otherwise → COMPOSITE (person/org/operation research)
        """
        name_lower = target_name.lower()
        type_lower = target_type.lower()
        notes = metadata.get('notes', '').lower()

        combined = f"{name_lower} {type_lower} {notes}"

        # Check for YouTube content
        if any(keyword in combined for keyword in self.YOUTUBE_KEYWORDS):
            return PackageType.YOUTUBE

        # Check for document content
        if any(keyword in combined for keyword in self.DOCUMENT_KEYWORDS):
            return PackageType.DOCUMENT

        # Default to composite for complex targets
        return PackageType.COMPOSITE

    def _generate_collection_urls(
        self,
        target_name: str,
        target_type: str,
        package_type: PackageType,
        metadata: Dict
    ) -> List[str]:
        """
        Generate initial collection URLs based on target.

        Deterministic heuristics for common sources.
        """
        urls = []

        if package_type == PackageType.YOUTUBE:
            # Generate YouTube search URL
            search_query = target_name.replace(' ', '+')
            urls.append(f"https://www.youtube.com/results?search_query={search_query}")

            # If podcast, add podcast-specific search
            if 'podcast' in target_type.lower():
                urls.append(f"https://www.youtube.com/@{target_name.replace(' ', '')}/videos")

        elif package_type == PackageType.DOCUMENT:
            # Generate document search URLs
            if 'book' in target_type.lower():
                # Google Books
                book_query = target_name.replace(' ', '+')
                urls.append(f"https://books.google.com/books?q={book_query}")

            if 'declassified' in metadata.get('notes', '').lower():
                # CIA FOIA
                urls.append("https://www.cia.gov/readingroom/")
                # NSA declassified
                urls.append("https://www.nsa.gov/news-features/declassified-documents/")

        else:  # COMPOSITE
            # Multi-source research
            search_query = target_name.replace(' ', '+')

            # General web search
            urls.append(f"https://www.google.com/search?q={search_query}")

            # If person, add biographical sources
            if target_type == 'person':
                urls.append(f"https://en.wikipedia.org/wiki/{target_name.replace(' ', '_')}")

        return urls

    def _generate_expected_outputs(
        self,
        target_name: str,
        package_type: PackageType
    ) -> List[str]:
        """
        Generate expected outputs based on package type.

        Deterministic output specifications.
        """
        safe_name = target_name.replace(' ', '_').replace('—', '-').lower()
        outputs = []

        if package_type == PackageType.YOUTUBE:
            outputs.extend([
                f"transcripts/{safe_name}_transcript.json",
                f"diarization/{safe_name}_speakers.json",
                f"evidence/{safe_name}_claims.json",
                f"media/{safe_name}_audio.mp3"
            ])

        elif package_type == PackageType.DOCUMENT:
            outputs.extend([
                f"documents/{safe_name}_text.txt",
                f"evidence/{safe_name}_claims.json",
                f"analysis/{safe_name}_summary.json"
            ])

        else:  # COMPOSITE
            outputs.extend([
                f"research/{safe_name}_overview.json",
                f"evidence/{safe_name}_claims.json",
                f"timeline/{safe_name}_events.json",
                f"network/{safe_name}_connections.json"
            ])

        return outputs

    def _validate_package_v0(self, package: Package) -> Tuple[bool, List[str]]:
        """
        V0 Validation: Schema validation.

        Rules:
        - Must have target_id
        - Must have package_type
        - Must have collection_urls (at least 1)
        - Must have expected_outputs (at least 1)
        """
        errors = []

        if not package.target_id:
            errors.append("Missing target_id")

        if not package.package_type:
            errors.append("Missing package_type")

        if not package.collection_urls or len(package.collection_urls) == 0:
            errors.append("Missing collection_urls")

        if not package.expected_outputs or len(package.expected_outputs) == 0:
            errors.append("Missing expected_outputs")

        return len(errors) == 0, errors

    def create_package(
        self,
        target_id: int,
        target_name: str,
        target_type: str,
        priority: int,
        metadata: Dict
    ) -> Package:
        """
        Create targeting package for a target.

        Deterministic package generation based on target characteristics.
        """
        # Determine package type
        package_type = self._determine_package_type(target_name, target_type, metadata)

        # Generate collection URLs
        collection_urls = self._generate_collection_urls(
            target_name,
            target_type,
            package_type,
            metadata
        )

        # Generate expected outputs
        expected_outputs = self._generate_expected_outputs(target_name, package_type)

        # Create package
        package = Package(
            package_id=None,  # Will be assigned on insert
            target_id=target_id,
            target_name=target_name,
            version=1,
            package_type=package_type,
            status=PackageStatus.DRAFT,
            collection_urls=collection_urls,
            expected_outputs=expected_outputs,
            validation_level=ValidationLevel.V0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={
                'target_type': target_type,
                'priority': priority,
                'auto_generated': True,
                'targeting_officer_version': '1.0'
            }
        )

        # V0 validation
        valid, errors = self._validate_package_v0(package)
        if valid:
            package.status = PackageStatus.READY
            package.metadata['v0_validation'] = {
                'passed': True,
                'timestamp': datetime.now().isoformat()
            }
        else:
            package.metadata['v0_validation'] = {
                'passed': False,
                'errors': errors,
                'timestamp': datetime.now().isoformat()
            }

        return package

    def save_package(self, package: Package) -> int:
        """Save package to database, return package_id"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO targeting_packages
            (target_id, version, package_type, status, collection_urls,
             expected_outputs, validation_level, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            package.target_id,
            package.version,
            package.package_type.value,
            package.status.value,
            json.dumps(package.collection_urls),
            json.dumps(package.expected_outputs),
            package.validation_level.value,
            json.dumps(package.metadata)
        ))

        package_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return package_id

    def get_targets_needing_packages(self) -> List[Dict]:
        """
        Find targets without valid packages.

        Rules:
        - status = 'new' (never researched)
        - OR no packages exist
        - OR all packages are in 'closed' status
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get all targets with status 'new'
        cursor.execute('''
            SELECT target_id, name, target_type, priority, status, metadata
            FROM targets
            WHERE status = 'new'
        ''')

        targets = []
        for row in cursor.fetchall():
            target_id, name, target_type, priority, status, metadata_json = row

            # Check if target has any active packages
            cursor.execute('''
                SELECT COUNT(*)
                FROM targeting_packages
                WHERE target_id = ?
                AND status NOT IN ('closed', 'validated')
            ''', (target_id,))

            active_packages = cursor.fetchone()[0]

            # If no active packages, needs new package
            if active_packages == 0:
                targets.append({
                    'target_id': target_id,
                    'name': name,
                    'target_type': target_type,
                    'priority': priority,
                    'status': status,
                    'metadata': json.loads(metadata_json) if metadata_json else {}
                })

        conn.close()
        return targets

    def submit_package_to_j5a(self, package_id: int, package: Package) -> bool:
        """
        Submit ready package to J5A overnight queue.

        Creates J5A task definition for package execution.
        """
        # Create J5A task definition
        j5a_task = {
            'task_id': f"sherlock_pkg_{package_id}",
            'task_type': 'sherlock_research',
            'package_id': package_id,
            'target_name': package.target_name,
            'package_type': package.package_type.value,
            'priority': package.metadata.get('priority', 3),
            'collection_urls': package.collection_urls,
            'expected_outputs': package.expected_outputs,
            'created_at': datetime.now().isoformat()
        }

        # Save to J5A queue directory
        j5a_queue_dir = Path("/home/johnny5/Johny5Alive/queue")
        j5a_queue_dir.mkdir(exist_ok=True)

        task_file = j5a_queue_dir / f"sherlock_pkg_{package_id}.json"
        with open(task_file, 'w') as f:
            json.dump(j5a_task, f, indent=2)

        # Update package status
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE targeting_packages
            SET status = ?, updated_at = ?
            WHERE package_id = ?
        ''', (PackageStatus.SUBMITTED.value, datetime.now().isoformat(), package_id))

        conn.commit()
        conn.close()

        return True

    def run_daily_sweep(self) -> SweepReport:
        """
        Execute daily sweep of target library.

        DETERMINISTIC WORKFLOW:
        1. Scan all targets
        2. Identify targets needing packages
        3. Create packages for those targets
        4. Validate packages (V0)
        5. Submit ready packages to J5A

        Returns:
            SweepReport with results
        """
        sweep_time = datetime.now()
        errors = []
        created_packages = []

        # Get total target count
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM targets')
        targets_scanned = cursor.fetchone()[0]
        conn.close()

        # Find targets needing packages
        targets_needing = self.get_targets_needing_packages()

        packages_created = 0
        packages_validated = 0
        packages_submitted = 0
        packages_failed = 0

        # Create packages
        for target in targets_needing:
            try:
                # Create package
                package = self.create_package(
                    target_id=target['target_id'],
                    target_name=target['name'],
                    target_type=target['target_type'],
                    priority=target['priority'],
                    metadata=target['metadata']
                )

                # Save package
                package_id = self.save_package(package)
                package.package_id = package_id
                packages_created += 1

                # Track validation
                if package.status == PackageStatus.READY:
                    packages_validated += 1

                    # Submit to J5A
                    if self.submit_package_to_j5a(package_id, package):
                        packages_submitted += 1
                else:
                    packages_failed += 1

                # Record created package
                created_packages.append({
                    'package_id': package_id,
                    'target_name': target['name'],
                    'package_type': package.package_type.value,
                    'status': package.status.value,
                    'urls_count': len(package.collection_urls),
                    'outputs_count': len(package.expected_outputs)
                })

            except Exception as e:
                errors.append(f"Failed to create package for {target['name']}: {str(e)}")

        return SweepReport(
            sweep_time=sweep_time,
            targets_scanned=targets_scanned,
            targets_needing_packages=len(targets_needing),
            packages_created=packages_created,
            packages_validated=packages_validated,
            packages_submitted_to_j5a=packages_submitted,
            packages_failed_validation=packages_failed,
            errors=errors,
            created_packages=created_packages
        )


def main():
    """Example usage and testing"""
    print("=" * 70)
    print("Sherlock Targeting Officer - Daily Sweep")
    print("=" * 70)
    print()

    officer = TargetingOfficer(db_path="sherlock.db")

    print("Executing daily sweep...")
    print("-" * 70)

    report = officer.run_daily_sweep()

    print(f"\nSweep completed at: {report.sweep_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("RESULTS:")
    print(f"  Targets scanned: {report.targets_scanned}")
    print(f"  Targets needing packages: {report.targets_needing_packages}")
    print(f"  Packages created: {report.packages_created}")
    print(f"  Packages validated (V0): {report.packages_validated}")
    print(f"  Packages submitted to J5A: {report.packages_submitted_to_j5a}")
    print(f"  Packages failed validation: {report.packages_failed_validation}")

    if report.errors:
        print(f"\nERRORS ({len(report.errors)}):")
        for error in report.errors:
            print(f"  ⚠️  {error}")

    if report.created_packages:
        print(f"\nCREATED PACKAGES ({len(report.created_packages)}):")
        for pkg in report.created_packages[:10]:  # Show first 10
            print(f"  • [{pkg['package_id']}] {pkg['target_name']}")
            print(f"    Type: {pkg['package_type']}, Status: {pkg['status']}")
            print(f"    URLs: {pkg['urls_count']}, Outputs: {pkg['outputs_count']}")

    print()
    print("=" * 70)
    print("✅ Daily sweep complete")
    print("=" * 70)

    # Save report
    report_path = f"targeting_officer_report_{report.sweep_time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump(report.to_dict(), f, indent=2)
    print(f"\n📄 Report saved: {report_path}")


if __name__ == "__main__":
    main()
