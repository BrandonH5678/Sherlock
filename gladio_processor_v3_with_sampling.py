#!/usr/bin/env python3
"""
Operation Gladio Voice Processor V3 - With Statistical Sampling Validation
Integrates statistical sampling validation to ensure output quality before full processing
"""

import os
import sys
import json
import time
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Import Sherlock components
from voice_engine import VoiceEngineManager, VoiceProcessingRequest, TranscriptionMode, ProcessingPriority
from evidence_schema_gladio import (
    GladioEvidenceDatabase, PersonDossier, Organization,
    Evidence, Claim, TimeReference, EvidenceType, ConfidenceLevel
)
from statistical_sampling_validator import StatisticalSamplingValidator


class GladioProcessorV3WithSampling(VoiceEngineManager):
    """
    Operation Gladio processor with integrated statistical sampling validation
    """

    def __init__(self):
        # Initialize parent VoiceEngineManager
        super().__init__(max_ram_gb=3.7)

        # Initialize components
        self.evidence_db = GladioEvidenceDatabase("gladio_intelligence.db")
        self.validator = StatisticalSamplingValidator(sample_size=3, validation_interval=10)

        # Processing statistics
        self.processing_stats = {
            "chunks_created": 0,
            "chunks_validated": 0,
            "chunks_processed": 0,
            "entities_extracted": 0,
            "relationships_found": 0,
            "processing_time": 0,
            "start_time": None,
            "validation_passed": False,
            "validation_reports": []
        }

        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def process_gladio_audiobook_with_validation(self, aaxc_file: str) -> bool:
        """
        Process Operation Gladio audiobook with statistical sampling validation
        """
        self.processing_stats["start_time"] = time.time()

        try:
            self.logger.info(f"🚀 Starting Operation Gladio processing with statistical sampling validation")
            self.logger.info(f"📊 Input: {aaxc_file}")

            # Load faster-whisper tiny model
            if not self._load_model(TranscriptionMode.FAST):
                self.logger.error("❌ Failed to load faster-whisper tiny model")
                return False

            # Phase 1: Create audio chunks
            self.logger.info("🔧 Phase 1: Creating audio chunks...")
            chunks = self._create_audio_chunks_with_validation(aaxc_file, chunk_duration=600)
            self.processing_stats["chunks_created"] = len(chunks)

            if not chunks:
                self.logger.error("❌ No valid audio chunks created")
                return False

            # Phase 2: Statistical sampling validation
            self.logger.info("🔍 Phase 2: Running statistical sampling validation...")
            validation_report = self.validator.validate_processing_pipeline(chunks)
            self.processing_stats["validation_reports"].append(validation_report)
            self.processing_stats["chunks_validated"] = validation_report.total_samples

            # Save validation report
            self.validator.save_validation_report(validation_report, "gladio_validation_report.json")

            # Check if processing should continue
            if not validation_report.processing_viability:
                self.logger.error("❌ Statistical sampling validation FAILED")
                self.logger.error("❌ Processing stopped to prevent resource waste")
                self._generate_validation_failure_report(validation_report)
                return False

            self.logger.info("✅ Statistical sampling validation PASSED")
            self.processing_stats["validation_passed"] = True

            # Phase 3: Full processing of validated chunks
            self.logger.info("⚙️ Phase 3: Processing validated chunks...")
            success = self._process_validated_chunks(chunks, validation_report)

            if success:
                # Phase 4: Generate final deliverables
                self.logger.info("📊 Phase 4: Generating final deliverables...")
                self._generate_final_deliverables_with_validation()

            processing_time = time.time() - self.processing_stats["start_time"]
            self.processing_stats["processing_time"] = processing_time

            if success:
                self.logger.info(f"✅ Operation Gladio processing completed in {processing_time/60:.1f} minutes")
                self._verify_final_deliverables()
            else:
                self.logger.error("❌ Processing failed during chunk processing phase")

            return success

        except Exception as e:
            self.logger.error(f"❌ Critical processing error: {e}")
            return False

    def _create_audio_chunks_with_validation(self, aaxc_file: str, chunk_duration: int = 600) -> List[str]:
        """
        Create audio chunks with immediate validation of each chunk
        """
        chunks = []
        audio_path = Path(aaxc_file)
        chunks_dir = audio_path.parent / "gladio_chunks_v3"
        chunks_dir.mkdir(exist_ok=True)

        try:
            # Get total duration
            result = subprocess.run([
                "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                "-of", "csv=p=0", aaxc_file
            ], capture_output=True, text=True, check=True)

            total_duration = float(result.stdout.strip())
            self.logger.info(f"📏 Total audio duration: {total_duration/3600:.2f} hours")

            chunk_count = int(total_duration // chunk_duration) + 1
            valid_chunks = 0
            consecutive_failures = 0

            for i in range(chunk_count):
                start_time = i * chunk_duration
                chunk_file = chunks_dir / f"gladio_chunk_{i+1:03d}.wav"

                # Extract chunk
                cmd = [
                    "ffmpeg", "-y", "-i", aaxc_file,
                    "-ss", str(start_time), "-t", str(chunk_duration),
                    "-acodec", "pcm_s16le", "-ar", "16000",
                    str(chunk_file)
                ]

                result = subprocess.run(cmd, capture_output=True, text=True)

                # Immediate validation of chunk
                if self._validate_chunk_immediately(chunk_file):
                    chunks.append(str(chunk_file))
                    valid_chunks += 1
                    consecutive_failures = 0
                    self.logger.info(f"✅ Valid chunk {i+1}: {chunk_file.name} ({chunk_file.stat().st_size} bytes)")
                else:
                    consecutive_failures += 1
                    self.logger.warning(f"⚠️ Invalid chunk {i+1}: {chunk_file.name}")

                # Stop early if too many consecutive failures (optimization)
                if consecutive_failures >= 10 and valid_chunks == 0:
                    self.logger.warning("⚠️ Too many consecutive chunk failures, stopping early")
                    break

                # Report progress every 10 chunks
                if (i + 1) % 10 == 0:
                    self.logger.info(f"📈 Progress: {i+1}/{chunk_count} chunks processed, {valid_chunks} valid")

            self.logger.info(f"📊 Chunk creation complete: {valid_chunks}/{chunk_count} chunks valid")
            return chunks

        except Exception as e:
            self.logger.error(f"❌ Audio chunking failed: {e}")
            return []

    def _validate_chunk_immediately(self, chunk_file: Path) -> bool:
        """
        Immediate validation of a single chunk
        """
        try:
            # Check file exists and has content
            if not chunk_file.exists() or chunk_file.stat().st_size < 1000:
                return False

            # Quick format validation with ffprobe
            result = subprocess.run([
                "ffprobe", "-v", "quiet", "-select_streams", "a:0",
                "-show_entries", "stream=duration",
                "-of", "csv=p=0", str(chunk_file)
            ], capture_output=True, text=True)

            if result.returncode == 0 and result.stdout.strip():
                duration = float(result.stdout.strip())
                return duration > 0.1  # At least 0.1 seconds

            return False

        except Exception:
            return False

    def _process_validated_chunks(self, chunks: List[str], validation_report) -> bool:
        """
        Process only the chunks that passed validation
        """
        if not chunks:
            self.logger.error("❌ No chunks available for processing")
            return False

        full_transcript = []
        processed_count = 0

        for i, chunk_path in enumerate(chunks):
            self.logger.info(f"🔄 Processing chunk {i+1}/{len(chunks)}: {Path(chunk_path).name}")

            try:
                # Create VoiceProcessingRequest
                request = VoiceProcessingRequest(
                    audio_path=chunk_path,
                    mode=TranscriptionMode.FAST,
                    priority=ProcessingPriority.BACKGROUND,
                    system="sherlock",
                    metadata={"chunk_index": i, "source": "Operation Gladio V3"}
                )

                # Process through VoiceEngineManager - use direct method call instead of missing method
                result = self.process_voice_request(request)

                if result and hasattr(result, 'text') and result.text:
                    full_transcript.append(result.text)
                    processed_count += 1

                    # Extract intelligence
                    self._extract_chunk_intelligence_with_validation(result.text, i)

                    self.logger.info(f"✅ Chunk {i+1} processed: {len(result.text)} characters")
                else:
                    self.logger.warning(f"⚠️ Chunk {i+1} produced no transcription")

            except Exception as e:
                self.logger.error(f"❌ Error processing chunk {i+1}: {e}")

            # Memory management
            import gc
            gc.collect()

        self.processing_stats["chunks_processed"] = processed_count

        # Save transcript
        if full_transcript:
            transcript_file = Path("operation_gladio_transcript_v3.txt")
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(full_transcript))
            self.logger.info(f"📝 Transcript saved: {transcript_file} ({len(full_transcript)} chunks)")

        return processed_count > 0

    def _extract_chunk_intelligence_with_validation(self, text: str, chunk_index: int):
        """
        Extract intelligence with validation metrics
        """
        import re

        extracted_entities = 0

        # Extract people
        people_patterns = [
            r'([A-Z][a-z]+ [A-Z][a-z]+)',
            r'(General [A-Z][a-z]+)',
            r'(Colonel [A-Z][a-z]+)',
            r'(Cardinal [A-Z][a-z]+)',
            r'(Pope [A-Z][a-z]+ [IVX]+)',
        ]

        people_found = set()
        for pattern in people_patterns:
            matches = re.findall(pattern, text)
            people_found.update(matches)

        # Add people to database
        for name in people_found:
            if len(name.split()) >= 2:
                person = PersonDossier(
                    primary_name=name,
                    aliases=[],
                    organizations=[],
                    timeline_events=[],
                    evidence_confidence=ConfidenceLevel.PROBABLE,
                    last_updated=datetime.now()
                )
                self.evidence_db.add_person(person)
                extracted_entities += 1

        # Extract organizations
        org_patterns = [
            r'(CIA)', r'(Vatican)', r'(Mafia)', r'(P-2|P2)', r'(Gladio)', r'(NATO)'
        ]

        orgs_found = set()
        for pattern in org_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            orgs_found.update(matches)

        # Add organizations to database
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
            extracted_entities += 1

        self.processing_stats["entities_extracted"] += extracted_entities
        self.logger.info(f"📊 Chunk {chunk_index+1}: {len(people_found)} people, {len(orgs_found)} organizations")

    def _generate_final_deliverables_with_validation(self):
        """
        Generate final deliverables with validation metrics included
        """
        # Get people using correct API
        all_people = self.evidence_db.search_people("")  # Empty search returns all

        report = {
            "processing_date": datetime.now().isoformat(),
            "source": "Operation Gladio by Paul L. Williams (audiobook)",
            "processing_method": "VoiceEngineManager + faster-whisper tiny + Statistical Sampling Validation",
            "validation_framework": "Statistical Sampling V1.0",
            "statistics": self.processing_stats,
            "validation_summary": {
                "validation_passed": self.processing_stats["validation_passed"],
                "chunks_created": self.processing_stats["chunks_created"],
                "chunks_validated": self.processing_stats["chunks_validated"],
                "chunks_processed": self.processing_stats["chunks_processed"],
                "processing_efficiency": self.processing_stats["chunks_processed"] / max(1, self.processing_stats["chunks_created"])
            },
            "database_summary": {
                "total_people": len(all_people),
                "total_entities": self.processing_stats["entities_extracted"],
                "processing_time_minutes": self.processing_stats["processing_time"] / 60
            },
            "deliverables": {
                "transcript_file": "operation_gladio_transcript_v3.txt",
                "intelligence_database": "gladio_intelligence.db",
                "validation_report": "gladio_validation_report.json",
                "processing_report": "gladio_processing_report_v3.json"
            }
        }

        with open("gladio_processing_report_v3.json", "w") as f:
            json.dump(report, f, indent=2, default=str)

        self.logger.info("📊 Processing report generated: gladio_processing_report_v3.json")

    def _generate_validation_failure_report(self, validation_report):
        """
        Generate detailed report when validation fails
        """
        failure_report = {
            "timestamp": datetime.now().isoformat(),
            "status": "VALIDATION_FAILED",
            "reason": "Statistical sampling validation failed to meet minimum quality thresholds",
            "validation_results": {
                "processing_viability": validation_report.processing_viability,
                "quality_metrics": {
                    "average_quality_score": validation_report.average_quality_score,
                    "transcription_success_rate": validation_report.transcription_success_rate,
                    "entity_extraction_rate": validation_report.entity_extraction_rate,
                    "format_success_rate": validation_report.format_success_rate
                },
                "samples_tested": validation_report.total_samples,
                "successful_samples": validation_report.successful_samples
            },
            "recommendations": validation_report.recommendations,
            "next_steps": [
                "Review AAXC decryption requirements",
                "Test alternative audio conversion methods",
                "Verify model compatibility with input format",
                "Consider different chunk size or processing parameters"
            ]
        }

        with open("gladio_validation_failure_report.json", "w") as f:
            json.dump(failure_report, f, indent=2)

        self.logger.info("📊 Validation failure report generated: gladio_validation_failure_report.json")

    def _verify_final_deliverables(self):
        """
        Verify all expected deliverables were created and contain valid data
        """
        self.logger.info("🔍 Verifying final deliverables...")

        deliverables = [
            ("operation_gladio_transcript_v3.txt", "transcript"),
            ("gladio_intelligence.db", "database"),
            ("gladio_processing_report_v3.json", "processing report"),
            ("gladio_validation_report.json", "validation report")
        ]

        for filename, description in deliverables:
            file_path = Path(filename)
            if file_path.exists() and file_path.stat().st_size > 100:
                self.logger.info(f"✅ {description}: {filename} ({file_path.stat().st_size} bytes)")
            else:
                self.logger.warning(f"⚠️ {description} missing or too small: {filename}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 gladio_processor_v3_with_sampling.py <aaxc_file>")
        sys.exit(1)

    aaxc_file = sys.argv[1]
    if not os.path.exists(aaxc_file):
        print(f"❌ File not found: {aaxc_file}")
        sys.exit(1)

    print("🎯 OPERATION GLADIO VOICE PROCESSOR V3")
    print("✅ Statistical Sampling Validation Integrated")
    print("Using VoiceEngineManager + faster-whisper tiny")
    print("=" * 60)
    print(f"Processing: {aaxc_file}")
    print()

    # Initialize processor with sampling validation
    processor = GladioProcessorV3WithSampling()

    # Start processing with validation
    success = processor.process_gladio_audiobook_with_validation(aaxc_file)

    if success:
        print("\n✅ OPERATION GLADIO PROCESSING COMPLETED!")
        print("📊 Check gladio_processing_report_v3.json for results")
        print("🔍 Check gladio_validation_report.json for validation details")
        print("🗄️ Intelligence database: gladio_intelligence.db")
        print("📝 Full transcript: operation_gladio_transcript_v3.txt")
    else:
        print("\n❌ PROCESSING FAILED OR VALIDATION FAILED")
        print("📁 Check validation and processing reports for details")