# Amazon Prime Video Automated Documentary Capture - Setup Guide

## Overview

This guide will help you set up automated capture and processing for Amazon Prime Video documentaries, specifically "Age of Disclosure". The system will:

1. **Automatically play** the video in a browser
2. **Capture audio** via PulseAudio loopback
3. **Capture subtitle speaker labels** via OCR
4. **Transcribe with Whisper** for high accuracy
5. **Merge speaker labels + transcription** for proper attribution
6. **Extract intelligence** with entity/claim tracking

## Prerequisites

- J5A server with GUI access (Linux Mint)
- Active Amazon Prime Video subscription
- Age of Disclosure available in your Prime Video library

## Setup Process

### Step 1: Install Dependencies

Run the automated setup script:

```bash
cd /home/johnny5/Sherlock/scripts
./setup_prime_video_environment.sh
```

This installs:
- **Playwright** (browser automation)
- **Tesseract OCR** (subtitle capture)
- **PulseAudio** (audio loopback)
- **FFmpeg** (recording)

### Step 2: Enable DRM in Firefox

Amazon Prime Video requires Widevine CDM for DRM protection.

**If the setup script reports Widevine is missing:**

1. Open Firefox on the server:
   ```bash
   DISPLAY=:0 firefox
   ```

2. Navigate to: `about:preferences`

3. Search for: "DRM"

4. Enable: ✅ **"Play DRM-controlled content"**

5. Firefox will automatically download Widevine (~30 seconds)

6. Verify by visiting: https://www.amazon.com/primevideo

### Step 3: Test Prime Video Access

Run the test script to verify everything works:

```bash
DISPLAY=:0 python3 /home/johnny5/Sherlock/scripts/test_prime_video_access.py
```

**What this does:**
- Opens Firefox with your existing profile (preserves login)
- Navigates to Prime Video
- Prompts you to log in (if needed)
- Asks you to navigate to "Age of Disclosure"
- Captures the video URL
- Saves configuration to `prime_video_config.json`

**Follow the prompts:**
1. Log into Amazon if prompted
2. Navigate to "Age of Disclosure" (search or browse)
3. Copy the URL from the address bar
4. Press Enter when ready

### Step 4: Verify Configuration

After the test script completes, verify the config file:

```bash
cat /home/johnny5/Sherlock/prime_video_config.json
```

Should contain:
```json
{
  "firefox_profile": "/home/johnny5/.mozilla/firefox/xxxxxxxx.default",
  "age_of_disclosure_url": "https://www.amazon.com/gp/video/detail/...",
  "verified_at": "2025-12-09 14:30:00",
  "display": ":0"
}
```

## Automated Processing

Once setup is complete, you have two options:

### Option A: Manual Trigger (Immediate)

```bash
cd /home/johnny5/Sherlock
python3 scripts/process_prime_video_documentary.py --url "YOUR_URL_HERE"
```

### Option B: Night Shift Queue (Automated)

Update the Age of Disclosure target to use the Prime Video URL:

```bash
python3 scripts/add_age_of_disclosure_target.py \
  --type video \
  --url "https://www.amazon.com/gp/video/detail/..."
```

Then Night Shift will automatically process it when resources are available.

## What Happens During Processing

```
1. [0:00] Browser automation starts
   ├─ Opens Firefox with your logged-in profile
   ├─ Navigates to Age of Disclosure
   ├─ Enables closed captions [CC]
   └─ Clicks play button

2. [0:10] Simultaneous capture begins
   ├─ Audio: PulseAudio loopback → age_of_disclosure.mp3
   └─ Subtitles: OCR on CC region → speaker_labels.json
       (Every 2 seconds: captures speaker + text + timestamp)

3. [1:50:00] Video ends, processing begins
   ├─ Whisper transcription (age_of_disclosure.mp3)
   ├─ Merge speaker labels with Whisper transcript
   └─ Output: age_of_disclosure_merged.json

4. [2:00:00] Intelligence extraction
   ├─ Identify speakers (Lue Elizondo, Dr. Puthoff, etc.)
   ├─ Extract claims by speaker
   ├─ Build entity network
   └─ Output: age_of_disclosure_intelligence.json
```

## Output Files

All outputs saved to: `/home/johnny5/Sherlock/prime_video_processing/age_of_disclosure/`

```
age_of_disclosure/
├── raw_audio.mp3                    # Captured audio (1hr 50min)
├── speaker_labels.json              # OCR'd subtitle speaker tags
├── whisper_transcript.json          # High-accuracy transcription
├── merged_transcript.json           # Combined: Whisper + speaker labels
├── intelligence_report.json         # Extracted claims, entities, timeline
└── processing_log.txt               # Full processing log
```

## Troubleshooting

### Issue: "Browser automation failed"
**Solution:** Make sure you're logged into the server GUI
```bash
# Check if X server is running
echo $DISPLAY  # Should show ":0"

# If empty, log into the server desktop first
```

### Issue: "Widevine not found"
**Solution:** Enable DRM in Firefox (see Step 2 above)

### Issue: "Prime Video won't play"
**Solution:** Verify login and subscription
```bash
# Test manually first
DISPLAY=:0 firefox https://www.amazon.com/primevideo
```

### Issue: "OCR not capturing speaker labels"
**Solution:** Check subtitle position or increase OCR frequency
```bash
# Run in debug mode
python3 process_prime_video_documentary.py --debug --url "..."
```

## System Requirements

- **RAM**: 8GB+ recommended (Whisper large-v3 needs ~3GB)
- **Disk**: ~2GB for 2-hour documentary processing
- **Display**: X11 server must be running (Linux Mint default)
- **Browser**: Firefox with DRM enabled
- **Network**: Stable connection for Prime Video streaming

## Privacy & Legal Notes

- This system captures content **you already own/subscribe to**
- Processing is **local** (no cloud services)
- Transcripts are for **personal research use** (fair use)
- No redistribution or DRM circumvention
- Browser uses your **existing Amazon session**

## Next Steps After Setup

Once "Age of Disclosure" is processed, the same system can handle:
- Other Prime Video documentaries
- Multi-witness interviews
- Lecture series
- Conference recordings

Just provide the URL and the system handles the rest.

## Support

If you encounter issues:
1. Check the processing log in the output directory
2. Verify all dependencies installed: `./setup_prime_video_environment.sh`
3. Test Prime Video access manually: `DISPLAY=:0 firefox`
4. Review this guide's troubleshooting section

---

**Ready to proceed?** Run Step 1 (install dependencies) and follow the prompts!
