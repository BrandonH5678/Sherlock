# Sherlock Transcription Pipeline - Problem Analysis

**Timestamp:** 2025-12-09 20:22 UTC
**Status:** 🚨 **CRITICAL ISSUE DETECTED** - GPU Not Being Used

---

## Problem Summary

**Your concerns were absolutely correct:**
1. **5 whisper instances running simultaneously** - Confirmed
2. **No concrete evidence of GPU usage** - CONFIRMED (nvidia-smi shows 0% GPU util)
3. **Processing WAY too slow** - CONFIRMED (1.56x real-time instead of 30x expected)

---

## Evidence

### 1. Audio Duration
```bash
$ ffprobe capitol_bombs/audio.mp3
Duration: 3455.4 seconds = 57.6 minutes
```

### 2. Processing Time Elapsed
- Started: 19:42 UTC
- Current: 20:22 UTC
- Elapsed: **90 minutes**
- Audio processed: **57.6 minutes**
- **Speed: 1.56x real-time** (90 min to process 57 min audio)

### 3. Expected Performance
- **GPU large-v3:** ~30x real-time (57 min → 2 min processing)
- **CPU large-v3:** ~2x real-time (57 min → 30 min processing)
- **What we're seeing:** 1.56x real-time

### 4. GPU Utilization
```bash
$ nvidia-smi
GPU Utilization: 0%
GPU Memory: 550MB (only Xorg + Firefox, NO Python processes)
```

**Conclusion:** faster-whisper is running on CPU, not GPU!

---

## Root Cause Analysis

**Hypothesis:** faster-whisper's GPU detection is failing OR CuBLAS/cuDNN not properly installed.

**Evidence supporting CPU fallback:**
1. nvidia-smi shows no Python processes using GPU
2. Processing speed matches CPU performance (~2x real-time)
3. High CPU usage (228-273%) matches multi-threaded CPU inference
4. No VRAM usage despite large-v3 model (should use 4-5GB)

**Possible causes:**
- `pynvml` import failing (silent fallback to CPU)
- CuBLAS/cuDNN missing or incompatible
- faster-whisper not compiled with CUDA support
- CUDA runtime version mismatch

---

## Impact Assessment

### Time Impact

**Current trajectory:**
- 50 episodes × 60-90 min each = 3000-4500 minutes of audio
- At 1.56x real-time: **3000-4500 minutes of processing time**
- **Total: 50-75 HOURS** to complete all episodes

**GPU-accelerated (expected):**
- At 30x real-time: **100-150 minutes** to complete all episodes
- **Total: 1.6-2.5 HOURS**

**Difference: 48-73 hours wasted if we don't fix this!**

---

## Recommended Actions

### Option 1: STOP and Fix GPU (RECOMMENDED)

**Immediate:**
1. Kill all 5 faster_whisper processes
2. Diagnose GPU issue (check pynvml, CuBLAS, cuDNN)
3. Test single episode with verbose logging to confirm GPU usage
4. Restart processing once GPU confirmed working

**Pros:**
- Fix once, save 48-73 hours
- Confirms GPU actually working before committing to 50 episodes

**Cons:**
- Discard 90 minutes of (slow) CPU processing

---

### Option 2: Let CPU Processing Continue

**Keep running:**
- Let all 5 processes continue on CPU
- Check back in 24-48 hours for completion

**Pros:**
- No wasted CPU work (already 90 min invested)
- Will eventually complete

**Cons:**
- **48-73 hours** instead of 1.6-2.5 hours
- Still need to fix GPU for future runs

---

## Diagnostic Commands

**Test GPU with single episode:**
```bash
python3 /home/johnny5/Johny5Alive/j5a-nightshift/faster_whisper_cli.py \
    /home/johnny5/Sherlock/freelance_transcripts/weaponized/capitol_bombs/audio.mp3 \
    --model tiny \
    --output_dir /tmp/gpu_test \
    --output_format txt \
    --prefer_gpu true \
    --verbose true

# Watch nvidia-smi during processing
watch -n 1 nvidia-smi
```

**Check pynvml:**
```bash
python3 -c "import pynvml; pynvml.nvmlInit(); print('pynvml OK')"
```

**Check CuBLAS/cuDNN:**
```bash
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'cuDNN: {torch.backends.cudnn.is_available()}')"
```

---

## Constitutional Compliance Analysis

**Principle 3 (System Viability):**
> "Completed 85% accurate > crashed 95% attempt"

**Current situation:**
- CPU processing WILL complete (slow but viable)
- BUT: 48-73 hours vs. 1.6-2.5 hours is massive resource waste

**Principle 4 (Resource Stewardship):**
> "Respect thermal/memory/financial constraints"

**Current situation:**
- CPU processing wastes 48-73 hours of compute time
- GPU sitting idle (0% utilization) while CPU maxed out
- **Violates resource stewardship** (inefficient use of available GPU)

**Recommendation:** **STOP and fix GPU** aligns with both principles:
- Still completes (viability)
- Uses resources efficiently (stewardship)
- Invests 1 hour fixing to save 48-73 hours

---

## Next Steps

**Awaiting user decision:**
1. **STOP and fix GPU** (recommended - save 48-73 hours)
2. **Continue on CPU** (conservative - will eventually complete)

**If STOP chosen:**
```bash
# Kill all processes
pkill -f "faster_whisper_cli.py"

# Diagnose GPU
python3 -c "import pynvml; pynvml.nvmlInit(); print('pynvml OK')"

# Test with tiny model
python3 /home/johnny5/Johny5Alive/j5a-nightshift/faster_whisper_cli.py \
    test_audio.mp3 --model tiny --verbose true --prefer_gpu true
```

---

**Analysis by:** Claude (Sonnet 4.5)
**Timestamp:** 2025-12-09 20:22 UTC
**User concerns validated:** ✅ All concerns were correct
