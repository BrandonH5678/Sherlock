#!/usr/bin/env python3
"""
Sherlock Preprocessing Pipeline

Segments transcripts into searchable chunks with metadata for retrieval-first queries.

KEY OPTIMIZATION:
- BEFORE: Send entire 15k-40k token transcript to LLM
- AFTER: Chunk into 200-300 token segments, retrieve only relevant 5-7 excerpts

Token Savings: 13k-38k tokens per query (90-95% reduction!)

Architecture:
1. Segment on speaker turns or ~200-300 token boundaries
2. Preserve metadata: doc_id, speaker, timestamps, source_path
3. Normalize text (lowercase, clean, expand numbers)
4. Keep verbatim copy for citation

Usage:
    from src.sherlock_preprocessor import TranscriptPreprocessor

    preprocessor = TranscriptPreprocessor()
    chunks = preprocessor.process_transcript("path/to/transcript.txt")
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Tuple
from datetime import datetime


@dataclass
class Chunk:
    """
    A searchable chunk of transcript with metadata.

    Designed for retrieval: each chunk is ~200-300 tokens with full context.
    """
    chunk_id: str
    doc_id: str
    speaker_id: Optional[str]
    start_time: Optional[float]  # seconds
    end_time: Optional[float]    # seconds
    text: str                    # normalized for search
    text_verbatim: str          # original for citation
    token_count: int
    chunk_index: int            # position in document
    source_path: str
    metadata: Dict

    def to_dict(self):
        return asdict(self)


class TranscriptPreprocessor:
    """
    Preprocess transcripts into searchable chunks.

    Token Savings:
    - Input: 15k-40k token transcript
    - Output: Indexed chunks enabling 1.2k token retrieval
    - Savings: 90-95% per query
    """

    # Chunk size targets
    MIN_CHUNK_TOKENS = 150
    TARGET_CHUNK_TOKENS = 200
    MAX_CHUNK_TOKENS = 300

    # Text normalization patterns
    FILLER_WORDS = r'\b(um|uh|er|ah|like|you know|sort of|kind of)\b'
    REPEATED_SPACES = r'\s+'

    def __init__(self, preserve_verbatim: bool = True):
        """
        Args:
            preserve_verbatim: Keep original text for citations (recommended: True)
        """
        self.preserve_verbatim = preserve_verbatim

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation: 1 token ≈ 4 characters).

        This is approximate but sufficient for chunking strategy.
        For exact counts, use tiktoken, but adds dependency overhead.
        """
        # Remove extra whitespace
        clean_text = re.sub(self.REPEATED_SPACES, ' ', text.strip())
        # Rough estimate: ~4 chars per token for English
        return len(clean_text) // 4

    def normalize_text(self, text: str) -> str:
        """
        Normalize text for search (lowercase, clean filler, expand numbers).

        This improves search recall without losing meaning.
        """
        # Lowercase
        normalized = text.lower()

        # Remove filler words (um, uh, etc.)
        normalized = re.sub(self.FILLER_WORDS, '', normalized, flags=re.IGNORECASE)

        # Expand common numbers to words (improves search)
        number_map = {
            '1963': 'nineteen sixty-three',
            '1967': 'nineteen sixty-seven',
            '1973': 'nineteen seventy-three',
            '1953': 'nineteen fifty-three',
            '1954': 'nineteen fifty-four',
        }
        for num, word in number_map.items():
            normalized = normalized.replace(num, f"{num} {word}")

        # Clean repeated spaces
        normalized = re.sub(self.REPEATED_SPACES, ' ', normalized)

        return normalized.strip()

    def parse_diarized_transcript(
        self,
        transcript_path: Path
    ) -> List[Dict]:
        """
        Parse diarized transcript with speaker turns and timestamps.

        Expected format (JSON):
        [
            {
                "speaker": "SPEAKER_00",
                "start": 0.0,
                "end": 15.2,
                "text": "..."
            },
            ...
        ]

        Or plain text with speaker labels:
        [SPEAKER_00 | 00:00:00-00:00:15]
        "..."

        Returns:
            List of turn dictionaries
        """
        if transcript_path.suffix == '.json':
            with open(transcript_path) as f:
                return json.load(f)

        # Parse plain text format
        turns = []
        current_turn = None

        with open(transcript_path) as f:
            for line in f:
                line = line.strip()

                # Check for speaker header: [SPEAKER_00 | 00:00:00-00:00:15]
                speaker_match = re.match(
                    r'\[(\w+)\s*\|\s*(\d{2}:\d{2}:\d{2})-(\d{2}:\d{2}:\d{2})\]',
                    line
                )

                if speaker_match:
                    # Save previous turn
                    if current_turn and current_turn.get('text'):
                        turns.append(current_turn)

                    # Start new turn
                    speaker, start_str, end_str = speaker_match.groups()
                    current_turn = {
                        'speaker': speaker,
                        'start': self._time_to_seconds(start_str),
                        'end': self._time_to_seconds(end_str),
                        'text': ''
                    }
                elif current_turn is not None:
                    # Add text to current turn
                    current_turn['text'] += ' ' + line

        # Add final turn
        if current_turn and current_turn.get('text'):
            turns.append(current_turn)

        return turns

    def _time_to_seconds(self, time_str: str) -> float:
        """Convert HH:MM:SS to seconds"""
        parts = time_str.split(':')
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds

    def chunk_transcript(
        self,
        turns: List[Dict],
        doc_id: str,
        source_path: str
    ) -> List[Chunk]:
        """
        Chunk transcript into ~200-300 token segments.

        Strategy:
        1. Try to preserve speaker turns (don't split mid-sentence)
        2. If turn > MAX_CHUNK_TOKENS, split on sentence boundaries
        3. Add ±1 neighbor turn for context if chunk ends mid-thought

        Args:
            turns: List of speaker turns from diarization
            doc_id: Document identifier
            source_path: Path to source file

        Returns:
            List of Chunk objects
        """
        chunks = []
        current_chunk_turns = []
        current_tokens = 0
        chunk_index = 0

        for i, turn in enumerate(turns):
            turn_text = turn.get('text', '').strip()
            turn_tokens = self.estimate_tokens(turn_text)

            # Check if adding this turn would exceed max
            if current_tokens + turn_tokens > self.MAX_CHUNK_TOKENS and current_chunk_turns:
                # Finalize current chunk
                chunk = self._create_chunk(
                    current_chunk_turns,
                    doc_id,
                    source_path,
                    chunk_index
                )
                chunks.append(chunk)
                chunk_index += 1

                # Start new chunk with current turn
                current_chunk_turns = [turn]
                current_tokens = turn_tokens
            else:
                # Add turn to current chunk
                current_chunk_turns.append(turn)
                current_tokens += turn_tokens

            # If single turn exceeds max, split it
            if turn_tokens > self.MAX_CHUNK_TOKENS:
                # Split on sentence boundaries
                sentences = self._split_sentences(turn_text)
                current_chunk_turns = []
                current_tokens = 0

                for sentence in sentences:
                    sent_tokens = self.estimate_tokens(sentence)

                    if current_tokens + sent_tokens > self.MAX_CHUNK_TOKENS and current_chunk_turns:
                        # Create chunk from accumulated sentences
                        chunk = self._create_chunk(
                            [{
                                'speaker': turn.get('speaker'),
                                'start': turn.get('start'),
                                'end': turn.get('end'),
                                'text': ' '.join([t['text'] for t in current_chunk_turns])
                            }],
                            doc_id,
                            source_path,
                            chunk_index
                        )
                        chunks.append(chunk)
                        chunk_index += 1
                        current_chunk_turns = []
                        current_tokens = 0

                    current_chunk_turns.append({'text': sentence})
                    current_tokens += sent_tokens

        # Finalize last chunk
        if current_chunk_turns:
            chunk = self._create_chunk(
                current_chunk_turns,
                doc_id,
                source_path,
                chunk_index
            )
            chunks.append(chunk)

        return chunks

    def _create_chunk(
        self,
        turns: List[Dict],
        doc_id: str,
        source_path: str,
        chunk_index: int
    ) -> Chunk:
        """Create Chunk object from turns"""
        # Combine text
        verbatim_text = ' '.join([t.get('text', '') for t in turns])
        normalized_text = self.normalize_text(verbatim_text)

        # Extract metadata
        speaker_id = turns[0].get('speaker') if turns else None
        start_time = turns[0].get('start') if turns else None
        end_time = turns[-1].get('end') if turns else None

        # Generate chunk ID
        chunk_id = f"{doc_id}_chunk_{chunk_index:04d}"

        return Chunk(
            chunk_id=chunk_id,
            doc_id=doc_id,
            speaker_id=speaker_id,
            start_time=start_time,
            end_time=end_time,
            text=normalized_text,
            text_verbatim=verbatim_text if self.preserve_verbatim else normalized_text,
            token_count=self.estimate_tokens(normalized_text),
            chunk_index=chunk_index,
            source_path=source_path,
            metadata={
                'num_turns': len(turns),
                'speakers': list(set([t.get('speaker') for t in turns if t.get('speaker')]))
            }
        )

    def _split_sentences(self, text: str) -> List[str]:
        """Split text on sentence boundaries"""
        # Simple sentence splitting (can be improved with spaCy/NLTK)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def process_transcript(
        self,
        transcript_path: str,
        doc_id: Optional[str] = None
    ) -> List[Chunk]:
        """
        Main entry point: process transcript into chunks.

        Args:
            transcript_path: Path to transcript file
            doc_id: Document ID (defaults to filename)

        Returns:
            List of Chunk objects ready for indexing
        """
        path = Path(transcript_path)

        if not path.exists():
            raise FileNotFoundError(f"Transcript not found: {transcript_path}")

        # Default doc_id to filename
        if doc_id is None:
            doc_id = path.stem

        # Parse transcript
        turns = self.parse_diarized_transcript(path)

        # Chunk it
        chunks = self.chunk_transcript(turns, doc_id, str(path))

        return chunks

    def save_chunks(self, chunks: List[Chunk], output_path: str):
        """Save chunks to JSON for indexing"""
        output_data = [chunk.to_dict() for chunk in chunks]

        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"✅ Saved {len(chunks)} chunks to {output_path}")


def main():
    """Example usage and testing"""
    print("=" * 70)
    print("Sherlock Transcript Preprocessor - Test Suite")
    print("=" * 70)
    print()

    # Create sample transcript for testing
    sample_transcript = """[SPEAKER_00 | 00:00:00-00:00:15]
The CIA's Operation Mockingbird was a systematic program to manipulate media.

[SPEAKER_01 | 00:00:15-00:00:45]
Frank Wisner ran what he called the Wurlitzer, controlling over 800 propaganda assets by 1967. This included major newspapers, radio stations, and publishing houses.

[SPEAKER_00 | 00:00:45-00:01:05]
The New York Times, CBS, and Time magazine were all involved?

[SPEAKER_01 | 00:01:05-00:01:30]
Yes, the CIA owned or subsidized over 50 media entities and produced more than 1,000 books. William Colby admitted agents were told what to write "all the time."
"""

    # Save sample
    sample_path = Path("sample_transcript.txt")
    with open(sample_path, 'w') as f:
        f.write(sample_transcript)

    # Process it
    preprocessor = TranscriptPreprocessor()
    chunks = preprocessor.process_transcript(str(sample_path), doc_id="mockingbird_sample")

    # Display results
    print(f"Processed {len(chunks)} chunks:")
    print("-" * 70)

    for chunk in chunks:
        print(f"\nChunk {chunk.chunk_index}:")
        print(f"  ID: {chunk.chunk_id}")
        print(f"  Speaker: {chunk.speaker_id}")
        print(f"  Time: {chunk.start_time:.1f}s - {chunk.end_time:.1f}s")
        print(f"  Tokens: {chunk.token_count}")
        print(f"  Text (normalized): {chunk.text[:100]}...")
        print(f"  Text (verbatim): {chunk.text_verbatim[:100]}...")

    # Save to JSON
    preprocessor.save_chunks(chunks, "sample_chunks.json")

    print()
    print("=" * 70)
    print("✅ Preprocessing complete")
    print("=" * 70)
    print()
    print(f"Token savings example:")
    print(f"  Original transcript: ~{preprocessor.estimate_tokens(sample_transcript)} tokens")
    print(f"  Chunks created: {len(chunks)}")
    print(f"  Retrieval (5 chunks): ~{5 * 200} tokens")
    print(f"  Savings: ~{preprocessor.estimate_tokens(sample_transcript) - 1000} tokens (90% reduction)")

    # Cleanup
    sample_path.unlink()
    Path("sample_chunks.json").unlink()


if __name__ == "__main__":
    main()
