# PKG-911: 9/11 Financial Foreknowledge & War on Terror Profiteering Network
## Campaign Status Document — Single Source of Truth

**Campaign ID:** PKG-911
**Created:** 2026-02-28
**Model Assignment:** Opus (analysis/orchestration/synthesis) | Sonnet (search/retrieval/ingestion)

---

## SESSION RESUME
> **Read this section first at every session start.**

**Current Phase:** ALL PHASES COMPLETE — CAMPAIGN CLOSED
**Last Completed Action:** Phase 8A final reports completed (Blackwater, Apollo, Network Synthesis); all 6 individual reports + 1 capstone network report written
**Next Action:** None — campaign complete. See `evidence/pkg911_network_intelligence_report.md` for final synthesis.
**DB State at Last Save:** 838 claims | 313 xrefs | 43 sources | 68 targets

**Campaign completed:** 2026-03-03

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
- [x] **Phase 6: 9/11 Financial Nexus Synthesis** (Opus) — COMPLETE 2026-02-28
  - [x] `evidence/pkg911_financial_nexus_synthesis.md` (722 lines)
- [x] **Phase 7: Retriever Deployment** (Sonnet) — COMPLETE 2026-02-28
  - [x] `scripts/pkg911_academic_papers_retriever.py` — run live: Poteshman (68 citations, E1); Chesney SSRN 1522157 (ZORA PDF found); NEW: 2011 MFJ rebuttal paper
  - [x] `scripts/pkg911_alex_brown_puts_retriever.py` — run live: IOSCO IOSCOPD121 (1.1MB retrieved); 9/11 Commission SS3 PDF retrieved; EDGAR EFTS working
  - [x] `scripts/pkg911_sec_filings_retriever.py`
  - [x] `scripts/pkg911_congressional_retriever.py`
  - [x] `scripts/pkg911_dod_contracts_retriever.py`
  - [x] `scripts/pkg911_foia_retriever.py`
  - [x] `evidence/pkg911_academic_papers_index.json`
  - [x] `evidence/pkg911_alex_brown_puts_index.json`
- [x] **Phase 8: Final Reports + Ingestion** (Opus reports, Sonnet scripts) — COMPLETE 2026-03-03
  - [x] `evidence/krongard_intelligence_report.md` (17KB, 2026-02-28)
  - [x] `evidence/alex_brown_intelligence_report.md` (13KB, 2026-02-28)
  - [x] `evidence/howard_krongard_intelligence_report.md` (13KB, 2026-02-28)
  - [x] `evidence/blackwater_intelligence_report.md` (20KB, 2026-03-03)
  - [x] `evidence/apollo_intelligence_report.md` (18KB, 2026-03-03)
  - [x] `evidence/pkg911_network_intelligence_report.md` (capstone, 2026-03-03)
  - [x] `scripts/ingest_pkg911_krongard.py` (22 claims, 10 xrefs)
  - [x] `scripts/ingest_pkg911_blackwater.py` (15 claims, 8 xrefs)
  - [x] `scripts/ingest_pkg911_apollo.py` (12 claims, 7 xrefs)
  - [x] `scripts/ingest_pkg911_rothschild.py` (7 claims, 5 xrefs)
  - [x] DB ingestion executed + verified — 838 claims, 313 xrefs, 43 sources

---

## Key Analytical Hypotheses

| ID | Hypothesis | Confidence | Status |
|----|-----------|-----------|--------|
| H1 | Krongard Cover-Up Mechanism: ran Alex. Brown during put options → CIA → shaped/suppressed SEC-CIA assessment | **Structural conflict confirmed 0.90; active exploitation 0.30; H0 coincidence 0.45-0.55 still leads** — SEC record destruction creates permanent epistemic gap | PHASE 6 COMPLETE — STRUCTURALLY CONFIRMED, OPERATIONALLY UNRESOLVABLE |
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
| 2026-02-28 | Phase 8B complete (ingestion scripts executed) | 838 | 313 | 43 | 68 |
| 2026-03-03 | Phase 8A complete (all reports written) — CAMPAIGN CLOSED | 838 | 313 | 43 | 68 |

---

## Current Phase: CAMPAIGN COMPLETE
## Final Status: All 8 phases completed. 33 deliverable files, ~12,000 lines, 56 claims, 30 xrefs ingested.

## Phase 6 Synthesis — Key Conclusions
1. **Informed trading statistically confirmed** — Poteshman + Chesney: 0.85-0.90 (E1 peer-reviewed)
2. **Krongard two-node circuit confirmed** — 0.95 (E1); 15-day gap Howard blocking → Prince Buzzy invite is strongest coordination indicator
3. **SEC record destruction creates permanent epistemic gap** — identity of "single US-based institutional investor" behind 95% of UAL puts is irrecoverable
4. **Krongard structural conflict in CIA-SEC consultation confirmed** — 0.90; active exploitation: 0.30
5. **Blackwater $1.5-2.1B through personal relationship, not procurement** — 0.85-0.90
6. **Seven-layer accountability evasion architecture** — probability of coincidental alignment: 0.05-0.10 (strongest case for deliberate design)
7. **Black $130M unexplained delta** — 0.95 for the delta; explanation: unnameable services 0.60
8. **Epstein's Rothschild credentials predate Wexner** — 0.75 (E1 testimony; corroboration unavailable, Élie died 2007)
9. **9/11/WoT network and Epstein network are PARALLEL SYSTEMS, not unified** — 0.70; no Krongard-Epstein or Prince-Epstein contact found
10. **Overall network: semi-emergent profiteering ecosystem** — 0.55-0.65; NOT centrally coordinated conspiracy 0.05-0.10
