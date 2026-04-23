# Sherlock Transcription Pipeline - File Index

**Quick navigation to all mission files**

---

## 📖 START HERE

**👉 `/home/johnny5/Sherlock/README_WHEN_YOU_RETURN.md`**
- **Read this first when you return**
- Quick status check commands
- What to expect
- How to intervene if needed

---

## 📊 Status & Monitoring

**Current Status:**
- `/home/johnny5/Sherlock/monitor_progress.sh` - Quick progress check (run this!)
- `/home/johnny5/Sherlock/processing_monitor.log` - Continuous monitoring log

**Detailed Status Reports:**
- `/home/johnny5/Sherlock/AUTONOMOUS_PROCESSING_STATUS.md` - Mission overview
- `/home/johnny5/Sherlock/PROCESSING_UPDATE_20251209_2011UTC.md` - Snapshot at 20:11 UTC
- `/home/johnny5/Sherlock/AUTONOMOUS_EXECUTION_SUMMARY.md` - Complete execution summary

---

## 🔧 Processing Infrastructure

**Main Processor:**
- `/home/johnny5/Sherlock/process_sherlock_transcription.py` - Episode processor

**Episode Lists:**
- `/home/johnny5/Sherlock/phase1_test_episode.json` - Test episode
- `/home/johnny5/Sherlock/tier1_episodes.json` - 15 P1 episodes
- `/home/johnny5/Sherlock/tier2_episodes.json` - 12 P2 episodes
- `/home/johnny5/Sherlock/tier3_episodes.json` - 10 P3 episodes
- `/home/johnny5/Sherlock/tier4_episodes.json` - 13 P4 episodes

**Monitoring Scripts:**
- `/home/johnny5/Sherlock/monitor_progress.sh` - Manual progress check
- `/home/johnny5/Sherlock/continuous_monitor.sh` - Auto-monitoring (running)

**Report Generator:**
- `/home/johnny5/Sherlock/generate_final_report.py` - Final consolidated report

---

## 📁 Output Directories

**Transcripts:**
- `/home/johnny5/Sherlock/freelance_transcripts/weaponized/` - Weaponized episodes
- `/home/johnny5/Sherlock/freelance_transcripts/american_alchemy/` - American Alchemy episodes

**Each episode directory contains:**
- `audio.mp3` - Source audio
- `audio.txt` - Plain text transcript
- `audio.json` - Structured transcript (segments, timestamps, confidence)
- `audio.srt` - SRT subtitles
- `audio.vtt` - VTT subtitles
- `metadata.json` - Episode metadata

---

## 📈 Results & Reports

**Per-Tier Results (populate as jobs complete):**
- `/home/johnny5/Sherlock/transcription_results_*.json` - One per batch job

**Final Report (generates when all complete):**
- `/home/johnny5/Sherlock/FINAL_PROCESSING_REPORT.json` - Consolidated metrics

**Logs:**
- `/home/johnny5/Sherlock/processing_monitor.log` - Continuous monitoring updates

---

## 🎯 Mission Reference

**Source Test Plan:**
- `/home/johnny5/Sherlock/TRANSCRIPTION_PIPELINE_TEST_PROMPT_COMPLETE.md` - Original 50-episode plan

---

## Quick Commands

**Check progress:**
```bash
/home/johnny5/Sherlock/monitor_progress.sh
```

**Count completions:**
```bash
find /home/johnny5/Sherlock/freelance_transcripts -name "audio.json" | wc -l
```

**See active transcriptions:**
```bash
ps aux | grep faster_whisper
```

**View monitoring log:**
```bash
tail -f /home/johnny5/Sherlock/processing_monitor.log
```

**Generate final report (when done):**
```bash
cd /home/johnny5/Sherlock && python3 generate_final_report.py
```

---

**Last Updated:** 2025-12-09 20:17 UTC
