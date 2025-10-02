#!/usr/bin/env python3
"""
Fix Thread 3 Speaker Constraints
Add George Knapp and other key speakers to database
"""

from datetime import datetime
from evidence_database import EvidenceDatabase, Speaker


def add_thread3_speakers():
    """Add key Thread 3 speakers to database"""
    db = EvidenceDatabase("/home/johnny5/Sherlock/evidence.db")

    speakers = [
        Speaker(
            speaker_id="george_knapp",
            name="George Knapp",
            title="Chief Investigative Reporter",
            organization="KLAS-TV Las Vegas",
            voice_embedding=None,
            confidence=1.0,
            first_seen="1987-01-01T00:00:00",
            last_seen=datetime.now().isoformat()
        ),
        Speaker(
            speaker_id="harry_reid",
            name="Harry Reid",
            title="Former Senate Majority Leader",
            organization="U.S. Senate",
            voice_embedding=None,
            confidence=1.0,
            first_seen="1989-01-01T00:00:00",
            last_seen="2021-12-28T00:00:00"
        ),
        Speaker(
            speaker_id="boris_sokolov",
            name="Boris Sokolov",
            title="Colonel",
            organization="USSR Ministry of Defense",
            voice_embedding=None,
            confidence=0.9,
            first_seen="1978-01-01T00:00:00",
            last_seen="1993-01-01T00:00:00"
        ),
        Speaker(
            speaker_id="james_lacatski",
            name="James Lacatski",
            title="Dr., Intelligence Analyst",
            organization="Defense Intelligence Agency",
            voice_embedding=None,
            confidence=1.0,
            first_seen="2008-01-01T00:00:00",
            last_seen=datetime.now().isoformat()
        ),
        Speaker(
            speaker_id="robert_bigelow",
            name="Robert Bigelow",
            title="Founder & CEO",
            organization="Bigelow Aerospace Advanced Space Studies (BAASS)",
            voice_embedding=None,
            confidence=1.0,
            first_seen="1995-01-01T00:00:00",
            last_seen=datetime.now().isoformat()
        )
    ]

    for speaker in speakers:
        success = db.add_speaker(speaker)
        if success:
            print(f"✅ Added speaker: {speaker.name}")
        else:
            print(f"⚠️  Speaker may already exist: {speaker.name}")

    print(f"\n✅ Processed {len(speakers)} speakers")


if __name__ == "__main__":
    print("=" * 60)
    print("Thread 3 Speaker Registration")
    print("=" * 60)
    add_thread3_speakers()
