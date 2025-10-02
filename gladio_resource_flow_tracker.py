#!/usr/bin/env python3
"""
Operation Gladio Resource Flow Tracker
Track money, weapons, drugs, and information flows between entities

Design: Pattern matching for resource transfers
Memory: <200MB
Pattern: Incremental batch processing
"""

import json
import re
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ResourceFlow:
    """Single resource flow between entities"""
    source_entity: str
    recipient_entity: str
    resource_type: str  # "money", "weapons", "drugs", "information"
    amount: str
    description: str
    line_number: int
    confidence: float = 0.6


class ResourceFlowTracker:
    """Extract resource flows from transcript"""

    def __init__(self, transcript_path: Path, entities_path: Path, checkpoint_dir: Path):
        self.transcript_path = Path(transcript_path)
        self.entities_path = Path(entities_path)
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Load entities
        self.entity_names = self.load_entity_names()

        # Resource flow patterns
        self.flow_patterns = {
            'money': [
                r'(\$[\d,]+(?:\s+(?:million|billion|thousand))?)',
                r'([\d,]+\s+(?:dollars|lira|pounds|marks))',
                r'([\d,]+\s+million)',
                r'paid\s+(.*?)\s+to',
                r'transferred\s+(.*?)\s+to',
                r'donated\s+(.*?)\s+to',
                r'funded\s+with\s+(.*)',
            ],
            'weapons': [
                r'(Stinger missiles?)',
                r'(weapons?)',
                r'(arms)',
                r'(munitions?)',
                r'(explosives?)',
                r'(\.57mm recoilless rifles?)',
                r'(hand grenades?)',
                r'shipped.*?(weapons|arms|munitions)',
            ],
            'drugs': [
                r'(heroin)',
                r'(cocaine)',
                r'(narcotics?)',
                r'(opium)',
                r'(methamphetamines?)',
                r'(marijuana)',
                r'drug.*?trafficking',
            ],
            'information': [
                r'(intelligence)',
                r'(documents?)',
                r'(files?)',
                r'(records?)',
                r'(classified.*?information)',
                r'shared.*?intelligence',
            ]
        }

        # Transfer verbs
        self.transfer_verbs = [
            'paid', 'transferred', 'provided', 'supplied', 'sent', 'shipped',
            'delivered', 'gave', 'donated', 'funded', 'financed', 'received'
        ]

    def load_entity_names(self) -> List[str]:
        """Load entity names from dossiers"""
        with open(self.entities_path) as f:
            data = json.load(f)

        names = []
        for name in data['dossiers'].keys():
            names.append(name)

        return names

    def find_entities_in_text(self, text: str) -> List[str]:
        """Find entity mentions in text"""
        found = []
        for name in self.entity_names:
            if name in text:
                found.append(name)
        return found

    def extract_resource_type_and_amount(self, text: str) -> List[tuple]:
        """Extract resource type and amount from text"""
        resources = []

        for resource_type, patterns in self.flow_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    amount = match.group(1) if match.lastindex and match.lastindex >= 1 else "unspecified"
                    resources.append((resource_type, amount))

        return resources

    def find_transfer_relationships(self, text: str, entities: List[str]) -> List[tuple]:
        """Find source->recipient relationships in text"""
        relationships = []

        # Look for transfer verbs
        for verb in self.transfer_verbs:
            # Pattern: entity1 <verb> ... to entity2
            for i, entity1 in enumerate(entities):
                for entity2 in entities[i+1:]:
                    # Check if both entities and verb are in text
                    if verb in text.lower():
                        # Determine direction based on verb position relative to entities
                        entity1_pos = text.find(entity1)
                        entity2_pos = text.find(entity2)
                        verb_pos = text.lower().find(verb)

                        if entity1_pos != -1 and entity2_pos != -1 and verb_pos != -1:
                            # entity1 <verb> ... entity2 (entity1 is source)
                            if entity1_pos < verb_pos < entity2_pos:
                                relationships.append((entity1, entity2))
                            # entity2 received from entity1
                            elif verb in ['received'] and entity2_pos < verb_pos < entity1_pos:
                                relationships.append((entity1, entity2))

        return relationships

    def extract_flows_from_batch(self, lines: List[str], start_line: int) -> List[ResourceFlow]:
        """Extract resource flows from batch"""
        flows = []

        for i, line in enumerate(lines):
            line_num = start_line + i

            # Find entities
            entities = self.find_entities_in_text(line)

            # Find resources
            resources = self.extract_resource_type_and_amount(line)

            # Find transfer relationships
            transfers = self.find_transfer_relationships(line, entities)

            # Create flows
            if resources and transfers:
                for source, recipient in transfers:
                    for resource_type, amount in resources:
                        flows.append(ResourceFlow(
                            source_entity=source,
                            recipient_entity=recipient,
                            resource_type=resource_type,
                            amount=amount,
                            description=line[:150],
                            line_number=line_num,
                            confidence=0.6
                        ))

        return flows

    def save_batch_checkpoint(self, batch_id: int, flows: List[ResourceFlow]):
        """Save flows to checkpoint"""
        checkpoint_file = self.checkpoint_dir / f"flows_batch_{batch_id:03d}.json"

        data = {
            'batch_id': batch_id,
            'flow_count': len(flows),
            'flows': [asdict(f) for f in flows],
            'timestamp': datetime.now().isoformat()
        }

        with open(checkpoint_file, 'w') as f:
            json.dump(data, f, indent=2)

    def process_transcript(self, batch_size: int = 50) -> Dict[str, int]:
        """Process transcript to extract resource flows"""

        print(f"Processing transcript: {self.transcript_path}")

        with open(self.transcript_path) as f:
            lines = f.readlines()

        total_flows = 0
        batch_id = 0

        for start_idx in range(0, len(lines), batch_size):
            end_idx = min(start_idx + batch_size, len(lines))
            batch_lines = lines[start_idx:end_idx]

            # Extract flows
            flows = self.extract_flows_from_batch(batch_lines, start_idx)

            # Save checkpoint
            self.save_batch_checkpoint(batch_id, flows)

            total_flows += len(flows)
            print(f"  Batch {batch_id:3d}: {len(flows)} resource flows found")

            batch_id += 1

        print(f"\nResource flow extraction complete!")
        print(f"  Total flows: {total_flows}")

        return {'total_flows': total_flows, 'total_batches': batch_id}

    def consolidate_flows(self) -> Dict:
        """Load and consolidate all flows"""

        print("\nConsolidating resource flows...")

        all_flows = []
        for checkpoint_file in sorted(self.checkpoint_dir.glob("flows_batch_*.json")):
            with open(checkpoint_file) as f:
                data = json.load(f)
                for flow_data in data['flows']:
                    all_flows.append(ResourceFlow(**flow_data))

        # Group by resource type
        by_type = {
            'money': [],
            'weapons': [],
            'drugs': [],
            'information': []
        }

        for flow in all_flows:
            if flow.resource_type in by_type:
                by_type[flow.resource_type].append(flow)

        print(f"  Money flows: {len(by_type['money'])}")
        print(f"  Weapons flows: {len(by_type['weapons'])}")
        print(f"  Drug flows: {len(by_type['drugs'])}")
        print(f"  Information flows: {len(by_type['information'])}")

        return by_type

    def save_flows(self, flows_by_type: Dict, output_path: Path):
        """Save consolidated flows"""

        data = {
            'metadata': {
                'total_flows': sum(len(flows) for flows in flows_by_type.values()),
                'money_flows': len(flows_by_type['money']),
                'weapons_flows': len(flows_by_type['weapons']),
                'drug_flows': len(flows_by_type['drugs']),
                'information_flows': len(flows_by_type['information']),
                'generated': datetime.now().isoformat()
            },
            'flows_by_type': {
                k: [asdict(f) for f in v] for k, v in flows_by_type.items()
            }
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\nSaved flows to {output_path}")


def main():
    """Track resource flows in Operation Gladio"""

    transcript_path = Path("/home/johnny5/Sherlock/audiobooks/operation_gladio/operation_gladio_transcript.txt")
    entities_path = Path("/home/johnny5/Sherlock/audiobooks/operation_gladio/entity_dossiers.json")
    checkpoint_dir = Path("/home/johnny5/Sherlock/audiobooks/operation_gladio/flow_checkpoints")
    output_path = Path("/home/johnny5/Sherlock/audiobooks/operation_gladio/resource_flows.json")

    tracker = ResourceFlowTracker(transcript_path, entities_path, checkpoint_dir)

    # Extract flows
    stats = tracker.process_transcript(batch_size=50)

    # Consolidate
    flows_by_type = tracker.consolidate_flows()

    # Save
    tracker.save_flows(flows_by_type, output_path)

    # Show samples
    print("\n" + "="*60)
    print("SAMPLE RESOURCE FLOWS:")
    print("="*60)

    for resource_type, flows in flows_by_type.items():
        if flows:
            print(f"\n{resource_type.upper()} ({len(flows)} total):")
            for flow in flows[:5]:
                print(f"  {flow.source_entity} -> {flow.recipient_entity}")
                print(f"    Amount: {flow.amount}")
                print(f"    Context: {flow.description[:100]}...")


if __name__ == "__main__":
    main()
