#!/usr/bin/env python3
"""Process Shared Context podcast episode with priority AI training focus"""
import sys
import logging
from pathlib import Path

sys.path.append("/home/johnny5/Sherlock")

from content_ingestion import ContentIngestionPipeline
from evidence_database import EvidenceDatabase

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

def process_shared_context_episode():
    """Process priority Shared Context episode about AI training"""

    youtube_url = "https://youtu.be/oW4lBSmLc5k?si=CEpFxq2X-SNnNaIL"

    logger.info("="*70)
    logger.info("SHARED CONTEXT EPISODE PROCESSING - AI TRAINING INTELLIGENCE")
    logger.info("="*70)

    # Phase 1: YouTube Download & Audio Extraction
    logger.info("Phase 1: Downloading YouTube episode...")
    ingestion = ContentIngestionPipeline(db_path="/home/johnny5/Sherlock/sherlock.db")

    try:
        result = ingestion.ingest_youtube_url(
            url=youtube_url,
            quality="audio",
            metadata={
                "target": "Shared Context Podcast",
                "source_type": "podcast_episode",
                "intelligence_focus": "AI_TRAINING"
            }
        )

        audio_file = result.file_path
        metadata = result.metadata

        logger.info(f"✅ Downloaded: {metadata.get('title', 'Unknown')}")
        logger.info(f"✅ Duration: {metadata.get('duration', 'Unknown')} seconds")
        logger.info(f"✅ Audio file: {audio_file}")

    except Exception as e:
        logger.error(f"❌ YouTube download failed: {e}")
        return None

    # Phase 2: Whisper Transcription (Direct faster-whisper)
    logger.info("\nPhase 2: Whisper transcription (faster-whisper medium)...")

    try:
        from faster_whisper import WhisperModel

        # Use medium model as selected by intelligent selector
        logger.info("Loading faster-whisper medium model...")
        model = WhisperModel("medium", device="cpu", compute_type="int8")

        logger.info(f"Transcribing {audio_file}...")
        segments, info = model.transcribe(audio_file, beam_size=5)

        # Collect all segments
        transcript_text = " ".join([segment.text for segment in segments])

        logger.info(f"✅ Transcription complete: {len(transcript_text)} characters")
        logger.info(f"   Language: {info.language} (probability: {info.language_probability:.2f})")
        logger.info(f"   Duration: {info.duration:.1f} seconds")

        # Save transcript
        transcript_path = Path(audio_file).parent / f"{Path(audio_file).stem}_transcript.txt"
        with open(transcript_path, 'w') as f:
            f.write(transcript_text)

        logger.info(f"✅ Transcript saved: {transcript_path}")

        return {
            'audio_file': audio_file,
            'transcript_file': str(transcript_path),
            'transcript_text': transcript_text,
            'metadata': metadata
        }

    except Exception as e:
        logger.error(f"❌ Transcription failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = process_shared_context_episode()

    if result:
        logger.info("\n" + "="*70)
        logger.info("✅ PROCESSING COMPLETE")
        logger.info("="*70)
        logger.info(f"Transcript: {result['transcript_file']}")
        logger.info(f"Characters: {len(result['transcript_text'])}")
