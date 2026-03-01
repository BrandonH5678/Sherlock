# PKG-911: 9/11 Financial Foreknowledge & War on Terror Profiteering Network
## Campaign Status Document — Single Source of Truth

**Campaign ID:** PKG-911
**Created:** 2026-02-28
**Model Assignment:** Opus (analysis/orchestration/synthesis) | Sonnet (search/retrieval/ingestion)

---

## SESSION RESUME
> **Read this section first at every session start.**

**Current Phase:** Phases 2-5 COMPLETE — Phase 6 NEXT
**Last Completed Action:** Phase 5 Sonnet research complete — `rothschild_research_phase1_asset_mgmt.md` (413 lines)
**Next Action:** Launch Opus agent for Phase 6 — 9/11 Financial Nexus Synthesis
**DB State at Last Save:** 782 claims | 283 xrefs | 39 sources | 68 targets (pre-ingestion; all research files written)

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
- [x] **Phase 1: Krongard / Alex. Brown biography** (Opus) — COMPLETE 2026-02-28
  - [x] `evidence/krongard_research_phase1_alex_brown.md` (528 lines)
  - [x] `evidence/krongard_research_phase2_cia.md` (544 lines)
- [x] **Phase 2: Krongard family circuit** (Opus) — COMPLETE 2026-02-28
  - [x] `evidence/krongard_research_phase3_howard_ig.md` (423 lines)
  - [x] `evidence/krongard_research_phase4_cheryl_conflict.md` (417 lines)
- [x] **Phase 3: Blackwater / Erik Prince** (Opus) — COMPLETE 2026-02-28
  - [x] `evidence/prince_research_phase1_blackwater.md` (664 lines)
  - [x] `evidence/prince_research_phase2_operations.md` (679 lines)
- [x] **Phase 4: Leon Black / Apollo / Mark Rowan** (Opus) — COMPLETE 2026-02-28
  - [x] `evidence/apollo_research_phase1_origins.md`
  - [x] `evidence/apollo_research_phase2_defense.md`
  - [x] `evidence/apollo_research_phase3_black_epstein.md`
  - [x] `evidence/apollo_research_phase4_rowan.md`
- [x] **Phase 5: Rothschild Asset Management** (Sonnet) — COMPLETE 2026-02-28
  - [x] `evidence/rothschild_research_phase1_asset_mgmt.md` (413 lines)
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
| H1 | Krongard Cover-Up Mechanism: ran Alex. Brown during put options → CIA → shaped/suppressed SEC-CIA assessment | **0.25-0.35** (revised down from 0.45 — H0 coincidence 0.45-0.55 competes) | PHASE 1 COMPLETE — UNRESOLVED |
| H2 | Krongard Family Circuit: Buzzy (CIA) + Howard (IG blocking) + Cheryl (IG capture) = integrated protection circuit | **TWO-NODE CONFIRMED 0.95; THREE-NODE NOT CONFIRMED 0.15** — Cheryl NOT on State IG Advisory Board; she was Senior Partner at Apollo Management 2002-2004 — creates Apollo-Krongard circuit instead | PHASE 2 COMPLETE — REVISED |
| H3 | Alex. Brown → Deutsche Bank → Epstein institutional continuity chain | 0.65 | PHASE 1 CONFIRMED — Deutsche Bank acquired Alex. Brown 1999; institutional continuity documented |
| H4 | Apollo/Drexel → BCCI era finance parallel (structural) | **Direct org connection 0.10; structural parallel 0.90** — Bear Stearns identified as bridge node between ecosystems | PHASE 4 COMPLETE |
| H5 | War on Terror profiteering circuit: Blackwater → CIA → IG protection → Apollo → political cover | **Apollo classified PERIPHERAL NODE** — direct WoT profiteering 0.10; Blackwater circuit fully confirmed (Buzzy + Howard + CPA Order 17 + pardons); Apollo Epstein link is primary not WoT | PHASES 3-4 COMPLETE |

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
| **NEW** Cheryl Krongard | Apollo Global Management (Target 68) | Cheryl was Senior Partner at Apollo Management 2002-2004 — creates Apollo-Krongard circuit | HIGH |
| **NEW** Erik Prince / Blackwater | CIA-to-Blackwater pipeline | Krongard, Cofer Black, Robert Richer, Enrique Prado all transitioned to Blackwater 2004-2007; 4 most senior CIA CT officers to same private company | HIGH |
| **NEW** Erik Prince | FSG / CITIC Group (China state-owned) | Prince built China-backed PMC (FSG) post-Blackwater; CI risk 0.75 — former CIA contractor partnered with Chinese state entity | HIGH |
| **NEW** Rothschild (EdR) | WEX-060 EXTENDED — E1 primary source | $25M contract Oct 5, 2015 between Epstein's Southern Trust Co. and Edmond de Rothschild Holding S.A. (Ariane de Rothschild); activated within 3 days of EdR's $45.245M DOJ settlement; Epstein arranged EdR's DOJ counsel (Ruemmler); Ariane had 12+ personal meetings 2013-2019 | CRITICAL |
| **NEW CRITICAL** Rothschild pre-1987 | Target 47 (Wexner) | Wexner testified under oath that Epstein cited "personal work for Rothschild family in France" as credential AND Élie de Rothschild (1917-2007) personally vouched for Epstein — predates Wexner relationship; **may invert conventional origin narrative** | CRITICAL |

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
| 2026-02-28 | Phases 1-5 complete (all research files written, not yet ingested) | 782 | 283 | 39 | 68 |

---

## Current Phase: Phase 5 — PENDING
## Next Action: Launch Sonnet agent — Rothschild Asset Management research
