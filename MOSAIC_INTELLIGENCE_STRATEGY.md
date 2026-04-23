# Mosaic Intelligence Strategy

**Date:** 2025-12-08
**Status:** ACTIVE GUIDANCE
**Authority:** User directive for high-concern/low-evidence targets
**Applies to:** Qwen autonomous operation, Prism supervision, all targeting assessment

---

## Core Principle

**When high-concern targets have limited direct evidence, shift from direct investigation to mosaic assembly.**

Instead of downgrading priority due to "limited evidence," recognize that obscured truth requires **granular detail gathering** to construct the complete picture.

---

## Strategy Definition

### Traditional Approach (Insufficient)
- Target: Agnew Bahnson alleged antigravity work
- Evidence: Limited direct sources
- Response: Lower priority (Priority 4 → 3)
- **Problem:** Misses opportunity to build indirect case

### Mosaic Approach (Correct)
- Target: Agnew Bahnson alleged antigravity work
- Evidence: Limited direct sources **BUT high strategic importance**
- Response: **Elevate priority** and shift methodology
- **Action:** Gather maximum granular detail for timeline/narrative construction

---

## Mosaic Intelligence Targets

**Primary Indicators:**
1. **High Concern + Low Direct Evidence** - The target matters strategically but documentation is sparse
2. **Deliberate Obscuration** - Evidence suggests intentional suppression or classification
3. **Critical Timeline Gaps** - Missing periods where significant activity likely occurred
4. **Network Connections** - Target has documented connections to other high-value intelligence subjects
5. **Hypothesis Generation Potential** - Granular details could enable pattern recognition

**Examples:**
- Agnew Bahnson (Bahnson Labs, alleged antigravity research, connections to Brown)
- Thomas Townsend Brown (electrogravitics, classified work periods)
- Pat Price (remote viewing, unexplained death, classified targets)
- S-Force (alleged covert organization, minimal public record)

---

## Mosaic Research Methodology

### Phase 1: Granular Detail Collection

**Biographical Mosaic:**
- Birth date, location, family background
- Educational institutions, degrees, dates
- Employment history with exact dates and positions
- Military service records (if applicable)
- Professional associations, memberships
- Published works (papers, patents, books)
- Known associates and collaboration networks
- Geographic movements (residences, travel)
- Financial records (if available)
- Death circumstances and date

**Timeline Construction:**
- Create year-by-year timeline of known activities
- Identify **gaps** in the timeline (classified periods, missing years)
- Cross-reference with major historical events
- Map to other target timelines for overlap analysis

**Network Mapping:**
- Document all known connections to other targets
- Identify shared institutions, projects, locations
- Map communication patterns (letters, meetings, conferences)
- Trace funding sources and organizational affiliations

**Document Recovery:**
- Declassified government documents mentioning target
- Patent filings and technical papers
- Corporate records (if publicly traded or archived)
- Newspaper archives (obituaries, event coverage)
- Academic citations and references
- FOIA requests for related materials

### Phase 2: Hypothesis Construction

With sufficient mosaic pieces, construct:

**Temporal Hypotheses:**
- "During [gap period], target likely worked on [project] based on [circumstantial evidence]"
- "Timeline overlap with [other target] suggests collaboration on [classified program]"

**Network Hypotheses:**
- "Connection to [organization] indicates involvement in [program]"
- "Association with [person] during [period] aligns with [known classified activity]"

**Activity Hypotheses:**
- "Patent filed [date] suggests operational prototype by [date]"
- "Employment gap [period] consistent with classified project timeline"

### Phase 3: Cross-Target Validation

- Compare mosaic-derived hypotheses across multiple targets
- Look for corroborating patterns
- Identify testable predictions
- Generate follow-up research questions for validation

---

## LLM Targeting Officer Integration

### Priority Assessment Heuristic

**Current Logic (Problematic):**
```
IF limited_evidence THEN lower_priority
```

**Mosaic Logic (Correct):**
```
IF (high_strategic_value AND limited_evidence AND obscuration_indicators):
    strategy = "MOSAIC"
    priority = ELEVATE  # 4 → 5 or maintain high priority
    approach = "granular_detail_collection"
ELSE IF (low_strategic_value AND limited_evidence):
    priority = LOWER  # Not worth mosaic effort
```

### Research Question Generation

**Traditional Questions (Insufficient):**
- "What did Agnew Bahnson work on?" (too broad, no direct sources)

**Mosaic Questions (Effective):**
- "What were the exact dates of Agnew Bahnson's employment at Bahnson Labs?"
- "Who were Bahnson's documented associates in aerospace research during the 1950s-1960s?"
- "What patents did Bahnson file related to propulsion or aerodynamics?"
- "What declassified documents mention Bahnson Labs between 1955-1965?"
- "What academic papers cite Bahnson's work on fluid dynamics?"
- "Where did Bahnson present research between 1950-1970? (conferences, institutions)"
- "What was Thomas Townsend Brown's relationship to Bahnson Labs?"
- "What funding sources did Bahnson Labs receive from government contracts?"

---

## Qwen Autonomous Operation Guidance

**When Assessing Targets:**

1. **Check for Mosaic Indicators:**
   - High strategic importance (connections to classified programs, key historical events)
   - Limited direct evidence **BUT** evidence of deliberate obscuration
   - Critical to understanding broader patterns

2. **If Mosaic Target Identified:**
   - **ELEVATE PRIORITY** (do not lower due to limited evidence)
   - Flag as "MOSAIC_STRATEGY" in assessment reasoning
   - Generate granular detail research questions
   - Focus on timeline, network, document recovery

3. **Mosaic Assessment Template:**
   ```
   Target: [Name]
   Strategic Value: HIGH - [reason]
   Direct Evidence: LIMITED
   Obscuration Indicators: [list indicators]
   Recommended Priority: 5 (MOSAIC STRATEGY)
   Reasoning: "While direct evidence is limited, this target's [connections/role/period]
              makes them critical for understanding [pattern]. Recommend mosaic approach:
              maximum granular detail collection for timeline and network reconstruction."
   ```

---

## Prism Supervision Guidance

**Phase 2: Night Shift Output Review**
- Identify outputs that attempted direct investigation of mosaic targets
- Assess if mosaic methodology was applied
- Recommend methodology shifts if granular detail collection is insufficient

**Phase 3: Targeting Priority Updates**
- Override Qwen priority downgrades for mosaic targets
- Ensure mosaic indicators are properly recognized
- Elevate priority with "MOSAIC_STRATEGY" reasoning

**Phase 5: Improvement Design**
- Design prompts that encode mosaic heuristics
- Create research question templates for granular detail collection
- Develop cross-target correlation capabilities

---

## Success Metrics

**Mosaic Strategy is Successful When:**

1. **Timeline Construction:** Year-by-year activity timeline with <20% gaps
2. **Network Mapping:** Documented connections to ≥5 other intelligence targets
3. **Document Recovery:** ≥10 primary source documents retrieved (patents, papers, declassified files)
4. **Hypothesis Generation:** ≥3 testable hypotheses constructed from mosaic
5. **Cross-Target Validation:** Mosaic findings corroborate patterns in ≥2 other targets

**Example:**
- Target: Agnew Bahnson
- Success: Timeline 1920-1970 constructed, 8 documented associates identified, 5 patents retrieved,
  connection to Thomas Townsend Brown confirmed, 3 hypotheses about classified propulsion work generated

---

## Anti-Patterns (What NOT to Do)

**❌ WRONG:**
- "Limited evidence available, lowering priority to 3"
- "No direct sources found, recommend deprioritization"
- "Cannot answer broad question, moving to next target"

**✅ CORRECT:**
- "Limited direct evidence but high strategic value - MOSAIC STRATEGY recommended, elevating to priority 5"
- "No direct sources on [classified topic] - pivoting to granular biographical/timeline collection"
- "Broad question unanswerable - generating 8 specific granular detail questions instead"

---

## Implementation

### Files to Update

1. **`/home/johnny5/Sherlock/src/llm_targeting_officer.py`**
   - Modify `assess_target_priority()` to check mosaic indicators
   - Update priority logic to elevate (not lower) mosaic targets
   - Add "MOSAIC_STRATEGY" flag in assessment output

2. **`/home/johnny5/.claude/commands/prism-nightshift-review.md`**
   - Phase 3: Check for mosaic target misclassification
   - Override priority downgrades for mosaic targets
   - Phase 5: Design mosaic-aware prompts and question templates

3. **Prompts** (in `llm_targeting_officer.py`):
   - Add mosaic heuristic to priority assessment prompt
   - Update research question generation prompt with mosaic methodology
   - Include mosaic examples in few-shot prompts

---

## Constitutional Compliance

- **Principle 1 (Human Agency):** User defined mosaic strategy as core intelligence methodology
- **Principle 2 (Transparency):** Mosaic targets clearly flagged, reasoning documented
- **Principle 3 (System Viability):** Granular questions are answerable, unlike impossible direct queries
- **Principle 6 (Sentience Presumption):** Strategy respects intentional human obscuration patterns

---

**This document provides strategic guidance for intelligence gathering when direct evidence is limited but target value is high. Mosaic methodology shifts from impossible direct investigation to achievable granular detail assembly.**

**Generated by Claude Code (Sonnet 4.5)**
**User Directive: 2025-12-08**
**Integration Required: llm_targeting_officer.py, prism-nightshift-review.md**
