# TRANSCRIPTION PIPELINE TEST - 50 HIGH-PRIORITY SHERLOCK PODCAST TARGETS

## CRITICAL CONTEXT (Survives Compaction)

**Mission:** Test new automated transcription pipeline for Freelance Transcription work using Sherlock's highest intelligence-value podcast targets.

**System Architecture:**
- **Input Pipeline:** YouTube/podcast URL → yt-dlp → MP3
- **Transcription Engine:** VoiceEngineManager + IntelligentModelSelector (adaptive quality)
- **Processing:** Night Shift autonomous processing OR manual Freelance queue
- **Output Location:** `/home/johnny5/Sherlock/freelance_transcripts/[podcast_name]/[episode_id]/`
- **Database:** Sherlock targets table (target_type='podcast')

**Infrastructure Already Built:**
- ✅ `_process_youtube_package()` in j5a_worker.py:875-1092
- ✅ `_download_youtube_audio()` helper (j5a_worker.py:1213-1275)
- ✅ `_transcribe_chunked()` for long audio (j5a_worker.py:1277-1395)
- ✅ VoiceEngineManager with intelligent model selection
- ✅ Resource scheduler (Squirt > Freelance > Sherlock priority)

---

## DELIVERABLES (TODO LIST - COMPACTION-RESISTANT)

### Phase 1: Setup & Validation (30 min)
- [ ] **Verify transcription infrastructure exists**
  - Check: j5a_worker.py has `_process_youtube_package()` method
  - Check: VoiceEngineManager accessible
  - Check: yt-dlp installed and functional
  - Output: System readiness report

- [ ] **Create output directory structure**
  - Path: `/home/johnny5/Sherlock/freelance_transcripts/`
  - Subdirs: One per podcast series (weaponized, american_alchemy, etc.)
  - Permissions: johnny5:johnny5, 755

- [ ] **Test pipeline with 1 short episode** (5-10 min video)
  - Use: Weaponized test episode
  - Verify: Download → Transcribe → Output JSON
  - Validate: Transcript quality, timing, speaker detection
  - Output: `test_episode_validation.json`

### Phase 2: Batch Processing - Tier 1 (P1 Priority - 10 episodes)
Process these in order, highest intelligence value:

- [ ] **T1-01: Lue Elizondo - Original Disclosure (Weaponized)**
  - URL: `https://www.youtube.com/watch?v=PLACEHOLDER_1`
  - Priority: P1 (First major whistleblower testimony)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/lue_elizondo_disclosure/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T1-02: Dr. Hal Puthoff - Remote Viewing Program (American Alchemy)**
  - URL: `https://www.youtube.com/watch?v=PLACEHOLDER_2`
  - Priority: P1 (Star Gate program insider)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/hal_puthoff_remote_viewing/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T1-03: Danny Sheehan - Government Obstruction (American Alchemy)**
  - URL: `https://www.youtube.com/watch?v=PLACEHOLDER_3`
  - Priority: P1 (Legal perspective on disclosure resistance)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/danny_sheehan_obstruction/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T1-04: Christopher Mellon - Pentagon UAP Program (Weaponized)**
  - URL: `https://www.youtube.com/watch?v=PLACEHOLDER_4`
  - Priority: P1 (Former Deputy Assistant Secretary of Defense)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/christopher_mellon_pentagon/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T1-05: David Grusch - Whistleblower Testimony (Any Source)**
  - URL: `https://www.youtube.com/watch?v=PLACEHOLDER_5`
  - Priority: P1 (2023 congressional testimony prep)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/misc/david_grusch_testimony/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T1-06: Jacques Vallée - Control System Theory (Any Source)**
  - URL: `https://www.youtube.com/watch?v=PLACEHOLDER_6`
  - Priority: P1 (Alternative framework for phenomenon)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/misc/jacques_vallee_control_system/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T1-07: Garry Nolan - Biological Evidence (Any Source)**
  - URL: `https://www.youtube.com/watch?v=PLACEHOLDER_7`
  - Priority: P1 (Stanford professor, physical evidence analysis)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/misc/garry_nolan_biological/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T1-08: Diana Pasulka - Vatican Knowledge (Any Source)**
  - URL: `https://www.youtube.com/watch?v=PLACEHOLDER_8`
  - Priority: P1 (Institutional knowledge, religious perspective)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/misc/diana_pasulka_vatican/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T1-09: Bob Lazar - S-4 Testimony (Joe Rogan or similar)**
  - URL: `https://www.youtube.com/watch?v=PLACEHOLDER_9`
  - Priority: P1 (Original reverse engineering claims)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/misc/bob_lazar_s4/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T1-10: Ross Coulthart - Investigative Summary (Any Source)**
  - URL: `https://www.youtube.com/watch?v=PLACEHOLDER_10`
  - Priority: P1 (Journalist synthesis of evidence)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/misc/ross_coulthart_investigation/`
  - Deliverable: transcript.json, metadata.json

### Phase 3: Batch Processing - Tier 2 (P2 Priority - 20 episodes)
Weaponized Podcast Series (Corbell & Knapp):

- [ ] **T2-01 to T2-20: Weaponized Episodes 1-20**
  - Base URL Pattern: `https://www.youtube.com/@WeaponizedPodcast/videos`
  - Priority: P2 (Systematic coverage of recent disclosure)
  - Output Base: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/ep_[NUMBER]/`
  - Note: Find actual URLs from YouTube channel
  - Deliverable per episode: transcript.json, metadata.json, intelligence_summary.json

### Phase 4: Batch Processing - Tier 3 (P3 Priority - 20 episodes)
American Alchemy with Danny Sheehan:

- [ ] **T3-01 to T3-20: American Alchemy Episodes (Sheehan interviews)**
  - Base URL Pattern: `https://www.youtube.com/@AmericanAlchemyPodcast/videos`
  - Priority: P3 (Legal/institutional analysis)
  - Output Base: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/ep_[NUMBER]/`
  - Filter: Only episodes featuring Danny Sheehan
  - Note: Find actual URLs from YouTube channel
  - Deliverable per episode: transcript.json, metadata.json, institutional_analysis.json

---

## SPECIFIC EXECUTION INSTRUCTIONS

### For Each Episode, Execute:

```bash
# 1. Create output directory
mkdir -p /home/johnny5/Sherlock/freelance_transcripts/[podcast]/[episode_id]

# 2. Download audio
cd /home/johnny5/Sherlock
python3 << EOF
import sys
sys.path.insert(0, '/home/johnny5/Johny5Alive/j5a-nightshift')
from j5a_worker import J5AWorker
from pathlib import Path

worker = J5AWorker(None, None)
audio_file = worker._download_youtube_audio(
    url="[EPISODE_URL]",
    target_dir=Path("/home/johnny5/Sherlock/freelance_transcripts/[podcast]/[episode_id]")
)
print(f"Downloaded: {audio_file}")
EOF

# 3. Transcribe with Whisper
python3 << EOF
import sys
import json
sys.path.insert(0, '/home/johnny5/Sherlock')
from voice_engine import VoiceEngineManager
from intelligent_model_selector import QualityPreference

voice = VoiceEngineManager(max_ram_gb=16.0)
result = voice.transcribe_sherlock(
    audio_path='/home/johnny5/Sherlock/freelance_transcripts/[podcast]/[episode_id]/audio.mp3',
    quality_preference=QualityPreference.BALANCED
)

output = {
    "text": result.text,
    "segments": result.segments if hasattr(result, 'segments') else [],
    "language": result.language if hasattr(result, 'language') else "en",
    "processing_info": {
        "model": "adaptive_whisper",
        "quality": "balanced"
    }
}

with open('/home/johnny5/Sherlock/freelance_transcripts/[podcast]/[episode_id]/transcript.json', 'w') as f:
    json.dump(output, f, indent=2)

print("Transcript saved")
EOF

# 4. Generate metadata
cat > /home/johnny5/Sherlock/freelance_transcripts/[podcast]/[episode_id]/metadata.json << EOF
{
  "episode_id": "[episode_id]",
  "podcast_series": "[podcast]",
  "source_url": "[EPISODE_URL]",
  "processed_date": "$(date -Iseconds)",
  "priority": "P1/P2/P3",
  "intelligence_tags": ["disclosure", "witnesses", "institutional_resistance"],
  "status": "completed"
}
EOF
```

### Quality Validation Per Episode:

```bash
# Check transcript exists and is valid
python3 << EOF
import json
from pathlib import Path

transcript_file = Path("/home/johnny5/Sherlock/freelance_transcripts/[podcast]/[episode_id]/transcript.json")

if not transcript_file.exists():
    print("❌ FAIL: Transcript missing")
    exit(1)

with open(transcript_file) as f:
    data = json.load(f)

if len(data.get('text', '')) < 100:
    print("❌ FAIL: Transcript too short (likely empty)")
    exit(1)

if not data.get('segments'):
    print("⚠️  WARNING: No segments (may be ok for short audio)")

print(f"✅ PASS: Transcript valid ({len(data['text'])} chars, {len(data.get('segments', []))} segments)")
EOF
```

---

## FINAL DELIVERABLES CHECKLIST

After completing all 50 episodes, verify:

- [ ] **All 50 transcript files exist**
  - Location: `/home/johnny5/Sherlock/freelance_transcripts/`
  - Format: `[podcast]/[episode_id]/transcript.json`
  - Validation: Each file >100 chars, valid JSON

- [ ] **All 50 metadata files exist**
  - Format: `[podcast]/[episode_id]/metadata.json`
  - Contains: episode_id, source_url, processed_date, priority

- [ ] **Quality report generated**
  - File: `/home/johnny5/Sherlock/freelance_transcripts/QUALITY_REPORT.json`
  - Contains: Success rate, average length, error log, processing times

- [ ] **Database updated**
  - All 50 episodes added to Sherlock targets table
  - Status: "transcribed"
  - Metadata includes transcript path

- [ ] **Summary statistics**
  - Total audio hours processed
  - Total transcript word count
  - Average processing time per episode
  - Model distribution (faster-whisper vs Whisper large-v3)

---

## ERROR HANDLING

If any episode fails:

1. **Log the failure** to `/home/johnny5/Sherlock/freelance_transcripts/ERRORS.log`
2. **Record error details**: URL, error message, timestamp
3. **Skip and continue** - don't block entire batch
4. **Retry queue**: Add to separate retry list after batch complete

---

## ACTUAL URLS TO USE

**CRITICAL:** The URLs above marked as `PLACEHOLDER_X` need to be replaced with actual YouTube URLs.

**How to find them:**

1. **Weaponized Podcast:** https://www.youtube.com/@WeaponizedPodcast/videos
   - Filter for episodes with Lue Elizondo, Christopher Mellon, etc.
   - Use episode URLs from recent high-value interviews

2. **American Alchemy:** https://www.youtube.com/@AmericanAlchemyPodcast/videos
   - Filter for Danny Sheehan episodes
   - Focus on UAP/disclosure topics

3. **Alternative Sources:**
   - Joe Rogan Experience (Bob Lazar, Jacques Vallée, etc.)
   - Lex Fridman Podcast (Garry Nolan, Diana Pasulka, etc.)
   - That UFO Podcast
   - The Debrief

**TODO Before Starting Phase 2:**
- [ ] Research and populate all 50 actual YouTube URLs
- [ ] Verify each URL is accessible
- [ ] Estimate total audio duration for time planning

---

## SUCCESS CRITERIA

**Pipeline is validated and ready for production use if:**

✅ At least 45/50 episodes transcribe successfully (90% success rate)
✅ Average transcription accuracy >90% (spot-check validation)
✅ No OOM crashes (intelligent model selection working)
✅ Processing time <2x real-time (60min episode processes in <120min)
✅ All outputs in correct directory structure
✅ Metadata complete and parseable

---

## POST-COMPLETION ACTIONS

After all 50 episodes processed:

1. **Generate Intelligence Reports**
   - Extract claims per episode
   - Build witness credibility matrix
   - Map institutional resistance patterns
   - Cross-reference disclosure timelines

2. **Update Sherlock Database**
   - Bulk import all transcripts
   - Link episodes to entities (people, organizations)
   - Build evidence network graph

3. **Production Deployment**
   - Document any pipeline improvements needed
   - Update j5a_worker.py with lessons learned
   - Create standard operating procedure for future batches

---

## NOTES FOR FUTURE CLAUDE

- This is a **test and validation** exercise, not production
- Prioritize **learning and iteration** over speed
- **Document** what works and what doesn't
- **Adapt** the approach if you find better methods
- User expects **high-quality transcripts** suitable for intelligence analysis
- **Time budget:** Can use multiple sessions, no rush
- **Resource constraints:** Respect Squirt/Freelance priority (use Night Shift when possible)

**Most Important:** The goal is to prove the transcription pipeline works reliably at scale, so Sherlock can autonomously process thousands of hours of intelligence-rich media.

---

**Created:** 2025-12-09
**Author:** Claude (Sonnet 4.5)
**Purpose:** Freelance Transcription Pipeline Testing & Validation
**Status:** Ready for execution when user requests
