#!/usr/bin/env python3
"""
Ingestion script: Operation Epic Fury — Week 5 Situation Report
Source: /home/johnny5/Downloads/sherlock-sitrep-week5.md
Period: March 28 – April 3, 2026 (Days 29–35)
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = "/home/johnny5/Sherlock/sherlock.db"
SOURCE_FILE = "/home/johnny5/Downloads/sherlock-sitrep-week5.md"

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def register_source(conn):
    source_id = "EPIC_FURY_W5"
    title = "Operation Epic Fury — Week 5 Situation Report (Mar 28 – Apr 3, 2026)"
    conn.execute("""
        INSERT OR REPLACE INTO evidence_sources
        (source_id, title, file_path, evidence_type, created_at, ingested_at, processing_status, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        source_id, title, SOURCE_FILE, "intelligence_brief",
        "2026-04-03", datetime.now().isoformat(), "ingested",
        json.dumps({
            "classification": "OSINT",
            "period": "2026-03-28 to 2026-04-03",
            "days": "29-35",
            "campaign": "EPIC-FURY",
            "type": "weekly_sitrep"
        })
    ))
    return source_id

def register_targets(conn):
    """Register new targets relevant to Operation Epic Fury."""
    targets = [
        (141, "Operation Epic Fury", "operation", 2, "active",
         json.dumps({"type": "US-Iran conflict simulation/tracking", "start_date": "2026-02-28", "scope": "multi-front regional war"})),
        (142, "Strait of Hormuz Blockade", "event", 1, "active",
         json.dumps({"status": "effectively closed to Western shipping", "toll_system": "$2M/vessel in yuan or crypto", "traffic": "10-20 ships/day vs 150 pre-war"})),
        (143, "IRGC Toll System", "operation", 2, "active",
         json.dumps({"corridor": "Qeshm-Larak islands", "currency": "Chinese yuan or cryptocurrency", "bilateral_access": ["China", "India", "Pakistan", "Malaysia", "Thailand"]})),
        (144, "Houthi Belligerency (2026)", "actor", 3, "active",
         json.dumps({"entered_war": "2026-03-28", "targets": "Israel (Beersheba, Eilat)", "status": "limited engagement"})),
        (145, "Ukraine Gulf Deployment", "operation", 3, "active",
         json.dumps({"personnel": "228 counter-drone specialists", "countries": ["Jordan", "Kuwait", "Qatar", "Saudi Arabia", "UAE"], "agreements": ["Saudi MOU", "Qatar 10-year", "UAE in principle"]})),
    ]
    for t in targets:
        conn.execute("""
            INSERT OR IGNORE INTO targets
            (target_id, name, target_type, priority, status, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (t[0], t[1], t[2], t[3], t[4], datetime.now().isoformat(), datetime.now().isoformat(), t[5]))

def ingest_claims(conn, source_id):
    """Extract and ingest structured claims from the sitrep."""
    claims = [
        # SECTION 1: US-Israeli Strikes on Iran
        ("EF5-001", "factual_event", "SPND nuclear research chief Ali Fuladvand killed in airstrike at Borujerd, Lorestan Province on March 28. Had survived targeted strike during June 2025 Twelve-Day War.", 0.90,
         "Section 1: US-Israeli Strikes", json.dumps(["Ali Fuladvand", "SPND", "Borujerd", "Lorestan"]), json.dumps(["strike", "nuclear", "assassination", "SPND"])),

        ("EF5-002", "factual_event", "Washington Post reported cumulative damage as of March 28: 4 key ballistic missile production facilities and 29 missile launch bases struck since February 28.", 0.85,
         "Section 1: Cumulative strike assessment", json.dumps(["Washington Post", "ballistic missile"]), json.dumps(["strike_assessment", "missile_production"])),

        ("EF5-003", "factual_event", "IDF confirmed strike on Khojir Military Complex facility producing critical missile components — one of only two such facilities in Iran (March 29).", 0.90,
         "Section 1: March 29 strikes", json.dumps(["IDF", "Khojir Military Complex"]), json.dumps(["strike", "missile_production", "khojir"])),

        ("EF5-004", "factual_event", "Trump issued ultimatum March 30: destroy all power plants, oil wells, and desalination plants if no deal reached and Strait not reopened.", 0.95,
         "Section 1: Trump ultimatum", json.dumps(["Trump", "Strait of Hormuz"]), json.dumps(["ultimatum", "escalation", "infrastructure"])),

        ("EF5-005", "factual_event", "Iran Red Crescent reported 300+ hospitals/medical facilities and 90,000+ homes damaged or destroyed, roughly half in Tehran (March 31–April 1).", 0.80,
         "Section 1: Humanitarian impact", json.dumps(["Iran Red Crescent", "Tehran"]), json.dumps(["humanitarian", "hospitals", "civilian_damage"])),

        ("EF5-006", "factual_event", "US extended Strait reopening deadline to April 7. Five-day pause on power plant strikes announced. Iran denied any negotiations took place.", 0.90,
         "Section 1: Diplomatic pause", json.dumps(["Strait of Hormuz", "US", "Iran"]), json.dumps(["deadline", "negotiation", "power_plants"])),

        ("EF5-007", "factual_event", "Pasteur Institute of Iran (century-old medical research center) struck April 2. Steel plants in Isfahan targeted — Netanyahu claimed 70% of Iran's steel production capacity destroyed.", 0.85,
         "Section 1: April 2 strikes", json.dumps(["Pasteur Institute", "Isfahan", "Netanyahu"]), json.dumps(["civilian_infrastructure", "steel", "medical"])),

        ("EF5-008", "factual_event", "B1 Bridge between Tehran and Karaj struck and collapsed April 2; 8 killed, 95 wounded. US claimed military drone transport use; Iran insisted civilian infrastructure.", 0.90,
         "Section 1: B1 Bridge", json.dumps(["B1 Bridge", "Tehran", "Karaj"]), json.dumps(["bridge", "civilian_infrastructure", "disputed_targeting"])),

        ("EF5-009", "factual_event", "Ballistic missile chief Makram Atimi and battalion commanders killed in Kermanshah strike April 2.", 0.85,
         "Section 1: Leadership targeting", json.dumps(["Makram Atimi", "Kermanshah"]), json.dumps(["assassination", "missile_program", "leadership"])),

        ("EF5-010", "factual_event", "F-15E fighter jet shot down over southwestern Iran April 3 — first US combat aircraft loss. One crew rescued, one missing. IRGC claims helicopter involved in rescue engaged by air defenses. Iran offering reward for capture of American aircrew.", 0.95,
         "Section 1: F-15E shootdown", json.dumps(["F-15E", "IRGC", "CSAR"]), json.dumps(["shootdown", "first_aircraft_loss", "CSAR", "escalation"])),

        ("EF5-011", "factual_event", "Iran Foreign Ministry reported 600+ schools and education centers hit since February 28 (as of April 3).", 0.75,
         "Section 1: Civilian damage", json.dumps(["Iran Foreign Ministry"]), json.dumps(["schools", "civilian_infrastructure", "cumulative"])),

        ("EF5-012", "statistical", "Cumulative Iran casualties as of April 3: Government figures 2,076 killed / 26,500 wounded. HRANA (independent NGO) documented 3,114 deaths by March 17 (1,354 civilian, 1,138 military, 622 unclassified). Iran International: 4,700+ security forces killed.", 0.80,
         "Section 1: Casualty figures", json.dumps(["HRANA", "Iran International"]), json.dumps(["casualties", "statistical", "disputed_figures"])),

        # SECTION 2: Iranian Retaliatory Strikes
        ("EF5-013", "factual_event", "Iranian missile volume reduced 90%+ from war's opening days. Approximately 300 total missiles fired at Israel since February 28, nearly half with cluster submunitions.", 0.85,
         "Section 2: Iran strike tempo", json.dumps(["Iran", "Israel"]), json.dumps(["missile", "cluster_munitions", "degraded_capability"])),

        ("EF5-014", "factual_event", "April 1: Residential building struck in Bnei Brak. Water infrastructure damaged. 14 injured near Tel Aviv including 11-year-old. Cumulative Israeli deaths: 19.", 0.90,
         "Section 2: Israel casualties", json.dumps(["Bnei Brak", "Tel Aviv", "Israel"]), json.dumps(["civilian_casualties", "water_infrastructure"])),

        ("EF5-015", "factual_event", "April 1: Iranian drone attack on Kuwait International Airport fuel depots caused massive fire. April 3: Kuwait desalination plant struck; Mina Al-Ahmadi refinery (Kuwait's largest) hit again with fires in multiple units.", 0.90,
         "Section 2: Kuwait strikes", json.dumps(["Kuwait International Airport", "Mina Al-Ahmadi"]), json.dumps(["GCC_targeting", "desalination", "refinery", "Kuwait"])),

        ("EF5-016", "factual_event", "April 2-3: UAE defense ministry engaged missile and drone attacks from Iran. Habshan gas facility in Abu Dhabi caught fire from intercepted strike debris, operations suspended. 12 foreign nationals injured.", 0.85,
         "Section 2: UAE strikes", json.dumps(["UAE", "Habshan", "Abu Dhabi", "Dubai"]), json.dumps(["GCC_targeting", "gas_facility", "UAE"])),

        ("EF5-017", "factual_event", "March 28: Prince Sultan Air Base attacked (second time that week). 29 US soldiers injured, 5 seriously. E-3 Sentry early warning aircraft reportedly damaged.", 0.85,
         "Section 2: Saudi base attack", json.dumps(["Prince Sultan Air Base", "E-3 Sentry"]), json.dumps(["US_military", "Saudi_Arabia", "AWACS"])),

        ("EF5-018", "factual_event", "QatarEnergy declared force majeure on all exports. Damage to world's biggest LNG plant components — repairs could take up to 5 years.", 0.90,
         "Section 2: Qatar LNG", json.dumps(["QatarEnergy", "LNG"]), json.dumps(["energy", "force_majeure", "LNG", "Qatar"])),

        ("EF5-019", "factual_event", "US casualty toll: 13 killed, 300+ injured (Pentagon figures as of late March). US Embassy in Riyadh struck by two drones. CIA headquarters in Riyadh reportedly hit.", 0.85,
         "Section 2: US military casualties", json.dumps(["Pentagon", "CIA", "Riyadh"]), json.dumps(["US_casualties", "embassy", "CIA"])),

        ("EF5-020", "factual_event", "UK Akrotiri base on Cyprus struck by drone, attributed to Hezbollah. Two ballistic missiles reportedly launched at Diego Garcia (denied by Iran).", 0.70,
         "Section 2: Expanded targeting", json.dumps(["Akrotiri", "Cyprus", "Hezbollah", "Diego Garcia"]), json.dumps(["UK_military", "expanded_targeting"])),

        # SECTION 3: Hezbollah / Lebanon Front
        ("EF5-021", "factual_event", "2026 Lebanon War running concurrently. March 27-28: 118 Hezbollah attack waves against Israel. Hezbollah claimed 40 military operations March 30 (rockets, mortars, UAVs).", 0.85,
         "Section 3: Lebanon front", json.dumps(["Hezbollah", "IDF", "Lebanon"]), json.dumps(["Lebanon_war", "multi_front"])),

        ("EF5-022", "factual_event", "Israel reportedly considering plan to destroy civilian infrastructure in Lebanese towns 2-3km from border to create buffer zone. Senior Hezbollah commander killed in Beirut strike (7 killed total).", 0.80,
         "Section 3: Israel Lebanon operations", json.dumps(["IDF", "Beirut", "Hezbollah"]), json.dumps(["buffer_zone", "leadership_targeting", "Lebanon"])),

        ("EF5-023", "factual_event", "Three Lebanese journalists killed in Israeli airstrike in Jezzine March 28. Two UNIFIL soldiers killed, two wounded near Bani Hayan. Cumulative: 1,000+ militants and civilians killed in Lebanon by late March.", 0.85,
         "Section 3: Lebanon casualties", json.dumps(["UNIFIL", "Jezzine"]), json.dumps(["journalist_deaths", "UNIFIL", "Lebanon_casualties"])),

        # SECTION 4: Houthi Involvement
        ("EF5-024", "factual_event", "Houthis formally entered 2026 war March 28 with ballistic missile attack toward Israel (Beersheba, intercepted). Second missile fired at Eilat. Leadership stated attacks continue until aggression on all fronts stops.", 0.90,
         "Section 4: Houthi entry", json.dumps(["Houthis", "Beersheba", "Eilat"]), json.dumps(["Houthi", "war_entry", "escalation"])),

        # SECTION 5: Strait of Hormuz
        ("EF5-025", "factual_event", "Strait of Hormuz traffic down from 150 vessels/day pre-war to 10-20 ships/day. 142 total transits March 1-25 versus 2,652 same period 2025.", 0.90,
         "Section 5: Hormuz traffic", json.dumps(["Strait of Hormuz", "Lloyd's List"]), json.dumps(["shipping", "blockade", "traffic_data"])),

        ("EF5-026", "factual_event", "IRGC toll system confirmed operational: $2M/vessel in Chinese yuan or cryptocurrency. Ships rerouted to Iranian-controlled corridor between Qeshm and Larak islands. 26 vessels confirmed transiting via IRGC toll route since March 13.", 0.90,
         "Section 5: IRGC toll system", json.dumps(["IRGC", "Qeshm", "Larak", "Lloyd's List"]), json.dumps(["toll_system", "yuan", "crypto", "Hormuz"])),

        ("EF5-027", "factual_event", "Bilateral Hormuz access agreements: China (most favorable), India (free passage), Pakistan (20-ship deal), Malaysia, Thailand. Pakistan offering to reflag third-party vessels.", 0.85,
         "Section 5: Bilateral access", json.dumps(["China", "India", "Pakistan", "Malaysia", "Thailand"]), json.dumps(["bilateral_access", "reflagging", "Hormuz"])),

        ("EF5-028", "factual_event", "UK hosted 40-nation virtual meeting April 2-3 on reopening Strait. US and Israel absent. 35 countries signed declaration. GCC Secretary-General called for UN-authorized use of force. Macron called military reopening 'unrealistic'.", 0.90,
         "Section 5: Diplomatic efforts", json.dumps(["UK", "GCC", "Macron", "UNSC"]), json.dumps(["diplomacy", "multilateral", "Hormuz"])),

        ("EF5-029", "factual_event", "April 3: First Western-flagged vessel (French CMA CGM Kribi) crossed the Strait of Hormuz. ~20,000 sailors and thousands of ships stranded.", 0.85,
         "Section 5: First Western transit", json.dumps(["CMA CGM Kribi", "France"]), json.dumps(["shipping", "Western_transit", "Hormuz"])),

        # SECTION 6: Ukraine Involvement
        ("EF5-030", "factual_event", "228 Ukrainian counter-drone specialists deployed across Jordan, Kuwait, Qatar, Saudi Arabia, and UAE. Defense cooperation: Saudi MOU, Qatar 10-year agreement, UAE agreement in principle. Ukraine proposed Magura sea drones for Hormuz defense.", 0.90,
         "Section 6: Ukraine deployment", json.dumps(["Ukraine", "Magura"]), json.dumps(["counter_drone", "Ukraine", "Gulf_deployment"])),

        # SECTION 7: Diplomatic Landscape
        ("EF5-031", "factual_event", "Pakistan emerged as mediator between US and Iran. Foreign ministers of Pakistan, Saudi Arabia, Turkey, Egypt met in Islamabad March 29. Iran rejected US 15-point peace plan. Iran demands Lebanon ceasefire as precondition.", 0.85,
         "Section 7: Mediation", json.dumps(["Pakistan", "Saudi Arabia", "Turkey", "Egypt"]), json.dumps(["mediation", "peace_plan", "preconditions"])),

        ("EF5-032", "factual_event", "Mojtaba Khamenei elected supreme leader March 8. IRGC warned 18 US tech firms (Apple, Google, Meta, Microsoft, Nvidia, Oracle, IBM, Palantir, others) would be targeted starting April 2 8pm Tehran time. Employees advised to evacuate.", 0.90,
         "Section 7: IRGC tech threat", json.dumps(["Mojtaba Khamenei", "IRGC", "Apple", "Google", "Meta", "Microsoft", "Nvidia"]), json.dumps(["tech_targeting", "IRGC_threat", "supreme_leader"])),

        ("EF5-033", "assessment", "NYT reported Iranian leadership 'paralyzed' with disrupted decision-making. Communications infrastructure damage causing paranoia and internal power struggles. IRGC-Pezeshkian rift deepening over war costs.", 0.75,
         "Section 7: Iranian internal dynamics", json.dumps(["NYT", "Pezeshkian", "IRGC"]), json.dumps(["internal_dynamics", "paralysis", "rift"])),

        ("EF5-034", "factual_event", "Saudi Arabia, UAE, Kuwait, and Bahrain reportedly pressuring Trump to continue war, arguing historic opportunity for regime change. Netanyahu proposed pipeline through Arabian Peninsula to Israeli ports to bypass Hormuz.", 0.75,
         "Section 7: GCC war advocacy", json.dumps(["Saudi Arabia", "UAE", "Kuwait", "Bahrain", "Netanyahu"]), json.dumps(["regime_change", "GCC_pressure", "pipeline"])),

        # SECTION 8: Economic Indicators
        ("EF5-035", "statistical", "Oil prices April 3: Brent $109.03/bbl (+7.8%), WTI $111.54/bbl (+11.4%). US gasoline ~$4.02/gal (+$1.04 pre-war). Diesel ~$5.45/gal (+45% pre-war). Oil supply loss ~10M bbl/day — largest in history.", 0.90,
         "Section 8: Oil/energy prices", json.dumps(["Brent", "WTI"]), json.dumps(["oil_price", "gasoline", "diesel", "supply_loss"])),

        ("EF5-036", "statistical", "IEA emergency release: 400M barrels coordinated 30+ nations. US SPR release: 172M barrels ongoing. TD Securities: ~1B barrels lost by end of April. Additional 450M barrel loss/month if war continues.", 0.85,
         "Section 8: Strategic reserves", json.dumps(["IEA", "SPR", "TD Securities"]), json.dumps(["SPR", "emergency_release", "supply_forecast"])),

        ("EF5-037", "statistical", "Bloomberg Economics: US CPI March estimated 3.4% YoY (up from 2.4% Feb). Goldman Sachs: US recession probability 30%. JPMorgan: US West Coast could face supply disruption by May. GasBuddy: gas could hit $5/gal record.", 0.80,
         "Section 8: Economic forecasts", json.dumps(["Bloomberg", "Goldman Sachs", "JPMorgan", "GasBuddy"]), json.dumps(["CPI", "recession", "supply_disruption", "forecast"])),

        ("EF5-038", "assessment", "Analysts warn mid-April is critical deadline — after SPR and rerouted flows exhausted, upward price pressure intensifies dramatically. WEF: structural shock to world economy, not just regional crisis.", 0.80,
         "Section 8: Critical timeline", json.dumps(["WEF", "CSIS"]), json.dumps(["critical_deadline", "structural_shock", "mid_April"])),

        # SECTION 9: Decision Nodes
        ("EF5-039", "assessment", "Six critical decision nodes next 7 days: (1) April 7 Strait deadline — Trump escalate to power/desalination strikes? (2) F-15 crew CSAR — escalate to ground op? (3) IRGC tech firm attacks materialize? (4) IRGC bridge retaliation? (5) UNSC vote April 4? (6) Trump ground troops — WSJ reported Trump 'open to' ground operation.", 0.85,
         "Section 9: Decision nodes", json.dumps(["Trump", "IRGC", "UNSC", "WSJ"]), json.dumps(["decision_nodes", "escalation_risk", "forecast"])),

        ("EF5-040", "factual_event", "Trump national address April 2: claimed 'core strategic objectives nearing completion,' threatened to bomb Iran 'back to the Stone Ages,' signaled escalation over next 2-3 weeks. Posted April 3: US 'hasn't even started destroying what's left.'", 0.95,
         "Section 1: Trump statements", json.dumps(["Trump"]), json.dumps(["presidential_rhetoric", "escalation", "national_address"])),
    ]

    for c in claims:
        conn.execute("""
            INSERT OR REPLACE INTO evidence_claims
            (claim_id, source_id, claim_type, text, confidence, context, entities, tags, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (c[0], source_id, c[1], c[2], c[3], c[4], c[5], c[6], datetime.now().isoformat()))

    return len(claims)

def ingest_cross_references(conn):
    """Cross-references linking Epic Fury claims to each other and existing DB entities."""
    xrefs = [
        # Internal structural cross-references
        ("xref_ef5_001", "F-15E Shootdown", "US Escalation Calculus",
         "escalation_trigger", "EF5-010,EF5-039", 0.90),

        ("xref_ef5_002", "Strait of Hormuz Blockade", "Oil Price Spike",
         "causal", "EF5-025,EF5-026,EF5-035", 0.95),

        ("xref_ef5_003", "IRGC Toll System", "China Yuan Settlement",
         "financial_architecture", "EF5-026,EF5-027", 0.90),

        ("xref_ef5_004", "Iran Missile Degradation (90%)", "GCC Infrastructure Targeting Shift",
         "strategic_adaptation", "EF5-013,EF5-015,EF5-016", 0.85),

        ("xref_ef5_005", "Houthi War Entry", "Multi-Front Escalation",
         "alliance_activation", "EF5-024,EF5-021", 0.90),

        ("xref_ef5_006", "Ukraine Counter-Drone Deployment", "GCC Defense Cooperation",
         "military_partnership", "EF5-030,EF5-017", 0.85),

        ("xref_ef5_007", "QatarEnergy Force Majeure", "Global LNG Supply Shock",
         "economic_impact", "EF5-018,EF5-038", 0.90),

        ("xref_ef5_008", "Trump April 7 Deadline", "Power Plant/Desalination Threat",
         "escalation_pathway", "EF5-004,EF5-006,EF5-039", 0.90),

        ("xref_ef5_009", "Iranian Leadership Paralysis", "IRGC-Pezeshkian Rift",
         "internal_dynamics", "EF5-033,EF5-032", 0.75),

        ("xref_ef5_010", "GCC Regime Change Advocacy", "War Continuation Pressure",
         "political_influence", "EF5-034,EF5-040", 0.80),

        ("xref_ef5_011", "Civilian Infrastructure Targeting (Bridges/Medical/Steel)", "Humanitarian Crisis",
         "escalation_pattern", "EF5-007,EF5-008,EF5-005,EF5-011", 0.90),

        ("xref_ef5_012", "SPR Depletion Timeline", "Mid-April Critical Deadline",
         "resource_constraint", "EF5-036,EF5-038", 0.85),

        ("xref_ef5_013", "IRGC Tech Firm Threat", "Mojtaba Khamenei Leadership",
         "command_authority", "EF5-032,EF5-033", 0.80),

        ("xref_ef5_014", "Pakistan Mediation", "Iran Peace Plan Rejection",
         "diplomatic_failure", "EF5-031,EF5-006", 0.85),

        # Cross-references to existing Sherlock DB entities
        ("xref_ef5_015", "Iranian Nuclear Program (Leverage Analysis)", "SPND Chief Assassination",
         "targeting_overlap", "EF5-001", 0.80),

        ("xref_ef5_016", "Iranian Sanctions Evasion Networks", "IRGC Yuan/Crypto Toll System",
         "sanctions_circumvention", "EF5-026,EF5-027", 0.85),
    ]

    for x in xrefs:
        conn.execute("""
            INSERT OR REPLACE INTO cross_references
            (xref_id, entity1, entity2, relationship_type, source_claims, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (x[0], x[1], x[2], x[3], x[4], x[5], datetime.now().isoformat()))

    return len(xrefs)

def main():
    conn = connect()

    print("=== Operation Epic Fury Week 5 — Ingestion ===\n")

    # 1. Register source
    source_id = register_source(conn)
    print(f"✓ Source registered: {source_id}")

    # 2. Register targets
    register_targets(conn)
    conn.commit()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM targets")
    print(f"✓ Targets registered (5 new): {c.fetchone()[0]} total")

    # 3. Ingest claims
    n_claims = ingest_claims(conn, source_id)
    conn.commit()
    c.execute("SELECT COUNT(*) FROM evidence_claims")
    print(f"✓ Claims ingested: {n_claims} new | {c.fetchone()[0]} total")

    # 4. Ingest cross-references
    n_xrefs = ingest_cross_references(conn)
    conn.commit()
    c.execute("SELECT COUNT(*) FROM cross_references")
    print(f"✓ Cross-references ingested: {n_xrefs} new | {c.fetchone()[0]} total")

    # Summary
    print(f"\n=== Ingestion Complete ===")
    print(f"Source: {source_id}")
    print(f"Claims: EF5-001 to EF5-{n_claims:03d}")
    print(f"XRefs: xref_ef5_001 to xref_ef5_{n_xrefs:03d}")
    print(f"Targets: IDs 141-145")

    conn.close()

if __name__ == "__main__":
    main()
