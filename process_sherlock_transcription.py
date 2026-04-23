#!/usr/bin/env python3
"""
Sherlock Transcription Pipeline Processor
Processes YouTube podcast episodes for intelligence analysis

Constitutional Basis: Principle 3 (System Viability) - Graceful degradation via GPU-aware processing
Integration: Uses Freelance Transcription infrastructure for Sherlock intelligence work
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import time

# Add parent directory to path for imports
sys.path.insert(0, '/home/johnny5/Johny5Alive')
sys.path.insert(0, '/home/johnny5/Johny5Alive/j5a-nightshift')

from intelligent_model_selector import IntelligentModelSelector

class SherlockTranscriptionProcessor:
    """Process YouTube podcasts for Sherlock intelligence analysis"""

    def __init__(self):
        self.output_base = Path("/home/johnny5/Sherlock/freelance_transcripts")
        self.model_selector = IntelligentModelSelector()
        self.results = []

    def download_audio(self, url: str, output_dir: Path) -> dict:
        """Download audio from YouTube URL using yt-dlp"""
        output_dir.mkdir(parents=True, exist_ok=True)
        audio_file = output_dir / "audio.mp3"
        metadata_file = output_dir / "metadata.json"

        print(f"  📥 Downloading from YouTube...")

        # Download with yt-dlp
        cmd = [
            "yt-dlp",
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "0",  # Best quality
            "--write-info-json",
            "--output", str(output_dir / "audio.%(ext)s"),
            url
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"yt-dlp failed: {result.stderr}",
                    "audio_file": None,
                    "metadata": None
                }

            # Check if files exist
            if not audio_file.exists():
                return {
                    "success": False,
                    "error": "Audio file not created",
                    "audio_file": None,
                    "metadata": None
                }

            # Load metadata if available
            info_json = output_dir / "audio.info.json"
            metadata = None
            if info_json.exists():
                with open(info_json, 'r') as f:
                    info = json.load(f)
                    metadata = {
                        "title": info.get("title"),
                        "duration": info.get("duration"),
                        "upload_date": info.get("upload_date"),
                        "channel": info.get("channel"),
                        "description": info.get("description", "")[:500]  # First 500 chars
                    }

                    # Save cleaner metadata
                    with open(metadata_file, 'w') as mf:
                        json.dump(metadata, mf, indent=2)

            # Get actual file size and duration
            file_size_mb = audio_file.stat().st_size / (1024 * 1024)

            return {
                "success": True,
                "audio_file": str(audio_file),
                "metadata": metadata,
                "file_size_mb": round(file_size_mb, 2)
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Download timeout (>10 minutes)",
                "audio_file": None,
                "metadata": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Download exception: {str(e)}",
                "audio_file": None,
                "metadata": None
            }

    def transcribe_audio(self, audio_file: str, output_dir: Path) -> dict:
        """Transcribe audio using GPU-accelerated Whisper"""
        # faster_whisper_cli.py outputs as audio.txt and audio.json
        transcript_txt = output_dir / "audio.txt"
        transcript_json = output_dir / "audio.json"

        print(f"  🎙️  Transcribing with GPU (large-v3 model)...")

        # Use faster_whisper_cli.py directly
        cmd = [
            "python3",
            "/home/johnny5/Johny5Alive/j5a-nightshift/faster_whisper_cli.py",
            audio_file,
            "--model", "large-v3",
            "--output_dir", str(output_dir),
            "--output_format", "txt,json",
            "--prefer_gpu", "true",
            "--word_timestamps"
        ]

        start_time = time.time()

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)

            duration = time.time() - start_time

            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Transcription failed: {result.stderr}",
                    "transcript_txt": None,
                    "transcript_json": None,
                    "duration": duration
                }

            # Verify outputs exist
            if not transcript_txt.exists() or not transcript_json.exists():
                return {
                    "success": False,
                    "error": "Transcript files not created",
                    "transcript_txt": None,
                    "transcript_json": None,
                    "duration": duration
                }

            # Calculate quality metrics from JSON
            with open(transcript_json, 'r') as f:
                transcript_data = json.load(f)

            # Extract segments for quality assessment
            segments = transcript_data.get("segments", [])
            if segments:
                avg_confidence = sum(seg.get("avg_logprob", 0) for seg in segments) / len(segments)
                word_count = sum(len(seg.get("text", "").split()) for seg in segments)
            else:
                avg_confidence = 0
                word_count = 0

            return {
                "success": True,
                "transcript_txt": str(transcript_txt),
                "transcript_json": str(transcript_json),
                "duration": round(duration, 1),
                "segment_count": len(segments),
                "word_count": word_count,
                "avg_confidence": round(avg_confidence, 3)
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Transcription timeout (>1 hour)",
                "transcript_txt": None,
                "transcript_json": None,
                "duration": time.time() - start_time
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Transcription exception: {str(e)}",
                "transcript_txt": None,
                "transcript_json": None,
                "duration": time.time() - start_time
            }

    def process_episode(self, episode_data: dict) -> dict:
        """Process a single episode: download + transcribe"""
        print(f"\n{'='*80}")
        print(f"🎯 {episode_data['id']}: {episode_data['title']}")
        print(f"   Priority: {episode_data['priority']} | Podcast: {episode_data['podcast']}")
        print(f"{'='*80}")

        # Determine output directory
        podcast_slug = episode_data['podcast'].lower().replace(' ', '_')
        episode_slug = episode_data['output_dir']
        output_dir = self.output_base / podcast_slug / episode_slug

        result = {
            "episode_id": episode_data['id'],
            "title": episode_data['title'],
            "url": episode_data['url'],
            "priority": episode_data['priority'],
            "podcast": episode_data['podcast'],
            "output_dir": str(output_dir),
            "timestamp": datetime.now().isoformat(),
            "success": False
        }

        # Step 1: Download
        download_result = self.download_audio(episode_data['url'], output_dir)
        result['download'] = download_result

        if not download_result['success']:
            print(f"  ❌ Download failed: {download_result['error']}")
            self.results.append(result)
            return result

        print(f"  ✅ Downloaded: {download_result['file_size_mb']} MB")

        # Step 2: Transcribe
        transcribe_result = self.transcribe_audio(download_result['audio_file'], output_dir)
        result['transcription'] = transcribe_result

        if not transcribe_result['success']:
            print(f"  ❌ Transcription failed: {transcribe_result['error']}")
            self.results.append(result)
            return result

        print(f"  ✅ Transcribed: {transcribe_result['word_count']} words in {transcribe_result['duration']}s")
        print(f"     Quality: {transcribe_result['segment_count']} segments, avg confidence {transcribe_result['avg_confidence']}")

        result['success'] = True
        self.results.append(result)
        return result

    def save_results(self, output_file: str):
        """Save processing results to JSON"""
        with open(output_file, 'w') as f:
            json.dump({
                "processing_timestamp": datetime.now().isoformat(),
                "total_episodes": len(self.results),
                "successful": sum(1 for r in self.results if r['success']),
                "failed": sum(1 for r in self.results if not r['success']),
                "episodes": self.results
            }, f, indent=2)

        print(f"\n📊 Results saved to: {output_file}")


def main():
    """Main execution"""
    processor = SherlockTranscriptionProcessor()

    # Episode definitions (from test plan)
    episodes = []

    # Read episode list from stdin or file
    import sys
    if len(sys.argv) > 1:
        # Load from JSON file
        with open(sys.argv[1], 'r') as f:
            episodes = json.load(f)
    else:
        print("Usage: python3 process_sherlock_transcription.py <episodes.json>")
        print("Or provide episodes via stdin")
        sys.exit(1)

    # Process all episodes
    print(f"\n🚀 Starting processing of {len(episodes)} episodes...")

    for episode in episodes:
        try:
            processor.process_episode(episode)
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR processing {episode.get('id', 'UNKNOWN')}: {str(e)}")
            processor.results.append({
                "episode_id": episode.get('id'),
                "success": False,
                "error": f"Critical exception: {str(e)}"
            })

    # Save results
    results_file = f"/home/johnny5/Sherlock/transcription_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    processor.save_results(results_file)

    # Print summary
    print(f"\n{'='*80}")
    print(f"✅ PROCESSING COMPLETE")
    print(f"{'='*80}")
    print(f"Total Episodes: {len(processor.results)}")
    print(f"Successful: {sum(1 for r in processor.results if r['success'])}")
    print(f"Failed: {sum(1 for r in processor.results if not r['success'])}")
    print(f"Results: {results_file}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
