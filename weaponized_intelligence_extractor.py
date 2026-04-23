#!/usr/bin/env python3
"""
Weaponized Podcast Intelligence Extraction System
Processes Weaponized podcast transcripts for UAP/UFO disclosure intelligence

Architecture: Extends Sherlock evidence database
Memory: <200MB per task (incremental save pattern)
Focus: UAP disclosure, Congressional action, defense contractors, whistleblowers
"""

import json
import re
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict

# Import Sherlock evidence database
try:
    from evidence_database import (
        EvidenceDatabase, EvidenceType, ClaimType,
        EvidenceSource, EvidenceClaim, Speaker
    )
except ImportError:
    print("Warning: evidence_database.py not found, will use local definitions")


@dataclass
class WeaponizedEntity:
    """Entity extracted from Weaponized podcast"""
    name: str
    entity_type: str  # person, organization, program, location, technology
    mention_count: int
    affiliations: List[str]
    roles: List[str]
    contexts: List[str]
    confidence: float


class WeaponizedIntelligenceExtractor:
    """
    Extract intelligence from Weaponized podcast transcripts

    Design: Incremental save pattern + Sherlock integration
    Memory: Checkpoint after each episode section
    Output: Evidence sources, claims, relationships in Sherlock DB
    """

    def __init__(self, evidence_db_path: str = "sherlock.db"):
        self.evidence_db = EvidenceDatabase(evidence_db_path)
        self.checkpoint_dir = Path("weaponized_checkpoints")
        self.checkpoint_dir.mkdir(exist_ok=True)

        # Entity patterns for UAP disclosure
        self.entity_patterns = {
            'people': [
                r'David\s+Gru[sz]+h',
                r'George\s+Knapp',
                r'Jeremy\s+Cor[bp]ell',
                r'Chuck\s+Schumer',
                r'Harry\s+Reid',
                r'Tim\s+Burchett',
                r'Kirsten\s+Gillibrand',
                r'Marco\s+Rubio',
                r'Cory\s+Booker',
                r'Chris\s+(?:Sharp|Mellon)',
                r'Luis\s+Elizondo',
                r'Christopher\s+Mellon',
                r'Bob\s+Lazar',
                r'Jacques\s+Vallee',
                r'Gary\s+Nolan',
                r'James\s+Lacatski',
                r'Robert\s+Bigelow',
                r'Eric\s+Davis',
                r'Hal\s+Puthoff',
                r'Michael\s+Shellenberger',
                r'Susan\s+Goh',
                r'Colonel\s+[A-Z][a-z]+',
                r'Dr\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?',
                r'Senator\s+[A-Z][a-z]+',
            ],
            'organizations': [
                r'(?:the\s+)?Pentagon',
                r'(?:the\s+)?DoD',
                r'(?:Department of Defense|Defense Department)',
                r'Lockheed\s+Martin',
                r'(?:the\s+)?CIA',
                r'(?:the\s+)?DIA',
                r'Defense\s+Intelligence\s+Agency',
                r'(?:the\s+)?FBI',
                r'(?:the\s+)?NSA',
                r'(?:the\s+)?Senate',
                r'(?:the\s+)?House(?:\s+of\s+Representatives)?',
                r'Intel(?:ligence)?\s+Committee',
                r'Armed\s+Services\s+Committee',
                r'Homeland\s+Security\s+Committee',
                r'AARO',
                r'AAWSAP',
                r'AATIP',
                r'BAASS',
                r'(?:the\s+)?New\s+York\s+Times',
                r'Liberation\s+Times',
                r'SpaceX',
                r'EG&G',
            ],
            'programs': [
                r'AARO',
                r'AAWSAP',
                r'AATIP',
                r'(?:Project\s+)?Blue\s+Book',
                r'Kona\s+Blue',
                r'Immaculate\s+Constellation',
                r'(?:National\s+Defense\s+)?Authorization\s+Act',
                r'NDAA',
                r'Intelligence\s+Authorization\s+Act',
                r'UAP\s+(?:review\s+)?board',
                r'JFK\s+(?:assassination\s+)?records?\s+board',
            ],
            'locations': [
                r'Area\s+51',
                r'S-4',
                r'Groom\s+Lake',
                r'Wright-Patterson',
                r'Pentagon',
                r'Capitol\s+Hill',
                r'Washington(?:\s+D\.?C\.?)?',
                r'Las\s+Vegas',
                r'Nevada',
            ],
            'technologies': [
                r'UAP(?:s)?',
                r'UFO(?:s)?',
                r'(?:non-human|extraterrestrial)\s+(?:intelligence|origin|craft|materials?)',
                r'(?:breakthrough|advanced)\s+technolog(?:y|ies)',
                r'(?:reverse\s+)?engineering',
                r'(?:element|Element)\s+115',
                r'metamaterial(?:s)?',
                r'(?:flying\s+)?saucer(?:s)?',
                r'(?:alien\s+)?craft',
            ]
        }

        # Disclosure-related keywords
        self.disclosure_keywords = {
            'legislation': ['amendment', 'bill', 'legislation', 'law', 'act', 'hearing'],
            'transparency': ['disclosure', 'transparency', 'declassify', 'release', 'public'],
            'coverup': ['classified', 'secret', 'hidden', 'concealed', 'coverup', 'lying'],
            'whistleblower': ['whistleblower', 'testimony', 'witness', 'testified', 'revealed'],
            'contractors': ['defense contractor', 'Lockheed', 'possession', 'materials', 'craft'],
        }

    def create_weaponized_evidence_source(self,
                                          episode_id: str,
                                          title: str,
                                          file_path: str,
                                          metadata: Dict) -> str:
        """
        Create evidence source entry for Weaponized episode

        Returns: source_id for reference in claims
        """
        source_id = f"weaponized_{episode_id}"

        metadata.update({
            'podcast': 'Weaponized',
            'hosts': ['George Knapp', 'Jeremy Corbell'],
            'topic': 'UAP Disclosure',
            'classification_level': 'Public',
        })

        source = EvidenceSource(
            source_id=source_id,
            title=title,
            url=metadata.get('url', None),
            file_path=file_path,
            evidence_type=EvidenceType.PODCAST,
            duration=metadata.get('duration', None),
            page_count=None,
            created_at=metadata.get('published_date', datetime.now().isoformat()),
            ingested_at=datetime.now().isoformat(),
            metadata=metadata
        )

        self.evidence_db.add_evidence_source(source)

        print(f"✅ Created evidence source: {source_id}")
        return source_id

    def extract_entities_from_transcript(self, text: str) -> Dict[str, List[WeaponizedEntity]]:
        """
        Extract entities from transcript using pattern matching

        Returns: Dict of entity_type -> List[WeaponizedEntity]
        """
        entities = {
            'people': {},
            'organizations': {},
            'programs': {},
            'locations': {},
            'technologies': {}
        }

        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entity_name = match.group(0)
                    # Normalize name
                    entity_name = re.sub(r'^(?:the\s+)', '', entity_name, flags=re.IGNORECASE).strip()

                    # Get context around mention
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    context = text[start:end]

                    # Accumulate or create entity
                    if entity_name not in entities[entity_type]:
                        entities[entity_type][entity_name] = WeaponizedEntity(
                            name=entity_name,
                            entity_type=entity_type.rstrip('s'),
                            mention_count=1,
                            affiliations=[],
                            roles=[],
                            contexts=[context],
                            confidence=0.8
                        )
                    else:
                        entities[entity_type][entity_name].mention_count += 1
                        entities[entity_type][entity_name].contexts.append(context)

        # Convert dicts to lists
        return {k: list(v.values()) for k, v in entities.items()}

    def extract_claims_from_transcript(self,
                                       text: str,
                                       source_id: str,
                                       speaker_name: str = "George Knapp") -> Tuple[List[str], List[Dict]]:
        """
        Extract atomic claims from transcript

        Returns: Tuple of (claim_ids, claims_data_list)
        """
        # Split into sentences for claim extraction
        sentences = re.split(r'(?<=[.!?])\s+', text)

        claim_ids = []
        claims_data = []  # NEW: Store claims for JSON backup

        # Keywords that indicate important claims
        important_keywords = [
            'testified', 'confirmed', 'revealed', 'stated', 'amendment',
            'legislation', 'hearing', 'classified', 'Lockheed', 'craft',
            'non-human', 'extraterrestrial', 'disclosure', 'whistleblower',
            'Grusch', 'Schumer', 'Congress', 'Pentagon', 'defense contractor'
        ]

        for i, sentence in enumerate(sentences):
            # Check if sentence contains important keywords
            if any(keyword.lower() in sentence.lower() for keyword in important_keywords):
                claim_id = f"{source_id}_claim_{i:04d}"

                # Determine claim type
                claim_type = ClaimType.FACTUAL
                if any(word in sentence.lower() for word in ['believe', 'think', 'feel', 'opinion']):
                    claim_type = ClaimType.OPINION
                elif '?' in sentence:
                    claim_type = ClaimType.QUESTION
                elif any(word in sentence.lower() for word in ['will', 'going to', 'expect']):
                    claim_type = ClaimType.PREDICTION

                # Extract entities from claim
                claim_entities = []
                for entity_type, patterns in self.entity_patterns.items():
                    for pattern in patterns:
                        matches = re.findall(pattern, sentence, re.IGNORECASE)
                        claim_entities.extend(matches)

                # Get surrounding context
                context_start = max(0, i - 2)
                context_end = min(len(sentences), i + 3)
                context = ' '.join(sentences[context_start:context_end])

                # Determine tags
                tags = ['weaponized', 'uap_disclosure']
                for tag_category, keywords in self.disclosure_keywords.items():
                    if any(kw.lower() in sentence.lower() for kw in keywords):
                        tags.append(tag_category)

                claim = EvidenceClaim(
                    claim_id=claim_id,
                    source_id=source_id,
                    speaker_id=speaker_name.lower().replace(' ', '_'),
                    claim_type=claim_type,
                    text=sentence.strip(),
                    confidence=0.85,
                    start_time=None,
                    end_time=None,
                    page_number=None,
                    context=context,
                    entities=list(set(claim_entities)),
                    tags=tags,
                    created_at=datetime.now().isoformat()
                )

                # NEW: Save claim data for JSON backup
                claim_dict = asdict(claim)
                # Convert enum to string for JSON serialization
                claim_dict['claim_type'] = claim_dict['claim_type'].value if hasattr(claim_dict['claim_type'], 'value') else str(claim_dict['claim_type'])
                claims_data.append(claim_dict)

                self.evidence_db.add_evidence_claim(claim)
                claim_ids.append(claim_id)

        print(f"✅ Extracted {len(claim_ids)} claims from {source_id}")
        return claim_ids, claims_data

    def process_weaponized_episode(self,
                                    transcript_path: Path,
                                    episode_id: str,
                                    title: str,
                                    metadata: Dict = None) -> Dict:
        """
        Process a Weaponized podcast episode transcript

        Returns: Processing statistics
        """
        if metadata is None:
            metadata = {}

        print(f"\n🔍 Processing Weaponized Episode: {title}")
        print(f"   Transcript: {transcript_path}")

        # Read transcript
        with open(transcript_path, 'r') as f:
            transcript_text = f.read()

        # Create evidence source
        source_id = self.create_weaponized_evidence_source(
            episode_id=episode_id,
            title=title,
            file_path=str(transcript_path),
            metadata=metadata
        )

        # Extract entities
        print(f"   Extracting entities...")
        entities = self.extract_entities_from_transcript(transcript_text)

        # Extract claims
        print(f"   Extracting claims...")
        claim_ids, claims_data = self.extract_claims_from_transcript(transcript_text, source_id)

        # NEW: Save claims to JSON backup
        claims_backup_path = self.checkpoint_dir / f"{episode_id}_claims_backup.json"
        with open(claims_backup_path, 'w') as f:
            json.dump({
                'source_id': source_id,
                'episode_id': episode_id,
                'title': title,
                'claims': claims_data,
                'total_claims': len(claims_data),
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        print(f"💾 Claims backup saved: {claims_backup_path}")

        # NEW: Save entities to JSON backup
        entities_backup_path = self.checkpoint_dir / f"{episode_id}_entities_backup.json"
        entities_serialized = {k: [asdict(e) for e in v] for k, v in entities.items()}
        with open(entities_backup_path, 'w') as f:
            json.dump({
                'source_id': source_id,
                'episode_id': episode_id,
                'title': title,
                'entities': entities_serialized,
                'total_entities': sum(len(v) for v in entities.values()),
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        print(f"💾 Entities backup saved: {entities_backup_path}")

        # Save checkpoint
        checkpoint = {
            'source_id': source_id,
            'episode_id': episode_id,
            'title': title,
            'entities_extracted': {k: len(v) for k, v in entities.items()},
            'claims_extracted': len(claim_ids),
            'timestamp': datetime.now().isoformat()
        }

        checkpoint_path = self.checkpoint_dir / f"{episode_id}_checkpoint.json"
        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint, f, indent=2)

        print(f"✅ Checkpoint saved: {checkpoint_path}")
        print(f"   Entities: {sum(checkpoint['entities_extracted'].values())}")
        print(f"   Claims: {checkpoint['claims_extracted']}")

        return checkpoint

    def generate_episode_summary(self, episode_id: str, output_dir: Path):
        """
        Generate intelligence summary for processed episode

        Output: Markdown report with key findings
        """
        print(f"\n📊 Generating summary for {episode_id}...")

        # Load checkpoint
        checkpoint_path = self.checkpoint_dir / f"{episode_id}_checkpoint.json"
        if not checkpoint_path.exists():
            print(f"❌ No checkpoint found for {episode_id}")
            return

        with open(checkpoint_path, 'r') as f:
            checkpoint = json.load(f)

        source_id = checkpoint['source_id']

        # Query database for this episode's claims
        conn = self.evidence_db.connection

        claims = conn.execute("""
            SELECT claim_type, text, entities, tags
            FROM evidence_claims
            WHERE source_id = ?
            ORDER BY created_at
        """, (source_id,)).fetchall()

        # Generate report
        report = f"""# Weaponized Episode Intelligence Summary

**Episode:** {checkpoint['title']}
**Episode ID:** {episode_id}
**Processed:** {checkpoint['timestamp']}
**System:** Sherlock Evidence Analysis System

## Statistics

- **Total Claims:** {checkpoint['claims_extracted']}
- **Entities Extracted:** {sum(checkpoint['entities_extracted'].values())}
  - People: {checkpoint['entities_extracted'].get('people', 0)}
  - Organizations: {checkpoint['entities_extracted'].get('organizations', 0)}
  - Programs: {checkpoint['entities_extracted'].get('programs', 0)}
  - Locations: {checkpoint['entities_extracted'].get('locations', 0)}
  - Technologies: {checkpoint['entities_extracted'].get('technologies', 0)}

## Key Findings

"""

        # Group claims by tag
        claims_by_tag = {}
        for claim in claims:
            claim_type, text, entities_json, tags_json = claim
            tags = json.loads(tags_json) if tags_json else []
            for tag in tags:
                if tag not in claims_by_tag:
                    claims_by_tag[tag] = []
                claims_by_tag[tag].append(text)

        # Report key categories
        for category in ['legislation', 'whistleblower', 'contractors', 'transparency']:
            if category in claims_by_tag:
                report += f"\n### {category.title()}\n\n"
                for claim in claims_by_tag[category][:10]:  # Top 10
                    report += f"- {claim}\n"

        report += f"\n---\n\n**Classification:** UNCLASSIFIED\n"
        report += f"**Source:** Weaponized Podcast (George Knapp & Jeremy Corbell)\n"
        report += f"**Database:** Sherlock Evidence Analysis System\n"

        # Save report
        output_path = output_dir / f"{episode_id}_intelligence_summary.md"
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(report)

        print(f"✅ Summary saved: {output_path}")
        return report


def main():
    """Main execution: Scan and process all Weaponized transcripts"""
    print("=" * 80)
    print("WEAPONIZED PODCAST INTELLIGENCE EXTRACTION SYSTEM")
    print("=" * 80)

    extractor = WeaponizedIntelligenceExtractor()

    # Define episodes to process
    episodes = [
        {
            'id': 'capitol_bombs',
            'title': 'UFO Bombs Dropped On Capitol Hill',
            'path': '/home/johnny5/Sherlock/freelance_transcripts/weaponized/capitol_bombs/audio_transcription/audio_FORMATTED_DIARIZED.txt',
            'metadata': {'topic': 'Schumer Amendment, Congressional Hearings'}
        },
        {
            'id': 'lacatski_part1',
            'title': 'Dr. James Lacatski Interview - Part 1',
            'path': '/home/johnny5/Sherlock/freelance_transcripts/weaponized/lacatski_part1/audio_transcription/audio.txt',
            'metadata': {'guest': 'Dr. James Lacatski', 'topic': 'AAWSAP, DIA UFO Program'}
        },
        {
            'id': 'lacatski_part2',
            'title': 'Dr. James Lacatski Interview - Part 2',
            'path': '/home/johnny5/Sherlock/freelance_transcripts/weaponized/lacatski_part2/audio_transcription/audio.txt',
            'metadata': {'guest': 'Dr. James Lacatski', 'topic': 'AAWSAP Continued'}
        },
        {
            'id': 'borland_part1',
            'title': 'Douglas Borland Interview - Part 1',
            'path': '/home/johnny5/Sherlock/freelance_transcripts/weaponized/borland_part1/audio_transcription/audio.txt',
            'metadata': {'guest': 'Douglas Borland'}
        },
        {
            'id': 'borland_part2',
            'title': 'Douglas Borland Interview - Part 2',
            'path': '/home/johnny5/Sherlock/freelance_transcripts/weaponized/borland_part2/audio_transcription/audio.txt',
            'metadata': {'guest': 'Douglas Borland'}
        },
    ]

    print(f"\nFound {len(episodes)} episodes to process\n")

    # Process each episode
    results = []
    for episode in episodes:
        episode_path = Path(episode['path'])
        if not episode_path.exists():
            print(f"⚠️  Transcript not found: {episode_path}")
            continue

        try:
            result = extractor.process_weaponized_episode(
                transcript_path=episode_path,
                episode_id=episode['id'],
                title=episode['title'],
                metadata=episode.get('metadata', {})
            )
            results.append(result)

            # Generate summary
            output_dir = Path('/home/johnny5/Sherlock/evidence')
            extractor.generate_episode_summary(episode['id'], output_dir)

        except Exception as e:
            print(f"❌ Error processing {episode['id']}: {e}")
            import traceback
            traceback.print_exc()

    # Final summary
    print("\n" + "=" * 80)
    print("PROCESSING COMPLETE")
    print("=" * 80)
    print(f"Episodes processed: {len(results)}")
    print(f"Total claims extracted: {sum(r['claims_extracted'] for r in results)}")
    print(f"Total entities: {sum(sum(r['entities_extracted'].values()) for r in results)}")
    print("\nIntelligence summaries saved to: /home/johnny5/Sherlock/evidence/")
    print("=" * 80)


if __name__ == "__main__":
    main()
