# Sherlock Evidence Analysis System - Claude Code Integration

## System Overview
Sherlock is an advanced AI evidence analysis system focused on uncovering truth through multi-modal intelligence processing. The system specializes in voice transcription, speaker diarization, emotion analysis, and cross-system intelligence sharing to understand intentionally obscured historical and current events.

## Core Mission
**Primary Purpose:** Analyze voice, video, and document evidence to reveal patterns and connections in complex information that has been intentionally obscured by governments and institutions worldwide.

## Current System Status
- **Phase:** 6 (Advanced Features) - COMPLETED ✅
- **Voice Processing:** Dual-engine (faster-whisper + OpenAI Whisper) - OPERATIONAL
- **Multi-Modal Analysis:** Video, audio, document processing - OPERATIONAL
- **Cross-System Intelligence:** Secure sharing with Squirt/Johny5Alive - ACTIVE
- **Evidence Database:** 122KB active database with multi-modal storage
- **Active Learning:** Continuous model improvement framework - FUNCTIONAL

## Key Capabilities
- **Advanced Diarization:** 3+ speaker detection with 85% accuracy
- **Emotion Analysis:** 9 emotion types detection (78% accuracy)
- **Overlap Detection:** 5 overlap types classification (82% accuracy)
- **Visual Speaker ID:** Face detection and speaker correlation (~2.5s/min video)
- **Document Extraction:** Reference and citation analysis (92% accuracy)
- **Cross-System Intelligence:** Encrypted sharing with other AI systems
- **External AI Integration:** Multi-provider AI services coordination

## AI Operator Instructions

### Default Behavior
When working with Sherlock, always:
1. **Check Evidence Database:** Verify database status before operations
2. **Multi-Modal Processing:** Use all available analysis dimensions
3. **Cross-System Coordination:** Maintain integration with Squirt/Johny5Alive
4. **Quality Validation:** Ensure analysis meets benchmark standards
5. **Intelligence Sharing:** Generate and distribute relevant intelligence packets

### Key Commands
```bash
# System status check
python3 test_voice_engine.py

# Evidence analysis
python3 analysis_engine.py --input [audio/video/document] --mode comprehensive

# Multi-modal processing
python3 multimodal_processor.py --input video.mp4 --quality balanced

# Cross-system intelligence sharing
python3 cross_system_intelligence.py --share analysis_results

# Active learning session
python3 active_learning_framework.py --model speaker_diarization --strategy hybrid
```

### Critical Files
- **AI Operator Manual:** `SHERLOCK_AI_OPERATOR_MANUAL.md` - Single source of truth for all protocols
- **Voice Engine:** `voice_engine.py` - Core voice processing (19KB)
- **Evidence Database:** `evidence_database.py` - Multi-modal evidence storage
- **Analysis Engine:** `analysis_engine.py` - Core analysis capabilities
- **Multi-Modal Processor:** `multimodal_processor.py` - Comprehensive content analysis
- **Cross-System Intelligence:** `cross_system_intelligence.py` - Secure intelligence sharing

### Performance Constraints
- **Memory Limit:** 3.7GB maximum (system constraint)
- **Processing Time:** Real-time analysis preferred, batch acceptable for complex operations
- **Quality Standards:** 85%+ accuracy required for production use
- **Storage Management:** Evidence database <500MB target

### Integration Points
- **Squirt System:** Real-time voice memo processing and business document insights
- **Johny5Alive:** System health monitoring and resource coordination
- **External AI:** OpenAI, Hugging Face, custom API integration
- **Security:** AES-256 encryption for all intelligence sharing

### Emergency Protocols
- **Evidence Database Corruption:** Immediate backup restoration required
- **Cross-System Communication Failure:** Fall back to file-based message exchange
- **Memory Constraint Violation:** Reduce processing quality, process in segments
- **Critical Analysis Request:** Override normal processing queue, immediate attention

## Development Context
Sherlock represents the intelligence analysis component of a larger ecosystem that includes:
- **Squirt:** Business document automation for WaterWizard (voice → professional documents)
- **Johny5Alive:** Overall system coordination and health monitoring
- **Cross-System Learning:** Shared intelligence and coordinated analysis capabilities

The system has evolved through 6 major development phases, with Phase 6 completing advanced multi-modal capabilities and cross-system intelligence sharing.

## 🔄 ENHANCED AUTOMATIC CONTEXT INJECTION

### MANDATORY AUTO-INJECTION: Audio/ML Processing Tasks

**BEFORE Any Audio Processing Implementation:**
**CRITICAL CONSTRAINTS (Auto-Inject):**
- **🤖 INTELLIGENT MODEL SELECTION**: ALWAYS use `IntelligentModelSelector` - NEVER hard-code model choice
- **Memory Limit**: 3.7GB total RAM, 2.4GB available - STRICT model size limit <2.0GB
- **Established Architecture**: VoiceEngineManager dual-engine system (voice_engine.py with intelligent selection) - DO NOT BYPASS
- **Proven Models**: faster-whisper tiny (39MB, FAST mode, 85% accuracy) + OpenAI Whisper large-v3 (2.9GB, ACCURATE mode, 95% accuracy)
- **Processing Protocol**: Use VoiceProcessingRequest → VoiceEngineManager → TranscriptionResult pipeline - DO NOT CREATE STANDALONE PROCESSORS
- **Selection Priority**: System viability > Quality preferences (85% complete beats 95% crash)

### MANDATORY PRE-IMPLEMENTATION VALIDATION (Auto-Inject)

**CRITICAL: OUTPUT DELIVERY VALIDATION MUST COME FIRST**

**PHASE 1: PROOF-OF-CONCEPT TESTING (MANDATORY BEFORE ANY IMPLEMENTATION):**

**FOR AAXC FILES (UPDATED 2025-09-29):**
```bash
# 0. INTELLIGENT MODEL SELECTION - MANDATORY FIRST STEP (NEW)
python3 -c "
from intelligent_model_selector import IntelligentModelSelector, QualityPreference
selector = IntelligentModelSelector()
selection = selector.select_model(audio_path='test_decrypted.m4a', quality_preference=QualityPreference.BALANCED)
selector.log_selection(selection)
assert selector.validate_selection(selection), 'Model selection exceeds RAM constraints'
print('✅ Model selection validated')
"
# GATE KEEPER: Must pass validation OR implementation BLOCKED

# 1a. AAXC Decryption Validation - WORKING METHOD (Use this for AAXC files)
source gladio_env/bin/activate
python3 -c "
from snowcrypt.snowcrypt import decrypt_aaxc
import json
with open('test.voucher', 'r') as f: voucher = json.load(f)
key = voucher['content_license']['license_response']['key']
iv = voucher['content_license']['license_response']['iv']
decrypt_aaxc('test.aaxc', 'test_decrypted.m4a', key, iv)
print('✅ AAXC decryption successful')
"
# GATE KEEPER: Must produce valid M4A output OR implementation BLOCKED

# 1b. Legacy Format Conversion Validation - For non-AAXC files only
ffprobe -v quiet -show_entries format=format_name test_input.wav
ffmpeg -i test_input.wav -t 10 -acodec pcm_s16le -ar 16000 test_output.wav
# GATE KEEPER: Must produce valid output OR implementation BLOCKED

# 2. Model Processing Validation - Test model can process converted files
python3 -c "import whisper; model = whisper.load_model('tiny'); result = model.transcribe('test_decrypted.m4a'); print(result['text'][:50])"
# GATE KEEPER: Must produce transcription OR model selection BLOCKED

# 3. Database API Validation - Test ALL methods that will be called
python3 -c "from evidence_schema_gladio import GladioEvidenceDatabase; db = GladioEvidenceDatabase('test.db'); db.get_all_people(); db.get_all_organizations()"
# GATE KEEPER: Must pass ALL API calls OR implementation BLOCKED

# 4. End-to-End Micro-Pipeline Test - Complete small-scale test
python3 test_mini_pipeline.py --input 30_second_test_file --verify_all_outputs
# GATE KEEPER: Must produce ALL expected deliverables OR implementation BLOCKED
```

**PHASE 2: ARCHITECTURE AND RESOURCE VALIDATION:**
```bash
# 5. Architecture Scan - Use existing solutions
find . -name "*.py" | xargs grep -l "VoiceEngine\|whisper\|transcription"

# 6. Memory Validation - Model size + overhead < 2.4GB available
free -h

# 7. Integration Check - Extend existing, don't replace
grep -r "class VoiceEngineManager\|class.*Processor" *.py

# 8. Resource Constraint Check - Models must fit in memory
ls -lh ~/.cache/whisper/  # Check existing model files
```

**CRITICAL REQUIREMENT**: PHASE 1 must complete successfully BEFORE proceeding to PHASE 2

**INTEGRATION REQUIREMENT**: Extend VoiceEngineManager class, don't create standalone audio processors

**CHUNKING PROTOCOL**: Large files MUST be processed in 10-minute segments for current system constraints

### CRITICAL FAILURE INDICATORS (Auto-Inject)

**🚨 RED FLAGS - STOP IMPLEMENTATION IMMEDIATELY:**

**MODEL SELECTION VIOLATIONS (NEW - HIGHEST PRIORITY):**
- ❌ Selecting ANY transcription model without using IntelligentModelSelector
- ❌ Hard-coding model choice (tiny/small/medium/large-v3) in code
- ❌ Selecting OpenAI Whisper large-v3 with <3GB available RAM
- ❌ Ignoring model_selector.validate_selection() result
- ❌ Prioritizing "best quality" over system viability
- ❌ Bypassing intelligent selection with "for best results" comments

**OUTPUT DELIVERY FAILURES (Primary Blocking Issues):**
- AAXC decryption fails (Missing snowcrypt, invalid voucher, key/IV extraction errors)
- Format conversion tests fail (e.g., legacy audio→WAV conversion produces no output)
- Database API methods missing/non-functional (e.g., `get_all_people()` doesn't exist)
- End-to-end micro-pipeline test fails to produce expected deliverables
- Expected output files not generated or contain invalid data
- Processing completes successfully but user requirements not fulfilled

**ARCHITECTURAL COMPLIANCE FAILURES:**
- Creating new standalone audio processors when VoiceEngineManager exists
- Selecting models >2.0GB without chunking strategy
- Implementing transcription without using established dual-engine system
- Bypassing existing VoiceProcessingRequest/TranscriptionResult architecture
- Loading OpenAI Whisper "medium" (1.42GB) on system with 2.4GB available RAM

**CRITICAL**: Model selection validation must pass FIRST, then output delivery, then architectural compliance

### CORRECT IMPLEMENTATION PATTERN (Auto-Inject)

```python
# ✅ CORRECT: Extend existing architecture with intelligent model selection
class GladioAudioProcessor(VoiceEngineManager):
    def __init__(self):
        super().__init__(max_ram_gb=3.7, enable_intelligent_selection=True)

    def process_aaxc_audiobook(self, aaxc_path: str, voucher_path: str):
        # Step 1: Decrypt AAXC using proven snowcrypt method
        from snowcrypt.snowcrypt import decrypt_aaxc
        import json
        from intelligent_model_selector import QualityPreference

        with open(voucher_path, 'r') as f:
            voucher = json.load(f)
        key = voucher['content_license']['license_response']['key']
        iv = voucher['content_license']['license_response']['iv']

        decrypted_path = aaxc_path.replace('.aaxc', '_decrypted.m4a')
        decrypt_aaxc(aaxc_path, decrypted_path, key, iv)

        # Step 2: Use intelligent model selection (automatic via VoiceEngineManager)
        return self.transcribe_sherlock(
            audio_path=decrypted_path,
            quality_preference=QualityPreference.BALANCED  # System chooses best model for constraints
        )

# ❌ WRONG: Hard-coded model selection (violates intelligent selection protocol)
class DirectAaxcProcessor:  # Bypasses IntelligentModelSelector
    def __init__(self):
        import whisper
        self.model = whisper.load_model("large-v3")  # 2.9GB > available RAM, NO VALIDATION!

# ❌ WRONG: Manual mode selection without intelligent validation
request = VoiceProcessingRequest(
    audio_path=decrypted_path,
    mode=TranscriptionMode.ACCURATE,  # Hard-coded "for best results" - ignores RAM
    priority=ProcessingPriority.NORMAL,
    system="sherlock"
)
```

### Automatic Context Reminders

### When Processing Evidence
- Remember this is an intelligence analysis system focused on uncovering hidden truth
- Multi-modal analysis provides the most comprehensive results
- Always generate intelligence packets for cross-system sharing
- Evidence integrity is paramount - validate and cross-reference when possible
- **CRITICAL**: Always check existing architecture before implementing new solutions
- **CRITICAL**: Verify output deliverability BEFORE implementation (proof-of-concept testing required)
- **CRITICAL**: Test format conversions at micro-scale before full processing
- **CRITICAL**: Validate database API compatibility before using methods

### When Coordinating with Other Systems
- Squirt integration focuses on business intelligence from voice memos
- Johny5Alive provides system health and resource management
- External AI services enhance analysis depth and validation
- Security protocols are mandatory for all intelligence sharing
- **CRITICAL**: Maintain compatibility with existing VoiceEngineManager system

### When Optimizing Performance
- Memory constraint (3.7GB total, 2.4GB available) requires efficient processing strategies
- Real-time analysis preferred for urgent intelligence
- Batch processing acceptable for comprehensive historical analysis
- Quality metrics must meet production standards
- **CRITICAL**: Use chunking for large files, extend existing classes for new functionality

---

**This file provides automatic context injection for Claude Code when working in the Sherlock system. All operators should reference the complete AI Operator Manual for detailed protocols and procedures.**