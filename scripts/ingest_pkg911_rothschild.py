#!/usr/bin/env python3
"""Ingest Edmond de Rothschild Group intelligence reports into sherlock.db.

PKG-911 Phase 8B — Script 4 of 4.

Registers 1 evidence source (PKG911_ROTHSCHILD_001), extracts ~7 claims
for the Edmond de Rothschild Group / Rothschild Asset Management (RAM series),
and creates ~5 cross-references extending and connecting Rothschild findings
to existing targets.

NOTE: WEX-060 already exists in the DB (basic Epstein-Rothschild reference).
This script does NOT duplicate WEX-060. RAM claims EXTEND the record with
primary-source DOJ documentation. The DB target is listed as 'Rothschild Asset
Management' (target_id=63) but the analytical subject is the Edmond de
Rothschild Group (EdR) — legally distinct from Rothschild & Co (London/Paris).

Targets:
  63 — Rothschild Asset Management (actual subject: Edmond de Rothschild Group)
"""
import sqlite3
import json
from datetime import datetime

DB_PATH = "/home/johnny5/Sherlock/sherlock.db"

SOURCE = {
    "source_id": "PKG911_ROTHSCHILD_001",
    "title": "Edmond de Rothschild Group Intelligence Report (PKG-911 Phase 8B)",
    "file_path": "evidence/rothschild_research_phase1_asset_mgmt.md",
    "evidence_type": "intelligence_report",
}

# =============================================================================
# CLAIMS — 7 claims in RAM series (Rothschild Asset Management / EdR)
# WEX-060 already exists; this series EXTENDS it with primary-source detail.
# Each: (claim_id, claim_type, text, confidence, tags_json_string)
# =============================================================================

CLAIMS = [
    ("RAM-001", "factual",
     "Critical disambiguation: The Sherlock DB target 63 'Rothschild Asset Management' refers analytically to the Edmond de Rothschild Group (EdR), a Geneva-based Swiss/French private banking group headquartered at 18 rue de Rive, Geneva. Its CEO is Ariane de Rothschild (née Langner). EdR is legally and operationally distinct from Rothschild & Co (London/Paris M&A advisory, formerly N M Rothschild & Sons). The two branches of the Rothschild family disputed the use of the 'Rothschild' brand name commercially until a 2018 French court settlement. All Epstein-Rothschild connections in available primary sources relate to EdR, not Rothschild & Co.",
     0.99, '["E1", "rothschild", "EdR", "disambiguation", "Ariane_de_Rothschild", "PKG-911"]'),

    ("RAM-002", "factual",
     "On October 5, 2015, Jeffrey Epstein's Southern Trust Company (incorporated in the US Virgin Islands) signed a $25 million advisory contract with Edmond de Rothschild Holding S.A., countersigned by Ariane de Rothschild. The payment was activated within three days of EdR's own $45.245 million Department of Justice Swiss Bank Program non-prosecution agreement, signed December 18, 2015. The temporal proximity between Epstein's advisory fee activation and EdR's DOJ settlement resolution is a payment timing anomaly documented in DOJ primary source records.",
     0.90, '["E1", "rothschild", "EdR", "Southern_Trust", "25M_contract", "DOJ_NPA", "payment_anomaly", "PKG-911"]'),

    ("RAM-003", "factual",
     "Epstein introduced Kathryn Ruemmler (former Obama White House Counsel) to Edmond de Rothschild Group to represent them in their DOJ Swiss Bank Program negotiations, while simultaneously maintaining a personal advisory relationship with Ruemmler. Ruemmler negotiated the December 2015 non-prosecution agreement that directly triggered the activation of Epstein's own $25 million advisory fee from EdR. This creates a documented conflict of interest engineered by Epstein: he placed his personal attorney in position to generate his own advisory fee trigger. Ruemmler resigned from Goldman Sachs in February 2026 following public disclosure of this relationship.",
     0.90, '["E1", "rothschild", "EdR", "Ruemmler", "conflict_of_interest", "engineered_nexus", "Goldman_Sachs", "PKG-911"]'),

    ("RAM-004", "factual",
     "Ariane de Rothschild attended 12 or more documented personal meetings with Jeffrey Epstein between 2013 and 2019, based on DOJ scheduling records (E1). She made approximately $1 million in auction purchases on Epstein's behalf before the advisory contract was signed in 2015. The pre-contract purchasing relationship establishes that the Epstein-Ariane de Rothschild personal relationship predated and likely generated the formal contract, rather than the contract being a purely transactional arm's-length arrangement.",
     0.85, '["E1", "rothschild", "Ariane_de_Rothschild", "personal_meetings", "auction_purchases", "pre_contract_relationship", "PKG-911"]'),

    ("RAM-005", "factual",
     "Les Wexner testified under oath at a congressional deposition on February 18, 2026 (approximately 5 hours, at his New Albany mansion) that Epstein cited 'personal work for the Rothschild family in France' as a professional credential in the mid-to-late 1980s — before Wexner granted Epstein power of attorney in 1991 — and that Élie de Rothschild (1917-2007) personally vouched for Epstein during this period. If accurate, this places Epstein's Edmond de Rothschild relationship before his Wexner relationship, potentially inverting the conventional origin narrative in which Wexner was Epstein's primary introducer to the European financial elite. Confidence in accuracy of Wexner's testimony: 0.75 (E1 sworn testimony; Élie died 2007, independent corroboration unavailable).",
     0.70, '["E1", "E2", "rothschild", "Wexner_testimony", "Elie_de_Rothschild", "pre_Wexner_relationship", "origin_narrative", "PKG-911"]'),

    ("RAM-006", "factual",
     "DEA Operation Chain Reaction, launched December 17, 2010, investigated Epstein and 14 redacted co-conspirators for approximately $50 million in suspicious wire transfers. The operation ran through at least 2015 — concurrent with the period in which Epstein was brokering the Edmond de Rothschild DOJ non-prosecution agreement and signing the $25 million advisory contract. The identities of all 14 co-conspirators remain redacted in available DOJ records. The operation's confirmed DEA status is E1; co-conspirator identities are redacted E1.",
     0.85, '["E1", "rothschild", "DEA_Chain_Reaction", "wire_transfers", "co_conspirators_redacted", "concurrent_DOJ_timeline", "PKG-911"]'),

    ("RAM-007", "factual",
     "The term 'Rothschild' appears approximately 12,000 times across the 3.8 million pages of the DOJ Epstein document release (as of February 2026). This frequency far exceeds what a single 2015 advisory contract and its associated correspondence would generate, suggesting the Epstein-EdR relationship extends significantly beyond the documented $25 million contract. The full scope of the relationship has not been systematically analyzed. This represents a major unworked intelligence gap in the Epstein document corpus.",
     0.75, '["E2", "rothschild", "DOJ_document_release", "frequency_anomaly", "unanalyzed_scope", "intelligence_gap", "PKG-911"]'),
]

# =============================================================================
# CROSS-REFERENCES — 5 connections
# Each: (xref_id, entity1, entity2, relationship_type, source_claims, confidence)
# =============================================================================

CROSS_REFS = [
    ("xref_ram_001", "RAM_EdR_Rothschild", "WEX-060_Epstein_Rothschild",
     "EXTENDING_WEX_060_WITH_PRIMARY_SOURCE_DOJ_DOCUMENTATION",
     "RAM-001,RAM-002,RAM-003,RAM-004,WEX-060",
     0.90),

    ("xref_ram_002", "RAM_EdR_Rothschild", "Target47_Wexner",
     "WEXNER_TESTIMONY_PLACES_EPSTEIN_IN_ROTHSCHILD_ORBIT_BEFORE_WEXNER_RELATIONSHIP",
     "RAM-005,WEX-060,WEX-081",
     0.70),

    ("xref_ram_003", "RAM_EdR_Rothschild", "Target42_Epstein",
     "25M_CONTRACT_RUEMMLER_CONFLICT_ARIANE_MEETINGS_DEA_CONCURRENT",
     "RAM-002,RAM-003,RAM-004,RAM-006",
     0.90),

    ("xref_ram_004", "RAM_Ruemmler_Nexus", "EdR_DOJ_NPA_December_2015",
     "EPSTEIN_ENGINEERED_CONFLICT_ATTORNEY_GENERATES_OWN_FEE_TRIGGER",
     "RAM-003,RAM-002",
     0.85),

    ("xref_ram_005", "RAM_DOJ_Rothschild_12000_Appearances", "RAM_Unanalyzed_Intelligence_Gap",
     "FREQUENCY_ANOMALY_SUGGESTS_RELATIONSHIP_SCOPE_EXCEEDS_KNOWN_CONTRACT",
     "RAM-007",
     0.65),
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
                "script": "4_of_4",
                "description": "Edmond de Rothschild Group (EdR) intelligence report. Subject is EdR (Geneva), NOT Rothschild & Co (London/Paris). Extends WEX-060 with primary-source DOJ documentation. Key: $25M contract activated within 3 days of EdR DOJ NPA; Ruemmler conflict engineered by Epstein; 12,000+ DOJ document appearances suggesting unanalyzed scope.",
                "targets": {
                    "63": "Rothschild Asset Management (analytical subject: Edmond de Rothschild Group)",
                },
                "total_claims": len(CLAIMS),
                "total_xrefs": len(CROSS_REFS),
                "key_finding": "Payment timing anomaly: $25M fee activated within 3 days of EdR DOJ NPA",
                "prior_DB_rothschild_claim": "WEX-060",
                "intelligence_gap": "12,000 DOJ appearances vs single known $25M contract — unanalyzed scope",
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

    c.execute("SELECT COUNT(*) FROM evidence_claims WHERE claim_id LIKE 'RAM%'")
    ram_claims = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM cross_references WHERE xref_id LIKE 'xref_ram_%'")
    ram_xrefs = c.fetchone()[0]

    conn.close()

    print(f"\n{'='*60}")
    print(f"PKG-911 ROTHSCHILD INGESTION COMPLETE")
    print(f"{'='*60}")
    print(f"  Sources added this run:  {sources_added}")
    print(f"  Claims added this run:   {claims_added}")
    print(f"  Claims skipped (dupes):  {claims_skipped}")
    print(f"  Xrefs added this run:    {xrefs_added}")
    print(f"  Xrefs skipped (dupes):   {xrefs_skipped}")
    print(f"{'='*60}")
    print(f"  RAM-* claims in DB:      {ram_claims}")
    print(f"  xref_ram_* in DB:        {ram_xrefs}")
    print(f"{'='*60}")
    print(f"  DATABASE GRAND TOTALS:")
    print(f"    Total sources:         {total_sources}")
    print(f"    Total claims:          {total_claims}")
    print(f"    Total cross-refs:      {total_xrefs}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
