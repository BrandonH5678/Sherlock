#!/usr/bin/env python3
"""
Operation Gladio Voice Processor
Extends VoiceEngineManager for AAXC audiobook processing with intelligence extraction
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Import Sherlock components - using established architecture
from voice_engine import VoiceEngineManager, VoiceProcessingRequest, TranscriptionMode, ProcessingPriority
from evidence_schema_gladio import (
    GladioEvidenceDatabase, PersonDossier, Organization,
    Evidence, Claim, TimeReference, EvidenceType, ConfidenceLevel
)


class GladioVoiceProcessor(VoiceEngineManager):
    """
    Extends VoiceEngineManager for Operation Gladio audiobook processing
    Follows established dual-engine architecture with intelligence extraction
    """

    def __init__(self):
        # Initialize parent VoiceEngineManager with system constraints
        super().__init__(max_ram_gb=3.7)

        # Initialize Gladio evidence database
        self.evidence_db = GladioEvidenceDatabase("gladio_intelligence.db")

        # Processing statistics
        self.processing_stats = {
            "chunks_processed": 0,
            "entities_extracted": 0,
            "relationships_found": 0,
            "processing_time": 0,
            "start_time": None
        }

        # Setup logging
        self.logger = logging.getLogger(__name__)

    def process_gladio_audiobook(self, aaxc_file: str) -> bool:
        """
        Process Operation Gladio audiobook using established VoiceEngineManager architecture
        """
        self.processing_stats["start_time"] = time.time()

        try:
            self.logger.info(f"🚀 Starting Operation Gladio processing: {aaxc_file}")
            self.logger.info("📊 Using VoiceEngineManager dual-engine architecture")

            # Load faster-whisper tiny model (39MB) for memory efficiency
            if not self._load_model(TranscriptionMode.FAST):
                self.logger.error("❌ Failed to load faster-whisper tiny model")
                return False

            # Process in chunks to manage memory (10-minute segments)
            chunks = self._create_audio_chunks(aaxc_file, chunk_duration=600)  # 10 minutes

            full_transcript = []

            for i, chunk_path in enumerate(chunks):
                self.logger.info(f"🔄 Processing chunk {i+1}/{len(chunks)}: {chunk_path}")

                # Use established VoiceProcessingRequest architecture
                request = VoiceProcessingRequest(
                    audio_path=chunk_path,
                    mode=TranscriptionMode.FAST,  # faster-whisper tiny (39MB)
                    priority=ProcessingPriority.BACKGROUND,
                    system="sherlock",
                    metadata={"chunk_index": i, "source": "Operation Gladio"}
                )

                # Process through established pipeline
                result = self.transcribe_sherlock(request)

                if result and result.text:
                    full_transcript.append(result.text)
                    self.processing_stats["chunks_processed"] += 1

                    # Extract intelligence from this chunk
                    self._extract_chunk_intelligence(result.text, i)

                    self.logger.info(f"✅ Chunk {i+1} completed: {len(result.text)} characters")
                else:
                    self.logger.warning(f"⚠️ Chunk {i+1} produced no transcription")

                # Memory management between chunks
                import gc
                gc.collect()

            # Save complete transcript
            transcript_file = Path(aaxc_file).parent / "operation_gladio_transcript.txt"
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(full_transcript))

            self.logger.info(f"📝 Complete transcript saved: {transcript_file}")

            # Generate final intelligence report
            self._generate_intelligence_report()

            processing_time = time.time() - self.processing_stats["start_time"]
            self.processing_stats["processing_time"] = processing_time

            self.logger.info(f"✅ Operation Gladio processing completed in {processing_time/3600:.2f} hours")
            return True

        except Exception as e:
            self.logger.error(f"❌ Processing failed: {e}")
            return False

    def _create_audio_chunks(self, aaxc_file: str, chunk_duration: int = 600) -> List[str]:
        """
        Create audio chunks for memory-efficient processing
        """
        import subprocess

        chunks = []
        audio_path = Path(aaxc_file)
        chunks_dir = audio_path.parent / "gladio_chunks"
        chunks_dir.mkdir(exist_ok=True)

        try:
            # Get total duration using ffprobe (handles AAXC format)
            result = subprocess.run([
                "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                "-of", "csv=p=0", aaxc_file
            ], capture_output=True, text=True, check=True)

            total_duration = float(result.stdout.strip())
            self.logger.info(f"📏 Total audio duration: {total_duration/3600:.2f} hours")

            # Create chunks
            chunk_count = int(total_duration // chunk_duration) + 1

            for i in range(chunk_count):
                start_time = i * chunk_duration
                chunk_file = chunks_dir / f"gladio_chunk_{i+1:03d}.wav"

                # Extract chunk using ffmpeg
                cmd = [
                    "ffmpeg", "-y", "-i", aaxc_file,
                    "-ss", str(start_time), "-t", str(chunk_duration),
                    "-acodec", "pcm_s16le", "-ar", "16000",  # Convert to standard format
                    str(chunk_file)
                ]

                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0 and chunk_file.exists():
                    chunks.append(str(chunk_file))
                    self.logger.info(f"✅ Created chunk {i+1}: {chunk_file.name}")
                else:
                    self.logger.warning(f"⚠️ Failed to create chunk {i+1}")

            return chunks

        except Exception as e:
            self.logger.error(f"❌ Audio chunking failed: {e}")
            return []

    def _extract_chunk_intelligence(self, text: str, chunk_index: int):
        """
        Extract intelligence from transcript chunk and store in evidence database
        """
        import re

        # Extract people (names and titles)
        people_patterns = [
            r'([A-Z][a-z]+ [A-Z][a-z]+)',  # First Last
            r'(General [A-Z][a-z]+)',
            r'(Colonel [A-Z][a-z]+)',
            r'(Cardinal [A-Z][a-z]+)',
            r'(Pope [A-Z][a-z]+ [IVX]+)',
            r'([A-Z][a-z]+ Delle [A-Z][a-z]+)'  # Italian names
        ]

        people_found = set()
        for pattern in people_patterns:
            matches = re.findall(pattern, text)
            people_found.update(matches)

        # Create person dossiers
        for name in people_found:
            if len(name.split()) >= 2:  # At least first and last name
                person = PersonDossier(
                    primary_name=name,
                    aliases=[],
                    organizations=[],
                    timeline_events=[],
                    evidence_confidence=ConfidenceLevel.PROBABLE,
                    last_updated=datetime.now()
                )
                self.evidence_db.add_person(person)
                self.processing_stats["entities_extracted"] += 1

        # Extract organizations
        org_patterns = [
            r'(CIA)', r'(Vatican)', r'(Mafia)', r'(P-2|P2)', r'(Propaganda Due)',
            r'(Knights of Malta)', r'(Opus Dei)', r'(Banco Ambrosiano)',
            r'(IOR)', r'(Gladio)', r'(NATO)', r'(OSS)',
            r'(Ordine Nuovo)', r'(Avanguardia Nazionale)'
        ]

        orgs_found = set()
        for pattern in org_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            orgs_found.update(matches)

        # Create organization entries
        for org_name in orgs_found:
            org = Organization(
                name=org_name,
                aliases=[],
                founding_date=None,
                dissolution_date=None,
                declared_purpose="TBD",
                actual_purpose="TBD",
                membership=[],
                evidence_confidence=ConfidenceLevel.PROBABLE,
                last_updated=datetime.now()
            )
            self.evidence_db.add_organization(org)
            self.processing_stats["entities_extracted"] += 1

        self.logger.info(f"📊 Chunk {chunk_index+1}: {len(people_found)} people, {len(orgs_found)} organizations")

    def _generate_intelligence_report(self):
        """
        Generate comprehensive intelligence report
        """
        report = {
            "processing_date": datetime.now().isoformat(),
            "source": "Operation Gladio by Paul L. Williams (audiobook)",
            "processing_method": "VoiceEngineManager + faster-whisper tiny",
            "statistics": self.processing_stats,
            "database_summary": {
                "total_people": len(self.evidence_db.get_all_people()),
                "total_organizations": len(self.evidence_db.get_all_organizations()),
                "processing_time_hours": self.processing_stats["processing_time"] / 3600
            },
            "quality_metrics": {
                "chunks_processed": self.processing_stats["chunks_processed"],
                "average_confidence": "PROBABLE",
                "processing_method": "Chunked processing with faster-whisper tiny (39MB)"
            }
        }

        with open("gladio_intelligence_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)

        self.logger.info("📊 Intelligence report generated: gladio_intelligence_report.json")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 gladio_voice_processor.py <aaxc_file>")
        sys.exit(1)

    aaxc_file = sys.argv[1]
    if not os.path.exists(aaxc_file):
        print(f"❌ File not found: {aaxc_file}")
        sys.exit(1)

    print("🎯 OPERATION GLADIO VOICE PROCESSOR")
    print("Using VoiceEngineManager Architecture + faster-whisper tiny")
    print("=" * 60)
    print(f"Processing: {aaxc_file}")
    print()

    # Initialize processor (extends VoiceEngineManager)
    processor = GladioVoiceProcessor()

    # Start processing
    success = processor.process_gladio_audiobook(aaxc_file)

    if success:
        print("\n✅ OPERATION GLADIO PROCESSING COMPLETED!")
        print("📊 Check gladio_intelligence_report.json for results")
        print("🗄️ Intelligence database: gladio_intelligence.db")
        print("📝 Full transcript: operation_gladio_transcript.txt")
    else:
        print("\n❌ PROCESSING FAILED")
        print("📁 Check logs for details")