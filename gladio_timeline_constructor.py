#!/usr/bin/env python3
"""
Operation Gladio Timeline Constructor
Extract temporal events and build chronological timeline

Design: Date extraction with event sequencing
Memory: <200MB
Pattern: Batch processing with checkpoint saves
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict


@dataclass
class TimelineEvent:
    """Single event with temporal reference"""
    event_id: str
    year: Optional[int]
    month: Optional[int]
    day: Optional[int]
    time_description: str  # "early 1960s", "winter of 1963"
    event_description: str
    entities_involved: List[str]
    line_number: int
    confidence: float = 0.6


class TimelineConstructor:
    """Extract timeline events from transcript"""

    def __init__(self, transcript_path: Path, entities_path: Path, checkpoint_dir: Path):
        self.transcript_path = Path(transcript_path)
        self.entities_path = Path(entities_path)
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Load entities
        self.entity_names = self.load_entity_names()

        # Date patterns
        self.date_patterns = [
            # Full dates
            (r'(\w+)\s+(\d{1,2}),?\s+(\d{4})', 'full_date'),  # January 1, 1990
            (r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', 'numeric_date'),  # 1/15/1990

            # Year only
            (r'\b(19\d{2}|20\d{2})\b', 'year'),  # 1990

            # Decades
            (r'(early|mid|late)\s+(19\d0s|20\d0s)', 'decade'),  # early 1960s
            (r'the\s+(19\d0s|20\d0s)', 'decade'),  # the 1960s

            # Relative dates
            (r'(winter|spring|summer|fall|autumn) of (\d{4})', 'season'),
        ]

        # Event keywords
        self.event_keywords = [
            'founded', 'established', 'created', 'formed',
            'died', 'killed', 'assassinated', 'murdered',
            'elected', 'appointed', 'resigned', 'retired',
            'arrested', 'convicted', 'sentenced', 'imprisoned',
            'met with', 'spoke with', 'visited', 'traveled',
            'occurred', 'happened', 'took place'
        ]

    def load_entity_names(self) -> List[str]:
        """Load entity names from dossiers"""
        with open(self.entities_path) as f:
            data = json.load(f)

        names = list(data['dossiers'].keys())
        return names

    def find_entities_in_text(self, text: str) -> List[str]:
        """Find entities mentioned in text"""
        found = []
        for name in self.entity_names:
            if name in text:
                found.append(name)
        return list(set(found))  # Deduplicate

    def is_valid_year(self, text: str, match_pos: int, year: int) -> bool:
        """Validate that matched number is actually a year, not a document ID"""

        # Reject years outside reasonable range for Operation Gladio
        # Allow 1900-2025 (historical context through present)
        if year < 1900 or year > 2025:
            return False

        # Check context around match for document ID patterns
        context_start = max(0, match_pos - 15)
        context_end = min(len(text), match_pos + 25)
        context = text[context_start:context_end]

        # Reject if appears in document reference pattern (e.g., "B3-2058")
        if re.search(r'B\d+-\d{4}', context):
            return False

        # Reject if part of hyphenated number sequence (e.g., "2058-2068-2078")
        if re.search(r'\d{4}-\d{4}-\d{4}', context):
            return False

        # Reject if part of "and YYYY-YY" pattern (e.g., "and 2087-90")
        if re.search(r'and\s+\d{4}-\d{2}', context):
            return False

        return True

    def extract_dates(self, text: str) -> List[Dict]:
        """Extract dates from text"""
        dates = []

        for pattern, date_type in self.date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_info = {
                    'type': date_type,
                    'match_text': match.group(0),
                    'position': match.start()
                }

                # Parse based on type
                if date_type == 'year':
                    year = int(match.group(1))
                    # Validate year before adding
                    if not self.is_valid_year(text, match.start(), year):
                        continue  # Skip invalid years
                    date_info['year'] = year

                elif date_type == 'decade':
                    decade_str = match.group(2) if match.lastindex >= 2 else match.group(1)
                    year = int(decade_str[:4])  # Get base year (e.g., 1960)
                    if not self.is_valid_year(text, match.start(), year):
                        continue
                    date_info['year'] = year
                    date_info['time_description'] = match.group(0)

                elif date_type == 'season':
                    year = int(match.group(2))
                    if not self.is_valid_year(text, match.start(), year):
                        continue
                    date_info['year'] = year
                    date_info['time_description'] = match.group(0)

                elif date_type == 'full_date':
                    year = int(match.group(3))
                    if not self.is_valid_year(text, match.start(), year):
                        continue
                    date_info['year'] = year
                    date_info['time_description'] = match.group(0)

                dates.append(date_info)

        return dates

    def is_event_sentence(self, text: str) -> bool:
        """Check if sentence describes an event"""
        text_lower = text.lower()

        for keyword in self.event_keywords:
            if keyword in text_lower:
                return True

        return False

    def extract_events_from_batch(self, lines: List[str], start_line: int) -> List[TimelineEvent]:
        """Extract timeline events from batch"""
        events = []
        event_counter = 0

        for i, line in enumerate(lines):
            line_num = start_line + i

            # Check if line describes an event
            if not self.is_event_sentence(line):
                continue

            # Extract dates
            dates = self.extract_dates(line)

            if not dates:
                continue

            # Extract entities
            entities = self.find_entities_in_text(line)

            # Create event for each date
            for date_info in dates:
                event_id = f"event_{start_line}_{event_counter}"
                event_counter += 1

                events.append(TimelineEvent(
                    event_id=event_id,
                    year=date_info.get('year'),
                    month=date_info.get('month'),
                    day=date_info.get('day'),
                    time_description=date_info.get('time_description', date_info.get('match_text', '')),
                    event_description=line[:200],  # Truncate for storage
                    entities_involved=entities[:5],  # Top 5 entities
                    line_number=line_num,
                    confidence=0.6
                ))

        return events

    def save_batch_checkpoint(self, batch_id: int, events: List[TimelineEvent]):
        """Save events to checkpoint"""
        checkpoint_file = self.checkpoint_dir / f"timeline_batch_{batch_id:03d}.json"

        data = {
            'batch_id': batch_id,
            'event_count': len(events),
            'events': [asdict(e) for e in events],
            'timestamp': datetime.now().isoformat()
        }

        with open(checkpoint_file, 'w') as f:
            json.dump(data, f, indent=2)

    def process_transcript(self, batch_size: int = 50) -> Dict[str, int]:
        """Process transcript to extract timeline events"""

        print(f"Processing transcript for timeline events...")

        with open(self.transcript_path) as f:
            lines = f.readlines()

        total_events = 0
        batch_id = 0

        for start_idx in range(0, len(lines), batch_size):
            end_idx = min(start_idx + batch_size, len(lines))
            batch_lines = lines[start_idx:end_idx]

            # Extract events
            events = self.extract_events_from_batch(batch_lines, start_idx)

            # Save checkpoint
            self.save_batch_checkpoint(batch_id, events)

            total_events += len(events)
            print(f"  Batch {batch_id:3d}: {len(events)} events found")

            batch_id += 1

        print(f"\nTimeline extraction complete!")
        print(f"  Total events: {total_events}")

        return {'total_events': total_events, 'total_batches': batch_id}

    def consolidate_timeline(self) -> List[TimelineEvent]:
        """Load and sort all timeline events"""

        print("\nConsolidating timeline...")

        all_events = []
        for checkpoint_file in sorted(self.checkpoint_dir.glob("timeline_batch_*.json")):
            with open(checkpoint_file) as f:
                data = json.load(f)
                for event_data in data['events']:
                    all_events.append(TimelineEvent(**event_data))

        # Sort by year (events without year go to end)
        all_events.sort(key=lambda e: e.year if e.year else 9999)

        print(f"  Total events in timeline: {len(all_events)}")

        # Count by decade
        by_decade = defaultdict(int)
        for event in all_events:
            if event.year:
                decade = (event.year // 10) * 10
                by_decade[decade] += 1

        print("\nEvents by decade:")
        for decade in sorted(by_decade.keys()):
            print(f"  {decade}s: {by_decade[decade]} events")

        return all_events

    def save_timeline(self, events: List[TimelineEvent], output_path: Path):
        """Save timeline to JSON"""

        data = {
            'metadata': {
                'total_events': len(events),
                'earliest_year': min((e.year for e in events if e.year), default=None),
                'latest_year': max((e.year for e in events if e.year), default=None),
                'generated': datetime.now().isoformat()
            },
            'timeline': [asdict(e) for e in events]
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\nSaved timeline to {output_path}")


def main():
    """Build timeline for Operation Gladio"""

    transcript_path = Path("/home/johnny5/Sherlock/audiobooks/operation_gladio/operation_gladio_transcript.txt")
    entities_path = Path("/home/johnny5/Sherlock/audiobooks/operation_gladio/entity_dossiers.json")
    checkpoint_dir = Path("/home/johnny5/Sherlock/audiobooks/operation_gladio/timeline_checkpoints")
    output_path = Path("/home/johnny5/Sherlock/audiobooks/operation_gladio/timeline.json")

    constructor = TimelineConstructor(transcript_path, entities_path, checkpoint_dir)

    # Extract events
    stats = constructor.process_transcript(batch_size=50)

    # Consolidate and sort
    timeline = constructor.consolidate_timeline()

    # Save
    constructor.save_timeline(timeline, output_path)

    # Show samples
    print("\n" + "="*60)
    print("SAMPLE TIMELINE EVENTS:")
    print("="*60)

    # Show first 10 events
    for event in timeline[:10]:
        year_str = str(event.year) if event.year else "Unknown date"
        entities_str = ", ".join(event.entities_involved[:3]) if event.entities_involved else "No entities"
        print(f"\n{year_str}: {event.time_description}")
        print(f"  Entities: {entities_str}")
        print(f"  Event: {event.event_description[:100]}...")


if __name__ == "__main__":
    main()
