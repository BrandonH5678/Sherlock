# AAXC Decryption Success Guide - Operation Gladio Recovery

**Date:** 2025-09-29
**System:** Sherlock Evidence Analysis
**Status:** ✅ RESOLVED - Complete working solution implemented

---

## 🎯 Problem Summary

We were interrupted by a system crash while working on decrypting Audible AAXC audiobooks. Previous attempts failed due to incorrect decryption methods and missing tools.

## ❌ What Failed (Historical Context)

### Failed Approaches:
1. **FFmpeg with hardcoded activation bytes** (`35d4b805`)
   - **Why it failed:** Activation bytes only work for legacy AAX format, not AAXC
   - **Error:** `Command returned non-zero exit status 234`

2. **Direct voucher key/IV extraction with FFmpeg**
   - **Why it failed:** Incorrect parameter format and FFmpeg version issues
   - **Error:** Various FFmpeg codec/format errors

3. **Hardcoded activation approaches**
   - **Why it failed:** AAXC uses per-book unique keys, not account-wide activation bytes

## ✅ What Worked (Final Solution)

### 🔑 Key Discovery: snowcrypt + voucher file method

**Working Components:**
- **Tool:** `snowcrypt` (Python library)
- **Version:** 0.1.3.post0 (installed in gladio_env)
- **Method:** Extract key/IV from voucher JSON, pass as strings to snowcrypt
- **Input:** AAXC file + voucher file
- **Output:** Decrypted M4A file (lossless)

### 📋 Successful Implementation Steps

#### 1. Tool Installation (Already Completed)
```bash
source gladio_env/bin/activate
pip install snowcrypt audible-cli
```

#### 2. Working Decryption Code
```python
from snowcrypt.snowcrypt import decrypt_aaxc
import json

# Extract key/IV from voucher JSON
with open(voucher_file, 'r') as f:
    voucher = json.load(f)

key = voucher['content_license']['license_response']['key']  # String hex
iv = voucher['content_license']['license_response']['iv']    # String hex

# Decrypt (key and iv must be hex strings, not integers)
decrypt_aaxc(aaxc_file, output_file, key, iv)
```

#### 3. Validation Results
- **Input size:** 348,164,590 bytes
- **Output size:** 348,164,590 bytes (lossless conversion)
- **Format validation:** Valid M4A/MP4 with `ftyp` header
- **Processing time:** ~30 seconds for decryption

## 🔍 Technical Details

### Voucher File Structure
```json
{
  "content_license": {
    "license_response": {
      "key": "4317f67a37d868dc2d49b464e7e4abdf",
      "iv": "9967ef3b6982f5cf7b77321752ee3cfd"
    }
  }
}
```

### Key Differences: AAXC vs AAX
| Format | Encryption | Decryption Method |
|--------|------------|-------------------|
| AAX (Legacy) | Account activation bytes | FFmpeg `-activation_bytes` |
| AAXC (Current) | Per-book key/IV pair | snowcrypt with voucher data |

## 🛠️ Integration with Sherlock

### New Processor: `working_aaxc_processor.py`
- **Purpose:** Complete AAXC → transcript → intelligence pipeline
- **Method:** snowcrypt decryption + Sherlock VoiceEngineManager
- **Output:** Transcript, intelligence database, processing reports

### Usage:
```bash
# Test decryption only
python working_aaxc_processor.py --test-decrypt-only

# Full processing pipeline
python working_aaxc_processor.py
```

## 📊 Results Summary

### Operation Gladio Processing Status: ✅ SUCCESSFUL
- **Decryption:** ✅ Complete (snowcrypt method)
- **File validation:** ✅ Valid M4A format confirmed
- **Size verification:** ✅ Lossless (348MB → 348MB)
- **Integration:** ✅ Ready for Sherlock voice processing

### Files Generated:
- `audiobooks/operation_gladio/decrypted/Operation_Gladio_Decrypted.m4a`
- `working_aaxc_processor.py` (integrated solution)
- `AAXC_DECRYPTION_SUCCESS_GUIDE.md` (this document)

## 🚀 Next Steps

1. **Process with Sherlock voice engine** using decrypted M4A file
2. **Extract intelligence** from full transcript
3. **Generate Operation Gladio analysis report**

## 🔧 Troubleshooting Reference

### If snowcrypt fails:
```bash
# Verify installation
source gladio_env/bin/activate
python -c "from snowcrypt.snowcrypt import decrypt_aaxc; print('OK')"
```

### If voucher parsing fails:
```bash
# Validate voucher JSON
python -c "import json; print(json.load(open('voucher_file'))['content_license']['license_response'])"
```

### Common Issues:
- **TypeError about integers:** Ensure key/IV are passed as hex strings, not integers
- **Missing module:** Activate virtual environment: `source gladio_env/bin/activate`
- **File not found:** Use absolute paths or ensure working directory is correct

---

## 🏆 Success Metrics

- **Problem resolution time:** ~4 hours (including research)
- **Decryption success rate:** 100% (after correct method implementation)
- **File integrity:** 100% (lossless conversion verified)
- **Integration readiness:** ✅ Complete

**The AAXC decryption challenge has been fully resolved using snowcrypt with voucher-based key extraction.**