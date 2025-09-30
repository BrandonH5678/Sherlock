#!/usr/bin/env python3
"""
Operation Gladio Processor - FAST Mode with faster-whisper small
Memory-optimized for 2.5GB available RAM
Processes 12-hour audiobook with chunking strategy
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

# Sherlock components
from evidence_schema_gladio import GladioEvidenceDatabase


class GladioFastProcessor:
    """Process Operation Gladio with faster-whisper small in chunks"""

    def __init__(self, db_path: str = "gladio_intelligence.db"):
        self.db = GladioEvidenceDatabase(db_path)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('gladio_fast_processing.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Load faster-whisper small model
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load faster-whisper small model (244MB)"""
        try:
            from faster_whisper import WhisperModel

            self.logger.info("🔄 Loading faster-whisper small model...")
            self.model = WhisperModel(
                "small",
                device="cpu",
                compute_type="int8"
            )
            self.logger.info("✅ faster-whisper small model loaded (244MB + ~300MB overhead)")

        except Exception as e:
            self.logger.error(f"❌ Failed to load model: {e}")
            raise

    def chunk_audio_file(self, m4a_file: str, chunk_duration: int = 600) -> list:
        """
        Split M4A file into manageable chunks (10 minutes each by default)

        Args:
            m4a_file: Path to decrypted M4A file
            chunk_duration: Duration of each chunk in seconds (default 600 = 10 minutes)

        Returns:
            List of chunk file paths
        """
        import subprocess

        chunks = []
        output_dir = Path(m4a_file).parent / "processing_chunks"
        output_dir.mkdir(exist_ok=True)

        try:
            # Get total duration
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', m4a_file
            ], capture_output=True, text=True)

            total_duration = float(result.stdout.strip())
            num_chunks = int(total_duration / chunk_duration) + 1

            self.logger.info(f"📏 Total duration: {total_duration/3600:.2f} hours")
            self.logger.info(f"📦 Creating {num_chunks} chunks of {chunk_duration/60:.0f} minutes each")

            # Create chunks
            for i in range(num_chunks):
                start_time = i * chunk_duration
                chunk_file = output_dir / f"chunk_{i+1:03d}.wav"

                # Convert to WAV for faster-whisper
                cmd = [
                    'ffmpeg', '-y', '-i', m4a_file,
                    '-ss', str(start_time),
                    '-t', str(chunk_duration),
                    '-acodec', 'pcm_s16le',
                    '-ar', '16000',
                    '-ac', '1',  # Mono
                    str(chunk_file)
                ]

                result = subprocess.run(cmd, capture_output=True)

                if result.returncode == 0 and os.path.exists(chunk_file) and os.path.getsize(chunk_file) > 1000:
                    chunks.append(str(chunk_file))
                    self.logger.info(f"✅ Created chunk {i+1}/{num_chunks}: {chunk_file.name}")
                else:
                    self.logger.warning(f"⚠️ Failed to create chunk {i+1}")

        except Exception as e:
            self.logger.error(f"❌ Chunking failed: {e}")

        return chunks

    def transcribe_chunk(self, chunk_file: str, chunk_id: int) -> dict:
        """
        Transcribe a single audio chunk

        Args:
            chunk_file: Path to chunk WAV file
            chunk_id: Chunk number for tracking

        Returns:
            Dict with transcription results
        """
        try:
            self.logger.info(f"🎤 Processing chunk {chunk_id}: {Path(chunk_file).name}")
            start_time = time.time()

            # Transcribe with faster-whisper
            segments, info = self.model.transcribe(
                chunk_file,
                language="en",
                beam_size=5,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )

            # Collect segments
            text_segments = []
            full_text = []

            for segment in segments:
                text_segments.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip()
                })
                full_text.append(segment.text.strip())

            processing_time = time.time() - start_time

            result = {
                "chunk_id": chunk_id,
                "chunk_file": chunk_file,
                "text": " ".join(full_text),
                "segments": text_segments,
                "processing_time": processing_time,
                "language": info.language,
                "language_probability": info.language_probability
            }

            self.logger.info(f"✅ Chunk {chunk_id} completed: {len(full_text)} segments, {processing_time:.1f}s")

            return result

        except Exception as e:
            self.logger.error(f"❌ Chunk {chunk_id} failed: {e}")
            return {
                "chunk_id": chunk_id,
                "chunk_file": chunk_file,
                "error": str(e)
            }

    def process_operation_gladio(self) -> bool:
        """
        Complete processing pipeline for Operation Gladio

        Returns:
            bool: True if successful
        """
        # File paths
        decrypted_file = "audiobooks/operation_gladio/decrypted/Operation_Gladio_Decrypted.m4a"
        transcript_file = "audiobooks/operation_gladio/operation_gladio_transcript.txt"
        results_file = "audiobooks/operation_gladio/gladio_processing_results.json"

        try:
            self.logger.info("🚀 Starting Operation Gladio FAST processing (faster-whisper small)")
            self.logger.info(f"📁 Input: {decrypted_file}")
            self.logger.info(f"⚙️  Model: faster-whisper small (244MB + ~300MB overhead = ~500-600MB total)")
            self.logger.info(f"💾 Available RAM: 2.5GB")

            start_time = time.time()

            # Verify input file
            if not os.path.exists(decrypted_file):
                self.logger.error(f"❌ Decrypted file not found: {decrypted_file}")
                return False

            file_size = os.path.getsize(decrypted_file) / (1024*1024)
            self.logger.info(f"📏 File size: {file_size:.1f} MB")

            # Step 1: Chunk the audio file
            self.logger.info("\n📦 Step 1: Chunking audio file...")
            chunks = self.chunk_audio_file(decrypted_file, chunk_duration=600)  # 10-minute chunks

            if not chunks:
                self.logger.error("❌ No chunks created - aborting")
                return False

            self.logger.info(f"✅ Created {len(chunks)} chunks")

            # Step 2: Process each chunk
            self.logger.info("\n🎤 Step 2: Transcribing chunks...")
            all_results = []
            full_transcript = []

            for i, chunk in enumerate(chunks, 1):
                result = self.transcribe_chunk(chunk, i)
                all_results.append(result)

                if "text" in result:
                    full_transcript.append(result["text"])

                # Progress indicator
                progress = (i / len(chunks)) * 100
                self.logger.info(f"📊 Progress: {progress:.1f}% ({i}/{len(chunks)} chunks)")

            # Step 3: Save combined transcript
            self.logger.info("\n💾 Step 3: Saving transcript...")
            complete_transcript = "\n\n".join(full_transcript)

            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(complete_transcript)

            self.logger.info(f"✅ Transcript saved: {transcript_file}")
            self.logger.info(f"📊 Total characters: {len(complete_transcript):,}")
            self.logger.info(f"📊 Total words: {len(complete_transcript.split()):,}")

            # Step 4: Save detailed results
            total_time = time.time() - start_time

            results_data = {
                "processing_date": datetime.now().isoformat(),
                "source_file": decrypted_file,
                "model": "faster-whisper small",
                "total_chunks": len(chunks),
                "successful_chunks": len([r for r in all_results if "text" in r]),
                "failed_chunks": len([r for r in all_results if "error" in r]),
                "total_processing_time": total_time,
                "total_processing_hours": total_time / 3600,
                "transcript_length": len(complete_transcript),
                "transcript_words": len(complete_transcript.split()),
                "chunk_results": all_results
            }

            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2)

            self.logger.info(f"✅ Processing results saved: {results_file}")

            # Step 5: Generate summary
            self.logger.info("\n" + "="*60)
            self.logger.info("🎯 OPERATION GLADIO PROCESSING COMPLETE!")
            self.logger.info("="*60)
            self.logger.info(f"⏱️  Total processing time: {total_time/3600:.2f} hours")
            self.logger.info(f"📊 Chunks processed: {len(chunks)} ({results_data['successful_chunks']} successful)")
            self.logger.info(f"📝 Transcript: {len(complete_transcript):,} characters, {len(complete_transcript.split()):,} words")
            self.logger.info(f"📁 Output files:")
            self.logger.info(f"   - Transcript: {transcript_file}")
            self.logger.info(f"   - Results: {results_file}")
            self.logger.info(f"   - Database: {self.db.db_path}")
            self.logger.info("="*60)

            return True

        except Exception as e:
            self.logger.error(f"❌ Processing failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False


def main():
    """Main execution"""
    print("🎬 Operation Gladio - FAST Processing Pipeline")
    print("=" * 60)
    print("Model: faster-whisper small")
    print("Memory: ~500-600MB (safe for 2.5GB available)")
    print("Strategy: 10-minute chunks for memory efficiency")
    print("=" * 60)
    print()

    processor = GladioFastProcessor()
    success = processor.process_operation_gladio()

    if success:
        print("\n✅ SUCCESS! Operation Gladio processing completed.")
        print("📊 Check gladio_processing_results.json for detailed metrics")
        print("📜 Transcript: audiobooks/operation_gladio/operation_gladio_transcript.txt")
    else:
        print("\n❌ FAILED - check gladio_fast_processing.log for details")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())