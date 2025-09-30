#!/usr/bin/env python3
"""
Operation Gladio Processing Status Checker
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

def check_processing_status():
    """Check current status of Operation Gladio processing"""

    print("🎯 OPERATION GLADIO PROCESSING STATUS")
    print("=" * 50)
    print(f"Status check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check if processing is still running
    try:
        result = subprocess.run(['pgrep', '-f', 'direct_aaxc_processor'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("🟢 PROCESSING: ACTIVE - Direct AAXC processor is running")
            pids = result.stdout.strip().split('\n')
            print(f"   Process IDs: {', '.join(pids)}")
        else:
            print("🔴 PROCESSING: STOPPED - No active processor found")
    except Exception as e:
        print(f"❓ PROCESSING: UNKNOWN - Cannot check status ({e})")

    print()

    # Check log file
    log_file = "/home/johnny5/Sherlock/gladio_processing.log"
    if Path(log_file).exists():
        print("📄 LOG FILE STATUS:")
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    print(f"   Last log entry: {lines[-1].strip()}")
                    print(f"   Total log lines: {len(lines)}")
                else:
                    print("   Log file is empty")
        except Exception as e:
            print(f"   Error reading log: {e}")
    else:
        print("📄 LOG FILE: Not found")

    print()

    # Check database
    db_file = "/home/johnny5/Sherlock/gladio_intelligence.db"
    if Path(db_file).exists():
        print("🗄️ DATABASE STATUS:")
        file_size = Path(db_file).stat().st_size
        print(f"   File size: {file_size:,} bytes")
        print(f"   Created: {datetime.fromtimestamp(Path(db_file).stat().st_ctime)}")
        print(f"   Modified: {datetime.fromtimestamp(Path(db_file).stat().st_mtime)}")

        # Try to get entity counts
        try:
            import sqlite3
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            if tables:
                print("   Tables found:")
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                        count = cursor.fetchone()[0]
                        print(f"     {table[0]}: {count} records")
                    except:
                        print(f"     {table[0]}: Unable to count")
            else:
                print("   No tables found in database")

            conn.close()
        except Exception as e:
            print(f"   Database query error: {e}")
    else:
        print("🗄️ DATABASE: Not created yet")

    print()

    # Check processing report
    report_file = "/home/johnny5/Sherlock/gladio_processing_report.json"
    if Path(report_file).exists():
        print("📊 PROCESSING REPORT:")
        try:
            with open(report_file, 'r') as f:
                report = json.load(f)
                print(f"   Processing date: {report.get('processing_date', 'Unknown')}")
                stats = report.get('statistics', {})
                print(f"   Segments processed: {stats.get('segments_processed', 0)}")
                print(f"   Entities extracted: {stats.get('entities_extracted', 0)}")
                print(f"   Relationships found: {stats.get('relationships_found', 0)}")
        except Exception as e:
            print(f"   Error reading report: {e}")
    else:
        print("📊 PROCESSING REPORT: Not available yet")

    print()

    # Check transcript file
    transcript_file = "/home/johnny5/Sherlock/audiobooks/operation_gladio/operation_gladio_transcript.txt"
    if Path(transcript_file).exists():
        print("📝 TRANSCRIPT STATUS:")
        file_size = Path(transcript_file).stat().st_size
        print(f"   File size: {file_size:,} bytes")
        print(f"   Modified: {datetime.fromtimestamp(Path(transcript_file).stat().st_mtime)}")

        # Estimate progress based on file size
        if file_size > 0:
            # Rough estimate: 12 hours * 150 words/min * 5 chars/word = ~540,000 chars
            estimated_total = 540000
            progress = min(100, (file_size / estimated_total) * 100)
            print(f"   Estimated progress: {progress:.1f}%")
    else:
        print("📝 TRANSCRIPT: Not created yet")

    print()
    print("🔍 TO MONITOR PROGRESS:")
    print("   tail -f /home/johnny5/Sherlock/gladio_processing.log")
    print("   python3 check_gladio_status.py")
    print()

if __name__ == "__main__":
    check_processing_status()