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
  - Subdirs: weaponized/, american_alchemy/
  - Permissions: johnny5:johnny5, 755

- [ ] **Test pipeline with 1 short episode** (5-10 min video)
  - Use: Episode #26 - UFO Bombs Dropped On Capitol Hill
  - URL: https://www.youtube.com/watch?v=nfchje15k00
  - Verify: Download → Transcribe → Output JSON
  - Validate: Transcript quality, timing, speaker detection
  - Output: `test_episode_validation.json`

---

## Phase 2: Batch Processing - TIER 1 (P1 Priority - 15 episodes)

**Primary Source Whistleblowers & Government Insiders**

- [ ] **T1-01: Dr. James Lacatski - Pentagon UFO Program (PART 1)**
  - URL: `https://www.youtube.com/watch?v=Qu8pudJk_-A`
  - Priority: P1 (Ran Pentagon's secret UFO program)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/lacatski_part1/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T1-02: Dr. James Lacatski - Government UFO Boss (PART 2)**
  - URL: `https://www.youtube.com/watch?v=cggMuAjFJcI`
  - Priority: P1 (Monsters, Men in Black & UFO crashes)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/lacatski_part2/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T1-03: Dylan Borland - UFO Whistleblower (PART 1)**
  - URL: `https://www.youtube.com/watch?v=4H51UT2gs2g`
  - Priority: P1 (Reluctant whistleblower tells all)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/borland_part1/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T1-04: Dylan Borland - Legacy UFO Programs (PART 2)**
  - URL: `https://www.youtube.com/watch?v=-U2u43Vdt_g`
  - Priority: P1 (Truth about legacy programs)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/borland_part2/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T1-05: Immaculate Constellation Whistleblower (PART 1)**
  - URL: `https://www.youtube.com/watch?v=ZAxI-LDrDqA`
  - Priority: P1 (Whistleblower goes public)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/immaculate_part1/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T1-06: Immaculate Constellation (PART 2)**
  - URL: `https://www.youtube.com/watch?v=4n_bRtnIP14`
  - Priority: P1 (Whistleblower's journey)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/immaculate_part2/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T1-07: Immaculate Constellation (PART 3)**
  - URL: `https://www.youtube.com/watch?v=PtBVAxoHeaY`
  - Priority: P1 (Whistleblower honors oath)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/immaculate_part3/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T1-08: Jay Stratton - Most Important Government UFO Investigator**
  - URL: `https://www.youtube.com/watch?v=HB5e4mgJX2Q`
  - Priority: P1 (WEAPONIZED FLASHBACK)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/jay_stratton/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T1-09: CDR David Fravor - Best UFO Witness Ever**
  - URL: `https://www.youtube.com/watch?v=zRkh3xh5_yU`
  - Priority: P1 (Tic Tac primary witness, Episode #29)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/fravor_tictac/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T1-10: The Man Who Filmed The TIC TAC UFO**
  - URL: `https://www.youtube.com/watch?v=4opsdH4hY3s`
  - Priority: P1 (Primary footage source, Episode #27)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/tictac_filmer/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T1-11: Firsthand Military Witness - Four TIC TAC UAPs**
  - URL: `https://www.youtube.com/watch?v=YKFmK-NSnKI`
  - Priority: P1 (Episode #73)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/four_tictacs/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T1-12: Navy Warship Encounters Multiple TIC TAC Craft**
  - URL: `https://www.youtube.com/watch?v=Vum9ny7yytg`
  - Priority: P1 (Episode #72)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/navy_tictacs/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T1-13: Mike Gold NASA Testimony - UAP Mysteries**
  - URL: `https://www.youtube.com/watch?v=znisWF5qHnA`
  - Priority: P1 (NASA archives key, Episode #66)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/mike_gold_nasa/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T1-14: Dave Foley - Fight for UAP Transparency**
  - URL: `https://www.youtube.com/watch?v=SOzth5nQorw`
  - Priority: P1 (Storming the silence, Episode #83)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/dave_foley/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T1-15: UFO Bombs Dropped On Capitol Hill**
  - URL: `https://www.youtube.com/watch?v=nfchje15k00`
  - Priority: P1 (Episode #26)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/capitol_bombs/`
  - Deliverable: transcript.json, metadata.json

---

## Phase 3: Batch Processing - TIER 2 (P2 Priority - 12 episodes)

**Scientific/Academic Evidence**

- [ ] **T2-01: Diana Pasulka & Karl Nell - Biblical Truth of UFOs & Angels**
  - URL: `https://www.youtube.com/watch?v=aa9Xx5wI8Rw`
  - Priority: P2 (Institutional/religious perspective)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/pasulka_nell/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T2-02: Andrew Gallimore - DMT Opens The Alien Realm**
  - URL: `https://www.youtube.com/watch?v=8XD1ZiuhXoY`
  - Priority: P2 (Neuroscientist consciousness research)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/gallimore_dmt/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T2-03: Dr. John Brandenburg - Life on Mars Destroyed by Nuclear War**
  - URL: `https://www.youtube.com/watch?v=p0S0BfoZy0w`
  - Priority: P2 (Nuclear war hypothesis)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/brandenburg_mars/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T2-04: Joe McMoneagle - Mars Had Alien Life**
  - URL: `https://www.youtube.com/watch?v=JpLThEF2dTM`
  - Priority: P2 (Remote viewing Mars)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/mcmoneagle_mars/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T2-05: MIT Scientist - Aliens Are Simulating Our Reality**
  - URL: `https://www.youtube.com/watch?v=aKZ_MUbuk_Q`
  - Priority: P2 (Simulation theory)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/mit_simulation/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T2-06: Eric Wargo - UFOs, Synchronicities & Prophetic Dreams**
  - URL: `https://www.youtube.com/watch?v=hXYdkcv5TtY`
  - Priority: P2 (Temporal phenomena)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/wargo_dreams/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T2-07: Your Brain Is A Quantum Time Machine**
  - URL: `https://www.youtube.com/watch?v=RofQnByLwOo`
  - Priority: P2 (Eric Wargo consciousness research)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/quantum_brain/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T2-08: Salvatore Pais - Navy Scientist With UFO Patents**
  - URL: `https://www.youtube.com/watch?v=8TYMQOUDQBo`
  - Priority: P2 (Navy UFO technology patents)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/pais_patents/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T2-09: Matthew Pines - Age of Psionics**
  - URL: `https://www.youtube.com/watch?v=9QMrhcpJq8I`
  - Priority: P2 (UFOs, mind control, global power)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/pines_psionics/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T2-10: Matthew Pines - UFO Physics & Disclosure Under Trump**
  - URL: `https://www.youtube.com/watch?v=LpLFWdsIU7M`
  - Priority: P2 (UFO physics analysis)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/pines_physics/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T2-11: Psychic Spies & Alien Civilizations - Connection**
  - URL: `https://www.youtube.com/watch?v=H9Yr_bflXec`
  - Priority: P2 (Episode #37 - Hal Puthoff remote viewing)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/puthoff_psychic/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T2-12: John Blitch - DARPA Scientist Injured By An Alien**
  - URL: `https://www.youtube.com/watch?v=yAvD5UTziTo`
  - Priority: P2 (DARPA scientist testimony)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/blitch_darpa/`
  - Deliverable: transcript.json, metadata.json

---

## Phase 4: Batch Processing - TIER 3 (P3 Priority - 10 episodes)

**Legal/Institutional/Investigative**

- [ ] **T3-01: Danny Sheehan - UFOs & JFK: He Knew Too Much**
  - URL: `https://www.youtube.com/watch?v=C4rSj5Aum7w`
  - Priority: P3 (Legal perspective on disclosure)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/sheehan_jfk/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T3-02: Ross Coulthart - I Located A UFO Base In Arizona**
  - URL: `https://www.youtube.com/watch?v=V00WcEiKRAY`
  - Priority: P3 (Investigative journalism)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/coulthart_arizona/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T3-03: Richard Dolan - Defense Secretary Killed Over UFOs**
  - URL: `https://www.youtube.com/watch?v=GQlWf54K_7Y`
  - Priority: P3 (Historical institutional resistance)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/dolan_defsec/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T3-04: Harald Malmgren - Presidential Advisor Handled UFO Material**
  - URL: `https://www.youtube.com/watch?v=09KP8XVf5nY`
  - Priority: P3 (Presidential advisor testimony)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/malmgren_advisor/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T3-05: Did Henry Kissinger Oversee UFO Crash Retrieval?**
  - URL: `https://www.youtube.com/watch?v=Jpf0ZGY87c0`
  - Priority: P3 (Institutional knowledge)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/kissinger_crash/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T3-06: Tom O'Neill - CIA's Mind Control Program**
  - URL: `https://www.youtube.com/watch?v=75Je_0hZovQ`
  - Priority: P3 (MKUltra context)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/oneill_mkultra/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T3-07: Michael Shellenberger - Immaculate Constellation UFO Program**
  - URL: `https://www.youtube.com/watch?v=DPmO-2E7Ayg`
  - Priority: P3 (Breaking UFO story)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/shellenberger_ic/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T3-08: Richard Dolan - Centuries Of USO Cases**
  - URL: `https://www.youtube.com/watch?v=ABDlCbumob0`
  - Priority: P3 (Underwater UFO phenomena)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/dolan_uso/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T3-09: The Wall Street Journal Is Lying About UFOs**
  - URL: `https://www.youtube.com/watch?v=h0hAit-KH9A`
  - Priority: P3 (Media disinformation analysis)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/wsj_lying/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T3-10: Smearing the Brave - WSJ's War on UFO Truth**
  - URL: `https://www.youtube.com/watch?v=1xApIOjVgvU`
  - Priority: P3 (Episode #80)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/wsj_war/`
  - Deliverable: transcript.json, metadata.json

---

## Phase 5: Batch Processing - TIER 4 (P4 Priority - 13 episodes)

**Witness Testimonies & Cases**

- [ ] **T4-01: Charles Hall - I Spent 3 Years With Tall White Aliens At Area 51**
  - URL: `https://www.youtube.com/watch?v=QgxjtDS2sIQ`
  - Priority: P4 (Area 51 whistleblower)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/hall_area51/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T4-02: Greg Rogers - NASA Doctor: I Saw UFO In Secret Hangar**
  - URL: `https://www.youtube.com/watch?v=TNtlzEnl8rA`
  - Priority: P4 (NASA witness)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/rogers_nasa/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T4-03: Whitley Strieber - Aliens Live Among Us...I've Met Them**
  - URL: `https://www.youtube.com/watch?v=ABOP8ZJsyIk`
  - Priority: P4 (Close encounter testimony)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/strieber_aliens/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T4-04: Michael Herrera - I Saw A 300ft UFO In Indonesian Jungle**
  - URL: `https://www.youtube.com/watch?v=D2tKCFmJjks`
  - Priority: P4 (Military witness)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/herrera_jungle/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T4-05: Eric Davis - A US President Was Briefed on UFOs**
  - URL: `https://www.youtube.com/watch?v=LnAiNChnuEQ`
  - Priority: P4 (Presidential briefing disclosure)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/davis_potus/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T4-06: Ryan Graves - US Fighter Pilots Witness UFO**
  - URL: `https://www.youtube.com/watch?v=6WC4o2yY9Ws`
  - Priority: P4 (Fighter pilot testimony)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/graves_pilot/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T4-07: Sergeant Dan Sherman - NSA Hired Me To Speak To Aliens**
  - URL: `https://www.youtube.com/watch?v=Rfmy5oW_r9c`
  - Priority: P4 (NSA alien communication program)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/sherman_nsa/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T4-08: Robert Salas - UFO Shut Down 10 Nukes**
  - URL: `https://www.youtube.com/watch?v=-0g3lLGxNfc`
  - Priority: P4 (Air Force officer testimony)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/salas_nukes/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T4-09: Robert Hastings - UFOs Monitoring Nuclear Bases Globally**
  - URL: `https://www.youtube.com/watch?v=fzvwBBSmWYA`
  - Priority: P4 (Nuclear sites pattern)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/hastings_nukes/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T4-10: Col. Corso - Alien Bodies & Technology (Lost Tapes)**
  - URL: `https://www.youtube.com/watch?v=US4BNwU3q8Q`
  - Priority: P4 (Episode #87)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/corso_tapes/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T4-11: Thiago Ticchetti - UFOs Attacked 2,000 Humans**
  - URL: `https://www.youtube.com/watch?v=QQqVs4t_D-A`
  - Priority: P4 (Colares attacks, Episode #57)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/colares_attacks/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T4-12: Massive Mystery Cubes Invade Vandenberg Base**
  - URL: `https://www.youtube.com/watch?v=a-YuYaG3Lqc`
  - Priority: P4 (Military cops chase, Episode #71)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/weaponized/vandenberg_cubes/`
  - Deliverable: transcript.json, metadata.json

- [ ] **T4-13: Jake Barber - I Carried A UFO With My Helicopter**
  - URL: `https://www.youtube.com/watch?v=dnnpyNuPdXs`
  - Priority: P4 (Helicopter pilot whistleblower)
  - Output: `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/barber_helicopter/`
  - Deliverable: transcript.json, metadata.json

---

## EXECUTION SUMMARY

**Total Episodes:** 50
- **Weaponized Podcast:** 30 episodes
- **American Alchemy Podcast:** 20 episodes

**Intelligence Priority Distribution:**
- **P1 (Tier 1 - Primary Source):** 15 episodes (30%)
- **P2 (Tier 2 - Scientific):** 12 episodes (24%)
- **P3 (Tier 3 - Legal/Institutional):** 10 episodes (20%)
- **P4 (Tier 4 - Witness/Cases):** 13 episodes (26%)

**Estimated Metrics:**
- **Total Runtime:** ~50-60 hours of content
- **Total Transcription Time (GPU large-v3):** ~25-30 hours
- **Output Size (transcripts):** ~15-20 MB total
- **Intelligence Value:** Maximum priority UAP disclosure coverage

**Processing Strategy:**
1. Start with Phase 1 validation (test Episode #26)
2. Process Tier 1 (P1) episodes first - highest intelligence value
3. Continue through Tiers 2-4 sequentially
4. Use Night Shift processing (10pm-6am) to avoid Squirt/Freelance conflicts
5. GPU-accelerated Premium tier (large-v3 model) for maximum accuracy

**Success Criteria:**
- ✅ 90%+ transcription success rate (45+ episodes)
- ✅ Speaker diarization accuracy >85%
- ✅ Transcript quality suitable for intelligence analysis
- ✅ All metadata properly generated
- ✅ Pipeline proves viable for scaled deployment

---

**Created:** 2025-12-09
**Author:** Claude (Sonnet 4.5)
**Purpose:** Freelance Transcription Pipeline Testing & Validation
**Status:** COMPLETE - Ready for execution with all 50 actual YouTube URLs

