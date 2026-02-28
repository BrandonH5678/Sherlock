# PKG-911: 9/11 Financial Foreknowledge & War on Terror Profiteering Network
## Campaign Status Document — Single Source of Truth

**Campaign ID:** PKG-911
**Created:** 2026-02-28
**Model Assignment:** Opus (analysis/orchestration/synthesis) | Sonnet (search/retrieval/ingestion)

---

## SESSION RESUME
> **Read this section first at every session start.**

**Current Phase:** Phase 0 COMPLETE — Phase 1 PENDING
**Last Completed Action:** Target registration (IDs 59-68), context-refresh enhancement, campaign doc created
**Next Action:** Launch Opus agent for Phase 1 — Krongard/Alex. Brown biographical research
**DB State at Last Save:** 283 claims/xrefs (pre-campaign) | 68 targets | 39 sources

**To resume:** Run `/context-refresh` → read this file → proceed to next action above.

---

## Target Registry

| ID | Name | Type | Priority | Status |
|----|------|------|----------|--------|
| 59 | Alvin "Buzzy" Krongard | person | CRITICAL | registered |
| 60 | Alex. Brown / Deutsche Bank Alex. Brown | org | CRITICAL | registered |
| 61 | Howard Krongard | person | HIGH | registered |
| 62 | Cheryl Gordon Krongard | person | HIGH | registered |
| 63 | Rothschild Asset Management | org | MEDIUM | registered |
| 64 | Erik Prince | person | HIGH | registered |
| 65 | Blackwater / Academi | org | HIGH | registered |
| 66 | Leon Black | person | HIGH | registered (6 existing claims) |
| 67 | Mark Rowan | person | MEDIUM | registered |
| 68 | Apollo Global Management | org | HIGH | registered |

**Skipped:** "Al Carter" — operator confirmed name uncertain; omit pending clarification.

---

## Research Phase Status

- [x] **Phase 0: Setup** — targets registered, context-refresh enhanced, campaign doc created
- [ ] **Phase 1: Krongard / Alex. Brown biography** (Opus)
  - [ ] `evidence/krongard_research_phase1_alex_brown.md`
  - [ ] `evidence/krongard_research_phase2_cia.md`
- [ ] **Phase 2: Krongard family circuit** (Opus)
  - [ ] `evidence/krongard_research_phase3_howard_ig.md`
  - [ ] `evidence/krongard_research_phase4_cheryl_conflict.md`
- [ ] **Phase 3: Blackwater / Erik Prince** (Opus)
  - [ ] `evidence/prince_research_phase1_blackwater.md`
  - [ ] `evidence/prince_research_phase2_operations.md`
- [ ] **Phase 4: Leon Black / Apollo / Mark Rowan** (Sonnet search + Opus synthesis)
  - [ ] `evidence/apollo_research_phase1_origins.md`
  - [ ] `evidence/apollo_research_phase2_defense.md`
  - [ ] `evidence/apollo_research_phase3_black_epstein.md`
  - [ ] `evidence/apollo_research_phase4_rowan.md`
- [ ] **Phase 5: Rothschild Asset Management** (Sonnet)
  - [ ] `evidence/rothschild_research_phase1_asset_mgmt.md`
- [ ] **Phase 6: 9/11 Financial Nexus Synthesis** (Opus)
  - [ ] `evidence/pkg911_financial_nexus_synthesis.md`
- [ ] **Phase 7: Retriever Deployment** (Sonnet)
  - [ ] `scripts/pkg911_academic_papers_retriever.py` **PRIORITY 1**
  - [ ] `scripts/pkg911_alex_brown_puts_retriever.py` **PRIORITY 2**
  - [ ] `scripts/pkg911_sec_filings_retriever.py`
  - [ ] `scripts/pkg911_congressional_retriever.py`
  - [ ] `scripts/pkg911_dod_contracts_retriever.py`
  - [ ] `scripts/pkg911_foia_retriever.py`
- [ ] **Phase 8: Final Reports + Ingestion** (Opus reports, Sonnet scripts)
  - [ ] `evidence/krongard_intelligence_report.md`
  - [ ] `evidence/alex_brown_intelligence_report.md`
  - [ ] `evidence/howard_krongard_intelligence_report.md`
  - [ ] `evidence/blackwater_intelligence_report.md`
  - [ ] `evidence/apollo_intelligence_report.md`
  - [ ] `evidence/pkg911_network_intelligence_report.md`
  - [ ] `scripts/ingest_pkg911_krongard.py`
  - [ ] `scripts/ingest_pkg911_blackwater.py`
  - [ ] `scripts/ingest_pkg911_apollo.py`
  - [ ] `scripts/ingest_pkg911_rothschild.py`
  - [ ] DB ingestion executed + verified

---

## Key Analytical Hypotheses

| ID | Hypothesis | Confidence | Status |
|----|-----------|-----------|--------|
| H1 | Krongard Cover-Up Mechanism: ran Alex. Brown during put options → CIA → shaped/suppressed SEC-CIA assessment | 0.45 | UNDER INVESTIGATION |
| H2 | Krongard Family Circuit: Buzzy (CIA) + Howard (IG blocking) + Cheryl (IG capture) = integrated protection circuit | 0.70 | STRUCTURAL CONFIRMED, OPERATIONAL PENDING |
| H3 | Alex. Brown → Deutsche Bank → Epstein institutional continuity chain | 0.65 | PENDING PHASE 1 |
| H4 | Apollo/Drexel → BCCI era finance parallel (structural) | 0.35 | PENDING PHASE 4 |
| H5 | War on Terror profiteering circuit: Blackwater → CIA → IG protection → Apollo → political cover | 0.55 | PENDING PHASES 3-4 |

---

## Critical Existing DB Cross-Links

| New Target | Existing Target/Claim | Chain | Priority |
|-----------|----------------------|-------|----------|
| Buzzy Krongard | Target 34 (Tenet) | CIA Exec Dir under Tenet | CRITICAL |
| Buzzy Krongard | xref_ep_055 (Staley-Tenet) | Krongard was #3 at CIA during Tenet-Epstein comms | HIGH |
| Alex. Brown | Target 54 (9/11 Financial Foreknowledge) | Primary put options executing broker | CRITICAL |
| Alex. Brown | Deutsche Bank (6 existing claims) | Deutsche Bank acquired Alex. Brown 1999 | HIGH |
| Leon Black | xref_ep_034 (0.99), ST-028, FXR-006 | $170M Epstein payments already confirmed | HIGH |
| Howard Krongard | Target 65 (Blackwater) | IG blocked Blackwater investigations | HIGH |
| Rothschild AM | WEX-060 | $25M Epstein-Rothschild agreement | MEDIUM |

---

## Priority Evidence to Retrieve (Phase 7)

### E1 Academic Papers (highest priority)
1. **Poteshman (2006)** — "Unusual Option Market Activity and the Terrorist Attacks of September 11, 2001," *Journal of Business* (UIUC). Statistical proof of informed trading in UAL puts.
2. **Chesney, Crameri & Dâne (2011/2012)** — Swiss Finance Institute. Broader scope: airlines + financial firms + WTC tenants. Multiple statistically anomalous securities.
3. Any additional peer-reviewed follow-up or rebuttals.

### Alex. Brown as Primary Put Options Conduit (E1/E2 expected)
- 9/11 Commission Staff Reports (financial investigation monographs)
- Senate Intelligence Committee Joint Inquiry (2002) — financial foreknowledge section
- IOSCO full report (not just LCF-007 summary)
- WSJ/Bloomberg contemporaneous coverage citing SEC investigation and Alex. Brown

---

## Claim ID Prefixes

| Prefix | Target |
|--------|--------|
| BZK | Alvin "Buzzy" Krongard |
| ABR | Alex. Brown / Deutsche Bank Alex. Brown |
| HOK | Howard Krongard |
| CGK | Cheryl Gordon Krongard |
| ROT | Rothschild Asset Management |
| ERP | Erik Prince |
| BWK | Blackwater / Academi |
| LBK | Leon Black (extending existing claims) |
| MRW | Mark Rowan |
| APL | Apollo Global Management |
| P911 | Campaign-level cross-references |

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `scripts/ingest_wexner_dynasty.py` | Ingestion template (100 claims, 30 xrefs) |
| `scripts/ingest_greenberg.py` | Ingestion template (45 claims) |
| `scripts/epstein_web_intelligence.py` | Retriever script architecture |
| `evidence/SHERLOCK-20260222-006_lutnick_cantor_fitzgerald_9-11_intelligence_nexus.md` | Existing 9/11 research — DO NOT DUPLICATE |
| `evidence/greenberg_dynasty_intelligence_report.md` | Final report format |
| `.claude/plans/rustling-scribbling-kurzweil.md` | Full implementation plan |

---

## DB State Log

| Date | Phase | Claims | Xrefs | Sources | Targets |
|------|-------|--------|-------|---------|---------|
| 2026-02-28 | Phase 0 complete | 782 | 283 | 39 | 68 |

---

## Current Phase: Phase 1 — PENDING
## Next Action: Launch Opus agent — Krongard/Alex. Brown biographical research
