#!/usr/bin/env python3
"""
Human-in-the-Loop Review System for Squirt
Interactive interface for reviewing and correcting AI-extracted data
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from multi_input_processor import MultiInputProcessor, ProcessingResult, InputType


@dataclass
class ReviewCorrection:
    """Individual correction made during review"""
    field: str
    original_value: str
    corrected_value: str
    correction_type: str  # "add", "modify", "delete"
    confidence_impact: float  # How much this affects confidence in similar cases


@dataclass
class ReviewSession:
    """Complete review session with corrections and metadata"""
    session_id: str
    processing_result: ProcessingResult
    corrections: List[ReviewCorrection]
    final_data: Dict
    review_time: float
    reviewer_name: Optional[str]
    approved: bool
    learning_data: Dict


class HumanReviewSystem:
    """Interactive review system with learning capabilities"""

    def __init__(self):
        self.learning_database = Path("learning_data.json")
        self.review_history = Path("review_history.json")
        self.common_corrections = self._load_learning_data()

    def review_processing_result(self,
                               processing_result: ProcessingResult,
                               reviewer_name: Optional[str] = None) -> ReviewSession:
        """Interactive review of processing result with correction interface"""

        print("\n" + "=" * 60)
        print("👥 HUMAN REVIEW INTERFACE")
        print("=" * 60)

        session_id = f"review_{int(time.time())}"
        start_time = time.time()
        corrections = []

        # Display original input and processing summary
        self._display_processing_summary(processing_result)

        # Interactive review interface
        final_data = processing_result.extracted_data.copy()

        print(f"\n📝 EXTRACTED DATA REVIEW")
        print("=" * 40)

        # Review each extracted field
        for field, value in processing_result.extracted_data.items():
            if field in ["raw_text", "extraction_confidence", "extracted_at"]:
                continue  # Skip metadata fields

            corrected_value, correction_type = self._review_field(
                field, value, processing_result.input_type
            )

            if corrected_value != value:
                corrections.append(ReviewCorrection(
                    field=field,
                    original_value=str(value),
                    corrected_value=str(corrected_value),
                    correction_type=correction_type,
                    confidence_impact=self._calculate_confidence_impact(field, value, corrected_value)
                ))
                final_data[field] = corrected_value

        # Check for missing fields
        final_data = self._check_missing_fields(final_data, processing_result.input_type)

        # Final approval
        approved = self._get_final_approval(final_data)

        # Create review session
        review_session = ReviewSession(
            session_id=session_id,
            processing_result=processing_result,
            corrections=corrections,
            final_data=final_data,
            review_time=time.time() - start_time,
            reviewer_name=reviewer_name,
            approved=approved,
            learning_data=self._generate_learning_data(processing_result, corrections)
        )

        # Update learning system
        self._update_learning_system(review_session)

        # Save review history
        self._save_review_session(review_session)

        return review_session

    def _display_processing_summary(self, result: ProcessingResult):
        """Display summary of processing result"""
        print(f"📊 Input Type: {result.input_type.value}")
        print(f"⚡ Processing: {result.processing_time:.1f}s")
        print(f"📈 Confidence: {result.confidence:.1%}")
        print(f"🔍 Review Required: {'YES' if result.requires_review else 'NO'}")

        if result.errors:
            print(f"⚠️  Errors: {', '.join(result.errors)}")

        print(f"📄 Original Input: {result.original_input[:100]}...")

    def _review_field(self, field: str, value: str, input_type: InputType) -> Tuple[str, str]:
        """Review individual field with correction interface"""

        print(f"\n🔍 Reviewing: {field}")
        print(f"📄 Current value: {value}")

        # Show suggestions based on learning data
        suggestions = self._get_field_suggestions(field, value, input_type)
        if suggestions:
            print(f"💡 Suggestions: {', '.join(suggestions[:3])}")

        # Get user input
        while True:
            action = input(f"Action for '{field}' ([k]eep, [m]odify, [d]elete, [a]dd if empty): ").lower().strip()

            if action in ['k', 'keep', '']:
                return value, "keep"

            elif action in ['m', 'modify']:
                new_value = input(f"New value for '{field}': ").strip()
                return new_value, "modify"

            elif action in ['d', 'delete']:
                confirm = input(f"Delete '{field}'? (y/N): ").lower().strip()
                if confirm == 'y':
                    return "", "delete"

            elif action in ['a', 'add'] and not value:
                new_value = input(f"Add value for '{field}': ").strip()
                return new_value, "add"

            else:
                print("❌ Invalid action. Use 'k' (keep), 'm' (modify), 'd' (delete), or 'a' (add)")

    def _check_missing_fields(self, data: Dict, input_type: InputType) -> Dict:
        """Check for and add missing critical fields"""

        critical_fields = {
            InputType.VOICE_MEMO: ["client_name", "service_type"],
            InputType.SMS_MESSAGE: ["client_name", "service_type"],
            InputType.PAPER_WORKSHEET: ["client_name", "service_type"],
            InputType.MANUAL_ENTRY: ["client_name"]
        }

        required_fields = critical_fields.get(input_type, [])
        missing_fields = [field for field in required_fields if not data.get(field)]

        if missing_fields:
            print(f"\n⚠️  Missing critical fields: {', '.join(missing_fields)}")

            for field in missing_fields:
                add_field = input(f"Add '{field}'? (y/N): ").lower().strip()
                if add_field == 'y':
                    value = input(f"Value for '{field}': ").strip()
                    if value:
                        data[field] = value

        return data

    def _get_final_approval(self, final_data: Dict) -> bool:
        """Get final approval for the reviewed data"""

        print(f"\n📋 FINAL REVIEW")
        print("=" * 30)

        for field, value in final_data.items():
            if field not in ["raw_text", "extraction_confidence", "extracted_at"]:
                print(f"  {field}: {value}")

        while True:
            approval = input(f"\n✅ Approve this data for document generation? (y/N): ").lower().strip()

            if approval == 'y':
                return True
            elif approval in ['n', '']:
                return False
            else:
                print("❌ Please enter 'y' for yes or 'n' for no")

    def _get_field_suggestions(self, field: str, current_value: str, input_type: InputType) -> List[str]:
        """Get suggestions for field values based on learning data"""

        suggestions = []

        # Check learning database for common corrections
        if field in self.common_corrections:
            field_corrections = self.common_corrections[field]

            # Find similar values that were corrected
            for original, corrected in field_corrections.items():
                if self._similarity_score(current_value, original) > 0.7:
                    suggestions.append(corrected)

        # Add field-specific suggestions
        if field == "service_type":
            common_services = ["irrigation repair", "sprinkler installation", "valve replacement",
                             "system maintenance", "winterization", "spring startup"]
            suggestions.extend([s for s in common_services if s not in suggestions])

        elif field == "document_type":
            suggestions.extend(["service_call", "estimate", "invoice", "contract"])

        return suggestions[:5]  # Limit to top 5 suggestions

    def _similarity_score(self, str1: str, str2: str) -> float:
        """Calculate simple similarity score between strings"""
        if not str1 or not str2:
            return 0.0

        # Simple character-based similarity
        str1_lower = str1.lower()
        str2_lower = str2.lower()

        common_chars = sum(1 for c in str1_lower if c in str2_lower)
        total_chars = max(len(str1_lower), len(str2_lower))

        return common_chars / total_chars if total_chars > 0 else 0.0

    def _calculate_confidence_impact(self, field: str, original: str, corrected: str) -> float:
        """Calculate how much this correction should impact future confidence"""

        if original == corrected:
            return 0.0

        # More important fields have higher impact
        field_weights = {
            "client_name": 0.9,
            "service_type": 0.8,
            "amount": 0.7,
            "phone_number": 0.6,
            "address": 0.6,
            "document_type": 0.5
        }

        base_impact = field_weights.get(field, 0.3)

        # Larger changes have more impact
        similarity = self._similarity_score(original, corrected)
        change_magnitude = 1.0 - similarity

        return base_impact * change_magnitude

    def _generate_learning_data(self, processing_result: ProcessingResult, corrections: List[ReviewCorrection]) -> Dict:
        """Generate learning data from review session"""

        learning_data = {
            "input_type": processing_result.input_type.value,
            "original_confidence": processing_result.confidence,
            "correction_patterns": {},
            "field_accuracy": {},
            "common_mistakes": []
        }

        # Analyze correction patterns
        for correction in corrections:
            pattern_key = f"{correction.field}_{correction.correction_type}"
            if pattern_key not in learning_data["correction_patterns"]:
                learning_data["correction_patterns"][pattern_key] = []

            learning_data["correction_patterns"][pattern_key].append({
                "original": correction.original_value,
                "corrected": correction.corrected_value,
                "confidence_impact": correction.confidence_impact
            })

        # Calculate field accuracy
        total_fields = len(processing_result.extracted_data)
        corrected_fields = len(corrections)
        learning_data["field_accuracy"]["extraction_accuracy"] = (total_fields - corrected_fields) / total_fields

        # Identify common mistake patterns
        if corrected_fields > 0:
            learning_data["common_mistakes"] = [
                f"{corr.field}: {corr.original_value} → {corr.corrected_value}"
                for corr in corrections[:3]  # Top 3 mistakes
            ]

        return learning_data

    def _update_learning_system(self, review_session: ReviewSession):
        """Update the learning system with new correction data"""

        # Update common corrections database
        for correction in review_session.corrections:
            field = correction.field

            if field not in self.common_corrections:
                self.common_corrections[field] = {}

            self.common_corrections[field][correction.original_value] = correction.corrected_value

        # Save updated learning data
        self._save_learning_data()

    def _load_learning_data(self) -> Dict:
        """Load learning data from file"""
        try:
            if self.learning_database.exists():
                with open(self.learning_database, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load learning data: {e}")

        return {}

    def _save_learning_data(self):
        """Save learning data to file"""
        try:
            with open(self.learning_database, 'w') as f:
                json.dump(self.common_corrections, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save learning data: {e}")

    def _save_review_session(self, review_session: ReviewSession):
        """Save review session to history"""

        try:
            # Load existing history
            history = []
            if self.review_history.exists():
                with open(self.review_history, 'r') as f:
                    history = json.load(f)

            # Add new session (convert dataclass to dict)
            session_dict = asdict(review_session)
            # Convert ProcessingResult to dict manually since it's a complex object
            session_dict['processing_result'] = {
                'input_type': review_session.processing_result.input_type.value,
                'success': review_session.processing_result.success,
                'confidence': review_session.processing_result.confidence,
                'processing_time': review_session.processing_result.processing_time,
                'original_input': review_session.processing_result.original_input,
                'requires_review': review_session.processing_result.requires_review
            }

            history.append(session_dict)

            # Keep only last 100 sessions
            history = history[-100:]

            # Save updated history
            with open(self.review_history, 'w') as f:
                json.dump(history, f, indent=2)

        except Exception as e:
            print(f"Warning: Could not save review session: {e}")

    def get_learning_statistics(self) -> Dict:
        """Get statistics about the learning system"""

        stats = {
            "total_corrections": 0,
            "fields_learned": len(self.common_corrections),
            "accuracy_improvement": 0.0,
            "common_fields": []
        }

        for field, corrections in self.common_corrections.items():
            stats["total_corrections"] += len(corrections)

        stats["common_fields"] = sorted(
            self.common_corrections.keys(),
            key=lambda x: len(self.common_corrections[x]),
            reverse=True
        )[:5]

        return stats

    def batch_review(self, processing_results: List[ProcessingResult], reviewer_name: Optional[str] = None) -> List[ReviewSession]:
        """Review multiple processing results in batch"""

        print(f"🔄 Starting batch review of {len(processing_results)} items...")

        review_sessions = []

        for i, result in enumerate(processing_results, 1):
            print(f"\n📋 Reviewing item {i}/{len(processing_results)}")

            session = self.review_processing_result(result, reviewer_name)
            review_sessions.append(session)

            if not session.approved:
                print(f"⚠️  Item {i} not approved - consider reprocessing")

        print(f"\n✅ Batch review complete: {len(review_sessions)} items reviewed")

        return review_sessions


def main():
    """CLI interface for review system"""

    if len(sys.argv) < 2:
        print("Human Review System for Squirt")
        print("Usage:")
        print("  python human_review_system.py review <processing_result.json>")
        print("  python human_review_system.py stats")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "review":
        if len(sys.argv) < 3:
            print("❌ Processing result file required")
            sys.exit(1)

        result_file = sys.argv[2]

        try:
            # Load processing result (simplified for CLI)
            with open(result_file, 'r') as f:
                result_data = json.load(f)

            print(f"📄 Loaded processing result from {result_file}")

            # Create mock ProcessingResult for demonstration
            # In practice, this would be loaded from the actual result format
            processor = MultiInputProcessor()
            review_system = HumanReviewSystem()

            print("🔍 Starting interactive review...")
            # Note: This is a simplified version for CLI demonstration
            print("✅ Review system ready - integrate with actual processing results")

        except Exception as e:
            print(f"❌ Error loading result file: {e}")
            sys.exit(1)

    elif command == "stats":
        review_system = HumanReviewSystem()
        stats = review_system.get_learning_statistics()

        print("📊 Learning System Statistics")
        print("=" * 30)
        print(f"Total corrections learned: {stats['total_corrections']}")
        print(f"Fields with learning data: {stats['fields_learned']}")
        print(f"Most corrected fields: {', '.join(stats['common_fields'])}")

    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()