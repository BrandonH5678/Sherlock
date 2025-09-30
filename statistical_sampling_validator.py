#!/usr/bin/env python3
"""
Statistical Sampling Validation System for Sherlock
Implements periodic 3-segment sampling to validate processing pipeline quality
"""

import os
import sys
import json
import time
import random
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

# Import Sherlock components
try:
    from voice_engine import VoiceEngineManager, VoiceProcessingRequest, TranscriptionMode, ProcessingPriority
    from evidence_schema_gladio import GladioEvidenceDatabase
except ImportError:
    print("Warning: Sherlock components not available for import validation")


@dataclass
class SampleValidationResult:
    """Results from validating a single sample"""
    sample_id: str
    chunk_path: str
    format_valid: bool
    transcription_success: bool
    transcription_length: int
    entity_extraction_count: int
    processing_time: float
    error_message: Optional[str]
    quality_score: float  # 0.0 to 1.0


@dataclass
class ValidationReport:
    """Overall validation results for a sampling period"""
    timestamp: str
    total_samples: int
    successful_samples: int
    average_quality_score: float
    transcription_success_rate: float
    entity_extraction_rate: float
    format_success_rate: float
    processing_viability: bool  # Overall assessment
    recommendations: List[str]


class StatisticalSamplingValidator:
    """
    Implements statistical sampling validation for Sherlock processing pipelines
    """

    def __init__(self, sample_size: int = 3, validation_interval: int = 10):
        """
        Initialize validator

        Args:
            sample_size: Number of samples to test per validation cycle
            validation_interval: How often to run validation (every N chunks)
        """
        self.sample_size = sample_size
        self.validation_interval = validation_interval
        self.validation_history = []

        # Quality thresholds
        self.quality_thresholds = {
            "min_transcription_success_rate": 0.6,  # 60% chunks must transcribe
            "min_entity_extraction_rate": 0.3,      # 30% must extract entities
            "min_format_success_rate": 0.8,         # 80% must have valid format
            "min_average_quality_score": 0.5        # Overall quality score
        }

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def validate_processing_pipeline(self, chunks: List[str], processor_class=None) -> ValidationReport:
        """
        Validate processing pipeline using statistical sampling

        Args:
            chunks: List of available chunk paths
            processor_class: Optional processor class to test

        Returns:
            ValidationReport with assessment and recommendations
        """
        self.logger.info(f"🔍 Starting statistical sampling validation")
        self.logger.info(f"📊 Total chunks available: {len(chunks)}")

        # Select random sample
        sample_chunks = self._select_sample_chunks(chunks)
        self.logger.info(f"🎯 Selected {len(sample_chunks)} chunks for validation")

        # Validate each sample
        sample_results = []
        for i, chunk_path in enumerate(sample_chunks):
            self.logger.info(f"📋 Validating sample {i+1}/{len(sample_chunks)}: {chunk_path}")
            result = self._validate_single_sample(chunk_path, f"sample_{i+1}", processor_class)
            sample_results.append(result)

        # Generate validation report
        report = self._generate_validation_report(sample_results)
        self.validation_history.append(report)

        # Log results
        self._log_validation_results(report)

        return report

    def _select_sample_chunks(self, chunks: List[str]) -> List[str]:
        """
        Select representative sample chunks using stratified sampling
        """
        if len(chunks) <= self.sample_size:
            return chunks

        # Stratified sampling: beginning, middle, end + random
        sample_chunks = []

        if len(chunks) >= 3:
            # Always include beginning, middle, end
            sample_chunks.append(chunks[0])                    # Beginning
            sample_chunks.append(chunks[len(chunks) // 2])     # Middle
            sample_chunks.append(chunks[-1])                   # End

            # Fill remaining slots with random samples
            remaining_chunks = [c for c in chunks if c not in sample_chunks]
            remaining_needed = max(0, self.sample_size - 3)

            if remaining_needed > 0 and remaining_chunks:
                additional = random.sample(remaining_chunks,
                                         min(remaining_needed, len(remaining_chunks)))
                sample_chunks.extend(additional)
        else:
            # Too few chunks, take what we can
            sample_chunks = chunks[:self.sample_size]

        return sample_chunks

    def _validate_single_sample(self, chunk_path: str, sample_id: str, processor_class=None) -> SampleValidationResult:
        """
        Validate a single chunk sample through the complete pipeline
        """
        start_time = time.time()
        result = SampleValidationResult(
            sample_id=sample_id,
            chunk_path=chunk_path,
            format_valid=False,
            transcription_success=False,
            transcription_length=0,
            entity_extraction_count=0,
            processing_time=0.0,
            error_message=None,
            quality_score=0.0
        )

        try:
            # 1. Format validation
            result.format_valid = self._validate_audio_format(chunk_path)

            # 2. Transcription validation
            if result.format_valid:
                transcription_result = self._validate_transcription(chunk_path)
                if transcription_result:
                    result.transcription_success = True
                    result.transcription_length = len(transcription_result)

                    # 3. Entity extraction validation
                    if result.transcription_length > 10:  # Minimum viable transcription
                        entities = self._validate_entity_extraction(transcription_result)
                        result.entity_extraction_count = len(entities)

            # Calculate quality score
            result.quality_score = self._calculate_quality_score(result)

        except Exception as e:
            result.error_message = str(e)
            self.logger.warning(f"⚠️ Sample {sample_id} validation error: {e}")

        result.processing_time = time.time() - start_time
        return result

    def _validate_audio_format(self, chunk_path: str) -> bool:
        """
        Validate audio format and basic properties
        """
        try:
            if not os.path.exists(chunk_path):
                return False

            # Check file size (must be > 1KB)
            file_size = os.path.getsize(chunk_path)
            if file_size < 1000:
                return False

            # Use ffprobe to validate format
            result = subprocess.run([
                "ffprobe", "-v", "quiet", "-select_streams", "a:0",
                "-show_entries", "stream=duration,sample_rate",
                "-of", "csv=p=0", chunk_path
            ], capture_output=True, text=True)

            if result.returncode == 0 and result.stdout.strip():
                # Parse duration and sample rate
                output_parts = result.stdout.strip().split(',')
                if len(output_parts) >= 2:
                    duration = float(output_parts[0]) if output_parts[0] else 0
                    sample_rate = int(output_parts[1]) if output_parts[1] else 0

                    # Valid if duration > 0.1s and reasonable sample rate
                    return duration > 0.1 and 8000 <= sample_rate <= 48000

            return False

        except Exception as e:
            self.logger.warning(f"Format validation error for {chunk_path}: {e}")
            return False

    def _validate_transcription(self, chunk_path: str) -> Optional[str]:
        """
        Validate transcription capability using faster-whisper
        """
        try:
            from faster_whisper import WhisperModel

            # Use tiny model for quick validation
            model = WhisperModel('tiny', device='cpu')
            segments, info = model.transcribe(chunk_path)

            # Collect transcription text
            transcription_parts = []
            for segment in segments:
                if segment.text.strip():
                    transcription_parts.append(segment.text.strip())

            transcription = ' '.join(transcription_parts)

            # Return transcription if it contains actual content
            if len(transcription) > 5 and not all(c in ' .,!?' for c in transcription):
                return transcription

            return None

        except Exception as e:
            self.logger.warning(f"Transcription validation error for {chunk_path}: {e}")
            return None

    def _validate_entity_extraction(self, transcription: str) -> List[str]:
        """
        Validate entity extraction capability
        """
        import re

        entities = []

        # Test patterns from Operation Gladio
        people_patterns = [
            r'([A-Z][a-z]+ [A-Z][a-z]+)',  # First Last
            r'(General [A-Z][a-z]+)',
            r'(Colonel [A-Z][a-z]+)',
            r'(Cardinal [A-Z][a-z]+)',
            r'(Pope [A-Z][a-z]+ [IVX]+)',
        ]

        org_patterns = [
            r'(CIA)', r'(Vatican)', r'(Mafia)', r'(P-2|P2)',
            r'(Knights of Malta)', r'(Opus Dei)', r'(NATO)'
        ]

        # Extract people
        for pattern in people_patterns:
            matches = re.findall(pattern, transcription)
            entities.extend(matches)

        # Extract organizations
        for pattern in org_patterns:
            matches = re.findall(pattern, transcription, re.IGNORECASE)
            entities.extend(matches)

        return list(set(entities))  # Remove duplicates

    def _calculate_quality_score(self, result: SampleValidationResult) -> float:
        """
        Calculate overall quality score for a sample (0.0 to 1.0)
        """
        score = 0.0

        # Format validation (25%)
        if result.format_valid:
            score += 0.25

        # Transcription success (35%)
        if result.transcription_success:
            score += 0.35

            # Bonus for longer transcriptions (within reason)
            if result.transcription_length > 50:
                score += 0.1

        # Entity extraction (25%)
        if result.entity_extraction_count > 0:
            score += 0.15

            # Bonus for multiple entities
            if result.entity_extraction_count >= 3:
                score += 0.1

        # Processing efficiency (15%)
        if result.processing_time < 30:  # Under 30 seconds
            score += 0.15
        elif result.processing_time < 60:  # Under 1 minute
            score += 0.1

        return min(1.0, score)

    def _generate_validation_report(self, sample_results: List[SampleValidationResult]) -> ValidationReport:
        """
        Generate comprehensive validation report
        """
        total_samples = len(sample_results)
        successful_samples = sum(1 for r in sample_results if r.quality_score > 0.5)

        # Calculate metrics
        transcription_success_rate = sum(1 for r in sample_results if r.transcription_success) / total_samples
        entity_extraction_rate = sum(1 for r in sample_results if r.entity_extraction_count > 0) / total_samples
        format_success_rate = sum(1 for r in sample_results if r.format_valid) / total_samples
        average_quality_score = sum(r.quality_score for r in sample_results) / total_samples

        # Determine processing viability
        processing_viability = (
            transcription_success_rate >= self.quality_thresholds["min_transcription_success_rate"] and
            entity_extraction_rate >= self.quality_thresholds["min_entity_extraction_rate"] and
            format_success_rate >= self.quality_thresholds["min_format_success_rate"] and
            average_quality_score >= self.quality_thresholds["min_average_quality_score"]
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            transcription_success_rate, entity_extraction_rate,
            format_success_rate, average_quality_score
        )

        return ValidationReport(
            timestamp=datetime.now().isoformat(),
            total_samples=total_samples,
            successful_samples=successful_samples,
            average_quality_score=average_quality_score,
            transcription_success_rate=transcription_success_rate,
            entity_extraction_rate=entity_extraction_rate,
            format_success_rate=format_success_rate,
            processing_viability=processing_viability,
            recommendations=recommendations
        )

    def _generate_recommendations(self, trans_rate: float, entity_rate: float,
                                format_rate: float, quality_score: float) -> List[str]:
        """
        Generate actionable recommendations based on validation results
        """
        recommendations = []

        if format_rate < self.quality_thresholds["min_format_success_rate"]:
            recommendations.append(f"❌ Format validation failing ({format_rate:.1%}). Check audio conversion pipeline.")

        if trans_rate < self.quality_thresholds["min_transcription_success_rate"]:
            recommendations.append(f"❌ Transcription rate low ({trans_rate:.1%}). Consider different model or parameters.")

        if entity_rate < self.quality_thresholds["min_entity_extraction_rate"]:
            recommendations.append(f"⚠️ Entity extraction rate low ({entity_rate:.1%}). Review extraction patterns.")

        if quality_score < self.quality_thresholds["min_average_quality_score"]:
            recommendations.append(f"⚠️ Average quality below threshold ({quality_score:.1%}). Review entire pipeline.")

        if not recommendations:
            recommendations.append("✅ All quality metrics within acceptable thresholds.")

        return recommendations

    def _log_validation_results(self, report: ValidationReport):
        """
        Log validation results with clear assessment
        """
        self.logger.info("=" * 60)
        self.logger.info("📊 STATISTICAL SAMPLING VALIDATION RESULTS")
        self.logger.info("=" * 60)
        self.logger.info(f"📈 Samples Tested: {report.total_samples}")
        self.logger.info(f"✅ Successful Samples: {report.successful_samples}")
        self.logger.info(f"🎯 Quality Score: {report.average_quality_score:.1%}")
        self.logger.info(f"📝 Transcription Rate: {report.transcription_success_rate:.1%}")
        self.logger.info(f"🔍 Entity Extraction Rate: {report.entity_extraction_rate:.1%}")
        self.logger.info(f"📁 Format Success Rate: {report.format_success_rate:.1%}")

        viability_status = "✅ VIABLE" if report.processing_viability else "❌ NOT VIABLE"
        self.logger.info(f"⚖️ Processing Viability: {viability_status}")

        self.logger.info("💡 Recommendations:")
        for rec in report.recommendations:
            self.logger.info(f"   {rec}")
        self.logger.info("=" * 60)

    def save_validation_report(self, report: ValidationReport, filename: str = "validation_report.json"):
        """
        Save validation report to file
        """
        report_data = {
            "timestamp": report.timestamp,
            "metrics": {
                "total_samples": report.total_samples,
                "successful_samples": report.successful_samples,
                "average_quality_score": report.average_quality_score,
                "transcription_success_rate": report.transcription_success_rate,
                "entity_extraction_rate": report.entity_extraction_rate,
                "format_success_rate": report.format_success_rate,
                "processing_viability": report.processing_viability
            },
            "recommendations": report.recommendations,
            "quality_thresholds": self.quality_thresholds
        }

        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)

        self.logger.info(f"💾 Validation report saved: {filename}")


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) < 2:
        print("Usage: python3 statistical_sampling_validator.py <chunks_directory>")
        sys.exit(1)

    chunks_dir = sys.argv[1]
    chunks = [str(p) for p in Path(chunks_dir).glob("*.wav")]

    if not chunks:
        print(f"No WAV files found in {chunks_dir}")
        sys.exit(1)

    validator = StatisticalSamplingValidator(sample_size=3)
    report = validator.validate_processing_pipeline(chunks)
    validator.save_validation_report(report)