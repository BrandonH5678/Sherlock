#!/usr/bin/env python3
"""
Operation Gladio Entity Dossier Builder
Consolidates entity mentions into structured dossiers with deduplication

Design: Merge multiple mentions of same entity, build comprehensive profiles
Memory: <200MB
Pattern: Deduplication and aggregation
"""

import json
from pathlib import Path
from typing import List, Dict, Set
from dataclasses import dataclass, asdict, field
from collections import defaultdict
from datetime import datetime


@dataclass
class EntityDossier:
    """Consolidated dossier for a person or organization"""
    name: str
    entity_type: str  # "person" or "organization"
    aliases: List[str] = field(default_factory=list)
    mention_count: int = 0
    first_appearance_line: int = 0
    roles: List[str] = field(default_factory=list)
    affiliations: List[str] = field(default_factory=list)
    contexts: List[str] = field(default_factory=list)
    confidence: float = 0.0


class EntityDossierBuilder:
    """Build structured dossiers from raw entity mentions"""

    def __init__(self, checkpoint_dir: Path):
        self.checkpoint_dir = Path(checkpoint_dir)

        # Alias mapping for deduplication
        self.person_aliases = {
            'George H. W. Bush': ['George H.W. Bush', 'George Bush', 'Bush'],
            'Pope John Paul II': ['John Paul II', 'Pope John Paul'],
            'Pope Paul VI': ['Paul VI'],
            'Osama bin Laden': ['bin Laden', 'Osama'],
            'Malcolm X': ['Malcolm Little'],
            'Michele Sindona': ['Sindona'],
            'Roberto Calvi': ['Calvi'],
            'Licio Gelli': ['Gelli'],
            'Alan Dulles': ['Dulles'],
            'William Donovan': ['Donovan', 'Wild Bill'],
            'Giulio Andreotti': ['Andreotti'],
        }

        self.org_aliases = {
            'CIA': ['Central Intelligence Agency', 'Agency'],
            'FBI': ['Federal Bureau of Investigation'],
            'Vatican': ['Holy Mother Church', 'Church', 'Vatican Bank', 'IOR'],
            'OSS': ['Office of Strategic Services'],
            'NATO': ['North Atlantic Treaty Organization'],
            'P2': ['Propaganda Due'],
        }

        # Role extraction patterns
        self.role_keywords = [
            'director', 'president', 'minister', 'archbishop', 'cardinal',
            'bishop', 'general', 'admiral', 'agent', 'operative', 'chief',
            'chairman', 'founder', 'leader', 'head', 'commander'
        ]

    def normalize_name(self, name: str, entity_type: str) -> str:
        """Normalize entity name for deduplication"""

        # Check aliases
        if entity_type == "person":
            for canonical, aliases in self.person_aliases.items():
                if name in aliases or name == canonical:
                    return canonical

        elif entity_type == "organization":
            for canonical, aliases in self.org_aliases.items():
                if name in aliases or name == canonical:
                    return canonical

        # Default: clean whitespace
        return ' '.join(name.split())

    def extract_roles(self, contexts: List[str]) -> List[str]:
        """Extract roles from context strings"""
        roles = set()

        for context in contexts:
            context_lower = context.lower()
            for keyword in self.role_keywords:
                if keyword in context_lower:
                    # Try to extract fuller role phrase
                    for phrase in context.split('.'):
                        if keyword in phrase.lower():
                            roles.add(phrase.strip()[:100])  # Limit length
                            break

        return list(roles)[:5]  # Top 5 roles

    def extract_affiliations(self, contexts: List[str], entity_type: str) -> List[str]:
        """Extract organizational affiliations from contexts"""
        affiliations = set()

        # Common org names to look for
        org_names = [
            'CIA', 'FBI', 'Vatican', 'NATO', 'OSS', 'P2', 'Mafia',
            'Opus Dei', 'Red Brigades', 'Mujahideen', 'Al-Qaeda'
        ]

        for context in contexts:
            for org in org_names:
                if org in context:
                    affiliations.add(org)

        return list(affiliations)[:10]  # Top 10 affiliations

    def build_dossiers(self, entities: List[Dict]) -> Dict[str, EntityDossier]:
        """Build consolidated dossiers from raw entity mentions"""

        # Group mentions by normalized name
        mentions_by_name = defaultdict(list)

        for entity in entities:
            normalized = self.normalize_name(entity['name'], entity['entity_type'])
            mentions_by_name[(normalized, entity['entity_type'])].append(entity)

        # Build dossiers
        dossiers = {}

        for (name, entity_type), mentions in mentions_by_name.items():
            # Collect all contexts
            contexts = [m['context'] for m in mentions]

            # Sort mentions by line number to get first appearance
            mentions_sorted = sorted(mentions, key=lambda m: m['line_number'])

            # Build dossier
            dossier = EntityDossier(
                name=name,
                entity_type=entity_type,
                mention_count=len(mentions),
                first_appearance_line=mentions_sorted[0]['line_number'],
                contexts=contexts[:10],  # Keep top 10 contexts
                confidence=sum(m.get('confidence', 0.8) for m in mentions) / len(mentions)
            )

            # Extract roles and affiliations
            dossier.roles = self.extract_roles(contexts)
            dossier.affiliations = self.extract_affiliations(contexts, entity_type)

            # Collect aliases
            raw_names = set(m['name'] for m in mentions)
            dossier.aliases = [n for n in raw_names if n != name]

            dossiers[name] = dossier

        return dossiers

    def load_entities_from_checkpoints(self) -> List[Dict]:
        """Load all entities from checkpoint files"""
        all_entities = []

        for checkpoint_file in sorted(self.checkpoint_dir.glob("batch_*.json")):
            with open(checkpoint_file) as f:
                data = json.load(f)
                all_entities.extend(data['entities'])

        return all_entities

    def save_dossiers(self, dossiers: Dict[str, EntityDossier], output_path: Path):
        """Save dossiers to JSON file"""

        dossiers_data = {
            'metadata': {
                'total_entities': len(dossiers),
                'people': len([d for d in dossiers.values() if d.entity_type == 'person']),
                'organizations': len([d for d in dossiers.values() if d.entity_type == 'organization']),
                'generated': datetime.now().isoformat()
            },
            'dossiers': {name: asdict(d) for name, d in dossiers.items()}
        }

        with open(output_path, 'w') as f:
            json.dump(dossiers_data, f, indent=2)

        print(f"Saved {len(dossiers)} dossiers to {output_path}")

    def process(self, output_path: Path) -> Dict[str, EntityDossier]:
        """Full processing pipeline"""

        print(f"Loading entities from {self.checkpoint_dir}...")
        entities = self.load_entities_from_checkpoints()
        print(f"  Loaded {len(entities)} entity mentions")

        print("Building dossiers...")
        dossiers = self.build_dossiers(entities)
        print(f"  Created {len(dossiers)} unique entities")

        print("Saving dossiers...")
        self.save_dossiers(dossiers, output_path)

        return dossiers


def main():
    """Test dossier building"""

    checkpoint_dir = Path("/home/johnny5/Sherlock/audiobooks/operation_gladio/entity_checkpoints")
    output_path = Path("/home/johnny5/Sherlock/audiobooks/operation_gladio/entity_dossiers.json")

    if not checkpoint_dir.exists():
        print(f"ERROR: Checkpoint directory not found: {checkpoint_dir}")
        return

    builder = EntityDossierBuilder(checkpoint_dir)
    dossiers = builder.process(output_path)

    # Show top entities
    people = {name: d for name, d in dossiers.items() if d.entity_type == 'person'}
    orgs = {name: d for name, d in dossiers.items() if d.entity_type == 'organization'}

    print("\n" + "="*60)
    print("TOP PEOPLE (by mention count):")
    print("="*60)

    top_people = sorted(people.items(), key=lambda x: x[1].mention_count, reverse=True)[:15]
    for name, dossier in top_people:
        print(f"\n{name}")
        print(f"  Mentions: {dossier.mention_count}")
        print(f"  Roles: {', '.join(dossier.roles[:3])}" if dossier.roles else "  Roles: (none)")
        print(f"  Affiliations: {', '.join(dossier.affiliations[:3])}" if dossier.affiliations else "  Affiliations: (none)")

    print("\n" + "="*60)
    print("TOP ORGANIZATIONS (by mention count):")
    print("="*60)

    top_orgs = sorted(orgs.items(), key=lambda x: x[1].mention_count, reverse=True)[:15]
    for name, dossier in top_orgs:
        print(f"\n{name}")
        print(f"  Mentions: {dossier.mention_count}")
        print(f"  Aliases: {', '.join(dossier.aliases[:3])}" if dossier.aliases else "  Aliases: (none)")


if __name__ == "__main__":
    main()
