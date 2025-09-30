#!/usr/bin/env python3
"""
AAXC Processing Validation Pipeline for Operation Gladio
Validates decryption, transcription, and intelligence extraction
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Sherlock components
from voice_engine import VoiceEngineManager, VoiceProcessingRequest, TranscriptionMode, ProcessingPriority
from evidence_schema_gladio import GladioEvidenceDatabase


class AaxcValidationPipeline:
    """Complete validation pipeline for AAXC processing"""

    def __init__(self):
        self.voice_engine = VoiceEngineManager(max_ram_gb=3.7)
        self.db = GladioEvidenceDatabase("validation_test.db")

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('aaxc_validation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def validate_decryption_output(self, m4a_file: str) -> Dict:
        """Validate decrypted M4A file quality"""
        validation_result = {
            "file_exists": False,
            "file_size": 0,
            "format_valid": False,
            "duration": 0,
            "audio_properties": {}
        }

        try:
            if os.path.exists(m4a_file):
                validation_result["file_exists"] = True
                validation_result["file_size"] = os.path.getsize(m4a_file)

                # Check file format with ffprobe
                import subprocess
                result = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-print_format', 'json',
                    '-show_format', '-show_streams', m4a_file
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    probe_data = json.loads(result.stdout)
                    validation_result["format_valid"] = True
                    validation_result["duration"] = float(probe_data.get('format', {}).get('duration', 0))

                    # Extract audio properties
                    for stream in probe_data.get('streams', []):
                        if stream.get('codec_type') == 'audio':
                            validation_result["audio_properties"] = {
                                "codec": stream.get('codec_name'),
                                "sample_rate": stream.get('sample_rate'),
                                "channels": stream.get('channels'),
                                "bit_rate": stream.get('bit_rate')
                            }
                            break

        except Exception as e:
            self.logger.error(f"Decryption validation error: {e}")

        return validation_result

    def create_test_segments(self, m4a_file: str, num_segments: int = 3) -> List[str]:
        """Create test segments from M4A file for sampling validation"""
        segments = []

        try:
            # Get file duration
            import subprocess
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', m4a_file
            ], capture_output=True, text=True)

            if result.returncode == 0:
                duration = float(result.stdout.strip())
                self.logger.info(f"Audio duration: {duration:.1f} seconds ({duration/3600:.1f} hours)")

                # Create 3 strategic test segments
                segment_duration = 30  # 30 seconds each
                positions = [
                    (60, "beginning"),  # 1 minute in
                    (duration / 2, "middle"),  # Middle of file
                    (duration - 300, "end")  # 5 minutes from end
                ]

                output_dir = Path(m4a_file).parent / "validation_segments"
                output_dir.mkdir(exist_ok=True)

                for i, (start_time, position) in enumerate(positions):
                    if start_time > 0 and start_time < duration - segment_duration:
                        segment_file = output_dir / f"test_segment_{i+1}_{position}.wav"

                        # Extract segment as WAV for transcription
                        subprocess.run([
                            'ffmpeg', '-y', '-i', m4a_file,
                            '-ss', str(start_time), '-t', str(segment_duration),
                            '-acodec', 'pcm_s16le', '-ar', '16000',
                            str(segment_file)
                        ], capture_output=True)

                        if os.path.exists(segment_file) and os.path.getsize(segment_file) > 1000:
                            segments.append(str(segment_file))
                            self.logger.info(f"✅ Created test segment: {segment_file}")
                        else:
                            self.logger.warning(f"⚠️ Failed to create segment: {segment_file}")

        except Exception as e:
            self.logger.error(f"Segment creation error: {e}")

        return segments

    def validate_transcription_pipeline(self, test_segments: List[str]) -> Dict:
        """Validate transcription quality on test segments"""
        validation_results = {
            "total_segments": len(test_segments),
            "successful_transcriptions": 0,
            "total_transcription_length": 0,
            "average_processing_time": 0,
            "quality_scores": [],
            "detailed_results": []
        }

        total_processing_time = 0

        for i, segment_file in enumerate(test_segments):
            segment_result = {
                "segment_id": f"test_{i+1}",
                "file": segment_file,
                "success": False,
                "transcription_length": 0,
                "processing_time": 0,
                "quality_score": 0.0,
                "error": None
            }

            try:
                self.logger.info(f"🔄 Testing transcription for segment {i+1}: {segment_file}")

                start_time = time.time()

                # Create processing request
                request = VoiceProcessingRequest(
                    audio_path=segment_file,
                    mode=TranscriptionMode.FAST,  # Use fast mode for validation
                    priority=ProcessingPriority.IMMEDIATE,
                    system="validation"
                )

                # Process with Sherlock voice engine
                result = self.voice_engine.transcribe_sherlock(request)

                processing_time = time.time() - start_time
                total_processing_time += processing_time

                if result and result.transcript:
                    segment_result["success"] = True
                    segment_result["transcription_length"] = len(result.transcript)
                    segment_result["processing_time"] = processing_time

                    # Calculate quality score based on transcript length and processing time
                    expected_words = 30 * 2  # ~2 words per second for 30-second segment
                    actual_words = len(result.transcript.split())
                    length_score = min(actual_words / expected_words, 1.0)
                    speed_score = min(30 / processing_time, 1.0)  # Should process faster than real-time

                    segment_result["quality_score"] = (length_score + speed_score) / 2

                    validation_results["successful_transcriptions"] += 1
                    validation_results["total_transcription_length"] += len(result.transcript)
                    validation_results["quality_scores"].append(segment_result["quality_score"])

                    self.logger.info(f"✅ Segment {i+1} processed: {len(result.transcript)} chars, {processing_time:.1f}s, quality: {segment_result['quality_score']:.2f}")

                else:
                    segment_result["error"] = "No transcription result"
                    self.logger.warning(f"⚠️ Segment {i+1} failed: No transcription result")

            except Exception as e:
                segment_result["error"] = str(e)
                self.logger.error(f"❌ Segment {i+1} error: {e}")

            validation_results["detailed_results"].append(segment_result)

        # Calculate averages
        if validation_results["successful_transcriptions"] > 0:
            validation_results["average_processing_time"] = total_processing_time / validation_results["successful_transcriptions"]

        if validation_results["quality_scores"]:
            validation_results["average_quality_score"] = sum(validation_results["quality_scores"]) / len(validation_results["quality_scores"])
        else:
            validation_results["average_quality_score"] = 0.0

        return validation_results

    def generate_validation_report(self, decryption_validation: Dict, transcription_validation: Dict) -> Dict:
        """Generate comprehensive validation report"""

        # Calculate overall metrics
        decryption_success = decryption_validation["format_valid"] and decryption_validation["file_size"] > 100000000  # >100MB
        transcription_success_rate = transcription_validation["successful_transcriptions"] / max(transcription_validation["total_segments"], 1)

        # Processing viability assessment
        processing_viable = (
            decryption_success and
            transcription_success_rate >= 0.6 and
            transcription_validation["average_quality_score"] >= 0.3
        )

        report = {
            "validation_timestamp": datetime.now().isoformat(),
            "operation": "Operation Gladio AAXC Processing Validation",
            "decryption_validation": decryption_validation,
            "transcription_validation": transcription_validation,
            "overall_metrics": {
                "decryption_success": decryption_success,
                "transcription_success_rate": transcription_success_rate,
                "average_quality_score": transcription_validation["average_quality_score"],
                "processing_viable": processing_viable
            },
            "recommendations": []
        }

        # Generate recommendations
        if not decryption_success:
            report["recommendations"].append("❌ CRITICAL: Decryption validation failed - check AAXC/voucher integrity")

        if transcription_success_rate < 0.6:
            report["recommendations"].append("⚠️ WARNING: Low transcription success rate - check audio quality")

        if transcription_validation["average_quality_score"] < 0.5:
            report["recommendations"].append("⚠️ WARNING: Low quality scores - consider using ACCURATE mode")

        if processing_viable:
            report["recommendations"].append("✅ PROCEED: Processing pipeline validated - ready for full Operation Gladio analysis")
        else:
            report["recommendations"].append("❌ BLOCK: Processing not viable - resolve issues before proceeding")

        return report

    def run_full_validation(self, m4a_file: str) -> Dict:
        """Run complete validation pipeline"""
        self.logger.info("🚀 Starting AAXC processing validation pipeline")
        self.logger.info(f"Target file: {m4a_file}")

        # Step 1: Validate decryption output
        self.logger.info("🔍 Step 1: Validating decryption output...")
        decryption_validation = self.validate_decryption_output(m4a_file)

        if not decryption_validation["format_valid"]:
            self.logger.error("❌ Decryption validation failed - aborting")
            return {"error": "Decryption validation failed", "decryption_validation": decryption_validation}

        # Step 2: Create test segments
        self.logger.info("✂️ Step 2: Creating test segments...")
        test_segments = self.create_test_segments(m4a_file)

        if len(test_segments) < 2:
            self.logger.error("❌ Insufficient test segments created - aborting")
            return {"error": "Insufficient test segments", "segments_created": len(test_segments)}

        # Step 3: Validate transcription pipeline
        self.logger.info("🎤 Step 3: Validating transcription pipeline...")
        transcription_validation = self.validate_transcription_pipeline(test_segments)

        # Step 4: Generate final report
        self.logger.info("📊 Step 4: Generating validation report...")
        final_report = self.generate_validation_report(decryption_validation, transcription_validation)

        # Save report
        report_file = "operation_gladio_validation_report.json"
        with open(report_file, 'w') as f:
            json.dump(final_report, f, indent=2)

        self.logger.info(f"📋 Validation report saved: {report_file}")

        return final_report


def main():
    """Main execution function"""
    if len(sys.argv) != 2:
        print("Usage: python aaxc_validation_pipeline.py <decrypted_m4a_file>")
        sys.exit(1)

    m4a_file = sys.argv[1]
    if not os.path.exists(m4a_file):
        print(f"❌ File not found: {m4a_file}")
        sys.exit(1)

    validator = AaxcValidationPipeline()
    report = validator.run_full_validation(m4a_file)

    if "error" in report:
        print(f"❌ Validation failed: {report['error']}")
        sys.exit(1)

    # Print summary
    print("\n🎯 OPERATION GLADIO AAXC VALIDATION SUMMARY")
    print("=" * 50)

    overall = report["overall_metrics"]
    print(f"Decryption Success: {'✅' if overall['decryption_success'] else '❌'}")
    print(f"Transcription Success Rate: {overall['transcription_success_rate']:.1%}")
    print(f"Average Quality Score: {overall['average_quality_score']:.2f}")
    print(f"Processing Viable: {'✅ YES' if overall['processing_viable'] else '❌ NO'}")

    print("\n📋 Recommendations:")
    for rec in report["recommendations"]:
        print(f"  {rec}")

    print(f"\n📄 Full report: operation_gladio_validation_report.json")

    return 0 if overall["processing_viable"] else 1


if __name__ == "__main__":
    sys.exit(main())