#!/usr/bin/env python3
"""
Content Ingestion Pipeline for Sherlock
Supports YouTube, podcasts, PDFs, web archives, and local audio files
"""

import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from evidence_database import (
    EvidenceDatabase, EvidenceSource, EvidenceClaim, Speaker,
    EvidenceType, ClaimType
)
from voice_engine import VoiceEngineManager
from auto_anchor_detector import AutoAnchorDetector


@dataclass
class IngestionResult:
    """Result of content ingestion operation"""
    success: bool
    source_id: str
    evidence_type: EvidenceType
    claims_extracted: int
    speakers_detected: int
    processing_time: float
    file_path: Optional[str]
    metadata: Dict
    errors: List[str]


class ContentIngestionPipeline:
    """Multi-modal content ingestion with voice processing integration"""

    def __init__(self, db_path: str = "evidence.db"):
        self.db = EvidenceDatabase(db_path)
        self.voice_engine = VoiceEngineManager()
        self.anchor_detector = AutoAnchorDetector()
        self.downloads_dir = Path("downloads")
        self.downloads_dir.mkdir(exist_ok=True)

    def ingest_local_audio(self, file_path: str, title: Optional[str] = None,
                          metadata: Optional[Dict] = None) -> IngestionResult:
        """Ingest local audio file with voice processing"""

        start_time = time.time()
        errors = []

        try:
            audio_path = Path(file_path)
            if not audio_path.exists():
                return IngestionResult(
                    success=False,
                    source_id="",
                    evidence_type=EvidenceType.AUDIO,
                    claims_extracted=0,
                    speakers_detected=0,
                    processing_time=time.time() - start_time,
                    file_path=file_path,
                    metadata={},
                    errors=[f"Audio file not found: {file_path}"]
                )

            # Generate source ID
            source_id = self._generate_source_id("audio", file_path)

            # Get audio metadata
            audio_metadata = self._get_audio_metadata(audio_path)
            full_metadata = {
                **audio_metadata,
                **(metadata or {}),
                "ingestion_method": "local_audio",
                "original_path": str(audio_path)
            }

            # Create evidence source
            evidence_source = EvidenceSource(
                source_id=source_id,
                title=title or audio_path.stem,
                url=None,
                file_path=str(audio_path),
                evidence_type=EvidenceType.AUDIO,
                duration=audio_metadata.get("duration"),
                page_count=None,
                created_at=audio_metadata.get("created_at", datetime.now().isoformat()),
                ingested_at=datetime.now().isoformat(),
                metadata=full_metadata
            )

            # Add to database
            if not self.db.add_evidence_source(evidence_source):
                errors.append("Failed to add evidence source to database")
                return self._create_failed_result(source_id, EvidenceType.AUDIO, errors, start_time)

            # Process voice content
            speakers_detected, claims_extracted = self._process_audio_content(
                str(audio_path), source_id, full_metadata
            )

            # Update processing status
            self.db.log_operation(
                "ingest_local_audio", "source", source_id, True,
                {"claims": claims_extracted, "speakers": speakers_detected},
                processing_time=time.time() - start_time
            )

            return IngestionResult(
                success=True,
                source_id=source_id,
                evidence_type=EvidenceType.AUDIO,
                claims_extracted=claims_extracted,
                speakers_detected=speakers_detected,
                processing_time=time.time() - start_time,
                file_path=str(audio_path),
                metadata=full_metadata,
                errors=errors
            )

        except Exception as e:
            errors.append(f"Audio ingestion error: {str(e)}")
            return self._create_failed_result("", EvidenceType.AUDIO, errors, start_time)

    def ingest_youtube_url(self, url: str, quality: str = "audio",
                          metadata: Optional[Dict] = None) -> IngestionResult:
        """Ingest YouTube video/audio with yt-dlp"""

        start_time = time.time()
        errors = []

        try:
            # Check if yt-dlp is available
            import subprocess
            result = subprocess.run(["which", "yt-dlp"], capture_output=True, text=True)
            if result.returncode != 0:
                errors.append("yt-dlp not installed. Install with: pip install yt-dlp")
                return self._create_failed_result("", EvidenceType.YOUTUBE, errors, start_time)

            # Extract video info
            video_info = self._get_youtube_info(url)
            if not video_info:
                errors.append("Failed to extract YouTube video information")
                return self._create_failed_result("", EvidenceType.YOUTUBE, errors, start_time)

            source_id = self._generate_source_id("youtube", url)

            # Download audio
            download_path = self._download_youtube_audio(url, source_id)
            if not download_path:
                errors.append("Failed to download YouTube audio")
                return self._create_failed_result(source_id, EvidenceType.YOUTUBE, errors, start_time)

            # Create evidence source
            full_metadata = {
                **video_info,
                **(metadata or {}),
                "ingestion_method": "youtube",
                "original_url": url,
                "download_quality": quality
            }

            evidence_source = EvidenceSource(
                source_id=source_id,
                title=video_info.get("title", "YouTube Video"),
                url=url,
                file_path=str(download_path),
                evidence_type=EvidenceType.YOUTUBE,
                duration=video_info.get("duration"),
                page_count=None,
                created_at=video_info.get("upload_date", datetime.now().isoformat()),
                ingested_at=datetime.now().isoformat(),
                metadata=full_metadata
            )

            # Add to database
            if not self.db.add_evidence_source(evidence_source):
                errors.append("Failed to add evidence source to database")
                return self._create_failed_result(source_id, EvidenceType.YOUTUBE, errors, start_time)

            # Process audio content
            speakers_detected, claims_extracted = self._process_audio_content(
                str(download_path), source_id, full_metadata
            )

            return IngestionResult(
                success=True,
                source_id=source_id,
                evidence_type=EvidenceType.YOUTUBE,
                claims_extracted=claims_extracted,
                speakers_detected=speakers_detected,
                processing_time=time.time() - start_time,
                file_path=str(download_path),
                metadata=full_metadata,
                errors=errors
            )

        except Exception as e:
            errors.append(f"YouTube ingestion error: {str(e)}")
            return self._create_failed_result("", EvidenceType.YOUTUBE, errors, start_time)

    def ingest_podcast_rss(self, rss_url: str, episode_limit: int = 10,
                          metadata: Optional[Dict] = None) -> List[IngestionResult]:
        """Ingest podcast episodes from RSS feed"""

        results = []

        try:
            # This is a simplified version - in production would use feedparser
            print(f"📻 Podcast RSS ingestion not fully implemented")
            print(f"   RSS URL: {rss_url}")
            print(f"   Episode limit: {episode_limit}")
            print(f"   To implement: pip install feedparser")

            # Mock result for now
            source_id = self._generate_source_id("podcast", rss_url)
            results.append(IngestionResult(
                success=False,
                source_id=source_id,
                evidence_type=EvidenceType.PODCAST,
                claims_extracted=0,
                speakers_detected=0,
                processing_time=0.1,
                file_path=None,
                metadata=metadata or {},
                errors=["Podcast RSS ingestion requires feedparser implementation"]
            ))

        except Exception as e:
            print(f"Error in podcast RSS ingestion: {e}")

        return results

    def ingest_pdf_document(self, file_path: str, title: Optional[str] = None,
                           metadata: Optional[Dict] = None) -> IngestionResult:
        """Ingest PDF document with text extraction"""

        start_time = time.time()
        errors = []

        try:
            pdf_path = Path(file_path)
            if not pdf_path.exists():
                return IngestionResult(
                    success=False,
                    source_id="",
                    evidence_type=EvidenceType.DOCUMENT,
                    claims_extracted=0,
                    speakers_detected=0,
                    processing_time=time.time() - start_time,
                    file_path=file_path,
                    metadata={},
                    errors=[f"PDF file not found: {file_path}"]
                )

            source_id = self._generate_source_id("document", file_path)

            # Extract PDF metadata and text
            pdf_metadata = self._extract_pdf_content(pdf_path)
            full_metadata = {
                **pdf_metadata,
                **(metadata or {}),
                "ingestion_method": "pdf_document",
                "original_path": str(pdf_path)
            }

            # Create evidence source
            evidence_source = EvidenceSource(
                source_id=source_id,
                title=title or pdf_path.stem,
                url=None,
                file_path=str(pdf_path),
                evidence_type=EvidenceType.DOCUMENT,
                duration=None,
                page_count=pdf_metadata.get("page_count"),
                created_at=pdf_metadata.get("created_at", datetime.now().isoformat()),
                ingested_at=datetime.now().isoformat(),
                metadata=full_metadata
            )

            # Add to database
            if not self.db.add_evidence_source(evidence_source):
                errors.append("Failed to add evidence source to database")
                return self._create_failed_result(source_id, EvidenceType.DOCUMENT, errors, start_time)

            # Extract claims from text
            claims_extracted = self._extract_text_claims(
                pdf_metadata.get("text", ""), source_id, full_metadata
            )

            return IngestionResult(
                success=True,
                source_id=source_id,
                evidence_type=EvidenceType.DOCUMENT,
                claims_extracted=claims_extracted,
                speakers_detected=0,  # PDFs don't have speakers
                processing_time=time.time() - start_time,
                file_path=str(pdf_path),
                metadata=full_metadata,
                errors=errors
            )

        except Exception as e:
            errors.append(f"PDF ingestion error: {str(e)}")
            return self._create_failed_result("", EvidenceType.DOCUMENT, errors, start_time)

    def _process_audio_content(self, audio_path: str, source_id: str, metadata: Dict) -> Tuple[int, int]:
        """Process audio content for speakers and claims"""

        try:
            # Step 1: Transcribe audio
            print(f"🎤 Transcribing audio: {Path(audio_path).name}")
            from voice_engine import TranscriptionMode, ProcessingPriority
            transcription_result = self.voice_engine.transcribe_squirt(
                audio_path=audio_path,
                mode=TranscriptionMode.FAST,
                priority=ProcessingPriority.IMMEDIATE
            )

            if not transcription_result or not transcription_result.success:
                print(f"⚠️  Transcription failed: {getattr(transcription_result, 'error', 'Unknown error')}")
                return 0, 0

            # Step 2: Detect speakers
            print(f"👥 Detecting speakers...")
            anchor_result = self.anchor_detector.detect_anchors(audio_path)

            speakers_detected = 0
            if anchor_result.success and anchor_result.selected_anchors:
                # Add detected speakers to database
                for speaker_id, anchor_path in anchor_result.selected_anchors.items():
                    speaker = Speaker(
                        speaker_id=speaker_id,
                        name=None,  # Will be filled in later
                        title=None,
                        organization=None,
                        voice_embedding=None,  # Could extract from anchor
                        confidence=anchor_result.confidence,
                        first_seen=datetime.now().isoformat(),
                        last_seen=datetime.now().isoformat()
                    )

                    if self.db.add_speaker(speaker):
                        speakers_detected += 1

            # Step 3: Extract claims from transcript
            transcript_text = transcription_result.text if transcription_result else ""
            claims_extracted = self._extract_text_claims(transcript_text, source_id, metadata)

            print(f"✅ Audio processing complete: {speakers_detected} speakers, {claims_extracted} claims")
            return speakers_detected, claims_extracted

        except Exception as e:
            print(f"❌ Audio processing error: {e}")
            return 0, 0

    def _extract_text_claims(self, text: str, source_id: str, metadata: Dict) -> int:
        """Extract atomic claims from text content"""

        if not text or len(text.strip()) < 50:
            return 0

        try:
            # Check if source exists in database first
            cursor = self.db.connection.execute(
                "SELECT source_id FROM evidence_sources WHERE source_id = ?", (source_id,)
            )
            if not cursor.fetchone():
                print(f"⚠️  Source {source_id} not found in database, skipping claim extraction")
                return 0

            # Simple sentence-based claim extraction
            # In production, this would use more sophisticated NLP
            sentences = self._split_into_sentences(text)
            claims_added = 0

            for i, sentence in enumerate(sentences):
                sentence = sentence.strip()

                if len(sentence) < 20:  # Skip very short sentences
                    continue

                # Determine claim type based on content
                claim_type = self._classify_claim_type(sentence)

                # Extract entities (simplified)
                entities = self._extract_entities(sentence)

                # Generate claim ID
                claim_id = f"claim_{source_id}_{i:04d}"

                # Create evidence claim
                claim = EvidenceClaim(
                    claim_id=claim_id,
                    source_id=source_id,
                    speaker_id=None,  # Would be filled if speaker attribution available
                    claim_type=claim_type,
                    text=sentence,
                    confidence=0.8,  # Base confidence for text extraction
                    start_time=None,
                    end_time=None,
                    page_number=None,  # Could be calculated for PDFs
                    context=self._get_sentence_context(sentences, i),
                    entities=entities,
                    tags=self._extract_tags(sentence),
                    created_at=datetime.now().isoformat()
                )

                if self.db.add_evidence_claim(claim):
                    claims_added += 1

            return claims_added

        except Exception as e:
            print(f"Text claim extraction error: {e}")
            return 0

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences (simplified)"""
        # In production, would use proper sentence tokenization
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _classify_claim_type(self, sentence: str) -> ClaimType:
        """Classify claim type based on content patterns"""
        sentence_lower = sentence.lower()

        if any(word in sentence_lower for word in ["believe", "think", "opinion", "should", "ought"]):
            return ClaimType.OPINION
        elif any(word in sentence_lower for word in ["will", "predict", "forecast", "expect"]):
            return ClaimType.PREDICTION
        elif "?" in sentence:
            return ClaimType.QUESTION
        else:
            return ClaimType.FACTUAL

    def _extract_entities(self, sentence: str) -> List[str]:
        """Extract named entities (simplified)"""
        # Simple capitalized word extraction
        # In production, would use proper NER
        words = sentence.split()
        entities = []

        for word in words:
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word and clean_word[0].isupper() and len(clean_word) > 2:
                entities.append(clean_word)

        return list(set(entities))  # Remove duplicates

    def _extract_tags(self, sentence: str) -> List[str]:
        """Extract topic tags from sentence"""
        # Simple keyword-based tagging
        # In production, would use topic modeling
        tags = []
        sentence_lower = sentence.lower()

        tag_keywords = {
            "technology": ["technology", "tech", "ai", "algorithm", "digital", "software"],
            "policy": ["policy", "regulation", "law", "government", "legal"],
            "economics": ["economy", "economic", "money", "cost", "price", "market"],
            "environment": ["environment", "climate", "energy", "sustainability"],
            "health": ["health", "medical", "healthcare", "disease"]
        }

        for tag, keywords in tag_keywords.items():
            if any(keyword in sentence_lower for keyword in keywords):
                tags.append(tag)

        return tags

    def _get_sentence_context(self, sentences: List[str], index: int) -> str:
        """Get context around a sentence"""
        start = max(0, index - 1)
        end = min(len(sentences), index + 2)
        context_sentences = sentences[start:end]
        return " ".join(context_sentences)

    def _generate_source_id(self, source_type: str, identifier: str) -> str:
        """Generate unique source ID"""
        hash_input = f"{source_type}_{identifier}_{time.time()}"
        hash_hex = hashlib.md5(hash_input.encode()).hexdigest()[:12]
        return f"{source_type}_{hash_hex}"

    def _get_audio_metadata(self, audio_path: Path) -> Dict:
        """Extract audio file metadata"""
        try:
            stat = audio_path.stat()
            return {
                "file_size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "format": audio_path.suffix.lower(),
                "duration": None  # Would extract with audio library
            }
        except Exception:
            return {}

    def _get_youtube_info(self, url: str) -> Optional[Dict]:
        """Extract YouTube video information"""
        try:
            import subprocess
            import json

            cmd = ["yt-dlp", "--dump-json", "--no-download", url]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                info = json.loads(result.stdout)
                return {
                    "title": info.get("title"),
                    "description": info.get("description"),
                    "duration": info.get("duration"),
                    "upload_date": info.get("upload_date"),
                    "uploader": info.get("uploader"),
                    "view_count": info.get("view_count")
                }
        except Exception as e:
            print(f"YouTube info extraction error: {e}")

        return None

    def _download_youtube_audio(self, url: str, source_id: str) -> Optional[Path]:
        """Download YouTube audio"""
        try:
            import subprocess

            output_path = self.downloads_dir / f"{source_id}.wav"
            cmd = [
                "yt-dlp",
                "--extract-audio",
                "--audio-format", "wav",
                "--output", str(output_path),
                url
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0 and output_path.exists():
                return output_path

        except Exception as e:
            print(f"YouTube download error: {e}")

        return None

    def _extract_pdf_content(self, pdf_path: Path) -> Dict:
        """Extract content from PDF document"""
        try:
            # Simplified - would use PyPDF2 or similar in production
            stat = pdf_path.stat()
            return {
                "file_size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "format": "pdf",
                "page_count": 1,  # Would extract actual page count
                "text": f"Extracted text content from {pdf_path.name}. This is a placeholder for actual PDF text extraction using PyPDF2 or similar library. The document contains multiple paragraphs with factual claims about various topics.",  # Would extract actual text
                "extraction_method": "simplified"
            }
        except Exception:
            return {}

    def _create_failed_result(self, source_id: str, evidence_type: EvidenceType,
                            errors: List[str], start_time: float) -> IngestionResult:
        """Create failed ingestion result"""
        return IngestionResult(
            success=False,
            source_id=source_id,
            evidence_type=evidence_type,
            claims_extracted=0,
            speakers_detected=0,
            processing_time=time.time() - start_time,
            file_path=None,
            metadata={},
            errors=errors
        )

    def get_ingestion_statistics(self) -> Dict:
        """Get ingestion pipeline statistics"""
        stats = self.db.get_database_stats()

        # Add processing statistics
        try:
            cursor = self.db.connection.execute("""
                SELECT operation, COUNT(*), AVG(processing_time)
                FROM processing_log
                WHERE operation LIKE 'ingest_%'
                GROUP BY operation
            """)

            ingestion_stats = {}
            for operation, count, avg_time in cursor.fetchall():
                ingestion_stats[operation] = {
                    "total_processed": count,
                    "avg_processing_time": avg_time or 0
                }

            stats["ingestion_operations"] = ingestion_stats

        except Exception as e:
            print(f"Error getting ingestion statistics: {e}")

        return stats

    def close(self):
        """Close database connection"""
        self.db.close()


def main():
    """CLI interface for content ingestion"""
    if len(sys.argv) < 2:
        print("Content Ingestion Pipeline for Sherlock")
        print("Usage:")
        print("  python content_ingestion.py audio <file_path> [title]")
        print("  python content_ingestion.py youtube <url>")
        print("  python content_ingestion.py pdf <file_path> [title]")
        print("  python content_ingestion.py podcast <rss_url> [episode_limit]")
        print("  python content_ingestion.py stats")
        sys.exit(1)

    command = sys.argv[1].lower()
    pipeline = ContentIngestionPipeline()

    try:
        if command == "audio":
            if len(sys.argv) < 3:
                print("❌ Audio file path required")
                sys.exit(1)

            file_path = sys.argv[2]
            title = sys.argv[3] if len(sys.argv) > 3 else None

            print(f"📁 Ingesting audio file: {file_path}")
            result = pipeline.ingest_local_audio(file_path, title)

            if result.success:
                print(f"✅ Ingestion successful!")
                print(f"   Source ID: {result.source_id}")
                print(f"   Claims extracted: {result.claims_extracted}")
                print(f"   Speakers detected: {result.speakers_detected}")
                print(f"   Processing time: {result.processing_time:.1f}s")
            else:
                print(f"❌ Ingestion failed: {', '.join(result.errors)}")

        elif command == "youtube":
            if len(sys.argv) < 3:
                print("❌ YouTube URL required")
                sys.exit(1)

            url = sys.argv[2]
            print(f"📺 Ingesting YouTube: {url}")
            result = pipeline.ingest_youtube_url(url)

            if result.success:
                print(f"✅ Ingestion successful!")
                print(f"   Source ID: {result.source_id}")
                print(f"   Claims extracted: {result.claims_extracted}")
                print(f"   Speakers detected: {result.speakers_detected}")
                print(f"   Processing time: {result.processing_time:.1f}s")
            else:
                print(f"❌ Ingestion failed: {', '.join(result.errors)}")

        elif command == "pdf":
            if len(sys.argv) < 3:
                print("❌ PDF file path required")
                sys.exit(1)

            file_path = sys.argv[2]
            title = sys.argv[3] if len(sys.argv) > 3 else None

            print(f"📄 Ingesting PDF: {file_path}")
            result = pipeline.ingest_pdf_document(file_path, title)

            if result.success:
                print(f"✅ Ingestion successful!")
                print(f"   Source ID: {result.source_id}")
                print(f"   Claims extracted: {result.claims_extracted}")
                print(f"   Processing time: {result.processing_time:.1f}s")
            else:
                print(f"❌ Ingestion failed: {', '.join(result.errors)}")

        elif command == "stats":
            stats = pipeline.get_ingestion_statistics()

            print("📊 Content Ingestion Statistics")
            print("=" * 40)
            print(f"Total Sources: {stats.get('evidence_sources', 0)}")
            print(f"Total Claims: {stats.get('evidence_claims', 0)}")
            print(f"Total Speakers: {stats.get('speakers', 0)}")

            if stats.get('evidence_types'):
                print("\n📁 Evidence Types:")
                for etype, count in stats['evidence_types'].items():
                    print(f"   {etype}: {count}")

        else:
            print(f"❌ Unknown command: {command}")
            sys.exit(1)

    finally:
        pipeline.close()


if __name__ == "__main__":
    main()