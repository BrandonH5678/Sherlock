#!/usr/bin/env python3
"""Ingest Blackwater / Erik Prince intelligence reports into sherlock.db.

PKG-911 Phase 8B — Script 2 of 4.

Registers 1 evidence source (PKG911_BLACKWATER_001), extracts ~15 claims
across Erik Prince (ERP) and Blackwater (BWK), and creates ~8 cross-references
connecting Blackwater findings to existing targets.

Targets:
  64 — Erik Prince
  65 — Blackwater / Academi
"""
import sqlite3
import json
from datetime import datetime

DB_PATH = "/home/johnny5/Sherlock/sherlock.db"

SOURCE = {
    "source_id": "PKG911_BLACKWATER_001",
    "title": "Blackwater / Erik Prince Intelligence Report (PKG-911 Phase 8B)",
    "file_path": "evidence/prince_research_phase1_blackwater.md",
    "evidence_type": "intelligence_report",
}

# =============================================================================
# CLAIMS — 15 claims across ERP and BWK series
# Each: (claim_id, claim_type, text, confidence, tags_json_string)
# =============================================================================

CLAIMS = [
    # =========================================================================
    # ERP — Erik Prince (target_id=64)
    # =========================================================================
    ("ERP-001", "factual",
     "Erik Prince founded Blackwater USA in 1997 at Moyock, North Carolina. He is a Navy SEAL veteran (SEAL Team 8) and heir to Edgar Prince's automotive parts fortune, which sold to Johnson Controls for approximately $1.35 billion in 1996. The family inheritance provided the seed capital for Blackwater's initial training facility.",
     0.95, '["E1", "prince", "blackwater", "founding", "SEAL", "PKG-911"]'),

    ("ERP-002", "factual",
     "Prince met CIA Executive Director Alvin 'Buzzy' Krongard in post-9/11 meetings in late 2001. This personal relationship — developed over a matter of weeks — produced Blackwater's first CIA security contract in April 2002: $5.4 million, awarded without competitive bidding. The relationship between Krongard and Prince thus directly produced the foundational CIA-Blackwater financial relationship.",
     0.95, '["E1", "prince", "krongard", "CIA_contract", "no_bid", "PKG-911"]'),

    ("ERP-003", "factual",
     "Prince founded Frontier Services Group (FSG), listed on the Hong Kong Stock Exchange, in 2014. FSG is backed by CITIC Group, a Chinese state-owned conglomerate. FSG provides logistics for China's Belt and Road Initiative in Africa. Multiple American board members resigned citing national security concerns about a former senior CIA contractor operating a logistics company with Chinese state backing. Counterintelligence risk assessment: 0.75.",
     0.75, '["E2", "prince", "FSG", "CITIC", "China", "counterintelligence_risk", "PKG-911"]'),

    ("ERP-004", "factual",
     "On January 11, 2017, Prince attended a meeting in the Seychelles with Kirill Dmitriev, CEO of the Russian Direct Investment Fund. The meeting was arranged by George Nader, later convicted of federal sex trafficking charges. Prince testified to the House Intelligence Committee that the encounter was a 'chance meeting.' The Mueller investigation found evidence contradicting this characterization. Perjury confidence: 0.75.",
     0.80, '["E1", "E2", "prince", "seychelles", "Dmitriev", "Mueller", "Nader", "perjury_risk", "PKG-911"]'),

    ("ERP-005", "factual",
     "Prince submitted a 26-page proposal to the Trump administration in 2025 for a $25 billion private contractor deportation program. He visited the White House following the January 2025 inauguration. As of early 2026, Prince operates Vectus Global, a logistics and security firm with operations in Haiti. His post-Blackwater ventures have continued in the private military contractor space.",
     0.85, '["E1", "E2", "prince", "trump_2025", "deportation_proposal", "vectus_global", "PKG-911"]'),

    # =========================================================================
    # BWK — Blackwater / Academi (target_id=65)
    # =========================================================================
    ("BWK-001", "factual",
     "Blackwater's documented US government contract revenue from 2001 to 2009 is estimated at $1.5 to $2.1 billion, including up to $600 million in classified CIA contracts. The classified contract total cannot be confirmed from public sources. Rebranded from Blackwater to Xe Services (2009) and then Academi (2011) following reputational damage.",
     0.80, '["E1", "E2", "blackwater", "revenue", "CIA_contracts", "classified", "PKG-911"]'),

    ("BWK-002", "factual",
     "From approximately 2004 to 2009, the CIA contracted Blackwater for a targeted killing program aimed at al-Qaeda figures. The program was concealed from congressional intelligence oversight committees for approximately seven years at the direction of Vice President Dick Cheney. CIA Director Leon Panetta disclosed the program to Congress and cancelled it in June 2009. The program did not kill any terrorist suspects during its operational period.",
     0.90, '["E1", "blackwater", "assassination_program", "Cheney", "congressional_concealment", "Panetta", "PKG-911"]'),

    ("BWK-003", "factual",
     "On September 16, 2007, Blackwater contractors at Nisour Square, Baghdad killed 17 Iraqi civilians and wounded 20 others. The FBI found that at least 14 of the killings were without justification. Four Blackwater contractors were convicted between 2014 and 2018. President Trump pardoned all four on December 22, 2020.",
     0.99, '["E1", "blackwater", "Nisour_Square", "civilian_killings", "Trump_pardons", "PKG-911"]'),

    ("BWK-004", "factual",
     "Coalition Provisional Authority Order 17, signed on June 27, 2004 — two days before the handover of sovereignty to Iraq — granted all Coalition contractors complete immunity from Iraqi law. This legal immunity was created by design, timed precisely two days before Blackwater's biggest operational expansion began. The legal architecture of immunity preceded rather than followed Blackwater's worst documented abuses.",
     0.95, '["E1", "blackwater", "CPA_Order_17", "contractor_immunity", "Iraq", "legal_architecture", "PKG-911"]'),

    ("BWK-005", "factual",
     "A systematic CIA-to-Blackwater personnel pipeline operated within a three-year window (2004-2007): Alvin 'Buzzy' Krongard (CIA No. 3, Executive Director) joined Blackwater's advisory board in 2007. J. Cofer Black (CIA Counterterrorism Center Director) became Blackwater Vice Chairman in 2005. Robert Richer (CIA Deputy Director of Operations No. 2) became Blackwater VP Intelligence in 2005. Enrique Prado (CIA CTC Chief of Operations) became Blackwater VP Special Government Programs in 2006. All four senior CIA officials moved to Blackwater within the same window. Confidence this represents systematic institutional transfer rather than coincidence: 0.75.",
     0.85, '["E1", "blackwater", "CIA_pipeline", "Krongard", "Cofer_Black", "Richer", "Prado", "PKG-911"]'),

    ("BWK-006", "factual",
     "Blackwater's Presidential Airways and EP Aviation transported detainees to CIA black sites under the extraordinary rendition program. More than 1,245 rendition flights across 54 countries have been documented. Blackwater also provided security personnel and logistics at black site facilities. The aviation subsidiary thus served as the physical infrastructure for rendition.",
     0.85, '["E1", "blackwater", "extraordinary_rendition", "rendition_flights", "black_sites", "PKG-911"]'),

    ("BWK-007", "factual",
     "The CIA assassination program contracted to Blackwater was concealed from congressional intelligence oversight for approximately seven years (2002-2009), at the direction of Vice President Cheney. This represents one of the longest documented violations of statutory congressional notification requirements for covert action programs in the post-Church Committee era.",
     0.90, '["E1", "blackwater", "Cheney", "congressional_concealment", "oversight_violation", "PKG-911"]'),

    ("BWK-008", "assessment",
     "Seven-layer accountability evasion architecture documented for Blackwater's Iraq operations: (1) contractor status — not subject to UCMJ; (2) CPA Order 17 — Iraqi legal immunity; (3) Military Extraterritorial Jurisdiction Act gap — MEJA did not clearly cover CIA contractors; (4) classification — assassination program hidden; (5) Inspector General capture — Howard Krongard blocked Blackwater IG investigations; (6) congressional concealment — assassination program hidden for 7 years by Cheney; (7) presidential pardons — Trump 2020 pardons for Nisour Square convictions. Probability that all seven evasion layers aligned coincidentally without deliberate design: 0.05 to 0.10.",
     0.85, '["assessment", "blackwater", "accountability_evasion", "seven_layers", "architecture_of_impunity", "PKG-911"]'),

    ("BWK-009", "factual",
     "Blackwater's first CIA contract ($5.4M, April 2002, no competitive bid) was for 'security services' at CIA facilities. By 2007 the relationship had expanded to an estimated $600M in classified contracts, a 110x scale increase in five years. The rate of contract expansion without competitive bidding procedures is without documented parallel in CIA procurement history.",
     0.80, '["E1", "E2", "blackwater", "CIA_contract", "no_bid", "contract_expansion", "PKG-911"]'),

    ("BWK-010", "factual",
     "George Nader, who arranged the January 2017 Seychelles meeting between Erik Prince and Russian RDIF CEO Kirill Dmitriev, was convicted in federal court in 2020 on charges of transporting a minor for sexual activity and possession of child pornography. Nader's role as fixer for both the Prince-Dmitriev meeting and his own sex trafficking crimes places him at the intersection of the Blackwater/Prince network and the trafficking-adjacent nexus documented elsewhere in the Epstein-Maxwell campaign.",
     0.80, '["E1", "blackwater", "prince", "Nader", "sex_trafficking", "Dmitriev", "Epstein_nexus", "PKG-911"]'),
]

# =============================================================================
# CROSS-REFERENCES — 8 connections
# Each: (xref_id, entity1, entity2, relationship_type, source_claims, confidence)
# =============================================================================

CROSS_REFS = [
    ("xref_bwk_001", "ERP_Erik_Prince", "BZK_Buzzy_Krongard",
     "CIA_BLACKWATER_PERSONAL_RELATIONSHIP_AUTHORIZED_NO_BID_CONTRACT",
     "ERP-002,BWK-001,BWK-009",
     0.95),

    ("xref_bwk_002", "BWK_Blackwater", "HOK_Howard_Krongard",
     "IG_PROTECTION_CONCURRENT_WITH_BLACKWATER_OPERATIONS",
     "BWK-008,HOK-002,HOK-003,HOK-004",
     0.95),

    ("xref_bwk_003", "BWK_Blackwater", "Target34_George_Tenet",
     "DCI_TENET_OVERSAW_CIA_DURING_INITIAL_BLACKWATER_RELATIONSHIP_DEVELOPMENT",
     "BWK-001,BWK-002,ERP-002",
     0.80),

    ("xref_bwk_004", "ERP_Erik_Prince", "FSG_CITIC_China",
     "FORMER_CIA_CONTRACTOR_OPERATING_CHINESE_STATE_BACKED_LOGISTICS_CI_RISK",
     "ERP-003",
     0.75),

    ("xref_bwk_005", "BWK_Blackwater", "xref_ep_055_Staley_Tenet",
     "TENET_IN_EPSTEIN_ORBIT_VIA_STALEY_EMAIL_WHILE_DCI_OVER_BLACKWATER_CIA",
     "BWK-003,BWK-007",
     0.50),

    ("xref_bwk_006", "BWK_Blackwater", "BWK_Accountability_Architecture",
     "SEVEN_LAYER_EVASION_PROBABILITY_DELIBERATE_DESIGN_0_05_TO_0_10",
     "BWK-004,BWK-007,BWK-008,HOK-002,BWK-003",
     0.85),

    ("xref_bwk_007", "BWK_CIA_Personnel_Pipeline", "BZK_Buzzy_Krongard",
     "KRONGARD_AS_ANCHOR_OF_CIA_TO_BLACKWATER_REVOLVING_DOOR",
     "BWK-005,BZK-005,BZK-007",
     0.90),

    ("xref_bwk_008", "ERP_Erik_Prince", "George_Nader_Trafficking",
     "SEYCHELLES_MEETING_FIXER_CONVICTED_SEX_TRAFFICKING_EPSTEIN_NEXUS_ADJACENT",
     "ERP-004,BWK-010",
     0.70),
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
                "script": "2_of_4",
                "description": "Blackwater and Erik Prince intelligence report covering founding, CIA contracts, Nisour Square, rendition, CIA pipeline, CPA Order 17, seven-layer accountability evasion, FSG/China CI risk, and Seychelles/Nader connection",
                "targets": {
                    "64": "Erik Prince",
                    "65": "Blackwater / Academi",
                },
                "total_claims": len(CLAIMS),
                "total_xrefs": len(CROSS_REFS),
                "key_finding": "Seven-layer accountability evasion architecture; deliberate design probability 0.05-0.10",
                "CIA_pipeline": "Four senior CIA officials to Blackwater within 2004-2007 window",
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

    for prefix in ["ERP", "BWK"]:
        c.execute("SELECT COUNT(*) FROM evidence_claims WHERE claim_id LIKE ?",
                  (f"{prefix}%",))
        print(f"  {prefix}-* claims in DB: {c.fetchone()[0]}")

    c.execute("SELECT COUNT(*) FROM cross_references WHERE xref_id LIKE 'xref_bwk_%'")
    bwk_xrefs = c.fetchone()[0]

    conn.close()

    print(f"\n{'='*60}")
    print(f"PKG-911 BLACKWATER INGESTION COMPLETE")
    print(f"{'='*60}")
    print(f"  Sources added this run:  {sources_added}")
    print(f"  Claims added this run:   {claims_added}")
    print(f"  Claims skipped (dupes):  {claims_skipped}")
    print(f"  Xrefs added this run:    {xrefs_added}")
    print(f"  Xrefs skipped (dupes):   {xrefs_skipped}")
    print(f"{'='*60}")
    print(f"  xref_bwk_* in DB:        {bwk_xrefs}")
    print(f"{'='*60}")
    print(f"  DATABASE GRAND TOTALS:")
    print(f"    Total sources:         {total_sources}")
    print(f"    Total claims:          {total_claims}")
    print(f"    Total cross-refs:      {total_xrefs}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
