# Greenberg-DeBartolo Intelligence Campaign (PKG-EP Phase 5)

## Status: COMPLETE ✅
## Last Updated: 2026-02-24
## Model: claude-sonnet-4-6

---

## CAMPAIGN COMPLETE

All 11 research phases, both final reports, both ingestion scripts, and database ingestion have been completed successfully.

**Database totals after ingestion:** 782 claims, 280 cross-references, 39 sources (up from 697/253/37)

---

## Summary of Campaigns

### Campaign A: Alan "Ace" Greenberg (Target ID 57)

**Operator hypothesis:** Greenberg was likely CIA-connected and BCCI-linked.

**Verdict:**
- **BCCI connection: CONFIRMED E1** — Sandstorm Report primary source names Bear Stearns as one of four main BCCI Treasury brokers (1983-1986). SHERLOCK DB UPGRADE REQUIRED: BSB-* claims should be upgraded from E3 to E1.
- **CIA hypothesis: INDETERMINATE** (0.10 confidence) — structural circumstantial case is real; specific evidence is absent.
- **Bridge node hypothesis: CONFIRMED E2** — Greenberg is the documented structural hinge between Cohn organized crime network (1983 dinner), Epstein trafficking/intelligence network (founder patron 1976-2008), and BCCI intelligence banking network.
- **"Dalton parent" identity: RESOLVED** — it was the Greenberg family itself (son Ted tutored; daughter Lynne dated Epstein).
- **Liquid Funding Ltd. 60% ownership: UNRESOLVED** — most significant financial intelligence gap in the entire Epstein case.
- **LFL April 2008 payoff (three weeks after Bear Stearns collapse): UNEXPLAINED** — all liabilities paid in full in anomalous circumstances.

### Campaign B: Edward DeBartolo Sr. (Target ID 58)

**Operator hypothesis:** DeBartolo likely involved in US-side Operation Gladio.

**Verdict:**
- **Gladio hypothesis: NEGATIVE** (0.05 confidence) — E3 structural inference only; missing all four required documentation types (P2, CIA operational records, parliamentary confirmation, NATO stay-behind connection).
- **Organized crime documentation: CONFIRMED E2** — five separate agencies (DOJ, FBI, US Customs, PA Crime Commission, Columbus PD) independently documented organized crime associations.
- **Wexner nexus: CONFIRMED E2** — $1.7B Carter-Hawley-Hale joint venture (1984/1986); LA Times "two richest men in Ohio"; Shapiro murder file; both connected to Genovese family.
- **Metropolitan Bank Tampa: DOCUMENTED E2** — Grand Cayman routing; FDLE "shocked" finding; structural money laundering consistency; narcotics laundering not proven.
- **CIA hypothesis: INDETERMINATE** (0.10 confidence) — Trafficante-CIA connection E1 real but two inferential steps to DeBartolo.

---

## Files Written

### Campaign A — Greenberg:
| File | Lines | Status |
|------|-------|--------|
| `evidence/greenberg_research_phase1_career.md` | 278 | COMPLETE |
| `evidence/greenberg_research_phase2_epstein.md` | 374 | COMPLETE |
| `evidence/greenberg_research_phase3_cohn.md` | 329 | COMPLETE |
| `evidence/greenberg_research_phase4_bcci.md` | 437 | COMPLETE |
| `evidence/greenberg_research_phase5_synthesis.md` | ~340 | COMPLETE |
| `evidence/greenberg_dynasty_intelligence_report.md` | ~290 | COMPLETE |
| `scripts/ingest_greenberg.py` | ~340 | COMPLETE — 45 claims, 15 xrefs, 1 source |

### Campaign B — DeBartolo:
| File | Lines | Status |
|------|-------|--------|
| `evidence/debartolo_research_phase1_empire.md` | ~200 | COMPLETE |
| `evidence/debartolo_research_phase2_crime.md` | ~400 | COMPLETE |
| `evidence/debartolo_research_phase3_cia_mafia.md` | 367 | COMPLETE |
| `evidence/debartolo_research_phase4_gladio.md` | 407 | COMPLETE |
| `evidence/debartolo_research_phase5_wexner.md` | ~300 | COMPLETE |
| `evidence/debartolo_research_phase6_synthesis.md` | ~330 | COMPLETE |
| `evidence/debartolo_intelligence_report.md` | ~280 | COMPLETE |
| `scripts/ingest_debartolo.py` | ~310 | COMPLETE — 40 claims, 12 xrefs, 1 source |

### Supporting files:
- `evidence/donald_barr_oss_intelligence_profile.md` — OSS/CIA assessment (Donald Barr)

---

## Database State

| Metric | Before | After |
|--------|--------|-------|
| Total claims | 697 | 782 |
| Cross-references | 253 | 280 |
| Sources | 37 | 39 |
| Targets | 58 | 58 (Greenberg = 57, DeBartolo = 58) |

### New campaign claims:
- GRB-001 to GRB-045 (Greenberg, 45 claims)
- DEB-001 to DEB-040 (DeBartolo, 40 claims)

### New cross-references:
- xref_grb_001 to xref_grb_015 (Greenberg, 15 xrefs)
- xref_deb_001 to xref_deb_012 (DeBartolo, 12 xrefs)

---

## Outstanding Action Required

**SHERLOCK DB UPGRADE:** BSB-* claims (Bear Stearns-BCCI nexus, from Phase 3) should be upgraded from evidence tier E3 to E1 based on the Sandstorm Report primary source confirmation found in `evidence/sandstorm_part2_ocr.txt`. Run `scripts/upgrade_bsb_evidence_tier.py` (to be created) or manually update claim tags.

---

## Next PKG-EP Target

The operator has not specified. Candidates from the existing targeting framework:
- Target ID 12 (PROMIS/Inslaw) — deep intel program investigation
- Target ID 44 (Ehud Barak / Carbyne) — Israel intelligence tech nexus
- Target ID 51 (Gravity Symposium) — AAWSAP citation analysis
- Target ID 53 (TerraMar Project) — Ghislaine Maxwell's environmental organization front hypothesis
- Remaining Epstein financial investigation threads (LFL 60% ownership, Wexner block trading mechanics)

---

## Current Phase: DONE
## Next Action: None — campaign complete. Proceed to next PKG-EP target or commit changes.
