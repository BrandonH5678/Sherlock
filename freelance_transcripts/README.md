# Freelance Transcription Pipeline - Episode Directory

## Overview
This directory contains transcription outputs from the Freelance Transcription Pipeline testing operations for Sherlock intelligence extraction.

## Directory Structure
```
freelance_transcripts/
├── README.md                           # This file
├── priority_episodes_master.json      # Master list of all 50 priority episodes with status
├── pending_episodes.json              # List of 45 episodes awaiting transcription
└── weaponized/                        # Weaponized podcast episodes
    ├── capitol_bombs/                 # ✅ COMPLETED
    ├── lacatski_part1/                # ✅ COMPLETED
    ├── lacatski_part2/                # ✅ COMPLETED
    ├── borland_part1/                 # ✅ COMPLETED
    └── borland_part2/                 # ✅ COMPLETED
```

## Episode Files

### priority_episodes_master.json
Complete master list of all 50 priority podcast episodes for Sherlock intelligence analysis:
- **Total Episodes:** 50
- **Tier 1 (P1):** 15 episodes - Primary source whistleblowers & government insiders
- **Tier 2 (P2):** 12 episodes - Scientific/academic evidence
- **Tier 3 (P3):** 10 episodes - Legal/institutional/investigative analysis
- **Tier 4 (P4):** 13 episodes - Witness testimonies & specific cases
- **Transcribed:** 5 episodes (10%)
- **Pending:** 45 episodes (90%)

### pending_episodes.json
Filtered list containing only the 45 episodes that still need transcription. Use this file for pipeline processing queue.

## Processing Status

### Completed (5 episodes)
All transcripts located in `/home/johnny5/Sherlock/freelance_transcripts/weaponized/`:

1. **capitol_bombs** - "UFO Bombs Dropped On Capitol Hill" (T1-15)
   - Transcript: `audio_transcription/audio_diarized_enhanced.json` (676KB)
   - Evidence: `/home/johnny5/Sherlock/evidence/capitol_bombs_intelligence_summary.md`

2. **lacatski_part1** - "Dr. James Lacatski - Pentagon UFO Program PART 1" (T1-01)
   - Transcript: `audio_transcription/audio_diarized_enhanced.json` (701KB)
   - Evidence: `/home/johnny5/Sherlock/evidence/lacatski_part1_intelligence_summary.md`

3. **lacatski_part2** - "Dr. James Lacatski - Government UFO Boss PART 2" (T1-02)
   - Transcript: `audio_transcription/audio_diarized_enhanced.json` (105KB)
   - Evidence: `/home/johnny5/Sherlock/evidence/lacatski_part2_intelligence_summary.md`

4. **borland_part1** - "Dylan Borland - UFO Whistleblower PART 1" (T1-03)
   - Transcript: `audio_transcription/audio_diarized_enhanced.json` (521KB)
   - Evidence: `/home/johnny5/Sherlock/evidence/borland_part1_intelligence_summary.md`

5. **borland_part2** - "Dylan Borland - Legacy UFO Programs PART 2" (T1-04)
   - Transcript: `audio_transcription/audio_diarized_enhanced.json` (1.2MB)
   - Evidence: `/home/johnny5/Sherlock/evidence/borland_part2_intelligence_summary.md`

### Pending (45 episodes)
See `pending_episodes.json` for complete list of episodes ready for processing.

Priority P1 episodes remaining:
- T1-05: Immaculate Constellation Whistleblower (PART 1)
- T1-06: Immaculate Constellation (PART 2)
- T1-07: Immaculate Constellation (PART 3)
- T1-08: Jay Stratton - Most Important Government UFO Investigator
- T1-09: CDR David Fravor - Best UFO Witness Ever
- T1-10: The Man Who Filmed The TIC TAC UFO
- T1-11: Firsthand Military Witness - Four TIC TAC UAPs
- T1-12: Navy Warship Encounters Multiple TIC TAC Craft
- T1-13: Mike Gold NASA Testimony - UAP Mysteries
- T1-14: Dave Foley - Fight for UAP Transparency

## Transcript File Types

Each episode directory contains multiple transcript formats:

- **audio.json** - Raw transcription output
- **audio_diarized.json** - Speaker diarization applied
- **audio_diarized_enhanced.json** - Enhanced with vocabulary corrections
- **audio_diarized_enhanced_vocabpack.json** - Vocabpack-enhanced version
- **vocab_harvest.json** - Specialized vocabulary extracted
- **vocabpack.json** - Custom vocabulary definitions
- **metadata.json** - Episode metadata (title, URL, processing info)

## Usage for Pipeline Testing

### Load All Priority Episodes
```python
import json

with open('/home/johnny5/Sherlock/freelance_transcripts/priority_episodes_master.json') as f:
    master = json.load(f)
    print(f"Total episodes: {master['total_episodes']}")
    print(f"Pending: {master['pending_count']}")
```

### Load Only Pending Episodes
```python
import json

with open('/home/johnny5/Sherlock/freelance_transcripts/pending_episodes.json') as f:
    pending = json.load(f)
    episodes = pending['episodes']
    print(f"Ready to process: {len(episodes)} episodes")
```

### Process Next Batch
```python
# Get next 10 P1 episodes
next_batch = [ep for ep in pending['episodes'] if ep['priority'] == 'P1'][:10]
```

## Integration with Sherlock Evidence System

All completed transcripts feed into Sherlock's evidence database at:
- **Intelligence Summaries:** `/home/johnny5/Sherlock/evidence/*_intelligence_summary.md`
- **Evidence Database:** `/home/johnny5/Sherlock/sherlock.db`

## Media Retention Policy

**IMPORTANT:** Source audio/video files are subject to 48-hour auto-delete policy:
- **Staging:** `/var/lib/johnny5/media-staging/sherlock/` (48 hours)
- **Transcripts:** Permanent retention in this directory
- **Archives:** Manual archives in `/home/johnny5/Sherlock/archives/` (permanent)

## Notes

- All 5 completed episodes are Tier 1 (P1) priority
- Freelance Pipeline has proven capability with large-scale diarization and vocabulary enhancement
- Transcripts range from 105KB to 1.2MB indicating comprehensive coverage
- 10 more P1 episodes remain for highest-priority processing
- System tested and validated on Weaponized podcast format
