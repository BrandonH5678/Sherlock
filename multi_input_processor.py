#!/usr/bin/env python3
"""
Multi-Input Processing Pipeline for Squirt
Handles voice memos, paper worksheets (OCR), SMS messages, and manual entry
"""

import json
import re
import sys
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from squirt_voice_interface import SquirtVoiceInterface


class InputType(Enum):
    VOICE_MEMO = "voice_memo"
    PAPER_WORKSHEET = "paper_worksheet"
    SMS_MESSAGE = "sms_message"
    MANUAL_ENTRY = "manual_entry"


@dataclass
class ProcessingResult:
    """Result from input processing"""
    input_type: InputType
    success: bool
    extracted_data: Dict
    confidence: float
    processing_time: float
    original_input: str
    errors: List[str] = None
    requires_review: bool = False


class MultiInputProcessor:
    """Unified processor for all Squirt input types"""

    def __init__(self):
        self.voice_interface = SquirtVoiceInterface()

    def process_voice_memo(self,
                          audio_file: str,
                          mode: str = "fast",
                          employee_name: Optional[str] = None,
                          project_context: Optional[str] = None) -> ProcessingResult:
        """Process voice memo to structured data"""
        start_time = time.time()

        try:
            # Use existing voice interface
            voice_result = self.voice_interface.process_voice_memo(
                audio_file=audio_file,
                mode=mode,
                employee_name=employee_name,
                project_context=project_context
            )

            # Extract structured data from transcription
            extracted_data = self._extract_data_from_text(
                voice_result["transcription"]["text"],
                input_context="voice_memo"
            )

            # Add voice-specific metadata
            extracted_data.update({
                "transcription_confidence": voice_result["transcription"]["confidence"],
                "model_used": voice_result["transcription"]["model"],
                "employee_name": employee_name,
                "project_context": project_context
            })

            # Determine if review is needed based on confidence
            requires_review = (
                voice_result["transcription"]["confidence"] < 0.8 or
                extracted_data.get("extraction_confidence", 0) < 0.7
            )

            return ProcessingResult(
                input_type=InputType.VOICE_MEMO,
                success=True,
                extracted_data=extracted_data,
                confidence=voice_result["transcription"]["confidence"],
                processing_time=time.time() - start_time,
                original_input=audio_file,
                requires_review=requires_review
            )

        except Exception as e:
            return ProcessingResult(
                input_type=InputType.VOICE_MEMO,
                success=False,
                extracted_data={},
                confidence=0.0,
                processing_time=time.time() - start_time,
                original_input=audio_file,
                errors=[str(e)],
                requires_review=True
            )

    def process_paper_worksheet(self, image_file: str, employee_name: Optional[str] = None) -> ProcessingResult:
        """Process paper worksheet image using OCR to structured data"""
        start_time = time.time()

        try:
            # Note: This is a placeholder for OCR processing
            # In production, this would use Claude Vision API or similar OCR

            print(f"📸 Processing paper worksheet: {Path(image_file).name}")
            print("🔍 OCR extraction in progress...")

            # Simulate OCR processing
            time.sleep(2)

            # Placeholder extracted text (in production, this would come from OCR)
            # For now, we'll return a template structure
            ocr_text = f"[OCR would extract text from {image_file}]"

            extracted_data = self._extract_data_from_text(ocr_text, input_context="paper_worksheet")

            # Add OCR-specific metadata
            extracted_data.update({
                "image_file": image_file,
                "employee_name": employee_name,
                "ocr_method": "placeholder_ocr",  # Would be actual OCR method
                "needs_ocr_implementation": True
            })

            # Paper worksheets always need review due to OCR uncertainty
            requires_review = True

            return ProcessingResult(
                input_type=InputType.PAPER_WORKSHEET,
                success=True,
                extracted_data=extracted_data,
                confidence=0.6,  # Lower confidence for OCR
                processing_time=time.time() - start_time,
                original_input=image_file,
                requires_review=requires_review
            )

        except Exception as e:
            return ProcessingResult(
                input_type=InputType.PAPER_WORKSHEET,
                success=False,
                extracted_data={},
                confidence=0.0,
                processing_time=time.time() - start_time,
                original_input=image_file,
                errors=[str(e)],
                requires_review=True
            )

    def process_sms_message(self, sms_text: str, employee_name: Optional[str] = None) -> ProcessingResult:
        """Process SMS message to structured data"""
        start_time = time.time()

        try:
            print(f"📱 Processing SMS message...")
            print(f"📄 Content: {sms_text[:100]}...")

            # Extract structured data from SMS text
            extracted_data = self._extract_data_from_text(sms_text, input_context="sms_message")

            # Add SMS-specific metadata
            extracted_data.update({
                "employee_name": employee_name,
                "input_method": "sms",
                "character_length": len(sms_text)
            })

            # SMS needs review if it's unclear or very short
            requires_review = (
                len(sms_text.strip()) < 50 or
                extracted_data.get("extraction_confidence", 0) < 0.8
            )

            return ProcessingResult(
                input_type=InputType.SMS_MESSAGE,
                success=True,
                extracted_data=extracted_data,
                confidence=0.85,  # Good confidence for direct text
                processing_time=time.time() - start_time,
                original_input=sms_text,
                requires_review=requires_review
            )

        except Exception as e:
            return ProcessingResult(
                input_type=InputType.SMS_MESSAGE,
                success=False,
                extracted_data={},
                confidence=0.0,
                processing_time=time.time() - start_time,
                original_input=sms_text,
                errors=[str(e)],
                requires_review=True
            )

    def process_manual_entry(self, data: Dict, employee_name: Optional[str] = None) -> ProcessingResult:
        """Process manual JSON entry (baseline method)"""
        start_time = time.time()

        try:
            print(f"⌨️  Processing manual entry...")

            # Manual entry is already structured - just validate and pass through
            extracted_data = data.copy()
            extracted_data.update({
                "employee_name": employee_name,
                "input_method": "manual_entry",
                "validated": True
            })

            # Manual entry rarely needs review unless incomplete
            requires_review = self._check_data_completeness(extracted_data) < 0.9

            return ProcessingResult(
                input_type=InputType.MANUAL_ENTRY,
                success=True,
                extracted_data=extracted_data,
                confidence=1.0,  # Highest confidence for manual entry
                processing_time=time.time() - start_time,
                original_input=json.dumps(data),
                requires_review=requires_review
            )

        except Exception as e:
            return ProcessingResult(
                input_type=InputType.MANUAL_ENTRY,
                success=False,
                extracted_data={},
                confidence=0.0,
                processing_time=time.time() - start_time,
                original_input=json.dumps(data) if isinstance(data, dict) else str(data),
                errors=[str(e)],
                requires_review=True
            )

    def _extract_data_from_text(self, text: str, input_context: str) -> Dict:
        """Extract structured data from text using pattern matching and NLP"""

        extracted = {
            "raw_text": text,
            "input_context": input_context,
            "extracted_at": datetime.now().isoformat(),
            "extraction_confidence": 0.5  # Default confidence
        }

        # Common patterns for WaterWizard data extraction
        patterns = {
            "client_name": [
                r"client\s*:?\s*([A-Za-z\s]+)",
                r"customer\s*:?\s*([A-Za-z\s]+)",
                r"for\s+([A-Za-z\s]+)'s?\s+property",
                r"([A-Za-z\s]+)\s+needs",
            ],
            "phone_number": [
                r"(\d{3}[-.]?\d{3}[-.]?\d{4})",
                r"phone\s*:?\s*(\d{3}[-.]?\d{3}[-.]?\d{4})",
                r"call\s+(\d{3}[-.]?\d{3}[-.]?\d{4})",
            ],
            "address": [
                r"(\d+\s+[A-Za-z\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|way|circle|cir))",
                r"address\s*:?\s*(.+?)(?:\n|$)",
                r"location\s*:?\s*(.+?)(?:\n|$)",
            ],
            "service_type": [
                r"(irrigation|sprinkler|valve|repair|install|maintenance|winterize)",
                r"service\s*:?\s*([A-Za-z\s]+)",
                r"needs?\s+([A-Za-z\s]+)",
            ],
            "amount": [
                r"\$(\d+(?:\.\d{2})?)",
                r"(\d+)\s*dollars?",
                r"cost\s*:?\s*\$?(\d+(?:\.\d{2})?)",
            ],
            "urgency": [
                r"(urgent|emergency|asap|today|tomorrow)",
                r"by\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
            ]
        }

        # Extract using patterns
        confidence_scores = []

        for field, field_patterns in patterns.items():
            for pattern in field_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    extracted[field] = match.group(1).strip()
                    confidence_scores.append(0.8)  # Good pattern match
                    break

        # Calculate overall extraction confidence
        if confidence_scores:
            extracted["extraction_confidence"] = sum(confidence_scores) / len(confidence_scores)
        else:
            extracted["extraction_confidence"] = 0.3  # Low confidence if no patterns matched

        # Add service-specific extraction based on context
        if input_context == "voice_memo":
            extracted.update(self._extract_voice_specific_data(text))
        elif input_context == "sms_message":
            extracted.update(self._extract_sms_specific_data(text))

        return extracted

    def _extract_voice_specific_data(self, text: str) -> Dict:
        """Extract data specific to voice memos"""
        voice_data = {}

        # Voice memos often contain more context and rambling
        if "estimate" in text.lower() or "quote" in text.lower():
            voice_data["document_type"] = "estimate"
        elif "invoice" in text.lower() or "bill" in text.lower():
            voice_data["document_type"] = "invoice"
        elif "repair" in text.lower() or "fix" in text.lower():
            voice_data["document_type"] = "service_call"
        else:
            voice_data["document_type"] = "general"

        # Extract time references
        time_patterns = [
            r"(today|tomorrow|next week|this week)",
            r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
            r"(\d{1,2}:\d{2})"
        ]

        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                voice_data["time_reference"] = match.group(1)
                break

        return voice_data

    def _extract_sms_specific_data(self, text: str) -> Dict:
        """Extract data specific to SMS messages"""
        sms_data = {}

        # SMS messages are usually brief and urgent
        if len(text) < 100:
            sms_data["message_type"] = "brief"
        else:
            sms_data["message_type"] = "detailed"

        # Check for urgency indicators
        urgency_words = ["urgent", "emergency", "asap", "now", "today"]
        if any(word in text.lower() for word in urgency_words):
            sms_data["priority"] = "high"
        else:
            sms_data["priority"] = "normal"

        return sms_data

    def _check_data_completeness(self, data: Dict) -> float:
        """Check how complete the extracted data is"""
        required_fields = ["client_name", "service_type"]
        optional_fields = ["phone_number", "address", "amount"]

        required_score = sum(1 for field in required_fields if data.get(field)) / len(required_fields)
        optional_score = sum(1 for field in optional_fields if data.get(field)) / len(optional_fields)

        # Weight required fields more heavily
        return (required_score * 0.7) + (optional_score * 0.3)

    def create_unified_output(self, processing_result: ProcessingResult) -> Dict:
        """Create unified JSON output for Squirt document generation"""

        # Base structure for Squirt integration
        unified_output = {
            "input_metadata": {
                "input_type": processing_result.input_type.value,
                "processing_success": processing_result.success,
                "confidence": processing_result.confidence,
                "processing_time": processing_result.processing_time,
                "timestamp": datetime.now().isoformat(),
                "requires_human_review": processing_result.requires_review
            },
            "extracted_data": processing_result.extracted_data,
            "squirt_ready": processing_result.success and not processing_result.requires_review,
            "review_flags": []
        }

        # Add review flags based on confidence and completeness
        if processing_result.confidence < 0.8:
            unified_output["review_flags"].append("Low transcription confidence")

        if processing_result.extracted_data.get("extraction_confidence", 0) < 0.7:
            unified_output["review_flags"].append("Low data extraction confidence")

        completeness = self._check_data_completeness(processing_result.extracted_data)
        if completeness < 0.7:
            unified_output["review_flags"].append("Incomplete data extraction")

        if processing_result.errors:
            unified_output["review_flags"].extend(processing_result.errors)

        # Format for Squirt template system
        if processing_result.success:
            unified_output["squirt_template_data"] = self._format_for_squirt_templates(
                processing_result.extracted_data
            )

        return unified_output

    def _format_for_squirt_templates(self, extracted_data: Dict) -> Dict:
        """Format extracted data for Squirt's JSON template system"""

        template_data = {
            "client": {
                "name": extracted_data.get("client_name", ""),
                "phone": extracted_data.get("phone_number", ""),
                "address": extracted_data.get("address", "")
            },
            "services": [
                {
                    "description": extracted_data.get("service_type", ""),
                    "amount": self._parse_amount(extracted_data.get("amount", "0")),
                    "quantity": 1
                }
            ],
            "document_type": extracted_data.get("document_type", "service_call"),
            "priority": extracted_data.get("priority", "normal"),
            "notes": extracted_data.get("raw_text", "")[:500],  # Limit notes length
            "input_method": extracted_data.get("input_method", "multi_input"),
            "employee": extracted_data.get("employee_name", "")
        }

        return template_data

    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float"""
        if not amount_str:
            return 0.0

        # Remove non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', str(amount_str))

        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0


def main():
    """CLI interface for multi-input processing"""
    if len(sys.argv) < 3:
        print("Multi-Input Processor for Squirt")
        print("Usage:")
        print("  python multi_input_processor.py voice <audio_file> [--mode fast|accurate]")
        print("  python multi_input_processor.py paper <image_file>")
        print("  python multi_input_processor.py sms \"<message_text>\"")
        print("  python multi_input_processor.py manual '<json_data>'")
        sys.exit(1)

    processor = MultiInputProcessor()
    input_type = sys.argv[1].lower()
    input_data = sys.argv[2]

    try:
        if input_type == "voice":
            mode = "fast"
            if len(sys.argv) > 3 and sys.argv[3] == "--mode" and len(sys.argv) > 4:
                mode = sys.argv[4]

            result = processor.process_voice_memo(input_data, mode=mode)

        elif input_type == "paper":
            result = processor.process_paper_worksheet(input_data)

        elif input_type == "sms":
            result = processor.process_sms_message(input_data)

        elif input_type == "manual":
            data = json.loads(input_data)
            result = processor.process_manual_entry(data)

        else:
            print(f"❌ Unknown input type: {input_type}")
            sys.exit(1)

        # Create unified output
        unified_output = processor.create_unified_output(result)

        print("\n" + "=" * 50)
        print("📊 PROCESSING RESULT")
        print("=" * 50)
        print(json.dumps(unified_output, indent=2))

        # Save result
        timestamp = int(time.time())
        output_file = f"multi_input_result_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump(unified_output, f, indent=2)

        print(f"\n💾 Result saved: {output_file}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()