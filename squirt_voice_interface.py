#!/usr/bin/env python3
"""
Squirt Voice Processing Interface
User-friendly interface for WaterWizard employees to process voice memos
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, Optional

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from voice_engine import VoiceEngineManager, TranscriptionMode, ProcessingPriority


class SquirtVoiceInterface:
    """User interface for Squirt voice processing"""

    def __init__(self):
        self.engine = VoiceEngineManager()
        self.results = []

    def process_voice_memo(self,
                          audio_file: str,
                          mode: str = "fast",
                          employee_name: Optional[str] = None,
                          project_context: Optional[str] = None) -> Dict:
        """
        Process a voice memo with user choice of speed vs accuracy

        Args:
            audio_file: Path to audio file
            mode: "fast" for speed (<3 min) or "accurate" for quality (<20 min)
            employee_name: Name of employee for tracking
            project_context: Context about the work (service call, estimate, etc.)

        Returns:
            Processing result with transcription and metadata
        """

        if not Path(audio_file).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        # Convert mode string to enum
        transcription_mode = TranscriptionMode.FAST if mode.lower() == "fast" else TranscriptionMode.ACCURATE

        print(f"🎤 Processing voice memo: {Path(audio_file).name}")
        print(f"📊 Mode: {mode.upper()} ({'~2-3 minutes' if mode == 'fast' else '~15-20 minutes'})")
        if employee_name:
            print(f"👤 Employee: {employee_name}")
        if project_context:
            print(f"📋 Context: {project_context}")
        print("⏳ Starting transcription...")

        # Setup callback to capture results
        def on_result(result):
            self.results.append(result)
            print(f"\n✅ Transcription completed!")
            print(f"   Model used: {result.model_used}")
            print(f"   Processing time: {result.processing_time:.1f} seconds")
            print(f"   Confidence: {result.confidence:.1%}")
            print(f"   Text length: {len(result.text)} characters")

        # Start engine and process
        self.engine.start()

        try:
            # Submit transcription request
            self.engine.transcribe_squirt(
                audio_path=audio_file,
                mode=transcription_mode,
                priority=ProcessingPriority.IMMEDIATE,
                callback=on_result
            )

            # Wait for completion with progress indication
            timeout = 300 if mode == "fast" else 1500  # 5 min fast, 25 min accurate
            start_time = time.time()

            while len(self.results) == 0 and (time.time() - start_time) < timeout:
                elapsed = time.time() - start_time
                if mode == "fast":
                    progress = min(elapsed / 180, 1.0)  # Expect ~3 minutes
                else:
                    progress = min(elapsed / 1200, 1.0)  # Expect ~20 minutes

                bars = int(progress * 20)
                print(f"\r[{'=' * bars}{' ' * (20 - bars)}] {progress:.1%} ({elapsed:.0f}s)", end="", flush=True)
                time.sleep(2)

            if len(self.results) == 0:
                raise TimeoutError(f"Transcription timed out after {timeout} seconds")

            result = self.results[-1]

            # Return structured result for Squirt integration
            return {
                "transcription": {
                    "text": result.text,
                    "segments": result.segments,
                    "confidence": result.confidence,
                    "model": result.model_used,
                    "processing_time": result.processing_time
                },
                "metadata": {
                    "audio_file": audio_file,
                    "mode": mode,
                    "employee_name": employee_name,
                    "project_context": project_context,
                    "timestamp": time.time(),
                    "success": True
                },
                "squirt_ready": True  # Flag for Squirt integration
            }

        finally:
            self.engine.stop()

    def interactive_mode(self):
        """Interactive CLI mode for employee use"""
        print("🌊 WaterWizard Voice Memo Processor")
        print("=" * 40)

        while True:
            try:
                # Get audio file
                audio_file = input("\n📁 Audio file path (or 'quit'): ").strip()
                if audio_file.lower() in ['quit', 'exit', 'q']:
                    break

                if not audio_file:
                    continue

                if not Path(audio_file).exists():
                    print(f"❌ File not found: {audio_file}")
                    continue

                # Get processing mode
                print("\n🔧 Choose processing mode:")
                print("   [1] Fast (2-3 minutes, good for service calls)")
                print("   [2] Accurate (15-20 minutes, best for estimates/contracts)")

                mode_choice = input("Choice [1/2]: ").strip()
                mode = "fast" if mode_choice == "1" else "accurate"

                # Get employee info
                employee_name = input("👤 Employee name (optional): ").strip() or None
                project_context = input("📋 Project type (service call/estimate/contract): ").strip() or None

                # Process the voice memo
                result = self.process_voice_memo(
                    audio_file=audio_file,
                    mode=mode,
                    employee_name=employee_name,
                    project_context=project_context
                )

                # Display results
                self.display_result(result)

                # Save for review
                self.save_result(result)

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

    def display_result(self, result: Dict):
        """Display transcription result in user-friendly format"""
        print("\n" + "=" * 50)
        print("📝 TRANSCRIPTION RESULT")
        print("=" * 50)

        metadata = result["metadata"]
        transcription = result["transcription"]

        print(f"🎤 Audio: {Path(metadata['audio_file']).name}")
        print(f"🔧 Mode: {metadata['mode'].upper()}")
        print(f"⏱️  Processing: {transcription['processing_time']:.1f} seconds")
        print(f"📊 Confidence: {transcription['confidence']:.1%}")

        if metadata.get("employee_name"):
            print(f"👤 Employee: {metadata['employee_name']}")
        if metadata.get("project_context"):
            print(f"📋 Context: {metadata['project_context']}")

        print(f"\n📄 TRANSCRIBED TEXT:")
        print("-" * 50)
        print(transcription["text"])
        print("-" * 50)

    def save_result(self, result: Dict):
        """Save result for later review and Squirt integration"""
        timestamp = int(time.time())
        filename = f"voice_memo_{timestamp}.json"

        output_dir = Path("voice_memo_results")
        output_dir.mkdir(exist_ok=True)

        output_path = output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"💾 Result saved: {output_path}")

    def batch_process(self, audio_files: list, mode: str = "fast"):
        """Process multiple audio files in batch"""
        print(f"🔄 Batch processing {len(audio_files)} files in {mode} mode...")

        results = []

        for i, audio_file in enumerate(audio_files, 1):
            print(f"\n📁 Processing {i}/{len(audio_files)}: {Path(audio_file).name}")

            try:
                result = self.process_voice_memo(audio_file, mode)
                results.append(result)
                self.save_result(result)

            except Exception as e:
                print(f"❌ Failed to process {audio_file}: {e}")
                results.append({"error": str(e), "file": audio_file})

        print(f"\n✅ Batch processing complete: {len(results)} files processed")
        return results


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="WaterWizard Voice Memo Processor")
    parser.add_argument("audio_file", nargs="?", help="Audio file to process")
    parser.add_argument("--mode", choices=["fast", "accurate"], default="fast",
                       help="Processing mode (default: fast)")
    parser.add_argument("--employee", help="Employee name for tracking")
    parser.add_argument("--context", help="Project context (service call, estimate, etc.)")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Start interactive mode")
    parser.add_argument("--batch", nargs="+", help="Process multiple files")
    parser.add_argument("--output", help="Output file for results")

    args = parser.parse_args()

    interface = SquirtVoiceInterface()

    try:
        if args.interactive:
            interface.interactive_mode()

        elif args.batch:
            results = interface.batch_process(args.batch, args.mode)
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"📄 Batch results saved to {args.output}")

        elif args.audio_file:
            result = interface.process_voice_memo(
                audio_file=args.audio_file,
                mode=args.mode,
                employee_name=args.employee,
                project_context=args.context
            )

            interface.display_result(result)

            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"📄 Result saved to {args.output}")
            else:
                interface.save_result(result)

        else:
            parser.print_help()
            print("\n💡 Try: python squirt_voice_interface.py --interactive")

    except KeyboardInterrupt:
        print("\n\n👋 Processing interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()