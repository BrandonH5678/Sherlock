#!/usr/bin/env python3
"""Add Shared Context podcast target to Sherlock database"""
import sys
sys.path.append("/home/johnny5/Sherlock")

from seed_targets import import_targets

def add_shared_context_target():
    db_path = "/home/johnny5/Sherlock/sherlock.db"

    shared_context_target = {
        "name": "Shared Context Podcast",
        "target_type": "podcast_series",
        "priority": 1,  # Highest priority (before Weaponized)
        "status": "active",
        "metadata": {
            "description": "Podcast exploring technology, AI, and societal implications",
            "primary_focus": "AI training intelligence gathering",
            "priority_episode": "https://youtu.be/oW4lBSmLc5k?si=CEpFxq2X-SNnNaIL",
            "intelligence_focus_areas": [
                "AI training datasets and methods",
                "Training data sourcing and ethics",
                "Model architecture and capabilities",
                "AI alignment and safety research",
                "Corporate AI development practices",
                "AI policy and regulation"
            ],
            "processing_method": "whisper_transcription_dual_engine",
            "extraction_priority": "high"
        }
    }

    imported, skipped = import_targets(db_path, [shared_context_target])
    if imported > 0:
        print(f"\n✅ Added Shared Context podcast target (Priority {shared_context_target['priority']})")
    elif skipped > 0:
        print(f"\n⏭️  Shared Context podcast target already exists in database")

if __name__ == "__main__":
    add_shared_context_target()
