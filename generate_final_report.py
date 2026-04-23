#!/usr/bin/env python3
"""
Generate final consolidated report for Sherlock transcription pipeline
Aggregates results from all tier processing jobs
"""

import json
import glob
from pathlib import Path
from datetime import datetime

def load_tier_results():
    """Load all tier result JSON files"""
    results_dir = Path("/home/johnny5/Sherlock")
    result_files = sorted(results_dir.glob("transcription_results_*.json"))

    all_results = []
    for result_file in result_files:
        with open(result_file, 'r') as f:
            data = json.load(f)
            all_results.append({
                "file": result_file.name,
                "data": data
            })

    return all_results

def calculate_aggregate_metrics(all_results):
    """Calculate aggregate metrics across all tiers"""
    total_episodes = 0
    successful = 0
    failed = 0

    total_processing_time = 0
    total_word_count = 0
    total_segments = 0

    by_priority = {"P1": 0, "P2": 0, "P3": 0, "P4": 0}
    by_podcast = {"Weaponized": 0, "American Alchemy": 0}

    for result in all_results:
        data = result["data"]
        total_episodes += data.get("total_episodes", 0)
        successful += data.get("successful", 0)
        failed += data.get("failed", 0)

        for episode in data.get("episodes", []):
            if episode.get("success"):
                # Aggregate metrics
                if "transcription" in episode:
                    trans = episode["transcription"]
                    total_processing_time += trans.get("duration", 0)
                    total_word_count += trans.get("word_count", 0)
                    total_segments += trans.get("segment_count", 0)

                # Count by priority
                priority = episode.get("priority", "UNKNOWN")
                if priority in by_priority:
                    by_priority[priority] += 1

                # Count by podcast
                podcast = episode.get("podcast", "UNKNOWN")
                if podcast in by_podcast:
                    by_podcast[podcast] += 1

    return {
        "total_episodes": total_episodes,
        "successful": successful,
        "failed": failed,
        "success_rate": round(successful / total_episodes * 100, 1) if total_episodes > 0 else 0,
        "total_processing_time_minutes": round(total_processing_time / 60, 1),
        "total_word_count": total_word_count,
        "total_segments": total_segments,
        "avg_words_per_episode": round(total_word_count / successful, 0) if successful > 0 else 0,
        "by_priority": by_priority,
        "by_podcast": by_podcast
    }

def generate_report():
    """Generate final consolidated report"""
    print("=" * 80)
    print("SHERLOCK TRANSCRIPTION PIPELINE - FINAL REPORT")
    print("=" * 80)
    print()

    # Load all results
    all_results = load_tier_results()
    print(f"Found {len(all_results)} result files")
    print()

    # Calculate metrics
    metrics = calculate_aggregate_metrics(all_results)

    # Print summary
    print("📊 PROCESSING SUMMARY")
    print("=" * 80)
    print(f"Total Episodes Attempted: {metrics['total_episodes']}")
    print(f"✅ Successful: {metrics['successful']}")
    print(f"❌ Failed: {metrics['failed']}")
    print(f"Success Rate: {metrics['success_rate']}%")
    print()

    print("⏱️  PERFORMANCE METRICS")
    print("=" * 80)
    print(f"Total Processing Time: {metrics['total_processing_time_minutes']} minutes")
    print(f"Total Word Count: {metrics['total_word_count']:,} words")
    print(f"Total Segments: {metrics['total_segments']:,} segments")
    print(f"Average Words/Episode: {metrics['avg_words_per_episode']:,} words")
    print()

    print("📂 BY PRIORITY")
    print("=" * 80)
    for priority, count in sorted(metrics['by_priority'].items()):
        print(f"  {priority}: {count} episodes")
    print()

    print("🎙️  BY PODCAST")
    print("=" * 80)
    for podcast, count in metrics['by_podcast'].items():
        print(f"  {podcast}: {count} episodes")
    print()

    # Count output files
    output_dir = Path("/home/johnny5/Sherlock/freelance_transcripts")
    transcript_files = list(output_dir.glob("*/*/audio.json"))
    print(f"📁 OUTPUT FILES")
    print("=" * 80)
    print(f"Transcript JSONs: {len(transcript_files)}")
    print(f"Location: {output_dir}")
    print()

    # Save consolidated report
    report_file = Path("/home/johnny5/Sherlock/FINAL_PROCESSING_REPORT.json")
    with open(report_file, 'w') as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "metrics": metrics,
            "tier_results": [r["file"] for r in all_results]
        }, f, indent=2)

    print(f"💾 Full report saved to: {report_file}")
    print()
    print("=" * 80)
    print("✅ PROCESSING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    generate_report()
