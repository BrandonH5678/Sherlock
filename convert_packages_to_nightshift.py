#!/usr/bin/env python3
"""
Convert Sherlock Research Packages to Night Shift Jobs

Reads Sherlock packages from J5A queue directory and converts them
to Night Shift job format for overnight execution.

Usage:
    python3 convert_packages_to_nightshift.py
"""

import json
import sys
from pathlib import Path
from typing import List, Dict
from datetime import datetime


class PackageToJobConverter:
    """Convert Sherlock packages to Night Shift jobs"""

    def __init__(self):
        self.sherlock_queue_dir = Path("/home/johnny5/Johny5Alive/queue")
        self.nightshift_queue = Path("/home/johnny5/Johny5Alive/j5a-nightshift/ops/queue/nightshift_jobs.json")
        self.sherlock_inbox = Path("/home/johnny5/Sherlock/nightshift_inbox")
        self.sherlock_inbox.mkdir(exist_ok=True)

    def map_priority(self, sherlock_priority: int) -> str:
        """Map Sherlock priority (1-3) to Night Shift priority"""
        if sherlock_priority == 1:
            return "HIGH"
        elif sherlock_priority == 2:
            return "NORMAL"
        else:
            return "LOW"

    def determine_job_type(self, package_type: str) -> str:
        """Determine Night Shift job type from package type"""
        # All Sherlock packages are research tasks
        return "sherlock_research"

    def determine_job_class(self, package_type: str) -> str:
        """Determine job class from package type"""
        if package_type == "youtube":
            return "heavy"  # Video processing is resource-intensive
        elif package_type == "document":
            return "standard"  # Document processing is lightweight
        else:  # composite
            return "standard"  # Composite research is moderate

    def convert_package_to_job(self, package: Dict) -> Dict:
        """
        Convert Sherlock package to Night Shift job format

        Sherlock Package:
        {
            "task_id": "sherlock_pkg_6",
            "task_type": "sherlock_research",
            "package_id": 6,
            "target_name": "Weaponized Podcast",
            "package_type": "youtube",
            "priority": 1,
            "collection_urls": [...],
            "expected_outputs": [...],
            "created_at": "2025-12-06T15:33:03.184560"
        }

        Night Shift Job:
        {
            "job_id": "SHERLOCK_PKG_6",
            "type": "sherlock_research",
            "class": "heavy",
            "description": "Research: Weaponized Podcast (youtube)",
            "inputs": [{"urls": [...]}],
            "outputs": [{"kind": "json", "path": "..."}],
            "metadata": {
                "source": "targeting_officer",
                "priority": "HIGH",
                "package_id": 6,
                "target_name": "Weaponized Podcast",
                "package_type": "youtube",
                "created_at": "2025-12-06T15:33:03"
            }
        }
        """
        # Create job ID
        job_id = f"SHERLOCK_PKG_{package['package_id']}"

        # Map priority
        priority = self.map_priority(package['priority'])

        # Determine job class
        job_class = self.determine_job_class(package['package_type'])

        # Create description
        description = f"Research: {package['target_name']} ({package['package_type']})"

        # Convert inputs - save package to inbox
        package_file = self.sherlock_inbox / f"package_{package['package_id']}.json"
        with open(package_file, 'w') as f:
            json.dump(package, f, indent=2)

        inputs = [
            {
                "path": str(package_file),
                "type": "sherlock_package"
            }
        ]

        # Convert outputs
        outputs = []
        for expected_output in package['expected_outputs']:
            # Determine output kind from path
            if expected_output.endswith('.json'):
                kind = 'json'
            elif expected_output.endswith('.txt'):
                kind = 'text'
            elif expected_output.endswith('.mp3'):
                kind = 'audio'
            else:
                kind = 'file'

            # Make path absolute
            output_path = Path("/home/johnny5/Sherlock") / expected_output

            outputs.append({
                "kind": kind,
                "path": str(output_path)
            })

        # Create Night Shift job
        job = {
            "job_id": job_id,
            "type": "sherlock_research",
            "class": job_class,
            "description": description,
            "inputs": inputs,
            "outputs": outputs,
            "metadata": {
                "source": "targeting_officer",
                "priority": priority,
                "package_id": package['package_id'],
                "target_name": package['target_name'],
                "package_type": package['package_type'],
                "collection_urls": package['collection_urls'],
                "created_at": package['created_at'],
                "converted_at": datetime.now().isoformat()
            }
        }

        return job

    def load_sherlock_packages(self) -> List[Dict]:
        """Load all Sherlock packages from queue directory"""
        packages = []

        # Find all sherlock_pkg_*.json files
        for pkg_file in sorted(self.sherlock_queue_dir.glob("sherlock_pkg_*.json")):
            try:
                with open(pkg_file, 'r') as f:
                    package = json.load(f)
                    packages.append(package)
            except Exception as e:
                print(f"❌ Error loading {pkg_file}: {e}")

        return packages

    def load_existing_nightshift_jobs(self) -> List[Dict]:
        """Load existing Night Shift jobs"""
        if not self.nightshift_queue.exists():
            return []

        try:
            with open(self.nightshift_queue, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading nightshift jobs: {e}")
            return []

    def save_nightshift_jobs(self, jobs: List[Dict]):
        """Save Night Shift jobs to queue file"""
        try:
            with open(self.nightshift_queue, 'w') as f:
                json.dump(jobs, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving nightshift jobs: {e}")
            raise

    def run_conversion(self):
        """Execute conversion from Sherlock packages to Night Shift jobs"""
        print("=" * 70)
        print("Sherlock Package → Night Shift Job Converter")
        print("=" * 70)
        print()

        # Load Sherlock packages
        print("Loading Sherlock packages from queue...")
        packages = self.load_sherlock_packages()
        print(f"Found {len(packages)} packages")
        print()

        if not packages:
            print("No packages to convert. Exiting.")
            return

        # Load existing Night Shift jobs
        print("Loading existing Night Shift jobs...")
        existing_jobs = self.load_existing_nightshift_jobs()
        existing_job_ids = {job['job_id'] for job in existing_jobs}
        print(f"Found {len(existing_jobs)} existing jobs")
        print()

        # Convert packages
        print("Converting packages to Night Shift jobs...")
        print("-" * 70)

        new_jobs = []
        skipped = 0

        for package in packages:
            job_id = f"SHERLOCK_PKG_{package['package_id']}"

            # Check if already converted
            if job_id in existing_job_ids:
                print(f"⏭️  Skipped (already exists): {job_id} - {package['target_name']}")
                skipped += 1
                continue

            # Convert
            try:
                job = self.convert_package_to_job(package)
                new_jobs.append(job)
                print(f"✅ Converted: {job_id} - {package['target_name']}")
                print(f"   Type: {package['package_type']}, Priority: {job['metadata']['priority']}, Class: {job['class']}")
            except Exception as e:
                print(f"❌ Error converting {package['task_id']}: {e}")

        print()
        print("=" * 70)
        print(f"Conversion Summary:")
        print(f"  Total packages: {len(packages)}")
        print(f"  Converted: {len(new_jobs)}")
        print(f"  Skipped (already exists): {skipped}")
        print("=" * 70)
        print()

        if new_jobs:
            # Merge with existing jobs
            all_jobs = existing_jobs + new_jobs

            # Save to Night Shift queue
            print(f"Saving {len(all_jobs)} total jobs to Night Shift queue...")
            self.save_nightshift_jobs(all_jobs)
            print(f"✅ Night Shift queue updated: {self.nightshift_queue}")
            print()

            # Show priority breakdown
            print("Priority Breakdown:")
            priority_counts = {}
            for job in all_jobs:
                pri = job['metadata'].get('priority', 'UNKNOWN')
                priority_counts[pri] = priority_counts.get(pri, 0) + 1

            for priority, count in sorted(priority_counts.items()):
                print(f"  {priority}: {count} jobs")
            print()
        else:
            print("No new jobs to add.")


def main():
    converter = PackageToJobConverter()
    converter.run_conversion()


if __name__ == "__main__":
    main()
