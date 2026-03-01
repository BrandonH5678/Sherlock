#!/usr/bin/env python3
"""Ingest Krongard family intelligence reports into sherlock.db.

PKG-911 Phase 8B — Script 1 of 4.

Registers 1 evidence source (PKG911_KRONGARD_001), extracts ~18 claims
across Buzzy Krongard (BZK), Alex. Brown (ABR), Howard Krongard (HOK),
and Cheryl Gordon Krongard (CGK), and creates ~10 cross-references connecting
Krongard findings to existing targets.

Targets:
  59 — Alvin 'Buzzy' Krongard
  60 — Alex. Brown / Deutsche Bank Alex. Brown
  61 — Howard Krongard
  62 — Cheryl Gordon Krongard
"""
import sqlite3
import json
from datetime import datetime

DB_PATH = "/home/johnny5/Sherlock/sherlock.db"

SOURCE = {
    "source_id": "PKG911_KRONGARD_001",
    "title": "Krongard Family Intelligence Report (PKG-911 Phase 8B)",
    "file_path": "evidence/krongard_research_phase1_alex_brown.md",
    "evidence_type": "intelligence_report",
}

# =============================================================================
# CLAIMS — 18 claims across BZK, ABR, HOK, CGK series
# Each: (claim_id, claim_type, text, confidence, tags_json_string)
# =============================================================================

CLAIMS = [
    # =========================================================================
    # BZK — Alvin 'Buzzy' Krongard (target_id=59)
    # =========================================================================
    ("BZK-001", "factual",
     "Alvin 'Buzzy' Krongard served as CEO then Chairman of Alex. Brown & Sons from 1991-1997, the oldest US investment bank. He departed before Deutsche Bank's acquisition of Alex. Brown completed in 1999. His departure timing is analytically significant given subsequent pre-9/11 options activity traced to Alex. Brown accounts.",
     0.95, '["E1", "krongard", "alex_brown", "PKG-911"]'),

    ("BZK-002", "factual",
     "Buzzy Krongard joined the CIA as Counselor to the Director of Central Intelligence (DCI) in February 1998 — his first government role, arriving approximately 10 months before Deutsche Bank finalized the Alex. Brown acquisition. The transition from Wall Street to CIA was direct and rapid.",
     0.95, '["E1", "krongard", "CIA", "DCI_counselor", "PKG-911"]'),

    ("BZK-003", "factual",
     "Krongard was promoted to CIA Executive Director — the No. 3 position in the Agency — on March 16, 2001, approximately six months before the September 11 attacks. As Executive Director he oversaw all CIA operational programs, budget, and personnel during the most consequential period in post-Cold War CIA history.",
     0.99, '["E1", "krongard", "CIA", "executive_director", "9/11", "PKG-911"]'),

    ("BZK-004", "factual",
     "The SEC consulted the CIA during its post-9/11 investigation of anomalous pre-attack put options while Krongard held the CIA Executive Director position — creating a documented structural conflict of interest. His personal connection to Alex. Brown (which executed the UAL puts) and his CIA oversight role over any CIA cooperation with the SEC investigation were concurrent. Confidence that a structural conflict existed: 0.90. Confidence that Krongard actively exploited that conflict: 0.30 — no direct evidence of interference has been documented.",
     0.90, '["E2", "krongard", "SEC_investigation", "put_options", "conflict_of_interest", "PKG-911"]'),

    ("BZK-005", "factual",
     "Krongard personally authorized Blackwater USA's first CIA security contract in April 2002: $5.4 million, awarded without competitive bidding, based on his personal relationship with Erik Prince developed in post-9/11 meetings. This contract launched what became a $1.5-2.1 billion CIA-Blackwater financial relationship.",
     0.95, '["E1", "krongard", "blackwater", "CIA_contract", "no_bid", "PKG-911"]'),

    ("BZK-006", "factual",
     "Krongard served as CIA Executive Director from 2001 to 2004, overseeing all CIA operational programs during the peak War on Terror period. Programs under his administrative oversight included the CIA assassination program contracted to Blackwater, extraordinary rendition logistics, and enhanced interrogation at black sites.",
     0.99, '["E1", "krongard", "CIA", "WoT", "rendition", "PKG-911"]'),

    ("BZK-007", "factual",
     "Krongard joined the Blackwater USA advisory board in July 2007, receiving $3,500 per meeting. He resigned from the board on November 16, 2007 — two days after congressional testimony revealed his advisory role and his brother Howard's concurrent IG oversight of Blackwater contracts. The rapid resignation under congressional exposure is analytically significant.",
     0.95, '["E1", "krongard", "blackwater", "advisory_board", "congressional_exposure", "PKG-911"]'),

    ("BZK-008", "factual",
     "During congressional testimony, Krongard told investigators he did not know his brother Howard was on the Blackwater advisory board. Buzzy subsequently issued a public statement that directly contradicted Howard's denial — stating he had informed Howard of his board membership. The contradiction between the brothers' accounts raises a documented potential perjury issue (confidence: 0.70).",
     0.85, '["E1", "krongard", "howard_krongard", "blackwater", "perjury_risk", "PKG-911"]'),

    ("BZK-009", "factual",
     "Deutsche Bank acquired Alex. Brown in June 1999; Krongard remained as 'Senior Adviser' before transitioning to the CIA in 1998. Deutsche Bank was later fined $150 million by the New York State Department of Financial Services for enabling Jeffrey Epstein's financial activities post-conviction — maintaining over 40 accounts for Epstein's entities. This creates an institutional continuity chain: Alex. Brown (Krongard era) → Deutsche Bank Alex. Brown (acquisition) → Deutsche Bank (Epstein enablement), though Krongard's personal role in the later Epstein relationship is not documented.",
     0.65, '["E2", "krongard", "alex_brown", "deutsche_bank", "epstein", "institutional_chain", "PKG-911"]'),

    # =========================================================================
    # ABR — Alex. Brown / Deutsche Bank Alex. Brown (target_id=60)
    # =========================================================================
    ("ABR-001", "factual",
     "Alex. Brown & Sons was the executing broker for anomalous pre-9/11 put options on airline stocks, including 4,744 UAL (United Airlines) put contracts purchased September 6-7, 2001 and a large AMR (American Airlines) put block purchased September 10, 2001 — the day before the attacks. Alex. Brown is the single institution most documented in connection with these transactions.",
     0.95, '["E1", "alex_brown", "put_options", "UAL", "AMR", "9/11", "PKG-911"]'),

    ("ABR-002", "factual",
     "Poteshman (2006, Journal of Business, 68+ peer citations): Using proprietary CBOE data, the probability that the AMR put option activity in the days before 9/11 was the product of informed trading is calculated at greater than 99%. This is E1 peer-reviewed statistical evidence using the most authoritative available dataset, directly contradicting the 9/11 Commission's characterization of the put options as having an 'innocuous explanation.'",
     0.90, '["E1", "alex_brown", "put_options", "Poteshman_2006", "peer_reviewed", "9/11_commission_contradiction", "PKG-911"]'),

    ("ABR-003", "factual",
     "Chesney, Crameri & Mancini (Journal of Financial Stability 2015; SSRN 1522157): Identifies $15 million or more in informed trading gains across six or more companies in the period before 9/11, including Swiss Re, Merrill Lynch, and Morgan Stanley — extending the informed trading hypothesis beyond the airlines. E1 peer-reviewed evidence.",
     0.85, '["E1", "alex_brown", "put_options", "Chesney_2015", "peer_reviewed", "PKG-911"]'),

    ("ABR-004", "factual",
     "Mayo Shattuck III, then-CEO of Deutsche Bank Alex. Brown, resigned on September 12, 2001 — one day after the attacks — with no public explanation provided for the timing of his departure. Shattuck had been in the role since Deutsche Bank's 1999 acquisition of Alex. Brown.",
     0.90, '["E1", "alex_brown", "mayo_shattuck", "resignation", "timing_anomaly", "PKG-911"]'),

    ("ABR-005", "factual",
     "The SEC destroyed records related to its post-9/11 put options investigation as part of routine destruction procedures, creating a permanent epistemic gap. Separately, the 'single U.S.-based institutional investor' identified by the SEC as responsible for approximately 95% of the UAL put options purchased on September 6 has never been publicly named despite the SEC's investigation and the 9/11 Commission review.",
     0.90, '["E1", "E2", "alex_brown", "SEC_investigation", "records_destruction", "unidentified_investor", "PKG-911"]'),

    ("ABR-006", "factual",
     "The 9/11 Commission characterized the anomalous pre-attack put options as having an 'innocuous explanation' (Staff Statement 21, Footnote 130), citing SEC and FBI investigations that concluded no link to al-Qaeda. This characterization is directly contradicted by two subsequent peer-reviewed academic studies (Poteshman 2006; Chesney, Crameri & Mancini 2015) using independent quantitative methodologies.",
     0.90, '["E1", "alex_brown", "put_options", "9/11_commission", "peer_reviewed_contradiction", "PKG-911"]'),

    # =========================================================================
    # HOK — Howard Krongard (target_id=61)
    # =========================================================================
    ("HOK-001", "factual",
     "Howard 'Cookie' Krongard was appointed State Department Inspector General on May 2, 2005 by President George W. Bush. He had no prior government experience. His appointment as the State Department's chief watchdog — at the same time his brother Buzzy was recently departed from CIA leadership — placed the Krongard family in simultaneous senior positions across the national security apparatus.",
     0.95, '["E1", "howard_krongard", "state_dept_IG", "appointment", "PKG-911"]'),

    ("HOK-002", "factual",
     "A July 11, 2007 email from Howard Krongard to State Department IG staff (E1, House Oversight Committee exhibit) directed staff to stop ALL work on Blackwater contract investigations immediately. The email was sent 15 days before Erik Prince sent Buzzy Krongard an invitation to join the Blackwater advisory board (dated July 26, 2007), establishing a documented timeline of coordinated obstruction.",
     0.95, '["E1", "howard_krongard", "blackwater", "investigation_blocking", "email_evidence", "PKG-911"]'),

    ("HOK-003", "factual",
     "Howard Krongard simultaneously blocked three high-value investigations from his own IG office: (1) Blackwater arms smuggling probe; (2) the $736 million Baghdad Embassy construction fraud; (3) a $1 billion DynCorp procurement fraud investigation. Seven whistleblowers from within his own office testified to Congress about the obstruction pattern.",
     0.95, '["E1", "howard_krongard", "investigation_blocking", "baghdad_embassy", "DynCorp", "whistleblowers", "PKG-911"]'),

    ("HOK-004", "factual",
     "At the November 14, 2007 House Oversight Committee hearing, Howard Krongard denied under oath knowing that his brother Buzzy was on the Blackwater advisory board. He then called a recess, left the chamber to telephone Buzzy, returned, and recused himself. Buzzy subsequently issued a public statement confirming he had told Howard of his board position. The sequence constitutes a documented potential perjury, confidence 0.70.",
     0.85, '["E1", "howard_krongard", "perjury_risk", "congressional_hearing", "blackwater", "PKG-911"]'),

    ("HOK-005", "factual",
     "Howard Krongard resigned as State Department Inspector General on January 15, 2008. He was not eligible for retirement benefits. He faced no prosecution and no formal censure despite seven internal whistleblowers, documented email evidence of obstruction, and a congressional hearing establishing his blocking of three simultaneous investigations.",
     0.90, '["E1", "howard_krongard", "resignation", "no_prosecution", "impunity", "PKG-911"]'),

    # =========================================================================
    # CGK — Cheryl Gordon Krongard (target_id=62)
    # =========================================================================
    ("CGK-001", "factual",
     "Cheryl Gordon Krongard was a Senior Partner at Apollo Management (Leon Black's private equity firm) from 2002 to 2004 — a period concurrent with Buzzy Krongard's tenure as CIA Executive Director and Blackwater's receipt of its first CIA contracts. She is Buzzy Krongard's wife.",
     0.90, '["E1", "cheryl_krongard", "apollo", "leon_black", "CIA_concurrent", "PKG-911"]'),

    ("CGK-002", "assessment",
     "Three-node Krongard family circuit hypothesis (Buzzy + Howard + Cheryl = integrated institutional protection across CIA, State IG, and Apollo) is NOT confirmed. Exhaustive search found no evidence Cheryl Gordon Krongard held a position on the State Department IG Advisory Board or any other role structurally connecting her Apollo tenure to Howard's IG blockage of Blackwater investigations. The two-node circuit (Buzzy + Howard) is confirmed at 0.95 confidence. The three-node hypothesis remains at 0.25.",
     0.90, '["E2", "cheryl_krongard", "three_node_circuit", "negative_finding", "two_node_confirmed", "PKG-911"]'),
]

# =============================================================================
# CROSS-REFERENCES — 10 connections
# Each: (xref_id, entity1, entity2, relationship_type, source_claims, confidence)
# =============================================================================

CROSS_REFS = [
    ("xref_bzk_001", "BZK_Buzzy_Krongard", "HOK_Howard_Krongard",
     "FAMILY_CIRCUIT_TWO_NODE_CONFIRMED",
     "BZK-007,BZK-008,HOK-002,HOK-004,CGK-002",
     0.95),

    ("xref_bzk_002", "BZK_Buzzy_Krongard", "BWK_Blackwater",
     "PERSONAL_AUTHORIZATION_FIRST_CIA_CONTRACT",
     "BZK-005,BZK-007",
     0.95),

    ("xref_bzk_003", "BZK_Buzzy_Krongard", "ABR_AlexBrown",
     "FORMER_CEO_PUT_OPTIONS_PERIOD_OVERLAP",
     "BZK-001,BZK-002,BZK-009,ABR-001,ABR-004",
     0.75),

    ("xref_bzk_004", "ABR_AlexBrown", "Target54_911_Financial_Foreknowledge",
     "PRIMARY_EXECUTING_BROKER_ANOMALOUS_PUT_OPTIONS",
     "ABR-001,ABR-002,ABR-003,ABR-005,ABR-006",
     0.85),

    ("xref_bzk_005", "ABR_AlexBrown", "Deutsche_Bank_Epstein",
     "INSTITUTIONAL_CONTINUITY_CHAIN_ALEX_BROWN_TO_EPSTEIN_ENABLEMENT",
     "BZK-009,ABR-004",
     0.55),

    ("xref_bzk_006", "HOK_Howard_Krongard", "BWK_Blackwater",
     "IG_INVESTIGATION_BLOCKING_EMAIL_EVIDENCE_E1",
     "HOK-002,HOK-003,HOK-004,HOK-005",
     0.95),

    ("xref_bzk_007", "CGK_Cheryl_Krongard", "Target68_Apollo_Global",
     "SENIOR_PARTNER_2002_2004_CONCURRENT_CIA_BLACKWATER_CONTRACTS",
     "CGK-001,CGK-002",
     0.90),

    ("xref_bzk_008", "BZK_Buzzy_Krongard", "Target34_George_Tenet",
     "CIA_EXEC_DIR_UNDER_DCI_TENET_CONCURRENT_9_11_AND_WAR_ON_TERROR",
     "BZK-003,BZK-006",
     0.90),

    ("xref_bzk_009", "ABR_AlexBrown", "ERP_Erik_Prince",
     "KRONGARD_AS_BRIDGE_ALEX_BROWN_TO_BLACKWATER_CIA_RELATIONSHIP",
     "BZK-001,BZK-005,BZK-007",
     0.80),

    ("xref_bzk_010", "HOK_Howard_Krongard", "BZK_Buzzy_Krongard",
     "COORDINATED_OBSTRUCTION_TIMELINE_HOK_EMAIL_JULY11_TO_BZK_BOARD_INVITE_JULY26",
     "HOK-002,BZK-007,BZK-008,HOK-004",
     0.85),
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
                "script": "1_of_4",
                "description": "Krongard family intelligence report covering Buzzy (CIA Exec Dir), Alex. Brown put options, Howard (State IG obstruction), and Cheryl (Apollo concurrent role)",
                "targets": {
                    "59": "Alvin 'Buzzy' Krongard",
                    "60": "Alex. Brown / Deutsche Bank Alex. Brown",
                    "61": "Howard Krongard",
                    "62": "Cheryl Gordon Krongard",
                },
                "total_claims": len(CLAIMS),
                "total_xrefs": len(CROSS_REFS),
                "key_finding": "Two-node Krongard circuit confirmed (Buzzy+Howard); HOK email July 11 precedes BZK board invite July 26",
                "three_node_circuit": "NOT_CONFIRMED (0.25)",
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

    for prefix in ["BZK", "ABR", "HOK", "CGK"]:
        c.execute("SELECT COUNT(*) FROM evidence_claims WHERE claim_id LIKE ?",
                  (f"{prefix}%",))
        print(f"  {prefix}-* claims in DB: {c.fetchone()[0]}")

    c.execute("SELECT COUNT(*) FROM cross_references WHERE xref_id LIKE 'xref_bzk_%'")
    bzk_xrefs = c.fetchone()[0]

    conn.close()

    print(f"\n{'='*60}")
    print(f"PKG-911 KRONGARD INGESTION COMPLETE")
    print(f"{'='*60}")
    print(f"  Sources added this run:  {sources_added}")
    print(f"  Claims added this run:   {claims_added}")
    print(f"  Claims skipped (dupes):  {claims_skipped}")
    print(f"  Xrefs added this run:    {xrefs_added}")
    print(f"  Xrefs skipped (dupes):   {xrefs_skipped}")
    print(f"{'='*60}")
    print(f"  xref_bzk_* in DB:        {bzk_xrefs}")
    print(f"{'='*60}")
    print(f"  DATABASE GRAND TOTALS:")
    print(f"    Total sources:         {total_sources}")
    print(f"    Total claims:          {total_claims}")
    print(f"    Total cross-refs:      {total_xrefs}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
