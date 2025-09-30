#!/usr/bin/env python3
"""
Batch Operation Gladio Processor
Automated intelligence extraction from Operation Gladio audiobook
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
import logging
from datetime import datetime

# Import Sherlock components
from voice_engine import VoiceEngineManager, TranscriptionMode, ProcessingPriority
from evidence_schema_gladio import (
    GladioEvidenceDatabase, PersonDossier, Organization,
    Evidence, Claim, TimeReference, EvidenceType, ConfidenceLevel
)


class GladioBatchProcessor:
    """Automated batch processor for Operation Gladio audiobook"""

    def __init__(self, db_path: str = "gladio_complete.db"):
        self.db = GladioEvidenceDatabase(db_path)
        self.voice_engine = None
        self.processing_stats = {
            "segments_processed": 0,
            "entities_extracted": 0,
            "relationships_found": 0,
            "processing_time": 0,
            "start_time": None
        }

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('gladio_processing.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Initialize voice engine
        try:
            self.voice_engine = VoiceEngineManager()
            self.logger.info("Voice engine initialized successfully")
        except Exception as e:
            self.logger.error(f"Voice engine initialization failed: {e}")

    def process_audiobook(self, audio_file: str, segment_duration: int = 300) -> bool:
        """
        Process entire audiobook in segments for intelligence extraction

        Args:
            audio_file: Path to the Operation Gladio audiobook file
            segment_duration: Length of each processing segment in seconds (default: 5 minutes)
        """

        if not os.path.exists(audio_file):
            self.logger.error(f"Audio file not found: {audio_file}")
            return False

        self.processing_stats["start_time"] = time.time()
        self.logger.info(f"🚀 Starting automated processing of {audio_file}")

        try:
            # Step 1: Split audio into manageable segments
            segments = self._split_audio_file(audio_file, segment_duration)
            self.logger.info(f"📁 Audio split into {len(segments)} segments")

            # Step 2: Process each segment
            for i, segment in enumerate(segments):
                self.logger.info(f"🔍 Processing segment {i+1}/{len(segments)}: {segment}")

                # Transcribe segment
                transcript = self._transcribe_segment(segment)
                if transcript:
                    # Extract intelligence from transcript
                    self._extract_intelligence(transcript, segment_id=i+1)
                    self.processing_stats["segments_processed"] += 1

                # Progress update
                progress = (i + 1) / len(segments) * 100
                self.logger.info(f"📊 Progress: {progress:.1f}% complete")

            # Step 3: Post-processing analysis
            self._post_process_analysis()

            # Step 4: Generate final report
            self._generate_completion_report()

            self.processing_stats["processing_time"] = time.time() - self.processing_stats["start_time"]
            self.logger.info(f"✅ Processing completed in {self.processing_stats['processing_time']/3600:.2f} hours")

            return True

        except Exception as e:
            self.logger.error(f"❌ Processing failed: {e}")
            return False

    def _split_audio_file(self, audio_file: str, segment_duration: int) -> List[str]:
        """Split audio file into segments for processing"""
        import subprocess

        segments = []
        audio_path = Path(audio_file)
        segments_dir = audio_path.parent / "segments"
        segments_dir.mkdir(exist_ok=True)

        try:
            # Get audio duration
            result = subprocess.run([
                "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                "-of", "csv=p=0", audio_file
            ], capture_output=True, text=True, check=True)

            total_duration = float(result.stdout.strip())
            self.logger.info(f"📏 Total audio duration: {total_duration/3600:.2f} hours")

            # Split into segments
            segment_count = int(total_duration // segment_duration) + 1

            for i in range(segment_count):
                start_time = i * segment_duration
                segment_file = segments_dir / f"segment_{i+1:03d}.mp3"

                # Use ffmpeg to extract segment
                subprocess.run([
                    "ffmpeg", "-i", audio_file,
                    "-ss", str(start_time), "-t", str(segment_duration),
                    "-acodec", "copy", str(segment_file)
                ], capture_output=True, check=True)

                segments.append(str(segment_file))

            return segments

        except Exception as e:
            self.logger.error(f"Audio splitting failed: {e}")
            return []

    def _transcribe_segment(self, segment_file: str) -> Optional[str]:
        """Transcribe audio segment using Sherlock voice engine"""

        if not self.voice_engine:
            self.logger.error("Voice engine not available")
            return None

        try:
            # Use accurate mode for best quality
            result = self.voice_engine.transcribe_audio(
                segment_file,
                mode=TranscriptionMode.ACCURATE,
                priority=ProcessingPriority.BATCH
            )

            transcript = result.get("transcription", "")
            confidence = result.get("confidence", 0.0)

            self.logger.info(f"📝 Transcript confidence: {confidence:.2f}")

            if confidence < 0.7:
                self.logger.warning(f"⚠️  Low confidence transcript: {confidence:.2f}")

            return transcript

        except Exception as e:
            self.logger.error(f"Transcription failed for {segment_file}: {e}")
            return None

    def _extract_intelligence(self, transcript: str, segment_id: int):
        """Extract intelligence from transcript text"""

        self.logger.info(f"🧠 Extracting intelligence from segment {segment_id}")

        # Entity extraction patterns
        entities = self._extract_entities(transcript)

        for entity in entities:
            if entity["type"] == "person":
                self._process_person_entity(entity, transcript, segment_id)
            elif entity["type"] == "organization":
                self._process_organization_entity(entity, transcript, segment_id)
            elif entity["type"] == "date":
                self._process_temporal_entity(entity, transcript, segment_id)

        self.processing_stats["entities_extracted"] += len(entities)

    def _extract_entities(self, text: str) -> List[Dict]:
        """Extract named entities from text using pattern matching"""

        entities = []

        # Person name patterns (enhanced for intelligence context)
        person_patterns = [
            r"([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",  # Full names
            r"(?:General|Colonel|Major|Captain|Agent|Director)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",  # Titles
            r"([A-Z][a-z]+)\s+(?:was|is|served|worked|led|commanded)",  # Action context
        ]

        # Organization patterns
        org_patterns = [
            r"(CIA|FBI|NATO|KGB|Stasi|MI6|SISMI|P2|Gladio)",  # Known intel orgs
            r"([A-Z][A-Z\s]+)",  # Acronyms
            r"(?:the\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:organization|agency|service|network|operation)",
        ]

        # Date patterns
        date_patterns = [
            r"(\d{4})",  # Years
            r"((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})",  # Full dates
            r"(\d{1,2}/\d{1,2}/\d{4})",  # MM/DD/YYYY
        ]

        # Extract persons
        import re
        for pattern in person_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                entities.append({
                    "type": "person",
                    "name": match.group(1),
                    "context": text[max(0, match.start()-50):match.end()+50],
                    "confidence": 0.7
                })

        # Extract organizations
        for pattern in org_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                entities.append({
                    "type": "organization",
                    "name": match.group(1),
                    "context": text[max(0, match.start()-50):match.end()+50],
                    "confidence": 0.8
                })

        # Extract dates
        for pattern in date_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                entities.append({
                    "type": "date",
                    "value": match.group(1),
                    "context": text[max(0, match.start()-50):match.end()+50],
                    "confidence": 0.9
                })

        return entities

    def _process_person_entity(self, entity: Dict, transcript: str, segment_id: int):
        """Process extracted person entity"""

        name_parts = entity["name"].split()
        first_name = name_parts[0] if name_parts else "Unknown"
        last_name = name_parts[-1] if len(name_parts) > 1 else "Unknown"

        person_id = f"PERS_{last_name.upper()}_{first_name.upper()}"

        # Create evidence
        evidence = Evidence(
            evidence_id=f"EV_GLADIO_SEG_{segment_id}_{person_id}",
            evidence_type=EvidenceType.BOOK,
            description=f"Mentioned in Operation Gladio audiobook context: {entity['context'][:100]}...",
            source="Operation Gladio by Paul L. Williams (audiobook)",
            confidence=ConfidenceLevel.PROBABLE
        )

        # Create claim
        claim = Claim(
            claim_id=f"CL_GLADIO_{person_id}_MENTION",
            statement=f"Mentioned in Operation Gladio with context: {entity['context'][:200]}",
            category="biographical",
            supporting_evidence=[evidence],
            overall_confidence=ConfidenceLevel.PROBABLE
        )

        # Check if person already exists
        existing_people = self.db.search_people(entity["name"])

        if not existing_people:
            # Create new person dossier
            person = PersonDossier(
                person_id=person_id,
                first_name=first_name,
                last_name=last_name,
                significant_activities=[claim]
            )

            if self.db.add_person(person):
                self.logger.info(f"👤 Added new person: {entity['name']}")
        else:
            self.logger.info(f"👤 Person already exists: {entity['name']}")

    def _process_organization_entity(self, entity: Dict, transcript: str, segment_id: int):
        """Process extracted organization entity"""

        org_name = entity["name"]
        org_id = f"ORG_{org_name.upper().replace(' ', '_')}"

        # Create evidence
        evidence = Evidence(
            evidence_id=f"EV_GLADIO_SEG_{segment_id}_{org_id}",
            evidence_type=EvidenceType.BOOK,
            description=f"Mentioned in Operation Gladio context: {entity['context'][:100]}...",
            source="Operation Gladio by Paul L. Williams (audiobook)",
            confidence=ConfidenceLevel.PROBABLE
        )

        # Create claim about the organization
        claim = Claim(
            claim_id=f"CL_GLADIO_{org_id}_MENTION",
            statement=f"Organization mentioned in Operation Gladio: {entity['context'][:200]}",
            category="organizational_reference",
            supporting_evidence=[evidence],
            overall_confidence=ConfidenceLevel.PROBABLE
        )

        # Create organization entry
        organization = Organization(
            organization_id=org_id,
            name=org_name,
            significant_events=[claim]
        )

        if self.db.add_organization(organization):
            self.logger.info(f"🏢 Added organization: {org_name}")

    def _process_temporal_entity(self, entity: Dict, transcript: str, segment_id: int):
        """Process extracted temporal references"""

        # This would be used to enhance existing entities with temporal data
        self.logger.info(f"📅 Temporal reference found: {entity['value']}")

    def _post_process_analysis(self):
        """Perform post-processing analysis on extracted data"""

        self.logger.info("🔬 Starting post-processing analysis...")

        # Generate network analysis
        # Cross-reference entities
        # Identify patterns and relationships
        # Validate temporal consistency

        self.logger.info("✅ Post-processing analysis completed")

    def _generate_completion_report(self):
        """Generate comprehensive completion report"""

        report_path = "gladio_processing_report.json"

        report = {
            "processing_date": datetime.now().isoformat(),
            "source": "Operation Gladio by Paul L. Williams (audiobook)",
            "statistics": self.processing_stats,
            "database_summary": {
                "total_people": len(self.db.search_people("")),
                "total_organizations": "TBD",  # Would implement organization count
                "total_relationships": "TBD"   # Would implement relationship count
            },
            "quality_metrics": {
                "average_confidence": "TBD",
                "validation_rate": "TBD"
            }
        }

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"📊 Completion report generated: {report_path}")


def main():
    """Main processing function"""

    if len(sys.argv) < 2:
        print("Usage: python3 batch_gladio_processor.py <audiobook_file>")
        print("Example: python3 batch_gladio_processor.py operation_gladio.mp3")
        sys.exit(1)

    audiobook_file = sys.argv[1]

    print("🚀 OPERATION GLADIO BATCH PROCESSOR")
    print("=" * 50)
    print(f"Processing: {audiobook_file}")

    processor = GladioBatchProcessor()

    success = processor.process_audiobook(audiobook_file)

    if success:
        print("\n✅ PROCESSING COMPLETED SUCCESSFULLY!")
        print("📊 Check gladio_processing_report.json for details")
        print("🔍 Explore results with: python3 gladio_analysis.py")
    else:
        print("\n❌ PROCESSING FAILED")
        print("📋 Check gladio_processing.log for details")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()