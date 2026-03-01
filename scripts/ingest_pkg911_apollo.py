#!/usr/bin/env python3
"""Ingest Apollo Global Management / Leon Black / Mark Rowan intelligence reports
into sherlock.db.

PKG-911 Phase 8B — Script 3 of 4.

Registers 1 evidence source (PKG911_APOLLO_001), extracts ~12 claims across
Leon Black (LBK), Apollo Global Management (APL), and Mark Rowan (MRW), and
creates ~7 cross-references connecting Apollo findings to existing targets.

NOTE: LBK numbering starts at LBK-006. Existing claims ST-028, FXR-006,
WW4-008, EFN-003, and WEX-073 are the prior DB references to Leon Black/Apollo;
LBK-001 through LBK-005 are reserved to acknowledge those cross-campaign
references. This script writes LBK-006 onwards as the first dedicated LBK series.

Targets:
  66 — Leon Black
  67 — Mark Rowan
  68 — Apollo Global Management
"""
import sqlite3
import json
from datetime import datetime

DB_PATH = "/home/johnny5/Sherlock/sherlock.db"

SOURCE = {
    "source_id": "PKG911_APOLLO_001",
    "title": "Apollo Global Management / Leon Black Intelligence Report (PKG-911 Phase 8B)",
    "file_path": "evidence/apollo_research_phase1_origins.md",
    "evidence_type": "intelligence_report",
}

# =============================================================================
# CLAIMS — 12 claims across LBK, APL, MRW series
# LBK numbering starts at LBK-006 (LBK-001 through LBK-005 reserved for
# cross-campaign references: ST-028, FXR-006, WW4-008, EFN-003, WEX-073).
# Each: (claim_id, claim_type, text, confidence, tags_json_string)
# =============================================================================

CLAIMS = [
    # =========================================================================
    # LBK — Leon Black (target_id=66)
    # =========================================================================
    ("LBK-006", "factual",
     "Leon Black served as Head of Mergers and Acquisitions at Drexel Burnham Lambert from 1986 to 1990, working directly under Michael Milken's junk bond operation. He was the primary bridge between Milken's high-yield financing machine and corporate transaction execution. Black departed before Drexel's February 1990 bankruptcy filing, taking client relationships and deal-making infrastructure with him.",
     0.95, '["E1", "leon_black", "Drexel", "Milken", "junk_bonds", "PKG-911"]'),

    ("LBK-007", "factual",
     "Apollo Global Management was co-founded in 1990 by Leon Black, Josh Harris, and Marc Rowan, built from Drexel Burnham Lambert's ashes using its client relationships, deal structures, and personnel. Credit Lyonnais served as an early institutional limited partner. The $170 million in payments to Jeffrey Epstein from Black occurred entirely between 2012 and 2017 — years after Epstein's 2008 federal conviction for soliciting a minor. Black thus knowingly paid Epstein during the entirety of the payment period with full knowledge of Epstein's criminal history. This is E1 undisputed chronology.",
     0.99, '["E1", "leon_black", "apollo", "epstein", "post_conviction_payments", "PKG-911"]'),

    ("LBK-008", "factual",
     "The $170 million Black paid Epstein from 2012 to 2017 is analytically divided as follows: maximum plausible legitimate advisory fees given Epstein's lack of formal credentials and the nature of tax and estate planning services are estimated at $20 to $41 million by independent financial analysts. The Dechert LLP independent review commissioned by Apollo found 'no credible evidence of legitimate services' justifying the full amount. The unexplained delta of approximately $130 million is best explained by: unnameable services (confidence 0.60) or structured financial transactions that required a named intermediary (confidence 0.35). The full amount remains legally unexplained.",
     0.85, '["E1", "E2", "leon_black", "epstein", "170M_payments", "unexplained_delta", "Dechert_review", "PKG-911"]'),

    ("LBK-009", "factual",
     "Leon Black resigned as Apollo Global Management Chairman in February 2021 following Senate Finance Committee disclosure of the $170 million Epstein payments and a wave of LP pressure. He retained the CEO title initially before full departure. At the time of his departure, Apollo's assets under management totaled approximately $455 billion.",
     0.95, '["E1", "leon_black", "apollo", "resignation_2021", "senate_finance", "AUM", "PKG-911"]'),

    ("LBK-010", "assessment",
     "Leon Black's introduction vector to Jeffrey Epstein has not been confirmed at E1 or E2 evidence tier. Most probable introduction vectors assessed by confidence: (1) Wexner referral — Wexner and Black were both prominent Jewish philanthropists in overlapping New York-to-Columbus financial circles, confidence 0.60; (2) social circuit overlap — Harvard/art world intersection, confidence 0.50; (3) Bear Stearns/Greenberg connection — Drexel and Bear Stearns operated in overlapping junk-bond-era client networks, confidence 0.30. None confirmed.",
     0.65, '["E2", "E3", "leon_black", "epstein", "introduction_vector", "UNCONFIRMED", "PKG-911"]'),

    # =========================================================================
    # APL — Apollo Global Management (target_id=68)
    # =========================================================================
    ("APL-001", "factual",
     "Apollo Global Management was founded in 1990 using Drexel Burnham Lambert's organizational infrastructure, personnel, and client relationships. The Drexel-BCCI direct organizational connection is assessed at 0.10 confidence — no primary source documentation links Drexel to BCCI banking relationships. The structural parallel between Drexel's 1980s high-yield architecture and BCCI's parallel banking system (same era, same financial innovation era) is notable at 0.90 but does not constitute evidence of connection. Bear Stearns, confirmed as a BCCI Treasury broker (Sandstorm Report, E1), is the bridge node between the Drexel/Apollo ecosystem and the BCCI ecosystem.",
     0.80, '["E1", "E2", "apollo", "Drexel", "BCCI", "bear_stearns_bridge", "PKG-911"]'),

    ("APL-002", "assessment",
     "Apollo Global Management's War on Terror defense profiteering classification: PERIPHERAL NODE. Direct WoT profiteering confidence: 0.10 — Apollo's core private equity model targets financial services, chemicals, media, and consumer sectors rather than defense contractors. Indirect WoT beneficiary through 2008 financial crisis profits (buying distressed assets at the bottom): 0.80 — well-documented. Apollo's primary Sherlock significance is as the institutional vehicle for Leon Black's Epstein financial relationship, not as a 9/11 or War on Terror operational node.",
     0.85, '["assessment", "apollo", "WoT", "peripheral_node", "Epstein_primary_significance", "PKG-911"]'),

    ("APL-003", "factual",
     "Athene Holding Ltd. (Bermuda): Founded in 2009 by Marc Rowan as an insurance company designed to use Apollo's private equity investment capabilities to generate returns on insurance float. Grew from under $1 billion to over $300 billion in assets under management before merging with Apollo in a $11 billion deal completed in January 2022. The Bermuda domicile attracted scrutiny from the NAIC (National Association of Insurance Commissioners) and congressional committees over regulatory arbitrage and tax structure.",
     0.90, '["E1", "apollo", "Athene", "Rowan", "Bermuda", "regulatory_arbitrage", "PKG-911"]'),

    # =========================================================================
    # MRW — Mark Rowan (target_id=67)
    # =========================================================================
    ("MRW-001", "factual",
     "Marc Rowan (born 1962) co-founded Apollo with Black and Harris, holding Wharton BSE and MBA degrees. His role was as the credit and insurance strategist to Black's dealmaking role. He architected Athene and succeeded Black as Apollo CEO following Black's February 2021 departure. Whether Rowan was aware of Black's Epstein payments during the 2012-2017 period — given they shared Apollo's highest executive levels — is analytically relevant. Confidence that Rowan's claim of ignorance is accurate: 0.40.",
     0.75, '["E2", "mark_rowan", "apollo", "Athene", "Black_succession", "Epstein_awareness", "PKG-911"]'),

    ("MRW-002", "assessment",
     "Marc Rowan PKG-911 classification: LOW PRIORITY. No documented connections to Alvin Krongard, Alex. Brown, Erik Prince, Blackwater, put options, or the Cheney/Rumsfeld/Bush national security architecture. No documented connections to any 9/11-adjacent financial or intelligence network. His analytical significance relative to Leon Black in PKG-911 context is approximately one-tenth. Research resources should be directed to Black, Apollo, and the Wexner-Black financial relationship.",
     0.90, '["assessment", "mark_rowan", "LOW_PRIORITY", "PKG-911"]'),

    # =========================================================================
    # Additional cross-campaign synthesis claims
    # =========================================================================
    ("LBK-011", "factual",
     "The $170M Epstein payment timeline creates a precise chronological record: Epstein convicted June 30, 2008; registered as sex offender July 2008; Black's payments begin 2012 — four years after conviction, with full public knowledge of Epstein's criminal record. The payments continued through 2017, nine years after conviction. No single documented payment in the $170M total predates the conviction. Black's knowledge of Epstein's sex offender status throughout the payment period is E1 established fact.",
     0.99, '["E1", "leon_black", "epstein", "payment_chronology", "post_conviction", "sex_offender_registration", "PKG-911"]'),

    ("APL-004", "factual",
     "The Krongard family-Apollo connection: Cheryl Gordon Krongard (wife of CIA Executive Director Buzzy Krongard) served as Senior Partner at Apollo Management from 2002 to 2004. This creates a documented personnel link between Apollo's senior partnership and the CIA executive leadership during the peak War on Terror period and Blackwater's first CIA contracts. No evidence this link was operationally significant; the personnel connection is E1 documented fact.",
     0.90, '["E1", "apollo", "CGK_Cheryl_Krongard", "CIA_personnel_link", "WoT_period", "PKG-911"]'),
]

# =============================================================================
# CROSS-REFERENCES — 7 connections
# Each: (xref_id, entity1, entity2, relationship_type, source_claims, confidence)
# =============================================================================

CROSS_REFS = [
    ("xref_apl_001", "LBK_Leon_Black", "Target42_Epstein",
     "EXTENDING_XREF_EP_034_170M_CONFIRMED_130M_UNEXPLAINED_DELTA",
     "LBK-007,LBK-008,LBK-009,LBK-011",
     0.99),

    ("xref_apl_002", "APL_Apollo", "Target55_Bear_Stearns",
     "BEAR_STEARNS_BRIDGE_NODE_DREXEL_APOLLO_TO_BCCI_ECOSYSTEM",
     "APL-001,LBK-006",
     0.50),

    ("xref_apl_003", "APL_Apollo", "CGK_Cheryl_Krongard",
     "SENIOR_PARTNER_2002_2004_CIA_EXEC_DIR_CONCURRENT_PERSONNEL_LINK",
     "APL-004,CGK-001",
     0.90),

    ("xref_apl_004", "LBK_Leon_Black", "Target47_Wexner",
     "PARALLEL_FINANCIAL_PATRONS_WEXNER_TO_BLACK_REVENUE_SUBSTITUTION_HYPOTHESIS",
     "LBK-010,WEX-073",
     0.50),

    ("xref_apl_005", "LBK_Leon_Black", "LBK_Introduction_Vector",
     "INTRODUCTION_VECTOR_UNCONFIRMED_WEXNER_MOST_PROBABLE_0_60",
     "LBK-010",
     0.40),

    ("xref_apl_006", "APL_Athene_Bermuda", "BCCI_Offshore_Architecture",
     "STRUCTURAL_PARALLEL_BERMUDA_OFFSHORE_REGULATORY_ARBITRAGE",
     "APL-003,APL-001",
     0.35),

    ("xref_apl_007", "LBK_Leon_Black", "LBK_Post_Conviction_Payments",
     "FULL_170M_PAYMENT_SERIES_POST_2008_CONVICTION_E1_CHRONOLOGY",
     "LBK-007,LBK-008,LBK-011",
     0.99),
]


# =============================================================================
# EXECUTION
# =============================================================================

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()

    sources_added = 0
    claims_added = 0
    claims_skipped = 0
    xrefs_added = 0
    xrefs_skipped = 0

    # ---- Register source ----
    c.execute("SELECT source_id FROM evidence_sources WHERE source_id = ?",
              (SOURCE["source_id"],))
    if c.fetchone():
        print(f"SKIP source {SOURCE['source_id']}: already exists")
    else:
        c.execute("""
            INSERT INTO evidence_sources
                (source_id, title, file_path, evidence_type, created_at, ingested_at, processing_status, metadata)
            VALUES (?, ?, ?, ?, ?, ?, 'complete', ?)
        """, (
            SOURCE["source_id"],
            SOURCE["title"],
            SOURCE["file_path"],
            SOURCE["evidence_type"],
            now, now,
            json.dumps({
                "campaign": "PKG-911",
                "phase": "8B",
                "script": "3_of_4",
                "description": "Apollo Global Management, Leon Black, and Mark Rowan intelligence report. LBK numbering starts at LBK-006 (LBK-001 through LBK-005 reserved for cross-campaign references). Key: $170M payments entirely post-conviction; $130M unexplained delta; Dechert review found no credible evidence of legitimate services justifying full amount.",
                "targets": {
                    "66": "Leon Black",
                    "67": "Mark Rowan",
                    "68": "Apollo Global Management",
                },
                "total_claims": len(CLAIMS),
                "total_xrefs": len(CROSS_REFS),
                "key_finding": "$170M payments entirely post-2008 conviction; unexplained delta ~$130M",
                "WoT_classification": "PERIPHERAL NODE (0.10 direct)",
                "prior_DB_black_claims": ["ST-028", "FXR-006", "WW4-008", "EFN-003", "WEX-073"],
            })
        ))
        sources_added += 1
        print(f"Added source: {SOURCE['source_id']} -- {SOURCE['title']}")

    # ---- Insert claims ----
    for claim_id, claim_type, text, confidence, tags in CLAIMS:
        c.execute("SELECT claim_id FROM evidence_claims WHERE claim_id = ?",
                  (claim_id,))
        if c.fetchone():
            print(f"  SKIP claim {claim_id}: already exists")
            claims_skipped += 1
            continue

        c.execute("""
            INSERT INTO evidence_claims
                (claim_id, source_id, claim_type, text, confidence, tags, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (claim_id, SOURCE["source_id"], claim_type, text, confidence, tags, now))
        claims_added += 1

    print(f"  Claims added: {claims_added} | skipped: {claims_skipped}")

    # ---- Insert cross-references ----
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

    conn.commit()

    # ---- Verification summary ----
    c.execute("SELECT COUNT(*) FROM evidence_sources")
    total_sources = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM evidence_claims")
    total_claims = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM cross_references")
    total_xrefs = c.fetchone()[0]

    for prefix in ["LBK", "APL", "MRW"]:
        c.execute("SELECT COUNT(*) FROM evidence_claims WHERE claim_id LIKE ?",
                  (f"{prefix}%",))
        print(f"  {prefix}-* claims in DB: {c.fetchone()[0]}")

    c.execute("SELECT COUNT(*) FROM cross_references WHERE xref_id LIKE 'xref_apl_%'")
    apl_xrefs = c.fetchone()[0]

    conn.close()

    print(f"\n{'='*60}")
    print(f"PKG-911 APOLLO INGESTION COMPLETE")
    print(f"{'='*60}")
    print(f"  Sources added this run:  {sources_added}")
    print(f"  Claims added this run:   {claims_added}")
    print(f"  Claims skipped (dupes):  {claims_skipped}")
    print(f"  Xrefs added this run:    {xrefs_added}")
    print(f"  Xrefs skipped (dupes):   {xrefs_skipped}")
    print(f"{'='*60}")
    print(f"  xref_apl_* in DB:        {apl_xrefs}")
    print(f"{'='*60}")
    print(f"  DATABASE GRAND TOTALS:")
    print(f"    Total sources:         {total_sources}")
    print(f"    Total claims:          {total_claims}")
    print(f"    Total cross-refs:      {total_xrefs}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
