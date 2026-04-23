#!/usr/bin/env python3
"""
Sherlock Transcription Pipeline - OpenAI Whisper Implementation
Processes YouTube podcast episodes using OpenAI Whisper large-v3 GPU acceleration

Model: OpenAI Whisper large-v3 (superior quality baseline)
Performance: ~10x real-time on RTX 4060
Constitutional Basis: Principle 3 (System Viability) + Efficiency-Quality Pairing
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import time
import whisper
import torch

class SherlockOpenAIWhisperProcessor:
    """Process YouTube podcasts using OpenAI Whisper for Sherlock intelligence analysis"""

    def __init__(self, model_size="large-v3"):
        self.output_base = Path("/home/johnny5/Sherlock/freelance_transcripts")
        self.model_size = model_size
        self.results = []

        # Load Whisper model on GPU
        print(f"🔧 Loading OpenAI Whisper model '{model_size}' on GPU...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model(model_size, device=device)
        print(f"✅ Model loaded on {device}")

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

            # Get actual file size
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
        """Transcribe audio using OpenAI Whisper GPU acceleration"""
        transcript_txt = output_dir / "audio.txt"
        transcript_json = output_dir / "audio.json"
        transcript_srt = output_dir / "audio.srt"
        transcript_vtt = output_dir / "audio.vtt"

        print(f"  🎙️  Transcribing with OpenAI Whisper {self.model_size} on GPU...")

        start_time = time.time()

        try:
            # Transcribe with word-level timestamps
            result = self.model.transcribe(
                audio_file,
                language="en",
                task="transcribe",
                word_timestamps=True,
                verbose=False
            )

            duration = time.time() - start_time

            # Extract text
            transcript_text = result["text"]

            # Save text output
            with open(transcript_txt, 'w', encoding='utf-8') as f:
                f.write(transcript_text)

            # Save JSON output (segments with timestamps)
            json_output = {
                "text": transcript_text,
                "segments": result["segments"],
                "language": result["language"]
            }
            with open(transcript_json, 'w', encoding='utf-8') as f:
                json.dump(json_output, f, indent=2, ensure_ascii=False)

            # Save SRT subtitles
            self.write_srt(result["segments"], transcript_srt)

            # Save VTT subtitles
            self.write_vtt(result["segments"], transcript_vtt)

            # Calculate quality metrics
            segments = result["segments"]
            if segments:
                # Average confidence from avg_logprob
                avg_confidence = sum(seg.get("avg_logprob", 0) for seg in segments) / len(segments)
                # Convert log prob to confidence (approximate)
                avg_confidence = min(1.0, max(0.0, avg_confidence + 1.0))  # Normalize

                word_count = len(transcript_text.split())
            else:
                avg_confidence = 0
                word_count = 0

            return {
                "success": True,
                "transcript_txt": str(transcript_txt),
                "transcript_json": str(transcript_json),
                "transcript_srt": str(transcript_srt),
                "transcript_vtt": str(transcript_vtt),
                "duration": round(duration, 1),
                "segment_count": len(segments),
                "word_count": word_count,
                "avg_confidence": round(avg_confidence, 3),
                "model": self.model_size,
                "device": str(self.model.device)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Transcription exception: {str(e)}",
                "transcript_txt": None,
                "transcript_json": None,
                "duration": time.time() - start_time
            }

    def write_srt(self, segments, output_path):
        """Write SRT subtitle file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, start=1):
                f.write(f"{i}\n")
                f.write(f"{self.format_timestamp(segment['start'], srt=True)} --> ")
                f.write(f"{self.format_timestamp(segment['end'], srt=True)}\n")
                f.write(f"{segment['text'].strip()}\n\n")

    def write_vtt(self, segments, output_path):
        """Write VTT subtitle file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            for segment in segments:
                f.write(f"{self.format_timestamp(segment['start'])} --> ")
                f.write(f"{self.format_timestamp(segment['end'])}\n")
                f.write(f"{segment['text'].strip()}\n\n")

    def format_timestamp(self, seconds, srt=False):
        """Format timestamp for SRT/VTT"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        if srt:
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        else:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

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
        print(f"     Quality: {transcribe_result['segment_count']} segments, confidence {transcribe_result['avg_confidence']}")
        print(f"     Model: {transcribe_result['model']} on {transcribe_result['device']}")

        result['success'] = True
        self.results.append(result)
        return result

    def save_results(self, output_file: str):
        """Save processing results to JSON"""
        with open(output_file, 'w') as f:
            json.dump({
                "processing_timestamp": datetime.now().isoformat(),
                "model": self.model_size,
                "device": str(self.model.device),
                "total_episodes": len(self.results),
                "successful": sum(1 for r in self.results if r['success']),
                "failed": sum(1 for r in self.results if not r['success']),
                "episodes": self.results
            }, f, indent=2)

        print(f"\n📊 Results saved to: {output_file}")


def main():
    """Main execution"""
    import sys

    if len(sys.argv) > 1:
        # Load from JSON file
        episode_file = sys.argv[1]
        with open(episode_file, 'r') as f:
            episodes = json.load(f)
    else:
        print("Usage: python3 process_sherlock_openai_whisper.py <episodes.json>")
        sys.exit(1)

    # Create processor with large-v3 model
    processor = SherlockOpenAIWhisperProcessor(model_size="large-v3")

    # Process all episodes
    print(f"\n🚀 Starting OpenAI Whisper processing of {len(episodes)} episodes...")
    print(f"   Model: {processor.model_size}")
    print(f"   Device: {processor.model.device}")

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
    results_file = f"/home/johnny5/Sherlock/transcription_results_openai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    processor.save_results(results_file)

    # Print summary
    print(f"\n{'='*80}")
    print(f"✅ PROCESSING COMPLETE")
    print(f"{'='*80}")
    print(f"Model: OpenAI Whisper {processor.model_size}")
    print(f"Device: {processor.model.device}")
    print(f"Total Episodes: {len(processor.results)}")
    print(f"Successful: {sum(1 for r in processor.results if r['success'])}")
    print(f"Failed: {sum(1 for r in processor.results if not r['success'])}")
    print(f"Results: {results_file}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
