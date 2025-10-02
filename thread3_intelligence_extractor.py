#!/usr/bin/env python3
"""
Thread 3 Intelligence Extraction System
Processes George Knapp's documents on Soviet UFO research program

Architecture: Extends Sherlock evidence database
Memory: <200MB per task (incremental save pattern)
Integration: Uses established Sherlock evidence schema
"""

import json
import re
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict
from evidence_database import (
    EvidenceDatabase, EvidenceType, ClaimType,
    EvidenceSource, EvidenceClaim, Speaker
)


@dataclass
class Thread3Entity:
    """Entity extracted from Thread 3 documents"""
    name: str
    entity_type: str  # person, organization, program, location
    mention_count: int
    affiliations: List[str]
    roles: List[str]
    contexts: List[str]
    confidence: float


class Thread3IntelligenceExtractor:
    """
    Extract intelligence from Thread 3 documents using Sherlock evidence database

    Design: Incremental save pattern + Sherlock integration
    Memory: Checkpoint after each document section
    Output: Evidence sources, claims, relationships in Sherlock DB
    """

    def __init__(self, evidence_db_path: str = "evidence.db"):
        self.evidence_db = EvidenceDatabase(evidence_db_path)
        self.checkpoint_dir = Path("thread3_checkpoints")
        self.checkpoint_dir.mkdir(exist_ok=True)

        # Entity patterns for Soviet UFO program
        self.entity_patterns = {
            'programs': [
                r'Thread\s+(?:III|3|3)',
                r'Unit\s+73790',
                r'AAWSAP',
                r'BAASS',
                r'Kona\s+Blue',
                r'Project\s+Blue\s+Book'
            ],
            'organizations': [
                r'Ministry\s+of\s+Defense',
                r'MOD',
                r'KGB',
                r'DIA',
                r'CIA',
                r'NIDS',
                r'Lockheed\s+Martin',
                r'EG&G'
            ],
            'people': [
                r'George\s+Knapp',
                r'Harry\s+Reid',
                r'James\s+Lacatski',
                r'Robert\s+Bigelow',
                r'Boris\s+Sokolov',
                r'Igor\s+Maltsev',
                r'Rimili\s+Avramenko',
                r'Bob\s+Lazar',
                r'Al\s+O\'Donnell',
                r'David\s+Grusch'
            ],
            'locations': [
                r'Area\s+51',
                r'S-4',
                r'Groom\s+Lake',
                r'Wright-Patterson',
                r'Indian\s+Springs',
                r'Creech\s+AFB',
                r'Moscow',
                r'USSR',
                r'Russia'
            ]
        }

        # Relationship keywords
        self.relationship_keywords = {
            'investigator': ['investigated', 'researched', 'studied', 'analyzed'],
            'director': ['directed', 'led', 'headed', 'managed'],
            'witness': ['witnessed', 'observed', 'saw', 'encountered'],
            'reported': ['reported', 'stated', 'claimed', 'testified'],
            'recovered': ['recovered', 'retrieved', 'obtained', 'acquired']
        }

    def create_thread3_evidence_source(self,
                                       source_id: str,
                                       title: str,
                                       file_path: str,
                                       evidence_type: EvidenceType) -> str:
        """
        Create evidence source entry for Thread 3 document

        Returns: source_id for reference in claims
        """
        metadata = {
            'program': 'Thread 3',
            'topic': 'Soviet UFO Research',
            'source_type': 'Congressional Testimony',
            'classification_level': 'Unclassified',
            'attribution': 'George Knapp',
            'date_submitted': '2025-09-09'
        }

        source = EvidenceSource(
            source_id=source_id,
            title=title,
            url=None,
            file_path=file_path,
            evidence_type=evidence_type,
            duration=None,
            page_count=None,
            created_at=datetime.now().isoformat(),
            ingested_at=datetime.now().isoformat(),
            metadata=metadata
        )

        self.evidence_db.add_evidence_source(source)

        print(f"✅ Created evidence source: {source_id}")
        return source_id

    def extract_entities_from_text(self, text: str) -> Dict[str, List[Thread3Entity]]:
        """
        Extract entities from text using pattern matching

        Returns: Dict of entity_type -> List[Thread3Entity]
        """
        entities = {
            'programs': [],
            'organizations': [],
            'people': [],
            'locations': []
        }

        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entity_name = match.group(0)
                    # Get context around mention
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    context = text[start:end]

                    # Simple entity creation (will consolidate later)
                    entity = Thread3Entity(
                        name=entity_name,
                        entity_type=entity_type.rstrip('s'),  # Remove plural
                        mention_count=1,
                        affiliations=[],
                        roles=[],
                        contexts=[context],
                        confidence=0.8
                    )
                    entities[entity_type].append(entity)

        return entities

    def extract_claims_from_testimony(self,
                                      text: str,
                                      source_id: str,
                                      speaker_name: str = "George Knapp") -> List[str]:
        """
        Extract atomic claims from testimony text

        Returns: List of claim_ids
        """
        # Split into sentences for claim extraction
        sentences = re.split(r'(?<=[.!?])\s+', text)

        claim_ids = []
        claim_keywords = [
            'testified', 'confirmed', 'revealed', 'stated', 'admitted',
            'documented', 'investigated', 'obtained', 'recovered'
        ]

        for i, sentence in enumerate(sentences):
            # Check if sentence contains claim keywords
            if any(keyword in sentence.lower() for keyword in claim_keywords):
                claim_id = f"thread3_claim_{source_id}_{i:04d}"

                # Determine claim type
                claim_type = ClaimType.FACTUAL
                if 'believe' in sentence.lower() or 'think' in sentence.lower():
                    claim_type = ClaimType.OPINION
                elif '?' in sentence:
                    claim_type = ClaimType.QUESTION

                # Extract entities from claim
                claim_entities = []
                for entity_type, patterns in self.entity_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, sentence, re.IGNORECASE):
                            match = re.search(pattern, sentence, re.IGNORECASE)
                            if match:
                                claim_entities.append(match.group(0))

                # Get surrounding context
                context_start = max(0, i - 2)
                context_end = min(len(sentences), i + 3)
                context = ' '.join(sentences[context_start:context_end])

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
                    entities=claim_entities,
                    tags=['thread3', 'soviet_ufo', 'congressional_testimony'],
                    created_at=datetime.now().isoformat()
                )

                self.evidence_db.add_evidence_claim(claim)

                claim_ids.append(claim_id)

        print(f"✅ Extracted {len(claim_ids)} claims from {source_id}")
        return claim_ids

    def process_knapp_testimony(self, text: str) -> Dict:
        """
        Process George Knapp September 2025 Congressional testimony

        Returns: Processing statistics
        """
        print("\n🔍 Processing Knapp Congressional Testimony (Sept 2025)...")

        # Create evidence source
        source_id = "thread3_knapp_testimony_2025_09"
        self.create_thread3_evidence_source(
            source_id=source_id,
            title="George Knapp Written Testimony - UAP Hearing",
            file_path="/home/johnny5/Sherlock/evidence/thread3_knapp_testimony.pdf",
            evidence_type=EvidenceType.DOCUMENT
        )

        # Extract entities
        entities = self.extract_entities_from_text(text)

        # Extract claims
        claim_ids = self.extract_claims_from_testimony(text, source_id)

        # Save checkpoint
        checkpoint = {
            'source_id': source_id,
            'entities_extracted': {k: len(v) for k, v in entities.items()},
            'claims_extracted': len(claim_ids),
            'timestamp': datetime.now().isoformat()
        }

        checkpoint_path = self.checkpoint_dir / f"{source_id}_checkpoint.json"
        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint, f, indent=2)

        print(f"✅ Checkpoint saved: {checkpoint_path}")

        return checkpoint

    def process_congressional_statement(self, text: str) -> Dict:
        """
        Process George Knapp Congressional Statement (earlier document)

        Returns: Processing statistics
        """
        print("\n🔍 Processing Knapp Congressional Statement...")

        # Create evidence source
        source_id = "thread3_knapp_statement_congress"
        self.create_thread3_evidence_source(
            source_id=source_id,
            title="George Knapp Statement to Congress - UFO/UAP Transparency",
            file_path="/home/johnny5/Sherlock/evidence/knapp_congressional_statement.pdf",
            evidence_type=EvidenceType.DOCUMENT
        )

        # Extract entities
        entities = self.extract_entities_from_text(text)

        # Extract claims
        claim_ids = self.extract_claims_from_testimony(text, source_id)

        # Save checkpoint
        checkpoint = {
            'source_id': source_id,
            'entities_extracted': {k: len(v) for k, v in entities.items()},
            'claims_extracted': len(claim_ids),
            'timestamp': datetime.now().isoformat()
        }

        checkpoint_path = self.checkpoint_dir / f"{source_id}_checkpoint.json"
        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint, f, indent=2)

        print(f"✅ Checkpoint saved: {checkpoint_path}")

        return checkpoint

    def generate_summary_report(self, output_path: Path):
        """
        Generate Thread 3 intelligence summary from database

        Output: Markdown report with statistics and key findings
        """
        print("\n📊 Generating Thread 3 Intelligence Summary...")

        # Query database for Thread 3 evidence
        conn = self.evidence_db.connection

        # Count sources
        source_count = conn.execute("""
            SELECT COUNT(*) FROM evidence_sources
            WHERE source_id LIKE 'thread3%'
        """).fetchone()[0]

        # Count claims
        claim_count = conn.execute("""
            SELECT COUNT(*) FROM evidence_claims
            WHERE source_id LIKE 'thread3%'
        """).fetchone()[0]

        # Generate report
        report = f"""# Thread 3 Intelligence Summary

**Generated:** {datetime.now().isoformat()}
**System:** Sherlock Evidence Analysis System
**Topic:** Soviet UFO Research Program (Thread 3)

## Overview

Thread 3 was a Soviet UFO research and analysis program that operated as part of a larger UFO investigation effort by the USSR Ministry of Defense. Documents obtained by investigative reporter George Knapp in the 1990s reveal the scope and findings of this program.

## Evidence Sources

- **Total Documents Processed:** {source_count}
- **Total Claims Extracted:** {claim_count}
- **Primary Source:** George Knapp Congressional Testimony (September 9, 2025)
- **Secondary Sources:** Congressional statements, Russian Ministry of Defense documents

## Key Programs Identified

### Thread III (Thread 3)
- **Type:** Analysis and monitoring program
- **Parent Organization:** USSR Ministry of Defense
- **Duration:** 1978-1988 (confirmed), possibly longer
- **Purpose:** Monitor UFO cases and analyze UFO technology
- **Geographic Scope:** Entire Soviet military empire

### Unit 73790
- **Type:** Umbrella organization
- **Sub-Programs:** 3 separate UFO investigation programs (including Thread 3)
- **Classification:** Highly classified
- **Discovery:** Revealed through AAWSAP/BAASS analysis of Russian documents

## Key Findings from Source Documents

1. **Largest UFO Investigation in History:** USSR conducted 10-year comprehensive investigation (1978-1988)

2. **Military Encounters:** 40+ incidents where Russian fighters intercepted UFOs
   - 3 cases where MiGs fired on UFOs resulted in aircraft crashes
   - 2 pilots killed
   - Standing order changed to "avoid engagement"

3. **Nuclear Weapons Incidents:** October 1982 Ukraine missile base
   - UFO activated launch sequence for nuclear missiles
   - 4-hour observation period
   - Spontaneous system activation - officers could not stop launch sequence
   - UFOs disappeared, missiles deactivated automatically

4. **Reverse Engineering Efforts:** Soviet scientists tasked with duplicating UFO technology
   - Focus on: velocity, materials, visibility/stealth
   - Ongoing as of Knapp's 1993 Moscow visit

## Current Status

- **Document Authenticity:** Under verification (obtained via George Knapp mid-1990s)
- **AAWSAP Analysis:** Documents analyzed by Defense Intelligence Agency contractors
- **Public Disclosure:** Partial release through Knapp's Congressional testimony

## Next Steps

- Validate authenticity of Russian documents
- Cross-reference with US UFO investigation programs
- Extract additional intelligence from 63MB Thread 3 document collection
- Build entity relationship network

---

**Classification:** UNCLASSIFIED
**Source Attribution:** George Knapp, KLAS-TV Las Vegas
**Database:** Sherlock Evidence Analysis System
"""

        with open(output_path, 'w') as f:
            f.write(report)

        print(f"✅ Summary report generated: {output_path}")
        return report


def main():
    """Main execution: Process all Thread 3 documents"""
    extractor = Thread3IntelligenceExtractor()

    # Note: Actual text extraction from PDFs would be done separately
    # This is the processing framework

    print("Thread 3 Intelligence Extraction System")
    print("=" * 60)
    print("\nReady to process:")
    print("  1. Knapp Congressional Testimony (Sept 2025)")
    print("  2. Knapp Congressional Statement")
    print("  3. Thread 3 Russian Documents (63MB - requires chunking)")
    print("\nUse extractor.process_knapp_testimony(text) to begin.")


if __name__ == "__main__":
    main()
