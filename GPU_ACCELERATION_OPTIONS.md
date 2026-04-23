# Sherlock Transcription - GPU Acceleration Options

**Timestamp:** 2025-12-09 20:28 UTC
**Status:** GPU acceleration blocked by missing cuDNN libraries

---

## Problem Identified

**Root cause:** Missing pynvml + cuDNN libraries

**What we fixed:**
- ✅ Installed `pynvml` (GPU monitoring)
- ✅ Verified PyTorch CUDA support working
- ✅ Verified faster-whisper can load models on GPU

**What's still broken:**
- ❌ cuDNN 9.x libraries not installed (faster-whisper's CT Translate2 backend needs them)
- ❌ Ubuntu repositories don't have cuDNN 9.x
- ❌ Requires manual installation from NVIDIA or alternative approach

---

## Three Options Forward

### Option 1: Install cuDNN 9.x from NVIDIA (Complex, ~30-60 min)

**Steps:**
1. Download cuDNN 9.x from NVIDIA Developer site (requires NVIDIA account)
2. Extract to `/usr/local/cuda/lib64/`
3. Update `LD_LIBRARY_PATH`
4. Test faster-whisper GPU acceleration

**Pros:**
- Fastest inference (~30x real-time with large-v3)
- Uses existing faster-whisper infrastructure
- CTranslate2 optimization

**Cons:**
- Manual download/setup required
- Requires NVIDIA Developer account
- 30-60 minutes to complete

---

### Option 2: Switch to WhisperX (Recommended by Chat)

**What is WhisperX:**
- Wrapper around faster-whisper
- Adds speaker diarization (WHO said WHAT)
- Word-level alignment
- Should work with PyTorch's bundled cuDNN

**Steps:**
1. Install WhisperX: `pip install whisperx`
2. Update processing script to use WhisperX API
3. Test GPU acceleration

**Pros:**
- Likely works with PyTorch's bundled cuDNN (no manual install)
- **Speaker diarization** (identify who's speaking - HUGE for podcasts!)
- Better word-level timestamps
- Recommended by Chat (external research)

**Cons:**
- Need to rewrite processing script
- Unknown if it works without standalone cuDNN
- Might be slightly slower than pure faster-whisper

---

### Option 3: Use OpenAI Whisper (Fallback, Slower)

**What is OpenAI Whisper:**
- Original Whisper implementation
- Pure PyTorch (works with bundled cuDNN)
- Slower than faster-whisper/WhisperX (~10x vs 30x real-time)

**Steps:**
1. Install: `pip install openai-whisper`
2. Update processing script
3. Works immediately with existing GPU/PyTorch setup

**Pros:**
- Zero setup (works with PyTorch's cuDNN)
- Known to work
- Simple API

**Cons:**
- **Slower:** ~10x real-time vs 30x (still way better than 1.56x CPU!)
- Higher VRAM usage
- No speaker diarization

---

## Performance Comparison

| Solution | Speed (large-v3) | Speaker Diarization | Setup Complexity | Works Now? |
|----------|------------------|---------------------|------------------|------------|
| **faster-whisper (current)** | 30x real-time | ❌ No | High (cuDNN install) | ❌ No |
| **WhisperX** | 25-30x real-time | ✅ YES | Medium (pip install) | ❓ Unknown |
| **OpenAI Whisper** | 10x real-time | ❌ No | Low (pip install) | ✅ Yes |
| **CPU fallback (current state)** | 1.56x real-time | ❌ No | None | ✅ Yes (slow) |

---

## Time Impact for 50 Episodes

**Assumptions:**
- 50 episodes × 70 min avg = 3,500 minutes of audio

| Solution | Processing Time | Time vs CPU |
|----------|----------------|-------------|
| **faster-whisper GPU (30x)** | 1.9 hours | **48x faster** |
| **WhisperX GPU (25x)** | 2.3 hours | **38x faster** |
| **OpenAI Whisper GPU (10x)** | 5.8 hours | **15x faster** |
| **CPU (current, 1.56x)** | **90 hours** | 1x (baseline) |

---

## Recommendation

### If you want speaker diarization (WHO said WHAT):
→ **Option 2: WhisperX**

**Why:**
- Chat recommended it (external research validation)
- Speaker diarization is HUGE for intelligence analysis (identify speakers in multi-person podcasts)
- Should work with PyTorch's bundled cuDNN (no manual install)
- Only slightly slower than pure faster-whisper

**Risk:** Might still need standalone cuDNN (unknown until we test)

---

### If you want fastest possible (speed > features):
→ **Option 1: Install cuDNN 9.x**

**Why:**
- Fastest inference (30x real-time)
- Already built processing infrastructure
- Most efficient use of GPU

**Cost:** 30-60 min setup time + NVIDIA account

---

### If you want it working NOW (low risk):
→ **Option 3: OpenAI Whisper**

**Why:**
- Works immediately
- Still 15x faster than CPU (5.8 hours vs 90 hours)
- No setup complexity

**Tradeoff:** 3x slower than faster-whisper/WhisperX

---

## My Recommendation

**Try WhisperX first (Option 2):**

```bash
# Test WhisperX installation and GPU support
pip3 install whisperx --break-system-packages

# Quick test
python3 -c "import whisperx; print('WhisperX OK')"

# Test GPU acceleration with tiny model
whisperx test_audio.mp3 --model tiny --device cuda --output_dir /tmp/whisperx_test
```

**If WhisperX fails due to cuDNN:**
→ Fall back to OpenAI Whisper (Option 3)

**If you want cuDNN anyway:**
→ I can guide you through Option 1 installation

---

## Next Steps

**Awaiting your decision:**
1. **Try WhisperX** (recommended - speaker diarization + speed)
2. **Install cuDNN 9.x** (fastest, but complex setup)
3. **Use OpenAI Whisper** (works now, slower but acceptable)

**Once you decide, I'll:**
- Install the chosen solution
- Update processing scripts
- Run a full test on one episode
- Restart the 50-episode batch processing

---

**Analysis by:** Claude (Sonnet 4.5)
**Timestamp:** 2025-12-09 20:28 UTC
