#!/usr/bin/env python3
"""Supplementary cross-reference ingestion for PKG-911 campaign.

Fills coverage gaps identified in the 2026-03-03 audit:
- 6 targets (ABR, HOK, CGK, ERP, LBK, MRW) lacked dedicated xref series
- Cross-campaign links (PKG-911 ↔ PKG-EP) were missing
- Negative findings (no connection documented) were not recorded
- Pardon pattern and parallel accountability gaps not cross-referenced

This script adds cross-references ONLY — no new claims or sources.
"""
import sqlite3
import json
from datetime import datetime

DB_PATH = "/home/johnny5/Sherlock/sherlock.db"

# =============================================================================
# CROSS-REFERENCES — Supplementary series for underserved targets
# Each: (xref_id, entity1, entity2, relationship_type, source_claims, confidence)
# =============================================================================

CROSS_REFS = [
    # =========================================================================
    # ABR — Alex. Brown (Target 60) — dedicated series
    # =========================================================================
    ("xref_abr_001", "ABR_AlexBrown", "Deutsche_Bank",
     "ACQUISITION_1999_INSTITUTIONAL_CONTINUITY",
     "ABR-001,ABR-004,BZK-009",
     0.99),

    ("xref_abr_002", "ABR_AlexBrown", "SEC_Record_Destruction",
     "PUT_OPTIONS_INVESTIGATION_RECORDS_DESTROYED_PERMANENT_EPISTEMIC_GAP",
     "ABR-005,ABR-006",
     0.90),

    ("xref_abr_003", "ABR_AlexBrown", "Target42_Epstein",
     "INSTITUTIONAL_CHAIN_ALEX_BROWN_TO_DEUTSCHE_BANK_TO_EPSTEIN_ENABLEMENT",
     "ABR-004,BZK-009",
     0.55),

    ("xref_abr_004", "ABR_Mayo_Shattuck_III", "ABR_AlexBrown",
     "CEO_RESIGNED_SEPT_12_2001_ONE_DAY_AFTER_ATTACKS_NO_PUBLIC_EXPLANATION",
     "ABR-004",
     0.90),

    ("xref_abr_005", "ABR_Poteshman_2006", "ABR_911_Commission_Staff_Statement_21",
     "PEER_REVIEWED_E1_CONTRADICTS_COMMISSION_INNOCUOUS_CHARACTERIZATION",
     "ABR-002,ABR-003,ABR-006",
     0.85),

    # =========================================================================
    # HOK — Howard Krongard (Target 61) — dedicated series
    # =========================================================================
    ("xref_hok_001", "HOK_Howard_Krongard", "Target58_DeBartolo",
     "TRUMP_PROTECTION_PATTERN_HOK_NO_PROSECUTION_DEB_PARDON",
     "HOK-005,DEB-037",
     0.55),

    ("xref_hok_002", "HOK_Howard_Krongard", "Dick_Cheney",
     "PARALLEL_CONCEALMENT_IG_BLOCKED_INVESTIGATIONS_CHENEY_BLOCKED_CONGRESSIONAL_NOTIFICATION",
     "HOK-002,HOK-003,BWK-002,BWK-007",
     0.75),

    ("xref_hok_003", "HOK_Howard_Krongard", "HOK_Whistleblower_Retaliation",
     "SEVEN_INTERNAL_WHISTLEBLOWERS_TWO_THREATENED_WITH_TERMINATION",
     "HOK-003,HOK-004",
     0.95),

    ("xref_hok_004", "HOK_Howard_Krongard", "Target42_Epstein",
     "NEGATIVE_FINDING_NO_DOCUMENTED_CONNECTION",
     "HOK-001",
     0.05),

    # =========================================================================
    # CGK — Cheryl Gordon Krongard (Target 62) — dedicated series
    # =========================================================================
    ("xref_cgk_001", "CGK_Cheryl_Krongard", "BZK_Buzzy_Krongard",
     "SPOUSE_CONCURRENT_APOLLO_SENIOR_PARTNER_AND_CIA_EXEC_DIR_2002_2004",
     "CGK-001,BZK-003,BZK-006",
     0.95),

    ("xref_cgk_002", "CGK_Cheryl_Krongard", "Target42_Epstein",
     "NEGATIVE_FINDING_NO_EVIDENCE_OF_EPSTEIN_RELATED_ACTIVITY",
     "CGK-002",
     0.00),

    # =========================================================================
    # ERP — Erik Prince (Target 64) — dedicated series
    # =========================================================================
    ("xref_erp_001", "ERP_Erik_Prince", "Target58_DeBartolo",
     "TRUMP_PARDON_PATTERN_BLACKWATER_DEC_2020_DEBARTOLO_FEB_2020",
     "BWK-003,ERP-005,DEB-037",
     0.65),

    ("xref_erp_002", "ERP_Erik_Prince", "Prince_DeVos_Political_Network",
     "COMBINED_20M_PLUS_REPUBLICAN_DONATIONS_SISTER_EDUCATION_SECRETARY",
     "ERP-001,ERP-005",
     0.95),

    ("xref_erp_003", "ERP_Erik_Prince", "Cofer_Black_Robert_Richer_Enrique_Prado",
     "CIA_COUNTERTERRORISM_LEADERSHIP_RECONSTITUTED_AT_BLACKWATER_2004_2007",
     "ERP-002,BWK-005",
     0.85),

    ("xref_erp_004", "ERP_Erik_Prince", "Target42_Epstein",
     "NEGATIVE_FINDING_NO_DOCUMENTED_DIRECT_CONNECTION",
     "ERP-001",
     0.10),

    ("xref_erp_005", "ERP_Erik_Prince", "George_Nader_Sex_Trafficking",
     "SEYCHELLES_MEETING_FIXER_CONVICTED_TRAFFICKING_2020_EPSTEIN_NEXUS_ADJACENT",
     "ERP-004,BWK-010",
     0.70),

    # =========================================================================
    # LBK — Leon Black (Target 66) — dedicated series
    # =========================================================================
    ("xref_lbk_001", "LBK_Leon_Black", "Deutsche_Bank",
     "PARALLEL_EPSTEIN_FINANCIAL_ENABLERS_BOTH_POST_CONVICTION",
     "LBK-007,LBK-011,BZK-009",
     0.80),

    ("xref_lbk_002", "LBK_Leon_Black", "Target57_Greenberg",
     "POTENTIAL_INTRODUCTION_VECTOR_BEAR_STEARNS_PATRON_NETWORK",
     "LBK-010,GRB-020",
     0.30),

    ("xref_lbk_003", "LBK_Leon_Black", "Target47_Wexner",
     "LARGEST_CASH_PATRON_170M_VS_FIRST_PATRON_1B_PLUS_REVENUE_SUBSTITUTION_0_50",
     "LBK-007,LBK-008,LBK-011,WEX-001",
     0.50),

    ("xref_lbk_004", "LBK_Leon_Black", "Drexel_Burnham_Lambert",
     "HEAD_OF_MA_1986_1990_FOUNDED_APOLLO_FROM_DREXEL_DIASPORA",
     "LBK-006,LBK-007",
     0.99),

    ("xref_lbk_005", "LBK_Leon_Black", "Dechert_LLP_Review",
     "INDEPENDENT_REVIEW_FOUND_NO_CREDIBLE_EVIDENCE_BUT_NARROWLY_SCOPED",
     "LBK-008",
     0.35),

    ("xref_lbk_006", "LBK_Leon_Black", "Target55_Bear_Stearns",
     "EPSTEIN_EMPLOYER_1976_1981_GREENBERG_PATRON_INTRODUCTION_VECTOR_CANDIDATE",
     "LBK-010,BSB-001",
     0.30),

    # =========================================================================
    # MRW — Mark Rowan (Target 67) — dedicated series
    # =========================================================================
    ("xref_mrw_001", "MRW_Mark_Rowan", "LBK_Leon_Black",
     "APOLLO_CO_FOUNDER_ASSUMED_CEO_AFTER_BLACK_EPSTEIN_FALLOUT",
     "MRW-001,MRW-002,LBK-009",
     0.90),

    ("xref_mrw_002", "MRW_Mark_Rowan", "Target42_Epstein",
     "NEGATIVE_FINDING_NO_DOCUMENTED_RELATIONSHIP_AWARENESS_OF_BLACK_PAYMENTS_0_55",
     "MRW-001",
     0.10),

    # =========================================================================
    # CROSS-CAMPAIGN: PKG-911 ↔ PKG-EP bridging xrefs
    # =========================================================================
    ("xref_p911_001", "PKG911_Krongard_Circuit", "PKG_EP_Tenet_Epstein",
     "CIA_LEADERSHIP_BRIDGE_KRONGARD_EXEC_DIR_UNDER_TENET_DCI_WHILE_TENET_IN_EPSTEIN_ORBIT",
     "BZK-003,BZK-006,xref_ep_055",
     0.50),

    ("xref_p911_002", "PKG911_Alex_Brown_Deutsche_Bank", "PKG_EP_Deutsche_Bank_Epstein",
     "INSTITUTIONAL_CONTINUITY_ALEX_BROWN_1999_ACQUISITION_TO_EPSTEIN_40_PLUS_ACCOUNTS",
     "ABR-004,BZK-009",
     0.55),

    ("xref_p911_003", "PKG911_Blackwater_Pardons", "PKG_EP_DeBartolo_Pardon",
     "TRUMP_PARDON_PATTERN_ACROSS_CAMPAIGNS_DEB_FEB_2020_BWK_DEC_2020",
     "BWK-003,DEB-037",
     0.65),

    ("xref_p911_004", "PKG911_Apollo_Black", "PKG_EP_Wexner_Epstein",
     "PARALLEL_FINANCIAL_PATRONS_REVENUE_SUBSTITUTION_HYPOTHESIS",
     "LBK-007,LBK-008,WEX-001,WEX-060",
     0.50),

    ("xref_p911_005", "PKG911_Apollo_Cheryl_Krongard", "PKG_EP_Epstein_Network",
     "PERSONNEL_ADJACENCY_CIA_EXEC_DIR_SPOUSE_AT_APOLLO_NO_OPERATIONAL_SIGNIFICANCE",
     "CGK-001,CGK-002,APL-004",
     0.90),

    ("xref_p911_006", "PKG911_Rothschild_Pre_1987", "PKG_EP_Wexner_Origin_Narrative",
     "EPSTEIN_ROTHSCHILD_CREDENTIALS_PREDATE_WEXNER_RELATIONSHIP_INVERTING_CONVENTIONAL_NARRATIVE",
     "RAM-005,WEX-060,WEX-081",
     0.75),

    ("xref_p911_007", "PKG911_Bear_Stearns_Bridge", "PKG_EP_BCCI_Epstein",
     "BEAR_STEARNS_AS_BRIDGE_NODE_DREXEL_APOLLO_TO_BCCI_AND_EPSTEIN_EMPLOYER",
     "BSB-001,BSB-006,LBK-010,APL-001",
     0.80),

    ("xref_p911_008", "PKG911_7_Layer_Accountability", "PKG_EP_Institutional_Failure_Pattern",
     "ACCOUNTABILITY_EVASION_ACROSS_CAMPAIGNS_WOT_AND_EPSTEIN_NETWORKS_BOTH_ZERO_SENIOR_PROSECUTIONS",
     "BWK-008,HOK-005,LBK-009",
     0.80),

    ("xref_p911_009", "PKG911_Prince_Nader", "PKG_EP_Trafficking_Network",
     "NADER_CONVICTED_SEX_TRAFFICKING_EPSTEIN_NEXUS_ADJACENT_PRINCE_OPERATIONAL_FIXER",
     "BWK-010,ERP-004",
     0.70),

    ("xref_p911_010", "PKG911_WoT_Epstein_Networks", "PKG_EP_Epstein_Network",
     "PARALLEL_SYSTEMS_NOT_INTEGRATED_SAME_INSTITUTIONAL_MILIEU_DIFFERENT_OPERATIONAL_CIRCUITS",
     "BZK-003,BWK-005,LBK-007,APL-002",
     0.70),
]


# =============================================================================
# EXECUTION
# =============================================================================

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()

    xrefs_added = 0
    xrefs_skipped = 0

    for xref_id, entity1, entity2, rel_type, source_claims, confidence in CROSS_REFS:
        c.execute("SELECT xref_id FROM cross_references WHERE xref_id = ?",
                  (xref_id,))
        if c.fetchone():
            print(f"  SKIP xref {xref_id}: already exists")
            xrefs_skipped += 1
            continue

        c.execute("""
            INSERT INTO cross_references
                (xref_id, entity1, entity2, relationship_type, source_claims, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (xref_id, entity1, entity2, rel_type, source_claims, confidence, now))
        xrefs_added += 1
        print(f"  Added xref {xref_id}: {entity1} <-> {entity2} ({confidence})")

    conn.commit()

    # ---- Summary ----
    total_xrefs = c.execute("SELECT COUNT(*) FROM cross_references").fetchone()[0]

    print(f"\n{'='*60}")
    print(f"PKG-911 SUPPLEMENTARY CROSS-REFERENCE INGESTION COMPLETE")
    print(f"{'='*60}")
    print(f"Cross-references added: {xrefs_added}")
    print(f"Cross-references skipped (already existed): {xrefs_skipped}")
    print(f"Total cross-references in DB: {total_xrefs}")
    print(f"{'='*60}")

    # ---- Coverage verification ----
    print(f"\nCOVERAGE VERIFICATION:")
    prefixes = {
        'abr': 'Alex. Brown (60)',
        'hok': 'Howard Krongard (61)',
        'cgk': 'Cheryl Krongard (62)',
        'erp': 'Erik Prince (64)',
        'lbk': 'Leon Black (66)',
        'mrw': 'Mark Rowan (67)',
        'p911': 'Cross-campaign',
    }
    for prefix, label in prefixes.items():
        count = c.execute("SELECT COUNT(*) FROM cross_references WHERE xref_id LIKE ?",
                         (f"xref_{prefix}%",)).fetchone()[0]
        print(f"  xref_{prefix}_*: {count} ({label})")

    conn.close()


if __name__ == "__main__":
    main()
