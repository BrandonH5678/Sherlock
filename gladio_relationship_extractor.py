#!/usr/bin/env python3
"""
Operation Gladio Relationship Extractor
Extract relationships between entities from transcript context

Design: Co-occurrence analysis with relationship typing
Memory: <200MB
Pattern: Incremental batch processing with checkpoints
"""

import json
import re
import sqlite3
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict


@dataclass
class RelationshipMention:
    """Single mention of a relationship between entities"""
    entity_1: str
    entity_2: str
    entity_1_type: str  # "person" or "organization"
    entity_2_type: str
    relationship_type: str  # "member", "leader", "funder", "operational"
    context: str
    line_number: int
    confidence: float = 0.7


class RelationshipExtractor:
    """Extract relationships from transcript based on entity co-occurrence"""

    def __init__(self, db_path: Path, transcript_path: Path, checkpoint_dir: Path):
        self.db_path = Path(db_path)
        self.transcript_path = Path(transcript_path)
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Load entities from database
        self.people = {}
        self.organizations = {}
        self.load_entities()

        # Relationship type patterns
        self.relationship_patterns = {
            'leadership': [
                r'(director|head|chief|chairman|president|leader) of',
                r'led by',
                r'under (the )?leadership',
                r'commanded by'
            ],
            'membership': [
                r'member of',
                r'belonged to',
                r'part of',
                r'worked for',
                r'served in'
            ],
            'funding': [
                r'funded by',
                r'financed by',
                r'paid by',
                r'received.*from',
                r'money from'
            ],
            'operational': [
                r'worked with',
                r'collaborated with',
                r'cooperated with',
                r'in cooperation with',
                r'along with'
            ],
            'creation': [
                r'founded',
                r'created',
                r'established',
                r'set up'
            ]
        }

    def load_entities(self):
        """Load entities from database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Load people
        cursor.execute("SELECT person_id, dossier_json FROM people")
        for person_id, json_data in cursor.fetchall():
            data = json.loads(json_data)
            self.people[data['name']] = {
                'id': person_id,
                'aliases': data.get('aliases', []),
                'mention_count': data.get('mention_count', 0)
            }

        # Load organizations
        cursor.execute("SELECT organization_id, organization_json FROM organizations")
        for org_id, json_data in cursor.fetchall():
            data = json.loads(json_data)
            self.organizations[data['name']] = {
                'id': org_id,
                'aliases': data.get('aliases', []),
                'mention_count': data.get('mention_count', 0)
            }

        conn.close()

        print(f"Loaded {len(self.people)} people, {len(self.organizations)} organizations")

    def find_entities_in_text(self, text: str) -> List[Tuple[str, str]]:
        """Find all entity mentions in text (returns list of (name, type) tuples)"""
        found = []

        # Find people
        for person_name in self.people.keys():
            if person_name in text:
                found.append((person_name, "person"))

        # Find organizations
        for org_name in self.organizations.keys():
            if org_name in text:
                found.append((org_name, "organization"))

        return found

    def classify_relationship(self, context: str) -> str:
        """Classify relationship type based on context"""
        context_lower = context.lower()

        for rel_type, patterns in self.relationship_patterns.items():
            for pattern in patterns:
                if re.search(pattern, context_lower):
                    return rel_type

        return "associated"  # Default relationship type

    def extract_relationships_from_batch(
        self,
        lines: List[str],
        start_line: int
    ) -> List[RelationshipMention]:
        """Extract relationships from a batch of lines"""
        relationships = []

        for i, line in enumerate(lines):
            line_num = start_line + i

            # Find entities in this line
            entities_found = self.find_entities_in_text(line)

            # If 2+ entities co-occur, extract relationship
            if len(entities_found) >= 2:
                # Create relationships for all pairs
                for j in range(len(entities_found)):
                    for k in range(j + 1, len(entities_found)):
                        entity_1_name, entity_1_type = entities_found[j]
                        entity_2_name, entity_2_type = entities_found[k]

                        # Classify relationship
                        rel_type = self.classify_relationship(line)

                        # Create relationship mention
                        relationships.append(RelationshipMention(
                            entity_1=entity_1_name,
                            entity_2=entity_2_name,
                            entity_1_type=entity_1_type,
                            entity_2_type=entity_2_type,
                            relationship_type=rel_type,
                            context=line[:200],  # First 200 chars
                            line_number=line_num,
                            confidence=0.7
                        ))

        return relationships

    def save_batch_checkpoint(self, batch_id: int, relationships: List[RelationshipMention]):
        """Save relationships to checkpoint file"""
        checkpoint_file = self.checkpoint_dir / f"relationships_batch_{batch_id:03d}.json"

        data = {
            'batch_id': batch_id,
            'relationship_count': len(relationships),
            'relationships': [asdict(r) for r in relationships],
            'timestamp': datetime.now().isoformat()
        }

        with open(checkpoint_file, 'w') as f:
            json.dump(data, f, indent=2)

    def process_transcript(self, batch_size: int = 50) -> Dict[str, int]:
        """Process transcript in batches to extract relationships"""

        print(f"Processing transcript: {self.transcript_path}")

        with open(self.transcript_path) as f:
            lines = f.readlines()

        total_batches = (len(lines) + batch_size - 1) // batch_size
        total_relationships = 0
        batch_id = 0

        for start_idx in range(0, len(lines), batch_size):
            end_idx = min(start_idx + batch_size, len(lines))
            batch_lines = lines[start_idx:end_idx]

            # Extract relationships
            relationships = self.extract_relationships_from_batch(batch_lines, start_idx)

            # Save checkpoint
            self.save_batch_checkpoint(batch_id, relationships)

            total_relationships += len(relationships)
            print(f"  Batch {batch_id:3d}: {len(relationships)} relationships found")

            batch_id += 1

        print(f"\nRelationship extraction complete!")
        print(f"  Total relationships: {total_relationships}")
        print(f"  Total batches: {batch_id}")

        return {
            'total_relationships': total_relationships,
            'total_batches': batch_id
        }

    def consolidate_relationships(self) -> List[Dict]:
        """Load and consolidate all relationships from checkpoints"""

        print("\nConsolidating relationships...")

        # Load all relationship mentions
        all_mentions = []
        for checkpoint_file in sorted(self.checkpoint_dir.glob("relationships_batch_*.json")):
            with open(checkpoint_file) as f:
                data = json.load(f)
                for rel_data in data['relationships']:
                    all_mentions.append(RelationshipMention(**rel_data))

        # Group by entity pair
        relationship_groups = defaultdict(list)

        for mention in all_mentions:
            # Normalize key (alphabetical order)
            key = tuple(sorted([
                (mention.entity_1, mention.entity_1_type),
                (mention.entity_2, mention.entity_2_type)
            ]))
            relationship_groups[key].append(mention)

        # Consolidate each group
        consolidated = []

        for (e1, e2), mentions in relationship_groups.items():
            # Most common relationship type
            rel_types = [m.relationship_type for m in mentions]
            most_common_type = max(set(rel_types), key=rel_types.count)

            # Aggregate confidence
            avg_confidence = sum(m.confidence for m in mentions) / len(mentions)

            consolidated.append({
                'entity_1': e1[0],
                'entity_1_type': e1[1],
                'entity_2': e2[0],
                'entity_2_type': e2[1],
                'relationship_type': most_common_type,
                'mention_count': len(mentions),
                'confidence': avg_confidence,
                'contexts': [m.context for m in mentions[:3]]  # Top 3 contexts
            })

        # Sort by mention count
        consolidated.sort(key=lambda x: x['mention_count'], reverse=True)

        print(f"  Consolidated {len(all_mentions)} mentions into {len(consolidated)} unique relationships")

        return consolidated

    def save_relationships(self, relationships: List[Dict], output_path: Path):
        """Save consolidated relationships to JSON"""

        data = {
            'metadata': {
                'total_relationships': len(relationships),
                'generated': datetime.now().isoformat()
            },
            'relationships': relationships
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Saved {len(relationships)} relationships to {output_path}")


def main():
    """Extract relationships from Operation Gladio transcript"""

    db_path = Path("/home/johnny5/Sherlock/gladio_intelligence.db")
    transcript_path = Path("/home/johnny5/Sherlock/audiobooks/operation_gladio/operation_gladio_transcript.txt")
    checkpoint_dir = Path("/home/johnny5/Sherlock/audiobooks/operation_gladio/relationship_checkpoints")
    output_path = Path("/home/johnny5/Sherlock/audiobooks/operation_gladio/relationships.json")

    extractor = RelationshipExtractor(db_path, transcript_path, checkpoint_dir)

    # Extract relationships
    stats = extractor.process_transcript(batch_size=50)

    # Consolidate
    consolidated = extractor.consolidate_relationships()

    # Save
    extractor.save_relationships(consolidated, output_path)

    # Show top relationships
    print("\n" + "="*60)
    print("TOP RELATIONSHIPS (by mention count):")
    print("="*60)

    for rel in consolidated[:20]:
        print(f"\n{rel['entity_1']} ({rel['entity_1_type']}) "
              f"--[{rel['relationship_type']}]--> "
              f"{rel['entity_2']} ({rel['entity_2_type']})")
        print(f"  Mentions: {rel['mention_count']}, Confidence: {rel['confidence']:.2f}")


if __name__ == "__main__":
    main()
