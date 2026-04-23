# Sherlock Intelligence Extraction - Complete Report

**Date:** 2026-01-07
**System:** Sherlock Evidence Analysis System
**Operator:** Claude (Sonnet 4.5)
**Task:** Standard intelligence extraction on 5 Weaponized podcast transcripts

---

## Executive Summary

✅ **Successfully processed 5 Weaponized podcast episodes** through Sherlock's standard intelligence extraction pipeline

### Processing Results

| Episode | Entities | Claims | Transcript Length | Status |
|---------|----------|--------|-------------------|--------|
| Capitol Bombs | 59 | 127 | 56,559 chars | ✅ Complete |
| Lacatski Part 1 | 43 | 44 | 48,853 chars | ✅ Complete |
| Lacatski Part 2 | 13 | 14 | 9,232 chars | ✅ Complete |
| Borland Part 1 | 18 | 23 | 44,565 chars | ✅ Complete |
| Borland Part 2 | 27 | 87 | 95,631 chars | ✅ Complete |
| **TOTALS** | **160** | **295** | **255,840 chars** | ✅ **5/5** |

---

## Detailed Results

### 1. Capitol Bombs - "UFO Bombs Dropped On Capitol Hill"
- **Source ID:** weaponized_capitol_bombs
- **Entities Extracted:** 59 total
  - People: 21 (Schumer, Grush, Burchett, Reid, Gillibrand, Rubio, Mellon, etc.)
  - Organizations: 16 (Pentagon, Senate, Lockheed Martin, CIA, AARO, etc.)
  - Programs: 6 (AAWSAP, AATIP, Immaculate Constellation, NDAA, etc.)
  - Locations: 4 (Area 51, Pentagon, Capitol Hill, Washington)
  - Technologies: 12 (UAPs, UFOs, non-human craft, advanced tech, etc.)
- **Claims Extracted:** 127 intelligence claims
- **Summary:** `/home/johnny5/Sherlock/evidence/capitol_bombs_intelligence_summary.md`

### 2. Lacatski Part 1 - "Dr. James Lacatski - Pentagon UFO Program"
- **Source ID:** weaponized_lacatski_part1
- **Entities Extracted:** 43 total
  - People: 13
  - Organizations: 12
  - Programs: 8
  - Locations: 3
  - Technologies: 7
- **Claims Extracted:** 44 intelligence claims
- **Summary:** `/home/johnny5/Sherlock/evidence/lacatski_part1_intelligence_summary.md`

### 3. Lacatski Part 2 - "Dr. James Lacatski - Government UFO Boss"
- **Source ID:** weaponized_lacatski_part2
- **Entities Extracted:** 13 total
  - People: 4
  - Organizations: 3
  - Programs: 2
  - Locations: 2
  - Technologies: 2
- **Claims Extracted:** 14 intelligence claims
- **Summary:** `/home/johnny5/Sherlock/evidence/lacatski_part2_intelligence_summary.md`

### 4. Borland Part 1 - "Dylan Borland - UFO Whistleblower"
- **Source ID:** weaponized_borland_part1
- **Entities Extracted:** 18 total
  - People: 6
  - Organizations: 5
  - Programs: 3
  - Locations: 2
  - Technologies: 2
- **Claims Extracted:** 23 intelligence claims
- **Summary:** `/home/johnny5/Sherlock/evidence/borland_part1_intelligence_summary.md`

### 5. Borland Part 2 - "Dylan Borland - Legacy UFO Programs"
- **Source ID:** weaponized_borland_part2
- **Entities Extracted:** 27 total
  - People: 8
  - Organizations: 7
  - Programs: 4
  - Locations: 3
  - Technologies: 5
- **Claims Extracted:** 87 intelligence claims
- **Summary:** `/home/johnny5/Sherlock/evidence/borland_part2_intelligence_summary.md`

---

## System Integration Status

### Evidence Database (sherlock.db)
- ✅ **5 Evidence Sources Created** - All episodes registered
- ⚠️ **0 Claims Saved** - FOREIGN KEY constraint failures (speaker_id missing)
- 📝 **Note:** Claims extracted but not persisted due to empty speakers table

### Extraction Artifacts Created

1. **Intelligence Summaries (Markdown)**
   - Location: `/home/johnny5/Sherlock/evidence/`
   - Format: Individual .md files per episode
   - Count: 5 files

2. **Processing Checkpoints (JSON)**
   - Location: `/home/johnny5/Sherlock/weaponized_checkpoints/`
   - Content: Extraction statistics per episode
   - Count: 5 files

3. **Comprehensive Report (JSON)**
   - File: `/home/johnny5/Sherlock/evidence/weaponized_intelligence_extraction_report.json`
   - Contains: Full extraction statistics + transcript excerpts

4. **Transcript Text Files**
   - Location: Each episode's `audio_transcription/` directory
   - Format: Plain text extracted from JSON
   - Count: 5 files

---

## Entity Recognition Performance

### Top Entities Extracted Across All Episodes

**People (21 unique across capitol_bombs):**
- David Grusch (whistleblower)
- Chuck Schumer (Senate Majority Leader)
- Tim Burchett (Congressman)
- Harry Reid (former Senator)
- Luis Elizondo
- Christopher Mellon
- James Lacatski
- Jeremy Corbell & George Knapp (hosts)

**Organizations (16 unique across capitol_bombs):**
- Pentagon / DoD
- Senate / House Intelligence Committees
- Lockheed Martin
- CIA, DIA, FBI, NSA
- AARO (All-domain Anomaly Resolution Office)
- BAASS (Bigelow Aerospace Advanced Space Studies)

**Programs:**
- AAWSAP (Advanced Aerospace Weapon System Applications Program)
- AATIP (Advanced Aerospace Threat Identification Program)
- Immaculate Constellation
- NDAA (National Defense Authorization Act)
- UAP Review Board

---

## Intelligence Value Assessment

### High-Value Intelligence Categories

1. **Legislative Action** (127 claims from Capitol Bombs)
   - Schumer Amendment analysis
   - NDAA UAP provisions
   - Congressional hearing preparations
   - Eminent domain implications

2. **Program Disclosure** (44 claims from Lacatski Part 1)
   - AAWSAP program details
   - DIA involvement
   - Defense contractor relationships
   - Classified program structures

3. **Whistleblower Testimony** (110 claims from Borland Parts 1&2)
   - Legacy program revelations
   - Technology access claims
   - Institutional resistance patterns
   - Disclosure movement insights

---

## Technical Notes

### Extraction Method
- **Tool:** `weaponized_intelligence_extractor.py`
- **Approach:** Pattern-based entity recognition + keyword claim extraction
- **Success Rate:** 100% transcript processing, 0% database persistence (FK constraints)

### Known Issues
1. **Speaker FK Constraint:** Claims couldn't be saved due to empty speakers table
2. **Solution Required:** Pre-populate speakers table or modify extractor to auto-create speakers

### Recommendations
1. Fix speaker table population in extraction pipeline
2. Re-run claim insertion after speaker resolution
3. Consider adding speaker diarization data to create proper speaker records

---

## Files Generated

```
/home/johnny5/Sherlock/
├── evidence/
│   ├── capitol_bombs_intelligence_summary.md
│   ├── lacatski_part1_intelligence_summary.md
│   ├── lacatski_part2_intelligence_summary.md
│   ├── borland_part1_intelligence_summary.md
│   ├── borland_part2_intelligence_summary.md
│   └── weaponized_intelligence_extraction_report.json
├── weaponized_checkpoints/
│   ├── capitol_bombs_checkpoint.json
│   ├── lacatski_part1_checkpoint.json
│   ├── lacatski_part2_checkpoint.json
│   ├── borland_part1_checkpoint.json
│   └── borland_part2_checkpoint.json
└── freelance_transcripts/weaponized/
    ├── capitol_bombs/audio_transcription/audio.txt
    ├── lacatski_part1/audio_transcription/audio.txt
    ├── lacatski_part2/audio_transcription/audio.txt
    ├── borland_part1/audio_transcription/audio.txt
    └── borland_part2/audio_transcription/audio.txt
```

---

## Next Steps (Recommendations)

1. **Fix Database Integration:**
   - Populate speakers table with George Knapp, Jeremy Corbell, guests
   - Re-run claim insertion to persist 295 extracted claims

2. **Enhanced Extraction:**
   - Add temporal claim analysis
   - Cross-reference claims across episodes
   - Build knowledge graph from entity relationships

3. **Continue Processing:**
   - 45 episodes remain in pending queue
   - Priority: 10 remaining P1 (Tier 1) episodes
   - Estimated: ~2,000 additional claims from remaining P1 episodes

---

**Status:** ✅ Intelligence Extraction Complete
**Quality:** High - 160 entities, 295 claims successfully extracted
**Database Status:** Partial - Sources saved, claims pending speaker resolution
**Ready for:** Analysis, cross-referencing, and continuation with remaining 45 episodes

