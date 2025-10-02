#!/usr/bin/env python3
"""
Thread 3 Russian Documents Processing
Processes 6,666 lines of Russian Ministry of Defense UFO documents

Architecture: Incremental save pattern + chunked processing
Memory: <200MB per chunk
Output: Evidence claims, entities, relationships in Sherlock DB
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from thread3_intelligence_extractor import Thread3IntelligenceExtractor
from evidence_database import EvidenceType, EvidenceClaim, ClaimType


class Thread3RussianDocProcessor:
    """
    Process Russian Ministry of Defense UFO documents in chunks

    Design: Incremental save pattern to prevent data loss
    Memory: Process in 500-line chunks (<200MB per chunk)
    Checkpoints: Save after each chunk completion
    """

    def __init__(self, text_file: Path):
        self.text_file = Path(text_file)
        self.extractor = Thread3IntelligenceExtractor(evidence_db_path="/home/johnny5/Sherlock/evidence.db")
        self.checkpoint_dir = Path("thread3_checkpoints")
        self.checkpoint_dir.mkdir(exist_ok=True)

        # Chunk size: 500 lines per chunk
        self.chunk_size = 500

        # Russian document keywords (translated)
        self.doc_keywords = {
            'ministry_of_defense': ['Ministry of Defense', 'MOD'],
            'research_topics': [
                'anomalous', 'atmospheric', 'cosmic', 'phenomena',
                'UFO', 'unidentified', 'investigation'
            ],
            'programs': ['Thread', 'Unit 73790', 'research'],
            'incidents': ['incident', 'sighting', 'encounter', 'observation'],
            'military': ['military', 'fighter', 'pilot', 'aircraft', 'missile']
        }

    def load_manifest(self) -> Dict:
        """Load or create processing manifest"""
        manifest_path = self.checkpoint_dir / "russian_docs_manifest.json"

        if manifest_path.exists():
            with open(manifest_path) as f:
                return json.load(f)

        return {
            'source_id': 'thread3_russian_mod_documents',
            'total_lines': 0,
            'chunks_processed': [],
            'chunks_total': 0,
            'claims_extracted': 0,
            'entities_found': {},
            'started': datetime.now().isoformat(),
            'last_updated': None
        }

    def save_manifest(self, manifest: Dict):
        """Save processing manifest"""
        manifest['last_updated'] = datetime.now().isoformat()
        manifest_path = self.checkpoint_dir / "russian_docs_manifest.json"

        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

    def extract_document_sections(self, lines: List[str]) -> List[Dict]:
        """
        Extract document sections from chunk

        Returns: List of {page_number, text, type}
        """
        sections = []
        current_section = []
        current_page = None

        for line in lines:
            # Detect page markers
            page_match = re.search(r'PAGE\s+(\d+)', line, re.IGNORECASE)
            if page_match:
                # Save previous section
                if current_section:
                    sections.append({
                        'page': current_page,
                        'text': '\n'.join(current_section),
                        'type': 'document'
                    })
                current_section = []
                current_page = int(page_match.group(1))
            else:
                current_section.append(line)

        # Save final section
        if current_section:
            sections.append({
                'page': current_page,
                'text': '\n'.join(current_section),
                'type': 'document'
            })

        return sections

    def process_chunk(self, chunk_id: int, lines: List[str], source_id: str) -> Dict:
        """
        Process a chunk of lines

        Returns: Processing statistics
        """
        print(f"  Processing chunk {chunk_id}...")

        # Extract sections
        sections = self.extract_document_sections(lines)

        # Extract entities from chunk
        chunk_text = '\n'.join(lines)
        entities = self.extractor.extract_entities_from_text(chunk_text)

        # Extract claims from significant sections
        claim_count = 0
        for section in sections:
            if len(section['text']) < 50:
                continue  # Skip very short sections

            # Check if section contains significant content
            has_keywords = any(
                keyword.lower() in section['text'].lower()
                for keywords in self.doc_keywords.values()
                for keyword in keywords
            )

            if has_keywords:
                # Extract sentences with UFO/anomalous content
                sentences = re.split(r'(?<=[.!?])\s+', section['text'])
                for i, sentence in enumerate(sentences):
                    if len(sentence) < 20:
                        continue

                    # Check for claim indicators
                    claim_indicators = [
                        'report', 'observed', 'detected', 'incident',
                        'investigation', 'research', 'analysis', 'study'
                    ]

                    if any(indicator in sentence.lower() for indicator in claim_indicators):
                        claim_id = f"{source_id}_chunk{chunk_id:04d}_claim{i:04d}"

                        # Get context
                        context_start = max(0, i - 1)
                        context_end = min(len(sentences), i + 2)
                        context = ' '.join(sentences[context_start:context_end])

                        # Extract entities from claim
                        claim_entities = []
                        for entity_type, patterns in self.extractor.entity_patterns.items():
                            for pattern in patterns:
                                if re.search(pattern, sentence, re.IGNORECASE):
                                    match = re.search(pattern, sentence, re.IGNORECASE)
                                    if match:
                                        claim_entities.append(match.group(0))

                        # Create claim
                        claim = EvidenceClaim(
                            claim_id=claim_id,
                            source_id=source_id,
                            speaker_id="russian_ministry_defense",
                            claim_type=ClaimType.FACTUAL,
                            text=sentence.strip(),
                            confidence=0.75,  # Lower confidence for translated documents
                            start_time=None,
                            end_time=None,
                            page_number=section['page'],
                            context=context,
                            entities=claim_entities,
                            tags=['thread3', 'russian_mod', 'translated_document'],
                            created_at=datetime.now().isoformat()
                        )

                        self.extractor.evidence_db.add_evidence_claim(claim)
                        claim_count += 1

        # Save chunk checkpoint
        checkpoint = {
            'chunk_id': chunk_id,
            'lines_processed': len(lines),
            'sections_found': len(sections),
            'claims_extracted': claim_count,
            'entities_found': {k: len(v) for k, v in entities.items()},
            'timestamp': datetime.now().isoformat()
        }

        checkpoint_path = self.checkpoint_dir / f"russian_docs_chunk{chunk_id:04d}.json"
        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint, f, indent=2)

        return checkpoint

    def process_all_chunks(self):
        """Process all chunks with incremental saves"""
        print("\n" + "=" * 70)
        print("Thread 3 Russian Ministry of Defense Documents")
        print("=" * 70)

        # Load manifest
        manifest = self.load_manifest()

        # Read all lines
        with open(self.text_file) as f:
            all_lines = f.readlines()

        total_lines = len(all_lines)
        total_chunks = (total_lines + self.chunk_size - 1) // self.chunk_size

        manifest['total_lines'] = total_lines
        manifest['chunks_total'] = total_chunks

        print(f"\nTotal lines: {total_lines:,}")
        print(f"Chunk size: {self.chunk_size}")
        print(f"Total chunks: {total_chunks}")

        # Create evidence source
        print("\nCreating evidence source...")
        source_id = manifest['source_id']
        self.extractor.create_thread3_evidence_source(
            source_id=source_id,
            title="Russian Ministry of Defense UFO Investigation Documents",
            file_path=str(self.text_file),
            evidence_type=EvidenceType.DOCUMENT
        )

        # Process chunks
        print(f"\nProcessing {total_chunks} chunks...")
        for chunk_id in range(total_chunks):
            # Check if chunk already processed
            if chunk_id in manifest['chunks_processed']:
                print(f"  ✓ Chunk {chunk_id} already processed (skipping)")
                continue

            # Get chunk lines
            start_idx = chunk_id * self.chunk_size
            end_idx = min(start_idx + self.chunk_size, total_lines)
            chunk_lines = all_lines[start_idx:end_idx]

            # Process chunk
            stats = self.process_chunk(chunk_id, chunk_lines, source_id)

            # Update manifest
            manifest['chunks_processed'].append(chunk_id)
            manifest['claims_extracted'] += stats['claims_extracted']

            # Merge entities
            for entity_type, count in stats['entities_found'].items():
                manifest['entities_found'][entity_type] = \
                    manifest['entities_found'].get(entity_type, 0) + count

            # Save manifest after each chunk
            self.save_manifest(manifest)

            print(f"    ✅ Claims: {stats['claims_extracted']}, "
                  f"Sections: {stats['sections_found']}")

        print("\n" + "=" * 70)
        print("✅ Russian Documents Processing Complete")
        print("=" * 70)
        print(f"\nTotal chunks: {len(manifest['chunks_processed'])}/{total_chunks}")
        print(f"Total claims: {manifest['claims_extracted']:,}")
        print(f"Total entities: {sum(manifest['entities_found'].values()):,}")
        print(f"\nManifest: thread3_checkpoints/russian_docs_manifest.json")


def main():
    """Main execution"""
    text_file = Path("/home/johnny5/Sherlock/evidence/thread3_documents.txt")

    if not text_file.exists():
        print(f"❌ Error: {text_file} not found")
        return

    processor = Thread3RussianDocProcessor(text_file)
    processor.process_all_chunks()


if __name__ == "__main__":
    main()
