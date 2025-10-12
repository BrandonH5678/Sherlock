#!/usr/bin/env python3
"""
UAP Science Document Evidence Integration
Processes "new science of UAP.pdf" chunks and integrates into Sherlock evidence database

This document appears to be scientific analysis of UAP phenomena.
Will extract claims, references, and cross-reference with existing operations.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from evidence_database import (
    EvidenceDatabase, EvidenceType, ClaimType,
    EvidenceSource, EvidenceClaim, Speaker
)


class UAPScienceIntegrator:
    """Process UAP Science PDF chunks and integrate into evidence database"""

    def __init__(self, db_path: str = "evidence.db"):
        self.db = EvidenceDatabase(db_path)
        self.chunks_dir = Path("/home/johnny5/Downloads/new science of UAP_chunks")
        self.checkpoint_dir = Path("uap_science_checkpoints")
        self.checkpoint_dir.mkdir(exist_ok=True)

        # Source document metadata
        self.source_id = "uap_science_doc_2024"
        self.total_pages = 195

        # Related operations for cross-reference
        self.related_operations = [
            'Thread 3',  # Soviet UFO research
            'Italy UFO',  # 1933 crash
            'S-Force'     # Classified military ops
        ]

    def create_source_evidence(self) -> str:
        """Create main evidence source entry for the document"""
        print("\n📄 Creating evidence source for UAP Science document...")

        source = EvidenceSource(
            source_id=self.source_id,
            title="The New Science of UAP",
            url="",  # Local PDF
            file_path='/home/johnny5/Downloads/new science of UAP.pdf',
            evidence_type=EvidenceType.DOCUMENT,
            duration=None,
            page_count=self.total_pages,
            created_at=datetime.now().isoformat(),
            ingested_at=datetime.now().isoformat(),
            metadata={
                'chunks_directory': str(self.chunks_dir),
                'total_chunks': 10,
                'document_type': 'scientific_analysis',
                'subject': 'UAP phenomena scientific investigation',
                'processing_status': 'chunked',
                'related_operations': self.related_operations
            }
        )

        source_id = self.db.add_evidence_source(source)
        print(f"✅ Created source: {source_id}")
        return source_id

    def extract_text_from_chunk(self, chunk_path: Path) -> str:
        """Extract text from a PDF chunk using PyMuPDF"""
        try:
            import fitz
        except ImportError:
            print("PyMuPDF not available in current environment")
            return ""

        doc = fitz.open(chunk_path)
        text_parts = []

        for page_num, page in enumerate(doc, 1):
            text_parts.append(f"\n--- Page {page_num} ---\n")
            text_parts.append(page.get_text())

        doc.close()
        return ''.join(text_parts)

    def process_chunk(self, chunk_num: int, chunk_path: Path) -> Dict:
        """Process a single PDF chunk and extract structured information"""
        print(f"\n🔍 Processing Chunk {chunk_num}: {chunk_path.name}")

        # Extract text
        text = self.extract_text_from_chunk(chunk_path)

        if not text:
            print(f"⚠️  No text extracted from chunk {chunk_num}")
            return {'chunk_num': chunk_num, 'status': 'failed', 'text_length': 0}

        # Save extracted text for reference
        text_file = self.checkpoint_dir / f"chunk_{chunk_num:03d}_text.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"✅ Extracted {len(text)} characters")
        print(f"📝 Saved to: {text_file}")

        # Return chunk processing summary
        return {
            'chunk_num': chunk_num,
            'chunk_path': str(chunk_path),
            'text_file': str(text_file),
            'text_length': len(text),
            'status': 'extracted',
            'preview': text[:500].replace('\n', ' ')[:200]
        }

    def analyze_chunk_content(self, chunk_info: Dict) -> List[Dict]:
        """Analyze extracted text for claims, entities, and references"""
        print(f"\n🧠 Analyzing content from chunk {chunk_info['chunk_num']}...")

        # Read the extracted text
        with open(chunk_info['text_file'], 'r', encoding='utf-8') as f:
            text = f.read()

        # Simple keyword extraction for now
        # In a full implementation, this would use NLP/LLM analysis
        findings = []

        # Look for key UAP-related terms
        keywords = {
            'craft': ['craft', 'object', 'vehicle', 'ship'],
            'phenomena': ['phenomenon', 'phenomena', 'event', 'incident'],
            'technology': ['propulsion', 'energy', 'technology', 'physics'],
            'witness': ['witness', 'observer', 'reported', 'saw'],
            'government': ['classified', 'government', 'military', 'intelligence'],
            'science': ['hypothesis', 'theory', 'evidence', 'analysis', 'research']
        }

        text_lower = text.lower()
        for category, terms in keywords.items():
            count = sum(text_lower.count(term) for term in terms)
            if count > 0:
                findings.append({
                    'category': category,
                    'mention_count': count,
                    'chunk_num': chunk_info['chunk_num']
                })

        return findings

    def process_all_chunks(self) -> List[Dict]:
        """Process all PDF chunks sequentially"""
        print(f"\n{'='*80}")
        print(f"🚀 PROCESSING UAP SCIENCE DOCUMENT")
        print(f"{'='*80}")
        print(f"Source: {self.chunks_dir}")
        print(f"Total chunks: 10")
        print(f"Database: evidence.db")

        # Create main source entry
        source_id = self.create_source_evidence()

        # Get all chunk files
        chunk_files = sorted(self.chunks_dir.glob("*_chunk_*.pdf"))
        print(f"\nFound {len(chunk_files)} chunk files")

        results = []
        all_findings = []

        for idx, chunk_path in enumerate(chunk_files, 1):
            # Extract chunk number from filename
            chunk_num = idx

            # Process chunk
            chunk_info = self.process_chunk(chunk_num, chunk_path)
            results.append(chunk_info)

            # Analyze content
            if chunk_info['status'] == 'extracted':
                findings = self.analyze_chunk_content(chunk_info)
                all_findings.extend(findings)

                # Save checkpoint
                checkpoint = {
                    'chunk_info': chunk_info,
                    'findings': findings,
                    'timestamp': datetime.now().isoformat()
                }
                checkpoint_file = self.checkpoint_dir / f"chunk_{chunk_num:03d}_checkpoint.json"
                with open(checkpoint_file, 'w') as f:
                    json.dump(checkpoint, f, indent=2)

        # Generate summary report
        self.generate_summary_report(results, all_findings)

        return results

    def generate_summary_report(self, results: List[Dict], findings: List[Dict]):
        """Generate summary report of processing"""
        print(f"\n{'='*80}")
        print(f"📊 PROCESSING SUMMARY")
        print(f"{'='*80}")

        total_chunks = len(results)
        successful = sum(1 for r in results if r['status'] == 'extracted')
        total_chars = sum(r.get('text_length', 0) for r in results)

        print(f"\nChunks Processed: {successful}/{total_chunks}")
        print(f"Total Characters Extracted: {total_chars:,}")

        # Category analysis
        if findings:
            print(f"\n📈 Content Analysis:")
            categories = {}
            for finding in findings:
                cat = finding['category']
                categories[cat] = categories.get(cat, 0) + finding['mention_count']

            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"  {cat.capitalize()}: {count} mentions")

        # Save full report
        report = {
            'processing_date': datetime.now().isoformat(),
            'source_id': self.source_id,
            'total_chunks': total_chunks,
            'successful_chunks': successful,
            'total_characters': total_chars,
            'chunk_results': results,
            'findings_summary': findings,
            'checkpoint_directory': str(self.checkpoint_dir)
        }

        report_file = self.checkpoint_dir / "processing_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n✅ Full report saved: {report_file}")
        print(f"📁 Text files saved: {self.checkpoint_dir}")
        print(f"\nNext Steps:")
        print(f"  1. Review extracted text files in {self.checkpoint_dir}")
        print(f"  2. Identify specific claims for database integration")
        print(f"  3. Extract author/speaker information")
        print(f"  4. Cross-reference with Thread 3, Italy UFO, S-Force operations")


def main():
    """Main processing workflow"""
    integrator = UAPScienceIntegrator()

    # Activate gladio environment for PyMuPDF access
    print("🔧 Using gladio_env for PDF processing...")

    # Process all chunks
    results = integrator.process_all_chunks()

    print(f"\n✅ Processing complete!")
    print(f"📊 Processed {len(results)} chunks")
    print(f"📁 Results in: {integrator.checkpoint_dir}")


if __name__ == "__main__":
    main()
