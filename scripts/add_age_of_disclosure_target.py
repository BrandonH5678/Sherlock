#!/usr/bin/env python3
"""
Add "Age of Disclosure" as P1 Priority Target to Sherlock Database

This script adds the Age of Disclosure as a highest priority (P1) target
for Sherlock intelligence gathering. Supports both video and audiobook formats.

Usage:
    python3 add_age_of_disclosure_target.py [--type TYPE] [--url URL]

Options:
    --type TYPE    Target type: 'video' or 'book' (default: video)
    --url URL      Prime Video URL (for video type)

Prerequisites:
- Sherlock database must exist at /home/johnny5/Sherlock/sherlock.db
"""

import sys
import sqlite3
import json
import argparse
from pathlib import Path
from datetime import datetime


def add_age_of_disclosure_target(
    db_path: str = "/home/johnny5/Sherlock/sherlock.db",
    target_type: str = "video",
    video_url: str = None
):
    """
    Add Age of Disclosure as P1 target to Sherlock database

    Args:
        db_path: Path to sherlock.db
        target_type: 'video' or 'book'
        video_url: Prime Video URL (required for video type)
    """
    db_file = Path(db_path)

    if not db_file.exists():
        print(f"❌ Error: Database not found at {db_path}")
        print("   Please create database or verify path")
        sys.exit(1)

    print("=" * 80)
    print("ADD AGE OF DISCLOSURE TARGET")
    print("=" * 80)
    print(f"Database: {db_path}")
    print()

    try:
        conn = sqlite3.connect(str(db_file))
        cursor = conn.cursor()

        # Check if target already exists
        existing = cursor.execute("""
            SELECT target_id, priority, status, target_type
            FROM targets
            WHERE name = ?
        """, ("Age of Disclosure",)).fetchone()

        # Build metadata based on type
        if target_type == "video":
            if not video_url:
                print("❌ Error: --url required for video type")
                conn.close()
                sys.exit(1)

            metadata = {
                "authors": ["Richard Dolan", "Bryce Zabel"],
                "format": "documentary_video",
                "source": "Amazon Prime Video",
                "video_url": video_url,
                "runtime_minutes": 110,  # 1hr 50min
                "topic": "UAP disclosure timeline and institutional resistance",
                "multi_speaker": True,  # Multiple witnesses/interviewees
                "intelligence_focus": [
                    "Government disclosure timelines",
                    "Whistleblower testimonies (multiple credible witnesses)",
                    "Institutional actors blocking disclosure",
                    "UAP evidence suppression patterns",
                    "Congressional oversight efforts",
                    "Historical precedents for disclosure",
                    "Public perception management",
                    "Witness credibility assessment"
                ],
                "processing_strategy": "Prime Video automated capture + OCR speaker labels + Whisper transcription",
                "priority_rationale": "P1 due to multiple credible witnesses and direct UAP disclosure evidence"
            }
        else:  # book
            metadata = {
                "author": "Richard Dolan, Bryce Zabel",
                "narrator": "Not specified",
                "publication_year": "Unknown",
                "topic": "UAP disclosure timeline and institutional resistance",
                "format": "audiobook",
                "source": "Amazon Audible (AAXC)",
                "single_speaker": True,
                "intelligence_focus": [
                    "Government disclosure timelines",
                    "Institutional actors blocking disclosure",
                    "UAP evidence suppression patterns",
                    "Whistleblower testimonies",
                    "Congressional oversight efforts",
                    "Historical precedents for disclosure",
                    "Public perception management"
                ],
                "processing_notes": "Single-speaker audiobook - use faster-whisper for efficiency",
                "priority_rationale": "P1 due to direct relevance to current UAP disclosure efforts"
            }

        if existing:
            print(f"⚠️  Target already exists:")
            print(f"   ID: {existing[0]}")
            print(f"   Priority: P{existing[1]}")
            print(f"   Status: {existing[2]}")
            print(f"   Type: {existing[3]}")
            print()

            response = input(f"Update to {target_type} type? (y/n): ").strip().lower()
            if response != 'y':
                print("Cancelled - no changes made")
                conn.close()
                sys.exit(0)

            # Update existing target

            cursor.execute("""
                UPDATE targets
                SET target_type = ?, priority = ?, status = ?, updated_at = ?, metadata = ?
                WHERE target_id = ?
            """, (
                target_type,
                1,  # P1 = Critical priority
                "new",  # Reset to new status
                datetime.now().isoformat(),
                json.dumps(metadata, indent=2),
                existing[0]
            ))

            print(f"✅ Updated target: {existing[0]}")

        else:
            # Insert new target
            cursor.execute("""
                INSERT INTO targets (name, target_type, priority, status, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                "Age of Disclosure",
                target_type,
                1,  # P1 = Critical priority
                "new",
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                json.dumps(metadata, indent=2)
            ))

            target_id = cursor.lastrowid
            print(f"✅ Added new target: {target_id}")

        conn.commit()

        # Verify target was added/updated
        result = cursor.execute("""
            SELECT target_id, name, target_type, priority, status, created_at, updated_at
            FROM targets
            WHERE name = ?
        """, ("Age of Disclosure",)).fetchone()

        print()
        print("=" * 80)
        print("TARGET DETAILS")
        print("=" * 80)
        print(f"Target ID:    {result[0]}")
        print(f"Name:         {result[1]}")
        print(f"Type:         {result[2]}")
        print(f"Priority:     P{result[3]} (Critical)")
        print(f"Status:       {result[4]}")
        print(f"Created:      {result[5]}")
        print(f"Updated:      {result[6]}")
        print("=" * 80)
        print()

        # Show next steps
        print("NEXT STEPS:")
        print()

        if target_type == "video":
            print("1. Run automated Prime Video capture:")
            print(f"   source /home/johnny5/Sherlock/primevideo_env/bin/activate")
            print(f"   DISPLAY=:0 python3 /home/johnny5/Sherlock/scripts/process_prime_video_documentary.py \\")
            print(f"       --url \"{video_url}\" \\")
            print(f"       --runtime 110")
            print()
            print("2. Outputs will be saved to:")
            print("   /home/johnny5/Sherlock/prime_video_processing/B0FMF7DZZL/")
            print()
            print("3. Or integrate with Night Shift:")
            print("   python3 /home/johnny5/Sherlock/src/sherlock_targeting_officer.py")
            print("   python3 /home/johnny5/Sherlock/convert_packages_to_nightshift.py")
        else:  # book
            print("1. Download AAXC from Amazon:")
            print("   source /home/johnny5/Sherlock/gladio_env/bin/activate")
            print("   audible download --aaxc --voucher -a [ASIN]")
            print()
            print("2. Move files to Sherlock:")
            print("   mkdir -p /home/johnny5/Sherlock/audiobooks/age_of_disclosure/")
            print("   mv *.aaxc *.voucher /home/johnny5/Sherlock/audiobooks/age_of_disclosure/")
            print()
            print("3. Generate targeting package:")
            print("   python3 /home/johnny5/Sherlock/src/sherlock_targeting_officer.py")
            print()
            print("4. Convert package to Night Shift job:")
            print("   python3 /home/johnny5/Sherlock/convert_packages_to_nightshift.py")

        print()
        print("=" * 80)
        print(f"✅ Age of Disclosure added as P1 {target_type} target")
        print("=" * 80)

        conn.close()

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Add Age of Disclosure as P1 target to Sherlock database"
    )
    parser.add_argument(
        "--type",
        choices=["video", "book"],
        default="video",
        help="Target type (default: video)"
    )
    parser.add_argument(
        "--url",
        help="Prime Video URL (required for video type)"
    )

    args = parser.parse_args()

    # Load URL from config if not provided
    video_url = args.url
    if args.type == "video" and not video_url:
        config_file = Path("/home/johnny5/Sherlock/prime_video_config.json")
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
                video_url = config.get("age_of_disclosure_url")

    add_age_of_disclosure_target(
        target_type=args.type,
        video_url=video_url
    )


if __name__ == "__main__":
    main()
