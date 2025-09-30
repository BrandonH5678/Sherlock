#!/usr/bin/env python3
"""
Enhanced Audiobook Processor for Sherlock
Multi-path AAXC decryption with J5A validation protocols

Based on ChatGPT research on Audible audiobook conversion:
- Path A: AAXtoMP3 script with voucher support
- Path B: Snowcrypt Python integration
- Path C: FFmpeg with activation bytes (AAX fallback)
- Path D: Direct processing attempts
"""

import os
import sys
import json
import time
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Add J5A validation system
sys.path.append('/home/johnny5/Johny5Alive/src')

# Import Sherlock components
from voice_engine import VoiceEngineManager, TranscriptionMode, ProcessingPriority
from evidence_schema_gladio import GladioEvidenceDatabase

try:
    from j5a_statistical_validator import J5AStatisticalValidator, ValidationScope, SystemTarget
    J5A_VALIDATION_AVAILABLE = True
except ImportError:
    J5A_VALIDATION_AVAILABLE = False
    print("Warning: J5A validation not available")


class AudioFormat(Enum):
    """Supported audio formats"""
    AAX = "aax"           # Older Audible format
    AAXC = "aaxc"         # Newer Audible format with voucher
    MP3 = "mp3"           # Standard audio
    M4A = "m4a"           # AAC audio
    M4B = "m4b"           # Audiobook format
    WAV = "wav"           # Uncompressed


class DecryptionMethod(Enum):
    """Available decryption methods"""
    AAXTOMP3_SCRIPT = "aaxtomp3"        # AAXtoMP3 script (community favorite)
    SNOWCRYPT_PYTHON = "snowcrypt"      # Pure Python solution
    FFMPEG_ACTIVATION = "ffmpeg_bytes"   # FFmpeg with activation bytes
    FFMPEG_VOUCHER = "ffmpeg_voucher"    # FFmpeg with voucher key/IV (AAXC)
    DIRECT_WHISPER = "direct_whisper"    # Direct processing attempt
    AUDIBLE_CLI = "audible_cli"         # Re-download with different format


@dataclass
class AudiobookFile:
    """Audiobook file information"""
    file_path: str
    format: AudioFormat
    size_bytes: int
    duration_hours: Optional[float]
    voucher_path: Optional[str] = None
    activation_bytes: Optional[str] = None
    chapters: Optional[int] = None
    title: Optional[str] = None
    author: Optional[str] = None


@dataclass
class DecryptionAttempt:
    """Track decryption attempts and results"""
    method: DecryptionMethod
    success: bool
    output_path: Optional[str]
    processing_time: float
    error_message: Optional[str]
    file_size_bytes: Optional[int] = None
    audio_duration: Optional[float] = None


class EnhancedAudiobookProcessor:
    """
    Enhanced audiobook processor with multi-path AAXC decryption

    Implements validation-focused protocols from J5A:
    - Statistical sampling before resource allocation
    - Output delivery validation
    - Thermal safety integration
    - Single-speaker optimization
    """

    def __init__(self, db_path: str = "gladio_intelligence.db"):
        self.db = GladioEvidenceDatabase(db_path)
        self.voice_engine = None

        # J5A validation system
        if J5A_VALIDATION_AVAILABLE:
            self.validator = J5AStatisticalValidator(sample_size=3)
        else:
            self.validator = None

        # Processing statistics
        self.processing_stats = {
            "start_time": None,
            "decryption_attempts": [],
            "validation_results": {},
            "transcription_stats": {},
            "entities_extracted": 0,
            "total_processing_time": 0
        }

        # Decryption method priority (based on ChatGPT research)
        self.decryption_priority = [
            DecryptionMethod.FFMPEG_VOUCHER,     # NEW: FFmpeg with voucher for AAXC
            DecryptionMethod.AAXTOMP3_SCRIPT,    # Most reliable for AAXC
            DecryptionMethod.SNOWCRYPT_PYTHON,   # Pure Python, pip installable
            DecryptionMethod.FFMPEG_ACTIVATION,  # Good for AAX format
            DecryptionMethod.AUDIBLE_CLI,        # Re-download as different format
            DecryptionMethod.DIRECT_WHISPER      # Last resort
        ]

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('enhanced_audiobook_processing.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def process_audiobook(self, audiobook_path: str) -> bool:
        """
        Process audiobook with validation-focused protocols

        Args:
            audiobook_path: Path to audiobook file (.aax or .aaxc)

        Returns:
            bool: Success status
        """
        self.processing_stats["start_time"] = time.time()

        try:
            self.logger.info(f"🎧 Starting enhanced audiobook processing: {audiobook_path}")

            # Phase 1: File Analysis and Validation
            audiobook = self._analyze_audiobook_file(audiobook_path)
            if not audiobook:
                self.logger.error("❌ Failed to analyze audiobook file")
                return False

            self.logger.info(f"📊 Audiobook: {audiobook.title} ({audiobook.format.value})")
            self.logger.info(f"📁 Size: {audiobook.size_bytes / 1024 / 1024:.1f}MB")
            if audiobook.duration_hours:
                self.logger.info(f"⏱️  Duration: {audiobook.duration_hours:.1f} hours")

            # Phase 2: J5A Pre-Processing Validation
            if not self._validate_pre_processing(audiobook):
                self.logger.error("❌ Pre-processing validation failed")
                return False

            # Phase 3: Multi-Path Decryption
            decrypted_audio = self._decrypt_audiobook(audiobook)
            if not decrypted_audio:
                self.logger.error("❌ All decryption methods failed")
                return False

            self.logger.info(f"✅ Decryption successful: {decrypted_audio}")

            # Phase 4: J5A Statistical Sampling Validation
            if not self._validate_decrypted_audio(decrypted_audio):
                self.logger.error("❌ Decrypted audio validation failed")
                return False

            # Phase 5: Single-Speaker Optimized Transcription
            transcript = self._transcribe_optimized(decrypted_audio, single_speaker=True)
            if not transcript:
                self.logger.error("❌ Transcription failed")
                return False

            # Phase 6: Intelligence Extraction and Database Population
            extraction_success = self._extract_and_store_intelligence(transcript, audiobook)
            if not extraction_success:
                self.logger.error("❌ Intelligence extraction failed")
                return False

            # Phase 7: J5A Output Validation
            if not self._validate_final_outputs(audiobook):
                self.logger.error("❌ Final output validation failed")
                return False

            # Generate completion report
            self._generate_processing_report(audiobook)

            total_time = time.time() - self.processing_stats["start_time"]
            self.logger.info(f"🎯 Enhanced processing completed in {total_time/3600:.2f} hours")

            return True

        except Exception as e:
            self.logger.error(f"❌ Processing failed with exception: {e}")
            return False

    def _analyze_audiobook_file(self, file_path: str) -> Optional[AudiobookFile]:
        """Analyze audiobook file and detect format/metadata"""
        try:
            if not os.path.exists(file_path):
                return None

            file_stats = os.stat(file_path)
            path_obj = Path(file_path)

            # Detect format from extension
            extension = path_obj.suffix.lower().lstrip('.')
            try:
                format_type = AudioFormat(extension)
            except ValueError:
                self.logger.warning(f"Unknown format: {extension}, assuming AAX")
                format_type = AudioFormat.AAX

            # Look for voucher file (for AAXC)
            voucher_path = None
            if format_type == AudioFormat.AAXC:
                voucher_file = path_obj.with_suffix('.voucher')
                if voucher_file.exists():
                    voucher_path = str(voucher_file)
                    self.logger.info(f"✅ Found voucher file: {voucher_path}")
                else:
                    self.logger.warning("⚠️ AAXC file without voucher - may cause decryption issues")

            # Extract title from filename
            title = path_obj.stem
            if "_" in title:
                title = title.replace("_", " ")

            # Detect duration (if possible)
            duration = None
            try:
                # Try to get duration with ffprobe
                result = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                    '-of', 'csv=p=0', file_path
                ], capture_output=True, text=True, timeout=30)

                if result.returncode == 0 and result.stdout.strip():
                    duration_seconds = float(result.stdout.strip())
                    duration = duration_seconds / 3600  # Convert to hours
            except Exception as e:
                self.logger.debug(f"Could not determine duration: {e}")

            # Check for activation bytes (for AAX)
            activation_bytes = None
            if format_type == AudioFormat.AAX:
                # Try to find activation bytes in environment or config
                activation_bytes = os.environ.get('AUDIBLE_ACTIVATION_BYTES', '35d4b805')  # From logs

            audiobook = AudiobookFile(
                file_path=file_path,
                format=format_type,
                size_bytes=file_stats.st_size,
                duration_hours=duration,
                voucher_path=voucher_path,
                activation_bytes=activation_bytes,
                title=title,
                author="Unknown"
            )

            return audiobook

        except Exception as e:
            self.logger.error(f"File analysis error: {e}")
            return None

    def _validate_pre_processing(self, audiobook: AudiobookFile) -> bool:
        """J5A validation checkpoint: Pre-processing validation"""
        self.logger.info("🔍 J5A Pre-processing validation...")

        validation_results = {
            "file_exists": os.path.exists(audiobook.file_path),
            "file_readable": os.access(audiobook.file_path, os.R_OK),
            "format_supported": audiobook.format in [AudioFormat.AAX, AudioFormat.AAXC],
            "size_reasonable": 10 * 1024 * 1024 < audiobook.size_bytes < 2 * 1024 * 1024 * 1024,  # 10MB - 2GB
            "voucher_available": audiobook.format != AudioFormat.AAXC or audiobook.voucher_path is not None,
            "activation_bytes_available": audiobook.format != AudioFormat.AAX or audiobook.activation_bytes is not None
        }

        success_count = sum(validation_results.values())
        total_checks = len(validation_results)
        success_rate = success_count / total_checks

        self.processing_stats["validation_results"]["pre_processing"] = {
            "success_rate": success_rate,
            "checks": validation_results,
            "passed": success_rate >= 0.8  # 80% threshold
        }

        for check, passed in validation_results.items():
            status = "✅" if passed else "❌"
            self.logger.info(f"  {status} {check}")

        if success_rate >= 0.8:
            self.logger.info(f"✅ Pre-processing validation passed ({success_rate:.1%})")
            return True
        else:
            self.logger.error(f"❌ Pre-processing validation failed ({success_rate:.1%})")
            return False

    def _decrypt_audiobook(self, audiobook: AudiobookFile) -> Optional[str]:
        """Multi-path decryption based on ChatGPT research"""
        self.logger.info("🔓 Starting multi-path decryption...")

        output_dir = Path(audiobook.file_path).parent / "decrypted"
        output_dir.mkdir(exist_ok=True)

        # Try each decryption method in priority order
        for method in self.decryption_priority:
            self.logger.info(f"🔧 Trying decryption method: {method.value}")

            attempt = self._attempt_decryption(audiobook, method, output_dir)
            self.processing_stats["decryption_attempts"].append(attempt)

            if attempt.success and attempt.output_path:
                self.logger.info(f"✅ Decryption successful with {method.value}")
                self.logger.info(f"📁 Output: {attempt.output_path}")
                return attempt.output_path
            else:
                self.logger.warning(f"❌ {method.value} failed: {attempt.error_message}")

        self.logger.error("❌ All decryption methods failed")
        return None

    def _attempt_decryption(self, audiobook: AudiobookFile, method: DecryptionMethod,
                          output_dir: Path) -> DecryptionAttempt:
        """Attempt single decryption method"""
        start_time = time.time()
        output_file = output_dir / f"decrypted_{method.value}.mp3"

        try:
            if method == DecryptionMethod.AAXTOMP3_SCRIPT:
                return self._decrypt_with_aaxtomp3(audiobook, output_file, start_time)
            elif method == DecryptionMethod.SNOWCRYPT_PYTHON:
                return self._decrypt_with_snowcrypt(audiobook, output_file, start_time)
            elif method == DecryptionMethod.FFMPEG_ACTIVATION:
                return self._decrypt_with_ffmpeg(audiobook, output_file, start_time)
            elif method == DecryptionMethod.FFMPEG_VOUCHER:
                return self._decrypt_with_ffmpeg_voucher(audiobook, output_file, start_time)
            elif method == DecryptionMethod.AUDIBLE_CLI:
                return self._decrypt_with_audible_cli(audiobook, output_file, start_time)
            elif method == DecryptionMethod.DIRECT_WHISPER:
                return self._decrypt_direct_whisper(audiobook, output_file, start_time)
            else:
                raise ValueError(f"Unknown decryption method: {method}")

        except Exception as e:
            return DecryptionAttempt(
                method=method,
                success=False,
                output_path=None,
                processing_time=time.time() - start_time,
                error_message=str(e)
            )

    def _decrypt_with_aaxtomp3(self, audiobook: AudiobookFile, output_file: Path, start_time: float) -> DecryptionAttempt:
        """Decrypt using AAXtoMP3 script (ChatGPT recommended)"""
        try:
            # Check if AAXtoMP3 is available
            aaxtomp3_path = "/tmp/AAXtoMP3/AAXtoMP3"
            if not os.path.exists(aaxtomp3_path):
                # Download AAXtoMP3
                self.logger.info("📥 Downloading AAXtoMP3 script...")
                subprocess.run([
                    'git', 'clone', 'https://github.com/KrumpetPirate/AAXtoMP3.git', '/tmp/AAXtoMP3'
                ], check=True, timeout=60)

            # Build command based on audiobook format
            cmd = [aaxtomp3_path]

            if audiobook.format == AudioFormat.AAX and audiobook.activation_bytes:
                cmd.extend(['--authcode', audiobook.activation_bytes])
            elif audiobook.format == AudioFormat.AAXC and audiobook.voucher_path:
                # For AAXC, run in directory with voucher file
                cmd_dir = Path(audiobook.file_path).parent
                cmd = ['./AAXtoMP3'] if aaxtomp3_path.startswith('./') else [aaxtomp3_path]
            else:
                raise ValueError("Missing authentication for AAXtoMP3")

            cmd.extend(['-e:mp3', '--single', audiobook.file_path])

            # Execute conversion
            self.logger.info(f"🔄 Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=Path(audiobook.file_path).parent if audiobook.format == AudioFormat.AAXC else None,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )

            if result.returncode == 0:
                # Find the generated MP3 file
                for potential_output in Path(audiobook.file_path).parent.glob("*.mp3"):
                    if potential_output.stat().st_size > 1024:  # At least 1KB
                        file_size = potential_output.stat().st_size
                        return DecryptionAttempt(
                            method=DecryptionMethod.AAXTOMP3_SCRIPT,
                            success=True,
                            output_path=str(potential_output),
                            processing_time=time.time() - start_time,
                            error_message=None,
                            file_size_bytes=file_size
                        )

            # If we get here, conversion failed
            return DecryptionAttempt(
                method=DecryptionMethod.AAXTOMP3_SCRIPT,
                success=False,
                output_path=None,
                processing_time=time.time() - start_time,
                error_message=f"AAXtoMP3 failed: {result.stderr}"
            )

        except subprocess.TimeoutExpired:
            return DecryptionAttempt(
                method=DecryptionMethod.AAXTOMP3_SCRIPT,
                success=False,
                output_path=None,
                processing_time=time.time() - start_time,
                error_message="AAXtoMP3 timeout"
            )
        except Exception as e:
            return DecryptionAttempt(
                method=DecryptionMethod.AAXTOMP3_SCRIPT,
                success=False,
                output_path=None,
                processing_time=time.time() - start_time,
                error_message=str(e)
            )

    def _decrypt_with_snowcrypt(self, audiobook: AudiobookFile, output_file: Path, start_time: float) -> DecryptionAttempt:
        """Decrypt using Snowcrypt Python library"""
        try:
            # Install snowcrypt if not available
            try:
                import snowcrypt
            except ImportError:
                self.logger.info("📥 Installing snowcrypt...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'snowcrypt'], check=True)
                import snowcrypt

            # Use snowcrypt for decryption
            if audiobook.format == AudioFormat.AAXC and audiobook.voucher_path:
                # AAXC with voucher
                with open(audiobook.voucher_path, 'rb') as voucher_file:
                    voucher_data = voucher_file.read()

                decrypted_data = snowcrypt.decrypt_aaxc(audiobook.file_path, voucher_data)
            elif audiobook.format == AudioFormat.AAX and audiobook.activation_bytes:
                # AAX with activation bytes
                decrypted_data = snowcrypt.decrypt_aax(audiobook.file_path, audiobook.activation_bytes)
            else:
                raise ValueError("Unsupported format or missing credentials for Snowcrypt")

            # Save decrypted audio
            with open(output_file, 'wb') as f:
                f.write(decrypted_data)

            file_size = output_file.stat().st_size
            if file_size > 1024:  # At least 1KB
                return DecryptionAttempt(
                    method=DecryptionMethod.SNOWCRYPT_PYTHON,
                    success=True,
                    output_path=str(output_file),
                    processing_time=time.time() - start_time,
                    error_message=None,
                    file_size_bytes=file_size
                )
            else:
                return DecryptionAttempt(
                    method=DecryptionMethod.SNOWCRYPT_PYTHON,
                    success=False,
                    output_path=None,
                    processing_time=time.time() - start_time,
                    error_message="Snowcrypt produced empty output"
                )

        except Exception as e:
            return DecryptionAttempt(
                method=DecryptionMethod.SNOWCRYPT_PYTHON,
                success=False,
                output_path=None,
                processing_time=time.time() - start_time,
                error_message=str(e)
            )

    def _decrypt_with_ffmpeg(self, audiobook: AudiobookFile, output_file: Path, start_time: float) -> DecryptionAttempt:
        """Decrypt using FFmpeg with activation bytes (AAX only)"""
        try:
            if audiobook.format != AudioFormat.AAX:
                raise ValueError("FFmpeg method only works with AAX format")

            if not audiobook.activation_bytes:
                raise ValueError("Missing activation bytes for FFmpeg decryption")

            cmd = [
                'ffmpeg',
                '-activation_bytes', audiobook.activation_bytes,
                '-i', audiobook.file_path,
                '-c:a', 'mp3',
                str(output_file),
                '-y'  # Overwrite output
            ]

            self.logger.info(f"🔄 Running: {' '.join(cmd[:-3])} [REDACTED] {' '.join(cmd[-1:])}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0 and output_file.exists():
                file_size = output_file.stat().st_size
                if file_size > 1024:
                    return DecryptionAttempt(
                        method=DecryptionMethod.FFMPEG_ACTIVATION,
                        success=True,
                        output_path=str(output_file),
                        processing_time=time.time() - start_time,
                        error_message=None,
                        file_size_bytes=file_size
                    )

            return DecryptionAttempt(
                method=DecryptionMethod.FFMPEG_ACTIVATION,
                success=False,
                output_path=None,
                processing_time=time.time() - start_time,
                error_message=f"FFmpeg failed: {result.stderr}"
            )

        except Exception as e:
            return DecryptionAttempt(
                method=DecryptionMethod.FFMPEG_ACTIVATION,
                success=False,
                output_path=None,
                processing_time=time.time() - start_time,
                error_message=str(e)
            )

    def _decrypt_with_ffmpeg_voucher(self, audiobook: AudiobookFile, output_file: Path, start_time: float) -> DecryptionAttempt:
        """Decrypt AAXC using FFmpeg with voucher file key and IV"""
        try:
            if audiobook.format != AudioFormat.AAXC:
                raise ValueError("FFmpeg voucher method only works with AAXC format")

            # Find and parse voucher file
            voucher_data = self._parse_voucher_file(audiobook.file_path)
            if not voucher_data:
                raise ValueError("No voucher file found or unable to parse")

            decryption_key = voucher_data.get('key')
            iv = voucher_data.get('iv')

            if not decryption_key or not iv:
                raise ValueError("Missing decryption key or IV in voucher file")

            # FFmpeg command with audible_key for AAXC
            cmd = [
                'ffmpeg',
                '-audible_key', decryption_key,
                '-audible_iv', iv,
                '-i', audiobook.file_path,
                '-c:a', 'mp3',
                str(output_file),
                '-y'  # Overwrite output
            ]

            self.logger.info(f"🔄 Running FFmpeg with voucher decryption: {audiobook.file_path}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # Longer timeout for full file
            )

            if result.returncode == 0 and output_file.exists():
                file_size = output_file.stat().st_size
                if file_size > 1024:
                    return DecryptionAttempt(
                        method=DecryptionMethod.FFMPEG_VOUCHER,
                        success=True,
                        output_path=str(output_file),
                        processing_time=time.time() - start_time,
                        error_message=None,
                        file_size_bytes=file_size
                    )

            return DecryptionAttempt(
                method=DecryptionMethod.FFMPEG_VOUCHER,
                success=False,
                output_path=None,
                processing_time=time.time() - start_time,
                error_message=f"FFmpeg voucher decryption failed: {result.stderr}"
            )
        except Exception as e:
            return DecryptionAttempt(
                method=DecryptionMethod.FFMPEG_VOUCHER,
                success=False,
                output_path=None,
                processing_time=time.time() - start_time,
                error_message=str(e)
            )

    def _parse_voucher_file(self, aaxc_file_path: str) -> Optional[Dict[str, str]]:
        """Parse voucher file to extract decryption key and IV"""
        try:
            aaxc_path = Path(aaxc_file_path)
            base_dir = aaxc_path.parent

            # Look for voucher files in the same directory
            for voucher_file in base_dir.glob("*.voucher"):
                with open(voucher_file, 'r') as f:
                    voucher_data = json.load(f)

                # Extract key and IV from license_response
                license_response = voucher_data.get('content_license', {}).get('license_response', {})
                key = license_response.get('key')
                iv = license_response.get('iv')

                if key and iv:
                    self.logger.info(f"📄 Found voucher with decryption credentials: {voucher_file.name}")
                    return {
                        'key': key,
                        'iv': iv,
                        'voucher_file': str(voucher_file)
                    }

        except Exception as e:
            self.logger.warning(f"⚠️ Error parsing voucher file: {e}")

        return None

    def _decrypt_with_audible_cli(self, audiobook: AudiobookFile, output_file: Path, start_time: float) -> DecryptionAttempt:
        """Attempt re-download with audible-cli in different format"""
        # This would require implementing audible-cli re-download
        # For now, return failure as it's complex to implement
        return DecryptionAttempt(
            method=DecryptionMethod.AUDIBLE_CLI,
            success=False,
            output_path=None,
            processing_time=time.time() - start_time,
            error_message="Audible CLI re-download not implemented"
        )

    def _decrypt_direct_whisper(self, audiobook: AudiobookFile, output_file: Path, start_time: float) -> DecryptionAttempt:
        """Last resort: try direct Whisper processing"""
        # This is what was failing before - just try to see if it works now
        return DecryptionAttempt(
            method=DecryptionMethod.DIRECT_WHISPER,
            success=False,
            output_path=None,
            processing_time=time.time() - start_time,
            error_message="Direct Whisper processing of encrypted files not supported"
        )

    def _validate_decrypted_audio(self, audio_path: str) -> bool:
        """J5A statistical sampling validation of decrypted audio"""
        self.logger.info("🔍 J5A Statistical sampling validation of decrypted audio...")

        if not self.validator:
            self.logger.warning("⚠️ J5A validator not available, skipping statistical sampling")
            # Basic validation instead
            return os.path.exists(audio_path) and os.path.getsize(audio_path) > 1024

        try:
            # Create test samples for validation
            test_inputs = [audio_path]

            validation_report = self.validator.validate_system_readiness(
                system_target=SystemTarget.SHERLOCK,
                validation_scope=ValidationScope.OUTPUT_DELIVERY,
                test_inputs=test_inputs
            )

            self.processing_stats["validation_results"]["decrypted_audio"] = {
                "processing_viability": validation_report.processing_viability,
                "success_rate": validation_report.success_rate,
                "format_success_rate": validation_report.format_success_rate,
                "average_quality_score": validation_report.average_quality_score
            }

            if validation_report.processing_viability:
                self.logger.info("✅ Decrypted audio validation passed")
                return True
            else:
                self.logger.error("❌ Decrypted audio validation failed")
                return False

        except Exception as e:
            self.logger.error(f"❌ Audio validation error: {e}")
            return False

    def _transcribe_optimized(self, audio_path: str, single_speaker: bool = True) -> Optional[str]:
        """Single-speaker optimized transcription using faster-whisper"""
        self.logger.info("🎤 Starting single-speaker optimized transcription...")

        try:
            if not self.voice_engine:
                self.voice_engine = VoiceEngineManager(max_ram_gb=3.0)  # J5A memory constraint

            # For Operation Gladio (single speaker), use faster-whisper in FAST mode
            mode = TranscriptionMode.FAST if single_speaker else TranscriptionMode.ACCURATE

            self.logger.info(f"🔧 Using transcription mode: {mode.value}")
            self.logger.info("⏳ Single-speaker processing - estimated time: 30-45 minutes")

            # Create transcription request
            from voice_engine import VoiceProcessingRequest

            request = VoiceProcessingRequest(
                audio_path=audio_path,
                mode=mode,
                priority=ProcessingPriority.BACKGROUND,
                system="sherlock_audiobook",
                single_speaker=single_speaker,
                language="en"
            )

            # Process with voice engine
            result = self.voice_engine.transcribe_sherlock(request)

            if result and result.success and result.transcript:
                transcript = result.transcript
                self.processing_stats["transcription_stats"] = {
                    "mode": mode.value,
                    "processing_time": result.processing_time,
                    "transcript_length": len(transcript),
                    "confidence_score": result.average_confidence,
                    "single_speaker": single_speaker
                }

                # Save transcript
                transcript_path = Path(audio_path).parent / "operation_gladio_transcript.txt"
                with open(transcript_path, 'w', encoding='utf-8') as f:
                    f.write(transcript)

                self.logger.info(f"✅ Transcription completed: {len(transcript):,} characters")
                return transcript
            else:
                self.logger.error("❌ Voice engine transcription failed")
                return None

        except Exception as e:
            self.logger.error(f"❌ Transcription error: {e}")
            return None

    def _extract_and_store_intelligence(self, transcript: str, audiobook: AudiobookFile) -> bool:
        """Extract intelligence and populate evidence database"""
        self.logger.info("🔍 Extracting intelligence from transcript...")

        try:
            # Use existing intelligence extraction from direct_aaxc_processor
            from direct_aaxc_processor import DirectAaxcProcessor

            extractor = DirectAaxcProcessor()
            extractor.db = self.db  # Use same database

            # Extract intelligence
            extractor._extract_intelligence(transcript)

            # Update processing stats
            people_count = len(self.db.get_all_people())
            org_count = len(self.db.get_all_organizations())

            self.processing_stats["entities_extracted"] = people_count + org_count

            self.logger.info(f"✅ Intelligence extraction completed:")
            self.logger.info(f"   👥 People: {people_count}")
            self.logger.info(f"   🏢 Organizations: {org_count}")

            return True

        except Exception as e:
            self.logger.error(f"❌ Intelligence extraction error: {e}")
            return False

    def _validate_final_outputs(self, audiobook: AudiobookFile) -> bool:
        """J5A final output validation"""
        self.logger.info("🔍 J5A Final output validation...")

        expected_outputs = [
            "operation_gladio_transcript.txt",
            "gladio_intelligence.db",
            "enhanced_audiobook_processing_report.json"
        ]

        validation_results = {}
        base_dir = Path(audiobook.file_path).parent

        for output_file in expected_outputs:
            file_path = base_dir / output_file
            exists = file_path.exists()
            size_ok = file_path.stat().st_size > 0 if exists else False

            validation_results[output_file] = {
                "exists": exists,
                "size_ok": size_ok,
                "valid": exists and size_ok
            }

        success_count = sum(1 for result in validation_results.values() if result["valid"])
        success_rate = success_count / len(expected_outputs)

        self.processing_stats["validation_results"]["final_outputs"] = {
            "success_rate": success_rate,
            "expected_outputs": expected_outputs,
            "results": validation_results
        }

        for output_file, result in validation_results.items():
            status = "✅" if result["valid"] else "❌"
            self.logger.info(f"  {status} {output_file}")

        if success_rate >= 0.8:  # 80% threshold
            self.logger.info(f"✅ Final output validation passed ({success_rate:.1%})")
            return True
        else:
            self.logger.error(f"❌ Final output validation failed ({success_rate:.1%})")
            return False

    def _generate_processing_report(self, audiobook: AudiobookFile):
        """Generate comprehensive processing report"""
        total_time = time.time() - self.processing_stats["start_time"]

        report = {
            "processing_date": datetime.now().isoformat(),
            "audiobook_info": {
                "title": audiobook.title,
                "format": audiobook.format.value,
                "size_mb": audiobook.size_bytes / 1024 / 1024,
                "duration_hours": audiobook.duration_hours,
                "voucher_used": audiobook.voucher_path is not None,
                "activation_bytes_used": audiobook.activation_bytes is not None
            },
            "processing_stats": {
                **self.processing_stats,
                "total_processing_time_hours": total_time / 3600
            },
            "decryption_summary": {
                "attempts": len(self.processing_stats["decryption_attempts"]),
                "successful_method": next(
                    (attempt.method.value for attempt in self.processing_stats["decryption_attempts"] if attempt.success),
                    None
                )
            },
            "validation_summary": self.processing_stats["validation_results"],
            "quality_metrics": {
                "pre_processing_passed": self.processing_stats["validation_results"].get("pre_processing", {}).get("passed", False),
                "audio_validation_passed": self.processing_stats["validation_results"].get("decrypted_audio", {}).get("processing_viability", False),
                "final_outputs_passed": self.processing_stats["validation_results"].get("final_outputs", {}).get("success_rate", 0) >= 0.8
            }
        }

        report_path = Path(audiobook.file_path).parent / "enhanced_audiobook_processing_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        self.logger.info(f"📊 Processing report saved: {report_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 enhanced_audiobook_processor.py <audiobook_file>")
        sys.exit(1)

    audiobook_path = sys.argv[1]
    if not os.path.exists(audiobook_path):
        print(f"❌ Audiobook file not found: {audiobook_path}")
        sys.exit(1)

    print("🚀 ENHANCED AUDIOBOOK PROCESSOR WITH J5A VALIDATION")
    print("=" * 60)
    print(f"Processing: {audiobook_path}")
    print("Features:")
    print("  🔓 Multi-path AAXC decryption (AAXtoMP3, Snowcrypt, FFmpeg)")
    print("  🔍 J5A statistical sampling validation")
    print("  🎤 Single-speaker optimization (faster-whisper)")
    print("  📊 Complete output delivery validation")
    print()

    processor = EnhancedAudiobookProcessor()
    success = processor.process_audiobook(audiobook_path)

    if success:
        print("✅ ENHANCED PROCESSING COMPLETED SUCCESSFULLY!")
        print("📊 Check enhanced_audiobook_processing_report.json for details")
        print("🔍 Explore results with: python3 gladio_analysis.py")
    else:
        print("❌ ENHANCED PROCESSING FAILED")
        print("📁 Check enhanced_audiobook_processing.log for details")