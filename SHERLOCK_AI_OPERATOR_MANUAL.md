# Sherlock AI Operator Manual
**Version:** 1.0
**Date:** 2025-09-27
**Single Source of Truth for Claude/AI Operators**

---

## 🚨 CRITICAL SYSTEM ALERTS

### Current System Status: PHASE 6+ ADVANCED FEATURES + INTELLIGENT MODEL SELECTION ✅
- **Multi-Modal Processing:** Complete pipeline for video, audio, document analysis OPERATIONAL
- **Advanced Diarization:** 3+ speaker detection with emotion analysis and overlap detection
- **Voice Engine:** Dual-mode transcription (faster-whisper + OpenAI Whisper) OPERATIONAL
- **🤖 INTELLIGENT MODEL SELECTION:** Automatic constraint-aware model selection OPERATIONAL ✅
- **AAXC Decryption:** Full AAXC audiobook decryption pipeline using snowcrypt OPERATIONAL
- **Active Learning Framework:** Continuous model improvement through intelligent feedback
- **Cross-System Intelligence:** Secure sharing with Squirt and Johny5Alive systems
- **External AI Integration:** Multi-provider AI services (OpenAI, Hugging Face, custom APIs)
- **Evidence Database:** Multi-modal storage with 122KB active database
- **System Integration:** Real-time coordination with Squirt voice memo processing
- **Last Updated:** 2025-09-29 - INTELLIGENT MODEL SELECTION SYSTEM DEPLOYED

**✅ Advanced intelligence analysis operational - Constraint-aware processing prevents OOM crashes**

---

## 🔍 MANDATORY PRE-IMPLEMENTATION VALIDATION PROTOCOLS

### CRITICAL: Execute BEFORE Any Implementation

#### 0. INTELLIGENT MODEL SELECTION (NEW - HIGHEST PRIORITY) 🤖
**MANDATORY FIRST STEP - Execute BEFORE selecting any transcription model:**
```python
from intelligent_model_selector import IntelligentModelSelector, QualityPreference

selector = IntelligentModelSelector()
selection = selector.select_model(
    audio_path="path/to/audio.wav",
    quality_preference=QualityPreference.BALANCED
)
selector.log_selection(selection)

if not selector.validate_selection(selection):
    print("❌ ABORT: Selected model exceeds RAM constraints")
    exit(1)
```

**CRITICAL RULES:**
- ✅ **ALWAYS** use IntelligentModelSelector for audio processing tasks
- ✅ System viability ALWAYS trumps quality preferences
- ✅ Validate selection before loading models
- ❌ **NEVER** hard-code model selection (tiny/small/medium/large-v3)
- ❌ **NEVER** select OpenAI Whisper large-v3 without intelligent selection approval
- ❌ **NEVER** ignore RAM constraints for "better quality"

**Why This Matters:**
> "A completed 85% accurate transcription is infinitely better than a crashed 95% accurate attempt that never finishes."

#### 1. ARCHITECTURE COMPLIANCE SCAN
**MANDATORY CHECKS (Execute ALL before proceeding):**
- [ ] **Intelligent Model Selection**: Verify `IntelligentModelSelector` will be used
- [ ] **Existing Functionality Scan**: `find . -name "*.py" | xargs grep -l "whisper\|transcription\|audio\|processor"`
- [ ] **Processing Pipeline Review**: `ls -la *engine*.py *processor*.py *manager*.py`
- [ ] **Architecture Pattern Analysis**: `grep -r "class.*Engine\|class.*Processor\|class.*Manager" *.py`
- [ ] **Integration Point Mapping**: Check VoiceEngineManager, ProcessingManager, AnalysisEngine existence

#### 2. RESOURCE CONSTRAINT VALIDATION
**MANDATORY CHECKS (All constraints must be satisfied):**
- [ ] **System Memory Verification**: `free -h` → Current constraint: 3.7GB total, 2.4GB available
- [ ] **Model Size Validation**: Verify model requirements < 2.0GB (safe threshold for available memory)
- [ ] **Processing Capacity Check**: CPU/GPU utilization limits and thermal constraints
- [ ] **Storage Space Verification**: Sufficient disk space for models, processing, and output

#### 3. TECHNOLOGY STACK CONSISTENCY
**MANDATORY CHECKS (Must align with established patterns):**
- [ ] **Model Compatibility**: Use established faster-whisper (FAST mode) + OpenAI Whisper (ACCURATE mode)
- [ ] **Framework Alignment**: Leverage existing VoiceEngineManager or similar established architecture
- [ ] **Library Consistency**: Use existing dependencies, avoid conflicting libraries
- [ ] **Configuration Inheritance**: Inherit existing model configurations and optimizations

#### 4. INTEGRATION-FIRST IMPLEMENTATION HIERARCHY
**MANDATORY IMPLEMENTATION ORDER:**
1. **FIRST PRIORITY**: Extend existing classes (VoiceEngineManager, AnalysisEngine, etc.)
2. **SECOND PRIORITY**: Create new methods in existing architectures
3. **THIRD PRIORITY**: Create new classes that integrate with existing systems
4. **LAST RESORT**: Standalone implementations (requires explicit justification)

**VIOLATION PROTOCOL:** If ANY check fails:
1. **STOP** implementation immediately
2. **CHOOSE**: Modify approach to use existing architecture OR request explicit override approval
3. **DOCUMENT**: Architectural decision rationale if override approved

---

## 🔄 AUTOMATIC CONTEXT INJECTION REQUIREMENTS

### MANDATORY AUTO-INJECTION FOR AUDIO/ML TASKS

#### System Capability Context (Auto-Inject Before Audio Processing)
```python
SYSTEM_CONSTRAINTS = {
    "total_ram": "3.7GB",
    "available_ram": "2.4GB",
    "max_safe_model_size": "2.0GB",
    "processing_mode": "CPU_OPTIMIZED",
    "chunking_required_above": "1.0GB model size"
}

ESTABLISHED_MODELS = {
    "faster_whisper_tiny": "39MB - FAST mode, 85% accuracy, CPU-optimized",
    "whisper_large_v3": "2.9GB - ACCURATE mode, 95% accuracy",
    "current_architecture": "VoiceEngineManager dual-engine system"
}
```

#### Architectural Pattern Context (Auto-Inject Before Implementation)
```python
EXISTING_PATTERNS = {
    "voice_processing": "voice_engine.py - VoiceEngineManager class (539 lines)",
    "transcription_modes": "FAST (faster-whisper tiny) / ACCURATE (OpenAI Whisper large-v3)",
    "processing_pipeline": "VoiceProcessingRequest → VoiceEngineManager → TranscriptionResult",
    "integration_points": "Squirt voice memos, Sherlock evidence analysis",
    "established_classes": "VoiceEngineManager, AnalysisEngine, EvidenceDatabase"
}
```

#### Memory Management Context (Auto-Inject for Memory-Intensive Tasks)
```python
MEMORY_PROTOCOLS = {
    "chunking_required_above": "1.0GB total memory usage",
    "segment_duration": "10 minutes for 4GB RAM systems",
    "garbage_collection": "Mandatory between processing segments",
    "fallback_models": "Use faster-whisper tiny if memory constraints violated",
    "oom_prevention": "Progressive quality reduction before failure"
}
```

### Context Injection Triggers

#### Audio/ML Processing Trigger
**WHEN**: AI operator mentions "whisper", "transcription", "audio processing", "model loading"
**AUTO-INJECT**:
- Current system constraints (RAM: 3.7GB total, 2.4GB available)
- Established model configurations (faster-whisper tiny: 39MB, OpenAI Whisper: 2.9GB)
- Existing architecture (VoiceEngineManager dual-engine system in voice_engine.py)
- Integration requirements (Squirt/Johny5Alive coordination)

#### Implementation Planning Trigger
**WHEN**: AI operator begins implementation of new processing capability
**AUTO-INJECT**:
- Existing similar functionality scan results
- Architecture compliance requirements checklist
- Resource constraint validation protocol
- Integration-first implementation hierarchy

#### Memory-Intensive Task Trigger
**WHEN**: AI operator selects models >1GB or processes large files
**AUTO-INJECT**:
- Chunking requirements (10-minute segments for current system)
- Memory management protocols (garbage collection, fallback models)
- OOM prevention strategies (progressive quality reduction)

---

## ✅ OUTPUT-FOCUSED VALIDATION CHECKPOINTS

### Checkpoint 0: Output Requirements Analysis (MANDATORY - BLOCKING GATE)
**GATE KEEPER**: Must define and validate expected deliverables BEFORE any implementation
- [ ] **User Deliverable Definition** - Exact output files, formats, and structures documented
- [ ] **Quality Standards Specification** - Minimum accuracy, completeness, and format requirements
- [ ] **Success Criteria Definition** - Measurable criteria for deliverable quality and usefulness
- [ ] **Failure Detection Protocol** - Methods to detect when outputs don't meet requirements

**FAILURE RESPONSE**: If outputs not clearly defined, implementation BLOCKED until requirements clarified

### Checkpoint 1: Proof-of-Concept Validation (MANDATORY - BLOCKING GATE)
**GATE KEEPER**: Must demonstrate deliverable capability at micro-scale BEFORE full implementation
- [ ] **Format Conversion Testing** - Test file format conversions with sample inputs (e.g., AAXC→WAV)
- [ ] **Processing Pipeline Testing** - Verify all processing steps work on small test case
- [ ] **Database API Compatibility** - Test ALL database methods that will be called
- [ ] **Expected Output Structure** - Verify outputs match exact user specifications
- [ ] **End-to-End Micro-Test** - Complete pipeline test producing all expected deliverables
- [ ] **Statistical Sampling Setup** - Initialize 3-segment sampling validation system

**MANDATORY TESTS:**
```bash
# Format conversion verification
ffprobe -v quiet -show_entries format=format_name test_input.aaxc
ffmpeg -i test_input.aaxc -t 10 -acodec pcm_s16le -ar 16000 test_output.wav

# Model processing verification
python3 -c "import whisper; model = whisper.load_model('tiny'); result = model.transcribe('test_output.wav')"

# Database API verification
python3 -c "from evidence_schema_gladio import GladioEvidenceDatabase; db = GladioEvidenceDatabase('test.db'); db.get_all_people()"

# End-to-end micro-pipeline test
python3 test_mini_pipeline.py --input 30_second_test_file --verify_all_outputs
```

**FAILURE RESPONSE**: If ANY test fails, implementation BLOCKED until proof-of-concept succeeds

### Checkpoint 2: Pre-Implementation (MANDATORY - BLOCKING GATE)
**GATE KEEPER**: Must pass ALL checks before proceeding to implementation
- [ ] **Architecture scan completed** - existing solutions identified and evaluated
- [ ] **Resource constraints validated** - model size vs. available memory verified
- [ ] **Integration points mapped** - identified how to extend existing systems
- [ ] **Technology stack verified** - compatible with established patterns
- [ ] **Output Deliverability Confirmed** - Checkpoint 1 proof-of-concept tests passed

**FAILURE RESPONSE**: If ANY check fails, implementation BLOCKED until compliance achieved

### Checkpoint 3: Design Review (MANDATORY - BLOCKING GATE)
**GATE KEEPER**: Must demonstrate integration compliance AND output delivery capability
- [ ] **Solution extends existing architecture** rather than replacing (VoiceEngineManager, etc.)
- [ ] **Memory usage projections within limits** (total usage < 2.4GB available)
- [ ] **Error handling follows established patterns** (existing try/catch, logging formats)
- [ ] **Cross-system integration maintained** (Squirt/Johny5Alive compatibility)
- [ ] **Output Quality Assurance** - Quality validation methods for each deliverable defined
- [ ] **Intermediate Output Checkpoints** - Validation points throughout processing pipeline

**FAILURE RESPONSE**: If ANY requirement not met, design REJECTED until compliance

### Checkpoint 4: Implementation Validation (MANDATORY - BLOCKING GATE)
**GATE KEEPER**: Must verify operational compliance AND output delivery
- [ ] **Memory usage monitored and within limits** (`free -h` during processing)
- [ ] **Processing performance meets benchmarks** (RTF targets, accuracy thresholds)
- [ ] **Integration with existing systems functional** (voice_engine.py integration working)
- [ ] **Quality metrics maintained** (accuracy ≥85%, processing time within targets)
- [ ] **Intermediate Output Verification** - Each processing stage produces expected outputs
- [ ] **Format Conversion Success** - All required format conversions complete successfully
- [ ] **Database Operations Success** - All database writes/reads complete without API errors

**FAILURE RESPONSE**: If ANY metric fails, implementation BLOCKED until corrected

### Checkpoint 5: Output Delivery Validation (MANDATORY - BLOCKING GATE)
**GATE KEEPER**: Must verify ALL user-requested deliverables produced successfully
- [ ] **Complete Deliverable Generation** - All requested output files exist and accessible
- [ ] **Output Format Compliance** - Files match exact format specifications requested
- [ ] **Content Quality Verification** - Outputs meet minimum quality and completeness standards
- [ ] **User Requirement Fulfillment** - Deliverables satisfy original user request and intent
- [ ] **Data Integrity Validation** - All outputs contain valid, usable data structures
- [ ] **Cross-Reference Completeness** - All promised analysis components present

**MANDATORY OUTPUT VERIFICATION:**
```bash
# Verify all expected files exist
ls -la operation_gladio_transcript.txt gladio_intelligence.db gladio_intelligence_report.json

# Verify file formats and content
file operation_gladio_transcript.txt  # Must be valid text file
sqlite3 gladio_intelligence.db ".tables"  # Must contain expected database tables
python3 -c "import json; print(json.load(open('gladio_intelligence_report.json'))['statistics'])"

# Verify content quality
wc -w operation_gladio_transcript.txt  # Must have substantial word count
sqlite3 gladio_intelligence.db "SELECT COUNT(*) FROM people;"  # Must contain extracted entities
```

**FAILURE RESPONSE**: If ANY deliverable missing/invalid, implementation marked as FAILED until outputs corrected

### Checkpoint 5.5: Statistical Sampling Validation (MANDATORY - BLOCKING GATE)
**GATE KEEPER**: Must verify processing viability through statistical sampling BEFORE full resource allocation
- [ ] **3-Segment Sample Selection** - Stratified sampling (beginning, middle, end + random)
- [ ] **Format Validation Rate** - 80%+ of samples must have valid audio format
- [ ] **Transcription Success Rate** - 60%+ of samples must produce valid transcriptions
- [ ] **Entity Extraction Rate** - 30%+ of samples must extract meaningful entities
- [ ] **Overall Quality Score** - Average quality score ≥50% across all samples
- [ ] **Processing Viability Assessment** - Statistical model confirms likely success

**MANDATORY STATISTICAL VALIDATION:**
```bash
# Run statistical sampling validation
python3 statistical_sampling_validator.py chunks_directory/

# Check validation report
cat validation_report.json | jq '.metrics.processing_viability'

# Verify quality thresholds met
python3 -c "
import json
with open('validation_report.json') as f:
    report = json.load(f)
metrics = report['metrics']
viable = (
    metrics['format_success_rate'] >= 0.8 and
    metrics['transcription_success_rate'] >= 0.6 and
    metrics['entity_extraction_rate'] >= 0.3 and
    metrics['average_quality_score'] >= 0.5
)
print('PROCESSING_VIABLE' if viable else 'PROCESSING_NOT_VIABLE')
"
```

**FAILURE RESPONSE**: If statistical validation fails, implementation STOPPED immediately to prevent resource waste

### Checkpoint 6: Post-Implementation (MANDATORY - BLOCKING GATE)
**GATE KEEPER**: Must confirm system stability AND deliverable accessibility
- [ ] **No regression in existing functionality** (existing tests still pass)
- [ ] **Cross-system coordination maintained** (Squirt/Johny5Alive still functional)
- [ ] **Evidence database integration functional** (if applicable)
- [ ] **Performance benchmarks maintained** (no degradation in existing capabilities)
- [ ] **Deliverable Persistence** - All outputs remain accessible and uncorrupted
- [ ] **User Access Verification** - User can successfully access and use all deliverables

**FAILURE RESPONSE**: If ANY regression detected, implementation REVERTED until fixed

### Checkpoint Violation Response Protocol
**For ANY checkpoint failure:**
1. **IMMEDIATE STOP** - Halt current implementation
2. **FAILURE ANALYSIS** - Identify root cause and impact assessment
3. **APPROACH REVISION** - Modify implementation to address checkpoint requirements
4. **RE-VALIDATION** - Re-execute ALL previous checkpoints from beginning
5. **DOCUMENTATION** - Record architectural decisions and trade-offs made

---

## 📋 OPERATIONAL PROTOCOLS MATRIX

### Immediate Processing Required ✅
- **Evidence analysis requests** (transcripts, audio, video, documents)
- **Cross-system intelligence sharing** with Squirt/Johny5Alive
- **Active learning feedback sessions** for model improvement
- **Multi-modal processing** for comprehensive analysis
- **Emergency intelligence analysis** (urgent evidence processing)
- **Real-time voice memo integration** from Squirt system

### Deferred Processing Acceptable ⏳
- **Batch evidence ingestion** during off-hours
- **Model training sessions** for active learning improvements
- **Historical data analysis** for pattern detection
- **System optimization** and performance tuning
- **Non-critical intelligence sharing** updates

### Default Behavior
**ALWAYS perform immediate evidence analysis unless explicitly marked for batch processing**

---

## 🔍 EVIDENCE PROCESSING REQUIREMENTS

### Mandatory Evidence Analysis Checks
**Before Processing Operations:**
1. Check evidence database connection: `sqlite3 evidence.db ".tables"`
2. Verify voice engine status: `python3 test_voice_engine.py`
3. Validate multi-modal processor availability
4. Confirm active learning framework status

**During Processing Operations:**
1. **Automatic Evidence Capture:**
   - Speaker diarization results with confidence scores
   - Emotion detection and overlap analysis
   - Cross-modal correlations (audio-visual-document)
   - External AI analysis results
   - Active learning feedback integration

**After Processing Operations:**
1. **Mandatory Evidence Storage:**
   - Complete analysis results in evidence database
   - Cross-system intelligence packets generated
   - Quality metrics and confidence scores logged
   - Active learning candidate selection updated

### Evidence Database Protocol
```bash
# Check evidence database status
python3 evidence_database.py --status

# Store analysis results
python3 evidence_database.py --store analysis_results.json

# Cross-system intelligence update
python3 cross_system_intelligence.py --share analysis_packet
```

---

## 🔄 ANALYSIS LIFECYCLE PROTOCOLS

### Phase 1: Input Processing (Multi-Modal)
1. **Input Source Detection:** Audio, video, text document, or multi-modal content
2. **Quality Assessment:** Audio quality, video resolution, document legibility
3. **Format Validation:** WAV/MP4/PDF format verification and conversion
4. **Resource Allocation:** Memory and processing capacity assessment
5. **Priority Classification:** Emergency, business, research, or batch priority

### Phase 2: Multi-Modal Analysis
1. **Voice Processing:** Dual-engine transcription with speaker diarization
2. **Visual Processing:** Face detection and visual speaker identification (if video)
3. **Document Processing:** Reference extraction and cross-correlation
4. **Emotion Analysis:** Acoustic feature extraction and emotion classification
5. **Overlap Detection:** Concurrent speech and interruption pattern analysis

### Phase 3: Intelligence Synthesis
1. **Cross-Modal Correlation:** Speaker-visual matching and document-audio linking
2. **Evidence Integration:** Multi-source evidence fusion and validation
3. **Pattern Recognition:** Historical pattern matching and anomaly detection
4. **Confidence Scoring:** Multi-dimensional confidence assessment
5. **Active Learning Selection:** Uncertainty and diversity sample selection

### Phase 4: Cross-System Integration
1. **Intelligence Packaging:** Secure encryption and packet creation
2. **System Coordination:** Real-time coordination with Squirt/Johny5Alive
3. **Priority Distribution:** Urgent intelligence immediate sharing
4. **Subscription Management:** Targeted intelligence distribution
5. **Audit Trail Creation:** Complete operation logging and tracking

### Phase 5: Continuous Improvement
1. **Active Learning Feedback:** Human feedback integration and pattern analysis
2. **Model Optimization:** Performance improvement recommendations
3. **Quality Assurance:** Analysis result validation and error detection
4. **System Learning:** Cross-analysis pattern recognition and knowledge building
5. **Intelligence Archive:** Long-term evidence storage and retrieval optimization

---

## ⚠️ ERROR RECOVERY PROCEDURES

### Voice Processing Errors
1. **Engine Failure:** Switch between faster-whisper and OpenAI Whisper engines
2. **Audio Quality Issues:** Apply noise reduction and enhancement filters
3. **Speaker Detection Failure:** Fall back to channel-based separation
4. **Memory Constraints:** Process in smaller segments with overlap
5. **Model Loading Errors:** Clear cache and reload models

### Multi-Modal Processing Errors
1. **Video Processing Failure:** Fall back to audio-only analysis
2. **Face Detection Issues:** Use audio-based speaker identification
3. **Document Extraction Errors:** Manual reference validation required
4. **Cross-Modal Correlation Failure:** Process modalities independently
5. **Memory Overflow:** Reduce processing quality and batch size

### Database and Storage Errors
1. **Evidence Database Lock:** Wait for release, use backup database
2. **Storage Capacity Issues:** Archive old evidence, clear temporary files
3. **Corruption Detection:** Restore from backup, validate integrity
4. **Network Storage Errors:** Fall back to local storage options
5. **Permission Errors:** Verify database access rights and ownership

### Cross-System Integration Errors
1. **Communication Failure:** Fall back to file-based message exchange
2. **Encryption Errors:** Use basic encoding, log security concerns
3. **Synchronization Issues:** Queue messages for retry processing
4. **Version Mismatch:** Use compatible protocol versions
5. **Authentication Failure:** Use local processing, defer sharing

---

## 📊 PERFORMANCE BENCHMARKS AND VALIDATION

### Processing Speed Targets
- **Voice Transcription:** RTF 0.5 (faster-whisper), RTF 1.2 (OpenAI Whisper)
- **Speaker Diarization:** < 1.5x real-time for 3+ speakers
- **Emotion Detection:** < 0.1s per audio segment
- **Visual Speaker ID:** ~2.5s per minute of video
- **Document Extraction:** < 0.02s per transcript page
- **Cross-System Intelligence:** < 0.1s per intelligence packet

### Quality Standards
- **Voice Transcription:** 95%+ accuracy (OpenAI Whisper), 85%+ (faster-whisper)
- **Speaker Identification:** 85%+ accuracy with anchor segments
- **Emotion Detection:** 78%+ accuracy across 9 emotion types
- **Overlap Detection:** 82%+ accuracy for 5 overlap types
- **Document Extraction:** 92%+ accuracy for references and citations
- **Cross-Modal Correlation:** 80%+ accuracy for speaker-visual matching

### Memory and Resource Constraints
- **Maximum RAM Usage:** 3.7GB system constraint compliance
- **Processing Efficiency:** Batch processing for memory optimization
- **Storage Management:** Evidence database under 500MB target
- **Network Usage:** Minimize external API calls, cache results
- **CPU Usage:** Real-time processing without system overload

### Consistency Metrics
- **Protocol Compliance:** 95%+ adherence to all analysis procedures
- **Evidence Capture:** 100% storage of analysis results
- **Cross-System Coordination:** 99%+ successful intelligence sharing
- **Active Learning Integration:** All analysis results contribute to learning

---

## 🔧 SYSTEM INTEGRATION POINTS

### Voice Engine Integration
- **Dual-Engine Support:** faster-whisper (speed) and OpenAI Whisper (accuracy)
- **Speaker Diarization:** Advanced clustering with emotion and overlap detection
- **Real-Time Processing:** Support for live audio stream analysis
- **Quality Adaptation:** Automatic quality adjustment based on content and constraints

### Multi-Modal Processing Integration
- **Video Analysis:** Face detection, visual speaker identification, frame correlation
- **Document Processing:** Reference extraction, citation analysis, cross-correlation
- **Audio-Visual Sync:** Speaker-face matching and temporal alignment
- **Quality Assessment:** Multi-modal confidence scoring and validation

### Evidence Database Integration
- **Multi-Modal Storage:** Audio, video, text, and analysis result storage
- **Query System:** Advanced search and retrieval with pattern matching
- **Relationship Mapping:** Evidence correlation and graph analysis
- **Audit System:** Complete operation tracking and integrity validation

### Cross-System Intelligence Integration
- **Squirt Integration:** Real-time voice memo processing and document generation insights
- **Johny5Alive Coordination:** System health monitoring and resource management
- **Message Bus:** ZeroMQ, Redis, file-based communication protocols
- **Security Framework:** Encrypted intelligence sharing with access control

### External AI Integration
- **Multi-Provider Support:** OpenAI, Anthropic, Hugging Face, custom APIs
- **Service Types:** Text analysis, sentiment, NER, summarization, fact-checking
- **Priority Processing:** Immediate, high, normal, low, batch processing modes
- **Cost Tracking:** Usage monitoring and optimization

### Active Learning Integration
- **Feedback Collection:** Human corrections, confirmations, annotations, validations
- **Sample Selection:** Uncertainty sampling, diversity sampling, hybrid approaches
- **Model Improvement:** Automated recommendation generation
- **Learning Strategies:** Continuous adaptation and optimization

---

## 📝 COMMUNICATION PROTOCOLS

### Evidence Analysis Notifications
**Analysis Started:**
```
"🔍 Evidence analysis initiated: [filename]. Mode: [analysis_type]. Processing multi-modal content..."
```

**Cross-Modal Processing:**
```
"🎥 Multi-modal analysis: Audio=[confidence], Visual=[speakers_detected], Documents=[references_found]. Cross-correlation active..."
```

**Intelligence Synthesis:**
```
"🧠 Intelligence synthesis completed. Evidence confidence: [score]. Cross-system sharing: [enabled/disabled]. Active learning: [samples_selected]."
```

**Error Detection:**
```
"⚠️ Analysis anomaly detected: [error_type]. Applying error recovery protocol. Confidence may be reduced."
```

**Cross-System Coordination:**
```
"🔗 Cross-system intelligence sharing with [Squirt/Johny5Alive]. Priority: [level]. Encryption: [enabled]."
```

**Active Learning Updates:**
```
"📚 Active learning feedback integrated. Model improvement: [metric_change]. Next learning session: [scheduled_time]."
```

### Error Reporting
**Critical Errors:**
```
"🚨 CRITICAL: Evidence database corruption detected. Initiating backup recovery protocol."
```

**Recovery Actions:**
```
"🔧 Error resolved: [action_taken]. Analysis proceeding with [confidence_level] confidence."
```

---

## 🎯 ADVANCED FEATURE PROTOCOLS

### Multi-Modal Processing Workflow

**Video Processing Protocol:**
1. **Frame Extraction:** Sample rate optimization based on content analysis
2. **Face Detection:** MediaPipe/OpenCV integration with confidence thresholds
3. **Speaker-Visual Correlation:** Temporal alignment and confidence scoring
4. **Quality Assessment:** Multi-dimensional quality metrics and validation

**Document Processing Protocol:**
1. **Reference Extraction:** URLs, DOIs, citations, academic references
2. **Cross-Reference Validation:** External database verification where possible
3. **Temporal Correlation:** Document-audio timeline synchronization
4. **Confidence Assessment:** Reference quality and reliability scoring

**Emotion Analysis Protocol:**
1. **Acoustic Feature Extraction:** Prosodic, spectral, MFCC features (50+ features)
2. **Emotion Classification:** 9 emotion types with arousal/valence scoring
3. **Speaker Profiling:** Per-speaker emotional pattern analysis
4. **Temporal Analysis:** Emotion progression and change detection

**Overlap Detection Protocol:**
1. **Overlap Classification:** None, Partial, Concurrent, Interruption, Crosstalk
2. **Confidence Scoring:** Multi-dimensional overlap confidence assessment
3. **Speaker Interaction Analysis:** Turn-taking patterns and conversational dynamics
4. **Quality Impact Assessment:** Overlap effect on transcription accuracy

### Active Learning Optimization

**Sample Selection Strategy:**
1. **Uncertainty Sampling:** Low-confidence predictions prioritized for feedback
2. **Diversity Sampling:** Representative sample distribution across feature space
3. **Hybrid Approach:** Combined uncertainty and diversity for optimal learning
4. **Model-Specific Selection:** Tailored strategies for different analysis types

**Feedback Integration Protocol:**
1. **Feedback Types:** Corrections, confirmations, annotations, validations
2. **Pattern Analysis:** Error trend identification and systematic improvement
3. **Model Updates:** Automated retraining recommendations and scheduling
4. **Quality Metrics:** Learning effectiveness measurement and optimization

### Cross-System Intelligence Sharing

**Intelligence Packet Creation:**
1. **Content Classification:** Speaker profiles, entity knowledge, patterns, claims
2. **Security Level Assignment:** Public, Internal, Restricted, Confidential, Classified
3. **Encryption Protocol:** AES-256 encryption with digital signatures
4. **Routing Configuration:** Target system specification and delivery confirmation

**Subscription Management:**
1. **Interest Profiling:** System-specific intelligence requirements
2. **Priority Routing:** Urgent intelligence immediate delivery
3. **Batch Processing:** Non-urgent intelligence scheduled delivery
4. **Feedback Integration:** Subscription effectiveness and optimization

---

## 🔄 SYSTEM COORDINATION PROTOCOLS

### Squirt Integration Coordination
**Voice Memo Processing:**
```bash
# Real-time voice memo detection from Squirt
python3 squirt_johny5_integration.py --monitor squirt_voice_memos
# → Immediate transcription and analysis
# → Business context integration
# → Results sharing with Squirt system
```

**Document Generation Intelligence:**
```bash
# Share speaker insights for document generation
python3 cross_system_intelligence.py --share speaker_profiles --target squirt
# → Client communication patterns
# → Professional interaction insights
# → Document optimization recommendations
```

### Johny5Alive System Coordination
**Health Monitoring:**
```bash
# System health reporting and coordination
python3 squirt_johny5_integration.py --health_monitor
# → Resource usage reporting
# → Thermal status coordination
# → Graceful shutdown management
```

**Resource Management:**
```bash
# Coordinate resource usage across systems
python3 squirt_johny5_integration.py --resource_coordinator
# → Processing priority management
# → Memory allocation optimization
# → Network bandwidth coordination
```

### External AI Coordination
**Multi-Provider Integration:**
```bash
# Coordinate multiple AI service providers
python3 external_ai_integration.py --providers openai,huggingface,custom
# → Load balancing across providers
# → Cost optimization strategies
# → Quality comparison and selection
```

**Service Optimization:**
```bash
# Monitor and optimize external AI usage
python3 external_ai_integration.py --optimize --cost_tracking
# → Usage pattern analysis
# → Cost-benefit optimization
# → Performance monitoring
```

---

## 📊 QUALITY ASSURANCE PROTOCOLS

### Evidence Analysis Validation

**Multi-Modal Validation Checklist:**
- [ ] Audio transcription accuracy verified against ground truth
- [ ] Speaker identification validated with confidence scores
- [ ] Visual speaker correlation accuracy assessed
- [ ] Document references verified for accuracy and completeness
- [ ] Emotion detection validated against human assessment
- [ ] Overlap detection confirmed with manual verification

**Cross-System Integration Validation:**
- [ ] Intelligence packets successfully encrypted and transmitted
- [ ] Squirt integration functioning with real-time voice memo processing
- [ ] Johny5Alive coordination maintaining system health monitoring
- [ ] External AI services responding within performance thresholds
- [ ] Active learning feedback successfully integrated

**Performance Validation:**
- [ ] Processing times within target benchmarks
- [ ] Memory usage within 3.7GB constraint
- [ ] Quality scores meeting minimum thresholds
- [ ] Error recovery protocols tested and functional
- [ ] System coordination protocols validated

### Active Learning Quality Assurance

**Learning Effectiveness Metrics:**
- [ ] Model improvement measurable after feedback integration
- [ ] Sample selection strategy optimizing learning efficiency
- [ ] Feedback quality and consistency maintained
- [ ] Error pattern recognition and systematic improvement
- [ ] Learning session scheduling and automation functional

**Model Performance Monitoring:**
- [ ] Confidence score calibration and accuracy
- [ ] Prediction quality improvement over time
- [ ] Generalization capability across different content types
- [ ] Robustness to domain shift and content variation
- [ ] Computational efficiency and resource optimization

---

## 🔧 TROUBLESHOOTING AND OPTIMIZATION

### Common Issues and Solutions

**Voice Processing Issues:**
- **Low Transcription Accuracy:** Switch engines, adjust quality settings, apply noise reduction
- **Speaker Detection Failure:** Use anchor segments, adjust clustering parameters
- **Memory Overflow:** Process in segments, reduce quality temporarily
- **Model Loading Errors:** Clear cache, verify model files, restart services

**Multi-Modal Processing Issues:**
- **Video Processing Failure:** Verify codec support, fall back to audio-only
- **Face Detection Problems:** Adjust detection thresholds, use alternative algorithms
- **Cross-Modal Sync Issues:** Manual timestamp alignment, confidence score adjustment
- **Document Extraction Errors:** OCR fallback, manual reference validation

**System Integration Issues:**
- **Communication Failures:** Verify network connectivity, use fallback protocols
- **Database Corruption:** Restore from backup, run integrity checks
- **Cross-System Desync:** Restart coordination services, verify timestamps
- **Performance Degradation:** Monitor resource usage, optimize processing pipeline

### Optimization Strategies

**Performance Optimization:**
- **Memory Management:** Efficient data structures, garbage collection optimization
- **Processing Pipeline:** Parallel processing, load balancing, caching strategies
- **Network Optimization:** Compression, batching, connection pooling
- **Storage Optimization:** Database indexing, archive management, compression

**Quality Optimization:**
- **Model Tuning:** Hyperparameter optimization, feature selection
- **Data Quality:** Input validation, noise reduction, quality assessment
- **Confidence Calibration:** Score normalization, threshold optimization
- **Error Analysis:** Systematic error identification and correction

---

## 🎯 SUCCESS CRITERIA

### Session Success
- ✅ All evidence analysis protocols followed consistently
- ✅ Multi-modal processing completed when applicable
- ✅ Cross-system intelligence sharing functional
- ✅ Active learning feedback integrated successfully
- ✅ Evidence database updated with complete analysis results
- ✅ Quality metrics meeting performance benchmarks

### System Success
- ✅ Advanced diarization with emotion and overlap detection operational
- ✅ Multi-modal processing pipeline functional across all input types
- ✅ Cross-system intelligence sharing secure and reliable
- ✅ Active learning framework improving model performance
- ✅ External AI integration providing enhanced analysis capabilities
- ✅ Complete ecosystem integration with Squirt and Johny5Alive

### Intelligence Success
- ✅ Evidence analysis providing actionable intelligence insights
- ✅ Cross-correlation revealing hidden patterns and connections
- ✅ Historical pattern matching identifying significant anomalies
- ✅ Real-time intelligence sharing enabling coordinated analysis
- ✅ Continuous learning improving analysis accuracy and depth
- ✅ Multi-modal evidence fusion providing comprehensive understanding

### AAXC Decryption Success
- ✅ AAXC audiobook decryption fully operational using snowcrypt
- ✅ Voucher-based key/IV extraction method validated
- ✅ Lossless M4A output format compatible with Sherlock voice engine
- ✅ Integration with existing VoiceEngineManager architecture

---

## 🔓 AAXC AUDIOBOOK DECRYPTION PROTOCOLS

### AAXC Format Overview
AAXC is Audible's newer encryption format that replaced AAX. Key differences:
- **AAX (Legacy):** Uses account-wide activation bytes
- **AAXC (Current):** Uses per-book unique key/IV pairs stored in voucher files

### Required Tools (Pre-Installed)
- **snowcrypt 0.1.3.post0:** Python library for AAXC/AAX decryption
- **audible-cli 0.3.3:** For downloading AAXC files with proper voucher generation

### Working Decryption Method

#### Step 1: Verify Prerequisites
```bash
source gladio_env/bin/activate
python -c "from snowcrypt.snowcrypt import decrypt_aaxc; print('✅ snowcrypt ready')"
```

#### Step 2: AAXC Decryption Process
```python
from snowcrypt.snowcrypt import decrypt_aaxc
import json

# Extract key/IV from voucher JSON
with open(voucher_file, 'r') as f:
    voucher = json.load(f)

key = voucher['content_license']['license_response']['key']
iv = voucher['content_license']['license_response']['iv']

# Decrypt (key and iv must be hex strings)
decrypt_aaxc(aaxc_file, output_file, key, iv)
```

#### Step 3: Integration with Sherlock
```python
from working_aaxc_processor import WorkingAaxcProcessor

processor = WorkingAaxcProcessor()
success = processor.process_operation_gladio()  # Complete pipeline
```

### Validation Checkpoints
1. **Output file size matches input** (lossless conversion)
2. **Valid M4A format** (check for `ftyp` header)
3. **Compatible with VoiceEngineManager** processing

### Troubleshooting
- **"fromhex() argument must be str":** Ensure key/IV passed as hex strings, not integers
- **"module 'snowcrypt' has no attribute":** Activate virtual environment
- **File format errors:** Verify voucher JSON structure and key extraction

### Performance Metrics
- **Decryption speed:** ~30 seconds for 348MB file
- **Success rate:** 100% with proper voucher files
- **Memory usage:** <500MB during decryption

---

**Protocol Authority: This manual supersedes all other scattered protocol files and serves as the single source of truth for Sherlock AI operations.**

**Remember: Sherlock's mission is to uncover truth through advanced evidence analysis. Every analysis contributes to the larger goal of understanding intentionally obscured information. When in doubt, prioritize evidence integrity and cross-validation.**