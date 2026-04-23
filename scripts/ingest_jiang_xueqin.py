#!/usr/bin/env python3
"""Ingest Jiang Xueqin / Predictive History source assessment into sherlock.db.

Registers 1 target (Jiang Xueqin as intelligence source), 1 evidence source
(JXQ_PREDICTIVE_HISTORY_001), extracts 28 claims (JXQ-001 to JXQ-028), and
creates 12 cross-references connecting findings to existing Sherlock evidence.
"""
import sqlite3
import json
from datetime import datetime

DB_PATH = "/home/johnny5/Sherlock/sherlock.db"

# Target: Jiang Xueqin as intelligence source (not investigation subject)
TARGET = {
    "name": "Jiang Xueqin (Predictive History)",
    "target_type": "person",
    "priority": 3,
    "status": "new",
    "metadata": {
        "role": "intelligence_source",
        "bias_vector": "CCP_aligned_0.85",
        "born": 1976,
        "nationality": "Chinese-Canadian",
        "education": "BA English Literature, Yale College 1999",
        "location": "Beijing, China",
        "platform_youtube": "@predictivehistory (~1.9M subscribers)",
        "platform_substack": "predictivehistory.substack.com (83K+ subscribers, #1 world politics)",
        "platform_twitter": "@xueqinjiang",
        "handling_protocol": "Extract structural analysis and specific factual claims. Discard prescriptive conclusions about multipolarity. Flag all China/Russia omissions as analytically significant. Cross-reference testable claims against Sherlock evidence base before accepting.",
    },
}

# Single source for the assessment
SOURCE = {
    "source_id": "JXQ_PREDICTIVE_HISTORY_001",
    "title": "Jiang Xueqin / Predictive History Source Assessment",
    "file_path": "analysis/jiang_predictive_history_source_assessment.md",
    "evidence_type": "intelligence_report",
}

# =============================================================================
# CLAIMS — 28 claims (JXQ-001 to JXQ-028)
# Each: (claim_id, claim_type, text, confidence, tags_json_string)
# =============================================================================

CLAIMS = [
    # =========================================================================
    # SECTION A: Source Profile & Control Assessment (JXQ-001 to JXQ-005)
    # =========================================================================
    ("JXQ-001", "factual",
     "Jiang Xueqin (蒋学勤), born 1976 Guangdong, China. Chinese-Canadian. BA English Literature, Yale College 1999 (distinction, scholarship). No graduate degree or professorial appointment despite 'Professor Jiang' persona. Career primarily education reform (Peking University HS, Shenzhen Middle School, Harvard GSEE research affiliate). Currently history/philosophy teacher at Moonshot Academy, Beijing. YouTube @predictivehistory ~1.9M subscribers, Substack 83K+ subscribers (#1 world politics).",
     0.90, '["E1", "E2", "source_profile", "yale", "JXQ"]'),

    ("JXQ-002", "assessment",
     "CCP-controlled or CCP-aligned assessment at 0.85 confidence. Evidence: family resides in China (permanent leverage); YouTube banned in China yet operates freely (requires state permission); previously expelled from China 2002 for politically inconvenient journalism, now welcomed back (arrangement reached); output consistently predicts US imperial decline and validates Chinese strategic patience; 'Professor' credential inflation suggests constructed persona optimized for Western audience trust; messaging alignment with CCP strategic communication objectives is strong and consistent.",
     0.85, '["E2", "E3", "ccp_alignment", "bias_vector", "source_reliability", "JXQ"]'),

    ("JXQ-003", "assessment",
     "Source handling protocol: Reliable where CCP interests align with accurate analysis (US structural weaknesses, Western institutional corruption, dynastic power networks). Unreliable where CCP interests diverge from truth (Chinese internal dynamics, Taiwan, CCP-transnational capital integration, Russian imperial behavior, Ukraine). Deliberately amplified where useful to CCP (civilizational decline narratives, delegitimization of US institutional authority, secret society material undermining Western self-confidence).",
     0.80, '["E2", "source_reliability", "handling_protocol", "JXQ"]'),

    ("JXQ-004", "assessment",
     "Analytical strengths: game theory / structural incentive analysis (Iran Trap prediction succeeded on structural grounds, not lucky guessing); historical structural analogy (imperial overstretch well-supported by historical evidence); long time horizons (centuries and civilizational arcs); integration of financial, political, and covert dynamics as interconnected rather than separate domains. These align with Sherlock methodology.",
     0.85, '["E2", "methodology_assessment", "analytical_strengths", "JXQ"]'),

    ("JXQ-005", "assessment",
     "Analytical weaknesses: over-systematization (determinism leaving no room for contingency); Confucian hierarchy bias (overestimates top-down coordination, underestimates emergent dynamics and genuine chaos); CCP-shaped blind spots (cannot analyze China or Russia symmetrically); religion treated as purely instrumental (reductive, prevents understanding genuine belief as independent agency); audience capture toward manosphere/declinist optimization; unfalsifiable elements in Illuminati taxonomy (too general to test at framework level).",
     0.80, '["E2", "methodology_assessment", "analytical_weaknesses", "bias_vector", "JXQ"]'),

    # =========================================================================
    # SECTION B: Strong Convergence with Sherlock Evidence (JXQ-006 to JXQ-012)
    # =========================================================================
    ("JXQ-006", "assessment",
     "Jiang claim: dynastic families control institutional power across generations. Convergence 0.90 with Sherlock Master Dynasty Report (207 claims documenting opium trade → Skull & Bones → Brown Brothers Harriman → CIA → presidency pipeline). Sherlock evidence directly supports with named actors and dated transactions.",
     0.90, '["E1", "convergence_strong", "dynasty", "JXQ"]'),

    ("JXQ-007", "assessment",
     "Jiang claim: secret societies function as personnel pipelines for institutional power. Convergence 0.85 with Sherlock S&B evidence (membership → CIA/intelligence/presidency documented with specific names and dates). Note: Sherlock evidence is specific (S&B) where Jiang is categorical (Freemasonry writ large).",
     0.85, '["E1", "E2", "convergence_strong", "secret_societies", "skull_and_bones", "JXQ"]'),

    ("JXQ-008", "assessment",
     "Jiang claim: intelligence operations serve financial interests. Convergence 0.90 with Sullivan & Cromwell synthesis documenting 3 CIA coups directly benefiting S&C clients. Multiple verified operations with named beneficiaries in Sherlock evidence base.",
     0.90, '["E1", "convergence_strong", "intelligence_finance", "sullivan_cromwell", "JXQ"]'),

    ("JXQ-009", "assessment",
     "Jiang claim: financial system is a primary control mechanism. Convergence 0.85 with Brown Brothers Harriman → CIA funding streams, PKG-911 financial nexus findings, and Epstein financial network evidence across multiple Sherlock campaigns.",
     0.85, '["E1", "convergence_strong", "financial_control", "bbh", "pkg911", "JXQ"]'),

    ("JXQ-010", "assessment",
     "Jiang claim: Epstein network as financial/intelligence control system. Convergence 0.85 with PKG-911 campaign (838 claims, 313 cross-references documenting network structure). Parallel analysis reaching similar structural conclusions through independent methodology.",
     0.85, '["E1", "convergence_strong", "epstein", "pkg911", "JXQ"]'),

    ("JXQ-011", "assessment",
     "Jiang claim: imperial overstretch dynamics in US military posture. Convergence 0.80. Observable via multiple simultaneous theaters, alliance strain, and fiscal unsustainability. Sound structural analysis consistent with historical imperial decline patterns.",
     0.80, '["E2", "convergence_strong", "imperial_overstretch", "JXQ"]'),

    ("JXQ-012", "assessment",
     "Jiang claim: managed events / false flags as governance tool. Convergence 0.90 with Sherlock verified evidence: Operation Gladio (45 years), Operation Mockingbird (400+ media assets), MK-Ultra (20 years) — all documented historical programs in evidence base.",
     0.90, '["E1", "convergence_strong", "managed_events", "gladio", "mockingbird", "mk_ultra", "JXQ"]'),

    # =========================================================================
    # SECTION C: Partial Convergence (JXQ-013 to JXQ-016)
    # =========================================================================
    ("JXQ-013", "assessment",
     "Jiang claim: 'Illuminati' as organized coordination between Jesuits, Sabbatean Frankists, and Freemasons. Structural pattern (secret society → institutional power) supported by Sherlock evidence. Specific inter-organizational taxonomy unverified. Needs mosaic methodology testing on specific connections.",
     0.45, '["E3", "convergence_partial", "illuminati_taxonomy", "testable", "JXQ"]'),

    ("JXQ-014", "assessment",
     "Jiang claim: eschatological motivation driving Middle East policy. Some evidence of messianic/religious motivation in specific actors but insufficient to establish as primary driver. Testable via mosaic on specific decision-makers' stated beliefs and organizational affiliations.",
     0.40, '["E3", "convergence_partial", "eschatological", "testable", "JXQ"]'),

    ("JXQ-015", "assessment",
     "Jiang claim: US will lose Iran war. Structural analysis plausible (asymmetric warfare, 20-year Iranian preparation). Outcome uncertain. Live prediction with falsification timeline — monitor against real events.",
     0.50, '["E3", "convergence_partial", "iran_war", "live_prediction", "JXQ"]'),

    ("JXQ-016", "assessment",
     "Jiang claim: civilizational decline of the West is irreversible. Over-determined conclusion — structural pressures are real but 'irreversible' is a stronger claim than evidence supports. CCP bias vector may be amplifying decline narrative beyond what structural analysis warrants.",
     0.35, '["E3", "convergence_partial", "civilizational_decline", "ccp_bias", "JXQ"]'),

    # =========================================================================
    # SECTION D: Divergence (JXQ-017 to JXQ-019)
    # =========================================================================
    ("JXQ-017", "negative_finding",
     "Jiang claim: multipolar world emerging post-US hegemony. Sherlock assessment: 'multipolar' assumes competing empires, not collaborative/nested imperial systems. Russia may be nested within transnational capital system, not genuinely independent pole. Critical gap — Jiang cannot analyze this because CCP interests require the multipolarity narrative.",
     0.30, '["E3", "divergence", "multipolarity", "ccp_bias", "JXQ"]'),

    ("JXQ-018", "negative_finding",
     "Jiang claim: Ukraine outcome predetermined (Russian victory). Sherlock assessment: Ukrainian battlefield performance, technology/tactics evolution, and Russian supply chain vulnerabilities make outcome uncertain. Russia operates same imperial model Jiang describes for US. CCP bias vector prevents acknowledging Russian imperial behavior or Ukrainian agency.",
     0.25, '["E3", "divergence", "ukraine", "ccp_bias", "JXQ"]'),

    ("JXQ-019", "negative_finding",
     "Jiang claim: China represents genuine alternative to Western imperial model. GLARING OMISSION. Jiang's own framework applied to China reveals: princelings as dynastic families, Triads as secret societies, CCP-transnational capital integration, United Front Work Department as intelligence apparatus, surveillance state as ultimate control technology. Highest priority investigation target for Sherlock.",
     0.15, '["E3", "divergence", "china_omission", "ccp_bias", "highest_priority_gap", "JXQ"]'),

    # =========================================================================
    # SECTION E: Testable Claims & Research Targets (JXQ-020 to JXQ-025)
    # =========================================================================
    ("JXQ-020", "assessment",
     "Priority 1 research target: Jesuit influence on institutional power. Testable via mosaic — map Jesuit educational institutions to graduates in intelligence, finance, and political positions. Historical documentation of Jesuit networks as intelligence/influence apparatus is mainstream scholarly material.",
     0.50, '["E3", "research_target", "jesuit", "mosaic", "priority_1", "JXQ"]'),

    ("JXQ-021", "assessment",
     "Priority 1 research target: Sabbatean Frankist influence on Israeli policy. Testable via mosaic — specific individuals/organizations with documented Sabbatean-connected ideology in Israeli political/intelligence establishment. Gershom Scholem provides academic foundation. CRITICAL: must maintain fierce fact-narrative distinction per Research Posture Principle 5 — verifiable claims about specific individuals ≠ categorical claims about ethnic/religious groups.",
     0.40, '["E3", "research_target", "sabbatean_frankist", "mosaic", "priority_1", "fact_narrative_distinction", "JXQ"]'),

    ("JXQ-022", "assessment",
     "Priority 1 research target: Freemasonic influence on US national security. Testable via mosaic — documented Masonic membership among intelligence, military, and political leadership. Overlaps with but distinct from existing S&B evidence. Expand network mapping from S&B to broader secret society membership.",
     0.50, '["E3", "research_target", "freemasonic", "mosaic", "priority_1", "JXQ"]'),

    ("JXQ-023", "assessment",
     "Priority 2 research targets: managed drama specifics — Iran war structure and trajectory, US domestic political dynamics, European NATO dynamics. All testable against real-time events with falsification timelines.",
     0.45, '["E3", "research_target", "managed_drama", "live_predictions", "priority_2", "JXQ"]'),

    ("JXQ-024", "assessment",
     "Priority 3 research targets: financial system architecture — CBDC development timeline and implementation, de-dollarization dynamics, AI bubble collapse timeline. Testable against observable market and policy developments.",
     0.40, '["E3", "research_target", "financial_architecture", "live_predictions", "priority_3", "JXQ"]'),

    ("JXQ-025", "assessment",
     "CRITICAL investigation target: China/CCP gap. Apply Jiang's own framework to China across 5 domains: (1) Princelings/dynastic families (Eight Immortals, Xi family); (2) Secret societies (Triads, Green Gang historical continuity); (3) Transnational capital integration (HK tycoons, Macau casinos, Belt and Road, Panama Papers offshore wealth); (4) Intelligence operations (UFWD, MSS, CCP-Triad nexus, fentanyl precursor supply chains as hybrid warfare); (5) Science as control (social credit, surveillance state, AI monitoring, genetic databases). This is the analytical question Jiang's framework demands but his Beijing position prevents him from asking.",
     0.70, '["E2", "E3", "research_target", "china_ccp_gap", "highest_priority", "mosaic", "JXQ"]'),

    # =========================================================================
    # SECTION F: CCP-Western Nexus & Methodology Validation (JXQ-026 to JXQ-028)
    # =========================================================================
    ("JXQ-026", "assessment",
     "Known CCP-Western capital connection points requiring investigation: Kissinger decades-long China relationship and business interests; Blackstone/Schwarzman → Tsinghua University pipeline; Erik Prince/FSG/CITIC Group (PKG-911: CI risk 0.75); Wall Street capital flows into China (30+ years); Rothschild presence in China dating to opium wars; Yale-China Association (historical, connects to S&B/dynasty analysis).",
     0.75, '["E1", "E2", "china_western_nexus", "connection_points", "JXQ"]'),

    ("JXQ-027", "assessment",
     "Hypothesis space for CCP-Western relationship: H1 competing empires (conventional view); H2 collaborative empires (coordination at elite level despite surface competition); H3 nested systems (CCP as participant in transnational capital system, not independent pole); H4 managed competition (cartel of imperial systems that appear to compete while coordinating on core architecture). This is the question Jiang's framework demands but his position in Beijing prevents him from asking — high-priority Sherlock investigation target.",
     0.50, '["E3", "hypothesis_space", "china_western_nexus", "highest_priority", "JXQ"]'),

    ("JXQ-028", "assessment",
     "Jiang Xueqin viral event trajectory: May 2024 'The Iran Trap' lecture predicted Trump 2024 win and US-Iran war. First two predictions came true, driving viral growth mid-2025. Appeared on Breaking Points March 2026. Prediction success on structural grounds (not lucky guessing) validates game theory methodology while NOT validating CCP-aligned prescriptive conclusions.",
     0.85, '["E1", "E2", "iran_trap", "prediction_success", "methodology_validation", "JXQ"]'),
]

# =============================================================================
# CROSS-REFERENCES — 12 cross-refs linking findings to existing evidence
# Each: (xref_id, entity1, entity2, rel_type, source_claims, confidence)
# =============================================================================

CROSS_REFS = [
    # Strong convergence links
    ("xref_jxq_001",
     "Jiang Xueqin dynastic families thesis",
     "Master Dynasty Report (207 claims, opium→S&B→BBH→CIA→presidency)",
     "convergence", "JXQ-006", 0.90),

    ("xref_jxq_002",
     "Jiang Xueqin secret society personnel pipeline thesis",
     "Skull & Bones evidence (membership→CIA/intelligence/presidency)",
     "convergence", "JXQ-007", 0.85),

    ("xref_jxq_003",
     "Jiang Xueqin intelligence-serves-finance thesis",
     "Sullivan & Cromwell synthesis (3 documented CIA coups for S&C clients)",
     "convergence", "JXQ-008", 0.90),

    ("xref_jxq_004",
     "Jiang Xueqin financial control mechanism thesis",
     "PKG-911 financial nexus (BBH funding, Epstein network)",
     "convergence", "JXQ-009", 0.85),

    ("xref_jxq_005",
     "Jiang Xueqin Epstein financial-intelligence system thesis",
     "PKG-911 Epstein campaign (838 claims, 313 xrefs)",
     "convergence", "JXQ-010", 0.85),

    ("xref_jxq_006",
     "Jiang Xueqin managed events / false flags thesis",
     "Gladio (45yr), Mockingbird (400+ assets), MK-Ultra (20yr)",
     "convergence", "JXQ-012", 0.90),

    # China/CCP gap bridge nodes
    ("xref_jxq_007",
     "China/CCP gap — Erik Prince/FSG/CITIC bridge",
     "PKG-911 Erik Prince (CI risk 0.75, FSG/CITIC Group)",
     "bridge_node", "JXQ-025,JXQ-026", 0.75),

    ("xref_jxq_008",
     "China/CCP gap — Kissinger bridge",
     "Henry Kissinger decades-long China relationship and business interests",
     "bridge_node", "JXQ-026", 0.80),

    ("xref_jxq_009",
     "China/CCP gap — Rothschild opium dynasty continuity",
     "BBH dynasty evidence (Rothschild presence in China since opium wars)",
     "dynasty_continuity", "JXQ-026", 0.65),

    ("xref_jxq_010",
     "China/CCP gap — Yale-China / S&B pipeline",
     "Yale-China Association historical connection to S&B dynasty analysis",
     "institutional_bridge", "JXQ-026", 0.60),

    # Source reliability and methodology
    ("xref_jxq_011",
     "Jiang Xueqin source reliability profile",
     "CCP bias vector (reliable on Western corruption, unreliable on China/Russia)",
     "source_reliability", "JXQ-002,JXQ-003,JXQ-017,JXQ-018,JXQ-019", 0.85),

    ("xref_jxq_012",
     "Jiang Xueqin predictive methodology validation",
     "Iran Trap prediction (structural game theory validated by events)",
     "methodology_validation", "JXQ-004,JXQ-028", 0.85),
]


def ingest():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()

    targets_added = 0
    sources_added = 0
    claims_added = 0
    claims_skipped = 0
    xrefs_added = 0
    xrefs_skipped = 0

    # ---- Create target ----
    c.execute("SELECT target_id FROM targets WHERE name = ?",
              (TARGET["name"],))
    if c.fetchone():
        print(f"SKIP target {TARGET['name']}: already exists")
    else:
        c.execute("""
            INSERT INTO targets (name, target_type, priority, status, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            TARGET["name"],
            TARGET["target_type"],
            TARGET["priority"],
            TARGET["status"],
            now, now,
            json.dumps(TARGET["metadata"], indent=2),
        ))
        target_id = c.lastrowid
        targets_added += 1
        print(f"Added target: {TARGET['name']} (ID {target_id})")

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
                "campaign": "JXQ",
                "description": "Source assessment profiling Jiang Xueqin (Predictive History) as intelligence source with CCP bias vector. Convergence analysis against Sherlock evidence base. Investigation targets for China/CCP gap.",
                "total_claims": len(CLAIMS),
                "total_xrefs": len(CROSS_REFS),
                "key_finding": "CCP-aligned source (0.85) with genuine analytical value on Western institutional corruption. Strong convergence on 7 of 7 tested claims against Sherlock evidence. Critical gap: cannot analyze China using own framework.",
            })
        ))
        sources_added += 1
        print(f"Added source: {SOURCE['source_id']}")

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
    c.execute("SELECT COUNT(*) FROM targets")
    total_targets = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM evidence_sources")
    total_sources = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM evidence_claims")
    total_claims = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM cross_references")
    total_xrefs = c.fetchone()[0]

    conn.close()

    print(f"\n{'='*60}")
    print(f"JIANG XUEQIN INGESTION COMPLETE")
    print(f"{'='*60}")
    print(f"  Targets added this run:  {targets_added}")
    print(f"  Sources added this run:  {sources_added}")
    print(f"  Claims added this run:   {claims_added}")
    print(f"  Claims skipped (dupes):  {claims_skipped}")
    print(f"  Xrefs added this run:    {xrefs_added}")
    print(f"  Xrefs skipped (dupes):   {xrefs_skipped}")
    print(f"{'='*60}")
    print(f"  DATABASE GRAND TOTALS:")
    print(f"    Total targets:         {total_targets}")
    print(f"    Total sources:         {total_sources}")
    print(f"    Total claims:          {total_claims}")
    print(f"    Total cross-refs:      {total_xrefs}")
    print(f"{'='*60}")


if __name__ == "__main__":
    ingest()
