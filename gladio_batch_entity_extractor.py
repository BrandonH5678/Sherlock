#!/usr/bin/env python3
"""
Operation Gladio Batch Entity Extractor
Incremental entity extraction with checkpoint pattern for low-memory processing

Design: Process transcript in small batches, save after each batch
Memory: <200MB per batch
Pattern: Incremental Save Pattern (prevents data loss from crashes)
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Set, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class EntityMention:
    """Single mention of an entity in transcript"""
    name: str
    entity_type: str  # "person" or "organization"
    context: str  # Surrounding text
    line_number: int
    confidence: float = 0.8


@dataclass
class CheckpointManifest:
    """Tracks which batches have been processed"""
    completed_batches: List[int]
    total_batches: int
    last_updated: str
    entities_extracted: int


class BatchEntityExtractor:
    """Extract entities from transcript in small batches with checkpoints"""

    def __init__(
        self,
        transcript_path: Path,
        checkpoint_dir: Path,
        batch_size: int = 50
    ):
        self.transcript_path = Path(transcript_path)
        self.checkpoint_dir = Path(checkpoint_dir)
        self.batch_size = batch_size

        # Create checkpoint directory
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Manifest tracking
        self.manifest_path = self.checkpoint_dir / "manifest.json"

        # Known entities patterns (expanded from transcript reading)
        self.person_patterns = [
            r'\b(Alan Dulles|William Donovan|Heinrich Himmler|Walter Schellenberg)\b',
            r'\b(Michele Sindona|Roberto Calvi|Archbishop Paul Marcinkus)\b',
            r'\b(Licio Gelli|Pope John Paul II|Pope Paul VI)\b',
            r'\b(Osama bin Laden|Abdullah Azam|Timothy Drew|Malcolm X)\b',
            r'\b(George H\.? ?W\.? Bush|William Casey|Vernon Walters)\b',
            r'\b(Giulio Andreotti|Aldo Moro|Tansu Ciller)\b',
            r'\b(Felice Casson|Arthur Rouse|Malcolm Byrne)\b',
            r'\b(Dr\.|General|Admiral|Archbishop|Cardinal|Sheikh|Prince)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            r'\b([A-Z][a-z]+\s+(?:de\s+)?[A-Z][a-z]+)\b(?=\s+(?:said|worked|founded|paid|served|testified))',
        ]

        self.org_patterns = [
            r'\b(CIA|OSS|FBI|NATO|KGB|SISMI|P2|IOR)\b',
            r'\b(Vatican Bank|Deutsche Bank|Banco Ambrosiano)\b',
            r'\b(Operation Gladio|Red Brigades|Grey Wolves)\b',
            r'\b(Opus Dei|Mafia|Sicilian Mafia|Gambino crime family)\b',
            r'\b(Mujahideen|Al-Qaeda|PKK|Kurdistan Workers)\b',
            r'\b(Senate|Parliament|Supreme Court|National Security Council)\b',
            r'\b(the\s+)?(CIA|Vatican|Mafia|Church|Agency)\b',
        ]

    def load_manifest(self) -> CheckpointManifest:
        """Load checkpoint manifest or create new one"""
        if self.manifest_path.exists():
            with open(self.manifest_path) as f:
                data = json.load(f)
                return CheckpointManifest(**data)

        # Count total batches
        with open(self.transcript_path) as f:
            total_lines = sum(1 for _ in f)
        total_batches = (total_lines + self.batch_size - 1) // self.batch_size

        return CheckpointManifest(
            completed_batches=[],
            total_batches=total_batches,
            last_updated=datetime.now().isoformat(),
            entities_extracted=0
        )

    def save_manifest(self, manifest: CheckpointManifest):
        """Save checkpoint manifest"""
        manifest.last_updated = datetime.now().isoformat()
        with open(self.manifest_path, 'w') as f:
            json.dump(asdict(manifest), f, indent=2)

    def extract_entities_from_batch(
        self,
        lines: List[str],
        start_line: int
    ) -> List[EntityMention]:
        """Extract entities from a batch of lines"""
        entities = []

        for i, line in enumerate(lines):
            line_num = start_line + i

            # Extract people
            for pattern in self.person_patterns:
                for match in re.finditer(pattern, line):
                    name = match.group(0)
                    # Clean up titles
                    name = re.sub(r'^(Dr\.|General|Admiral|Archbishop|Cardinal|Sheikh|Prince)\s+', '', name)

                    # Get context (50 chars before/after)
                    start = max(0, match.start() - 50)
                    end = min(len(line), match.end() + 50)
                    context = line[start:end].strip()

                    entities.append(EntityMention(
                        name=name,
                        entity_type="person",
                        context=context,
                        line_number=line_num,
                        confidence=0.8
                    ))

            # Extract organizations
            for pattern in self.org_patterns:
                for match in re.finditer(pattern, line):
                    name = match.group(0)
                    # Clean up
                    name = re.sub(r'^the\s+', '', name, flags=re.IGNORECASE)

                    start = max(0, match.start() - 50)
                    end = min(len(line), match.end() + 50)
                    context = line[start:end].strip()

                    entities.append(EntityMention(
                        name=name,
                        entity_type="organization",
                        context=context,
                        line_number=line_num,
                        confidence=0.8
                    ))

        return entities

    def save_batch_checkpoint(self, batch_id: int, entities: List[EntityMention]):
        """Save entities from a batch to checkpoint file"""
        checkpoint_file = self.checkpoint_dir / f"batch_{batch_id:03d}.json"

        entities_data = [asdict(e) for e in entities]

        with open(checkpoint_file, 'w') as f:
            json.dump({
                'batch_id': batch_id,
                'entity_count': len(entities),
                'entities': entities_data,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)

    def process_transcript(self) -> Dict[str, int]:
        """Process entire transcript in batches with checkpoints"""

        manifest = self.load_manifest()

        print(f"Processing transcript: {self.transcript_path}")
        print(f"Total batches: {manifest.total_batches}")
        print(f"Completed batches: {len(manifest.completed_batches)}")
        print(f"Checkpoint dir: {self.checkpoint_dir}")

        with open(self.transcript_path) as f:
            lines = f.readlines()

        batch_id = 0
        total_entities = 0

        for start_idx in range(0, len(lines), self.batch_size):
            # Skip if already completed
            if batch_id in manifest.completed_batches:
                print(f"  Batch {batch_id:3d}: SKIPPED (already completed)")
                batch_id += 1
                continue

            # Get batch
            end_idx = min(start_idx + self.batch_size, len(lines))
            batch_lines = lines[start_idx:end_idx]

            # Extract entities
            entities = self.extract_entities_from_batch(batch_lines, start_idx)

            # Save checkpoint
            self.save_batch_checkpoint(batch_id, entities)

            # Update manifest
            manifest.completed_batches.append(batch_id)
            manifest.entities_extracted += len(entities)
            self.save_manifest(manifest)

            total_entities += len(entities)
            print(f"  Batch {batch_id:3d}: {len(entities)} entities extracted")

            batch_id += 1

        print(f"\nExtraction complete!")
        print(f"  Total entities: {total_entities}")
        print(f"  Checkpoints: {len(manifest.completed_batches)}/{manifest.total_batches}")

        return {
            'total_entities': total_entities,
            'total_batches': manifest.total_batches,
            'completed_batches': len(manifest.completed_batches)
        }

    def load_all_entities(self) -> List[EntityMention]:
        """Load all entities from checkpoints"""
        all_entities = []

        for checkpoint_file in sorted(self.checkpoint_dir.glob("batch_*.json")):
            with open(checkpoint_file) as f:
                data = json.load(f)
                for entity_data in data['entities']:
                    all_entities.append(EntityMention(**entity_data))

        return all_entities


def main():
    """Test entity extraction"""

    transcript_path = Path("/home/johnny5/Sherlock/audiobooks/operation_gladio/operation_gladio_transcript.txt")
    checkpoint_dir = Path("/home/johnny5/Sherlock/audiobooks/operation_gladio/entity_checkpoints")

    if not transcript_path.exists():
        print(f"ERROR: Transcript not found: {transcript_path}")
        return

    extractor = BatchEntityExtractor(
        transcript_path=transcript_path,
        checkpoint_dir=checkpoint_dir,
        batch_size=50
    )

    # Process transcript
    stats = extractor.process_transcript()

    # Show sample entities
    print("\nSample entities:")
    entities = extractor.load_all_entities()

    people = [e for e in entities if e.entity_type == "person"][:10]
    orgs = [e for e in entities if e.entity_type == "organization"][:10]

    print(f"\nPeople ({len([e for e in entities if e.entity_type == 'person'])} total):")
    for p in people:
        print(f"  - {p.name} (line {p.line_number})")

    print(f"\nOrganizations ({len([e for e in entities if e.entity_type == 'organization'])} total):")
    for o in orgs:
        print(f"  - {o.name} (line {o.line_number})")


if __name__ == "__main__":
    main()
