#!/usr/bin/env python3
"""
Manual speaker enhancement for Buhler/Exodus Propulsion episode.
Pyannote lumped host (Jesse Michels) and guest (Dr. Buhler) into SPEAKER_02.
This script applies context-based rules to separate them.

Speakers:
  - Dr. Charles Buhler: Primary guest, NASA electrostatics, Exodus Propulsion CEO
  - Jesse Michels: Host (American Alchemy), asks questions, narrates intro
  - David Chester: Second guest, theoretical physicist, enters ~112:10 (1:52:10)
  - SPEAKER_00: Archival audio clips (Townsend Brown references)
  - SPEAKER_01: Elon Musk clips (intro montage only)
"""

import json
import re
from pathlib import Path
from collections import Counter

EPISODE_DIR = Path("/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/buhler_exodus_mOWwdIuyaQA")
INPUT_FILE = EPISODE_DIR / "audio_transcription" / "alignment_audio_enhanced" / "diarization_audio_aligned" / "audio_diarized.json"
OUTPUT_JSON = EPISODE_DIR / "audio_transcription" / "alignment_audio_enhanced" / "diarization_audio_aligned" / "audio_diarized_enhanced.json"
OUTPUT_TXT = EPISODE_DIR / "audio_transcription" / "alignment_audio_enhanced" / "diarization_audio_aligned" / "audio_diarized_enhanced_READABLE.txt"
CORRECTIONS_FILE = EPISODE_DIR / "audio_transcription" / "alignment_audio_enhanced" / "diarization_audio_aligned" / "audio_diarized_enhanced.corrections.json"

with open(INPUT_FILE) as f:
    data = json.load(f)

segments = data["segments"]

# Phase boundaries
INTRO_END = 210       # ~3:30 — intro montage ends, interview begins
CHESTER_ENTRY = 6730  # ~112:10 — David Chester introduced

# Known speaker mappings for non-SPEAKER_02
SPEAKER_MAP = {
    "SPEAKER_00": "Archival Audio",
    "SPEAKER_01": "Elon Musk (clip)",
}

# Question/host indicator patterns
HOST_PATTERNS = [
    # Direct questions
    r"^(So |And |But |Now |How |What |Where |When |Why |Who |Can |Could |Do |Did |Is |Are |Was |Were |Have |Has |Would |Will )",
    r"\?$",
    # Interview transition phrases
    r"^(Tell me|Walk me|Let me|Let's|I want to|I'd love|That's (fascinating|incredible|amazing|interesting|wild|crazy))",
    r"^(For (the |those |people |our |anyone ))",
    r"^(You (mentioned|said|were|have|think|do|did|started|grew|worked|ran|built))",
    # Host self-reference patterns (Jesse's style)
    r"(my (show|channel|audience|podcast|friend|buddy))",
    r"(American Alchemy)",
    r"(our (viewers|audience|listeners))",
    r"(I (brought|invited|asked|wanted to bring|want to bring))",
    # Introducing topics/guests
    r"^(We have|So we have|All right|Alright)",
    r"(David Chester|Chester here)",
    # Reactions (short host interjections)
    r"^(Wow|Holy (shit|cow)|No way|That's insane|Dude|Man|Incredible|Unbelievable|Fascinating)[\.\!]?$",
]

# Buhler content patterns (technical authority, first person experience)
BUHLER_PATTERNS = [
    r"(my (lab|experiments?|team|patent|data|results|approach|thrusters?|company|work))",
    r"(our (experiments?|lab|data|company|thrusters?|results|team|vacuum))",
    r"(I (discovered|found|measured|tested|built|designed|ran|published|showed|demonstrated|patented))",
    r"(at NASA|at Kennedy|Electrostatics Lab|Exodus Propulsion)",
    r"(micronewtons?|vacuum chamber|T-blade|thrust|electrostatic|QED|Casimir|quantum electrodynamics)",
    r"(2,?000 (variations|experiments))",
    r"(Townsend Brown)",
]

# Chester content patterns
CHESTER_PATTERNS = [
    r"(my (thesis|dissertation|research|work at|PhD))",
    r"(at MIT|at UCLA|general relativity|quantum field theory)",
    r"(from a (theoretical|physics|QFT|QED) (perspective|standpoint|point of view))",
]

corrections = []

def classify_segment(seg, idx):
    """Classify a SPEAKER_02 segment as Buhler, Michels, or Chester."""
    text = seg.get("text", "").strip()
    start = seg.get("start", 0)

    # Intro narration (before ~3:30) — this is Jesse's voiceover
    if start < INTRO_END:
        # Short interjections in intro are Buhler interview clips
        # Long narration is Jesse
        if any(kw in text.lower() for kw in ["i've always believed", "two decades", "hidden momentum",
                "2,000", "hurts my brain", "bending space-time", "these are very weird",
                "thrust mode", "i put them in", "lifters", "i take those", "power off",
                "can't explain that", "i just can't", "it does not move"]):
            return "Dr. Charles Buhler"
        if len(text) > 80:
            return "Jesse Michels"
        # Short clips could be either — default to narration context
        return "Jesse Michels"

    # After Chester entry — check for Chester patterns
    if start >= CHESTER_ENTRY:
        for pat in CHESTER_PATTERNS:
            if re.search(pat, text, re.IGNORECASE):
                return "David Chester"

    # Check host patterns
    host_score = 0
    for pat in HOST_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            host_score += 1

    # Check Buhler patterns
    buhler_score = 0
    for pat in BUHLER_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            buhler_score += 1

    # Short acknowledgments ("Yeah", "Right", "Mm-hmm", "Sure") — context dependent
    if len(text) < 15 and text.strip().rstrip('.!?,') in [
        "Yeah", "Right", "Mm-hmm", "Sure", "Exactly", "Okay", "OK",
        "Hmm", "Wow", "Interesting", "Really", "No", "Yes",
        "Clearly", "Obviously", "Absolutely", "Definitely", "True",
        "That's right", "That's correct", "Go ahead"
    ]:
        # If previous segment was a question (host), this acknowledgment is Buhler
        if idx > 0:
            prev = segments[idx-1]
            prev_text = prev.get("text", "").strip()
            if prev_text.endswith("?"):
                return "Dr. Charles Buhler"
            # If previous was long technical content (Buhler), short ack is host
            if len(prev_text) > 60:
                return "Jesse Michels"
        return "Dr. Charles Buhler"  # Default for ambiguous acks

    # Questions are almost always the host
    if text.endswith("?") and host_score > 0:
        return "Jesse Michels"

    # Strong technical content is Buhler
    if buhler_score >= 2:
        return "Dr. Charles Buhler"

    # Host score wins
    if host_score > buhler_score and host_score >= 2:
        return "Jesse Michels"

    # After Chester entry, longer technical segments could be Chester
    if start >= CHESTER_ENTRY and buhler_score == 0 and host_score == 0:
        # Look at surrounding context — if sandwiched between Buhler Q&A, could be Chester
        pass

    # Default: Buhler (he's the primary speaker ~75% of interview)
    return "Dr. Charles Buhler"


# Apply classifications
for i, seg in enumerate(segments):
    original_speaker = seg.get("speaker", "UNKNOWN")

    if original_speaker == "SPEAKER_02":
        new_speaker = classify_segment(seg, i)
        seg["speaker"] = new_speaker
        if new_speaker != "Dr. Charles Buhler":  # Only log non-default
            corrections.append({
                "segment_idx": i,
                "start": seg.get("start", 0),
                "original": original_speaker,
                "assigned": new_speaker,
                "text": seg.get("text", "")[:80],
                "reason": "context_classification"
            })
    elif original_speaker in SPEAKER_MAP:
        seg["speaker"] = SPEAKER_MAP[original_speaker]
        corrections.append({
            "segment_idx": i,
            "start": seg.get("start", 0),
            "original": original_speaker,
            "assigned": SPEAKER_MAP[original_speaker],
            "text": seg.get("text", "")[:80],
            "reason": "known_mapping"
        })
    elif original_speaker == "UNKNOWN":
        # Try to classify unknowns same way
        seg["speaker"] = "UNKNOWN"

# Save enhanced JSON
with open(OUTPUT_JSON, 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# Save corrections audit trail
with open(CORRECTIONS_FILE, 'w') as f:
    json.dump({
        "episode": "buhler_exodus_mOWwdIuyaQA",
        "method": "manual_context_classification",
        "total_corrections": len(corrections),
        "corrections": corrections
    }, f, indent=2)

# Generate READABLE.txt
with open(OUTPUT_TXT, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("TRANSCRIPT: NASA Chief: We Just Built Antigravity Propulsion!\n")
    f.write("GUEST: Dr. Charles Buhler (CEO, Exodus Propulsion Technologies)\n")
    f.write("HOST: Jesse Michels (American Alchemy)\n")
    f.write("SECOND GUEST: David Chester (Theoretical Physicist) — enters at 1:52:10\n")
    f.write(f"SEGMENTS: {len(segments)}\n")
    f.write("=" * 80 + "\n\n")

    current_speaker = None
    for seg in segments:
        speaker = seg.get("speaker", "UNKNOWN")
        start = seg.get("start", 0)
        end = seg.get("end", 0)
        text = seg.get("text", "").strip()

        start_m, start_s = int(start // 60), int(start % 60)
        end_m, end_s = int(end // 60), int(end % 60)

        if speaker != current_speaker:
            f.write(f"\n[{speaker}]\n")
            current_speaker = speaker

        f.write(f"[{start_m:02d}:{start_s:02d} - {end_m:02d}:{end_s:02d}] {text}\n")

# Print summary
speaker_counts = Counter(seg.get("speaker", "UNKNOWN") for seg in segments)
print(f"✓ Enhanced transcript saved: {OUTPUT_JSON}")
print(f"✓ Readable transcript saved: {OUTPUT_TXT}")
print(f"✓ Corrections audit trail: {CORRECTIONS_FILE}")
print(f"\nSpeaker distribution:")
for spk, count in speaker_counts.most_common():
    pct = count / len(segments) * 100
    print(f"  {spk}: {count} segments ({pct:.1f}%)")
print(f"\nTotal corrections: {len(corrections)}")
