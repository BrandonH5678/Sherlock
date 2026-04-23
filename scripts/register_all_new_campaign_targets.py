#!/usr/bin/env python3
"""Register all targets for 5 new campaigns: PKG-RESTRUCTURE, PKG-RUS, PKG-CHN, PKG-IRN, PKG-XFIN.

Starting from target ID 87 (auto-increment). Current DB: 86 targets.
"""
import sqlite3
import json
from datetime import datetime, timezone

DB_PATH = "/home/johnny5/Sherlock/sherlock.db"

TARGETS = [
    # =========================================================================
    # PKG-RESTRUCTURE: Managed Restructuring (12 targets)
    # =========================================================================
    {"name": "Wall Street-Bolshevik Connection", "target_type": "event_network", "priority": 1,
     "metadata": {"campaign": "PKG-RESTRUCTURE", "phase": 1,
                  "description": "Spence/Sutton thesis: did Western capital manage the Russian Revolution?"}},

    {"name": "WWI Cross-Faction Finance", "target_type": "event_network", "priority": 1,
     "metadata": {"campaign": "PKG-RESTRUCTURE", "phase": 2,
                  "description": "Who financed both sides of WWI? J.P. Morgan as Allied financier"}},

    {"name": "WWII Cross-Faction Connections", "target_type": "event_network", "priority": 2,
     "metadata": {"campaign": "PKG-RESTRUCTURE", "phase": 3,
                  "description": "BBH/Bush + Nazi finance, S&C relationships, Standard Oil/IG Farben"}},

    {"name": "Bretton Woods Design Process", "target_type": "event_network", "priority": 2,
     "metadata": {"campaign": "PKG-RESTRUCTURE", "phase": 4,
                  "description": "Who designed post-WWII architecture? Connections? Suppressed alternatives?"}},

    {"name": "Cold War Management Architecture", "target_type": "event_network", "priority": 2,
     "metadata": {"campaign": "PKG-RESTRUCTURE", "phase": 5,
                  "description": "Backchannel management 1947-1991, spheres of influence, mutual restraint"}},

    {"name": "Post-Soviet Restructuring", "target_type": "event_network", "priority": 2,
     "metadata": {"campaign": "PKG-RESTRUCTURE", "phase": 7,
                  "description": "Harvard Boys, shock therapy, Western capital → Russian assets"}},

    {"name": "Allen Dulles Portfolio (expanded)", "target_type": "person", "priority": 1,
     "metadata": {"campaign": "PKG-RESTRUCTURE", "phase": 5,
                  "description": "Expand PKG-MK finding: complete unified portfolio and post-1961 succession",
                  "extends": "Existing Allen Dulles target + PKG-MK findings"}},

    {"name": "George H.W. Bush Trajectory", "target_type": "person", "priority": 2,
     "metadata": {"campaign": "PKG-RESTRUCTURE", "phase": 5,
                  "description": "S&B → CIA → VP → President as successor coordinator hypothesis"}},

    {"name": "Henry Kissinger Network", "target_type": "person", "priority": 2,
     "metadata": {"campaign": "PKG-RESTRUCTURE", "phase": 6,
                  "description": "NSC → State → Kissinger Associates → decades of cross-faction consulting"}},

    {"name": "Epstein Dynasty (Deep Roots)", "target_type": "family_network", "priority": 2,
     "metadata": {"campaign": "PKG-RESTRUCTURE", "phase": 8,
                  "description": "JXQ thesis: Epstein family as long-standing dynastic power player"}},

    {"name": "Concert of Europe Succession", "target_type": "concept", "priority": 3,
     "metadata": {"campaign": "PKG-RESTRUCTURE", "phase": "context",
                  "description": "Did Concert's coordination mechanisms survive WWI? Through what channels?"}},

    {"name": "Current Restructuring Architecture", "target_type": "concept", "priority": 3,
     "metadata": {"campaign": "PKG-RESTRUCTURE", "phase": 9,
                  "description": "CBDC, AI governance, biological compliance, managed multipolarity"}},

    # =========================================================================
    # PKG-RUS: Russian Elite Ecosystem (10 targets)
    # =========================================================================
    {"name": "Putin Siloviki Network", "target_type": "network", "priority": 1,
     "metadata": {"campaign": "PKG-RUS", "phase": 1,
                  "description": "FSB/KGB alumni network as Russia's S&B equivalent"}},

    {"name": "Putin Offshore Wealth", "target_type": "financial", "priority": 1,
     "metadata": {"campaign": "PKG-RUS", "phase": 2,
                  "description": "Estimated $200B+ (Navalny investigations), Western structures holding it"}},

    {"name": "Ozero Cooperative", "target_type": "network", "priority": 2,
     "metadata": {"campaign": "PKG-RUS", "phase": 1,
                  "description": "Putin's original power base — dacha cooperative members → ruling elite"}},

    {"name": "Pre-Revolutionary Russian Aristocratic Remnants", "target_type": "dynasty", "priority": 2,
     "metadata": {"campaign": "PKG-RUS", "phase": 3,
                  "description": "Did old Russian elite families survive Soviet period? How?"}},

    {"name": "Russian Orthodox Church (Power Structure)", "target_type": "institution", "priority": 2,
     "metadata": {"campaign": "PKG-RUS", "phase": 4,
                  "description": "Financial assets, KGB penetration, Kremlin relationship"}},

    {"name": "Russian Organized Crime-State Nexus", "target_type": "network", "priority": 2,
     "metadata": {"campaign": "PKG-RUS", "phase": 5,
                  "description": "Vor v zakone, crime-intelligence integration, Western connections"}},

    {"name": "Russia-Israel Elite Network", "target_type": "network", "priority": 2,
     "metadata": {"campaign": "PKG-RUS", "phase": 6,
                  "description": "Emigration → Israeli elite, oligarchs in Israel, FSB-Mossad cooperation"}},

    {"name": "Russian Energy Oligarchs", "target_type": "network", "priority": 3,
     "metadata": {"campaign": "PKG-RUS", "phase": 7,
                  "description": "Gazprom, Rosneft, Lukoil — control, dynasty, Western finance"}},

    {"name": "Yeltsin-Era Western Brokers", "target_type": "network", "priority": 3,
     "metadata": {"campaign": "PKG-RUS", "phase": 7,
                  "description": "Who specifically brokered 1990s Western-Russian capital connections?"}},

    {"name": "Russian-Western Intelligence Liaison", "target_type": "network", "priority": 3,
     "metadata": {"campaign": "PKG-RUS", "phase": 8,
                  "description": "Documented cooperation/coordination between FSB/GRU and Western services"}},

    # =========================================================================
    # PKG-CHN: Chinese Elite Ecosystem (12 targets)
    # =========================================================================
    {"name": "Eight Immortals Families", "target_type": "dynasty", "priority": 1,
     "metadata": {"campaign": "PKG-CHN", "phase": 1,
                  "description": "Revolutionary founders → princeling dynasties (Xi, Bo, Deng descendants)"}},

    {"name": "CCP-Triad Historical Connection", "target_type": "network", "priority": 1,
     "metadata": {"campaign": "PKG-CHN", "phase": 2,
                  "description": "Green Gang, Du Yuesheng, CCP use of secret society structures"}},

    {"name": "United Front Work Department", "target_type": "institution", "priority": 1,
     "metadata": {"campaign": "PKG-CHN", "phase": 3,
                  "description": "Largest state-run influence/intelligence apparatus — global operations"}},

    {"name": "CCP Offshore Wealth", "target_type": "financial", "priority": 2,
     "metadata": {"campaign": "PKG-CHN", "phase": 4,
                  "description": "Panama Papers thread, offshore family wealth, shell companies"}},

    {"name": "Hong Kong Tycoon-CCP Pipeline", "target_type": "network", "priority": 2,
     "metadata": {"campaign": "PKG-CHN", "phase": 5,
                  "description": "Li Ka-shing, Macau casinos, HK as CCP-global finance interface"}},

    {"name": "Kissinger-China Connection", "target_type": "network", "priority": 2,
     "metadata": {"campaign": "PKG-CHN", "phase": 6,
                  "description": "How Kissinger 'opened China' — who benefited on both sides?",
                  "also_in": "PKG-RESTRUCTURE Phase 6"}},

    {"name": "Schwarzman/Blackstone-Tsinghua Pipeline", "target_type": "network", "priority": 2,
     "metadata": {"campaign": "PKG-CHN", "phase": 6,
                  "description": "Western finance → Chinese elite educational/institutional pipeline"}},

    {"name": "Prince/CITIC/FSG (expanded)", "target_type": "network", "priority": 2,
     "metadata": {"campaign": "PKG-CHN", "phase": 6,
                  "description": "Expand PKG-911 finding (CI risk 0.75) — CIA contractor + Chinese state capital",
                  "extends": "PKG-911 Erik Prince findings"}},

    {"name": "Yale-China Association", "target_type": "institution", "priority": 3,
     "metadata": {"campaign": "PKG-CHN", "phase": 6,
                  "description": "Historical S&B → China connection. Opium trade history."}},

    {"name": "Belt and Road as Capital Deployment", "target_type": "program", "priority": 3,
     "metadata": {"campaign": "PKG-CHN", "phase": "context",
                  "description": "Structural parallel to Western development finance as influence tool"}},

    {"name": "Chinese Surveillance State Architecture", "target_type": "program", "priority": 3,
     "metadata": {"campaign": "PKG-CHN", "phase": 7,
                  "description": "Social credit, AI monitoring — science as control mechanism"}},

    {"name": "Fentanyl Precursor Supply Chains", "target_type": "network", "priority": 3,
     "metadata": {"campaign": "PKG-CHN", "phase": "context",
                  "description": "Possible hybrid warfare or criminal-state enterprise"}},

    # =========================================================================
    # PKG-IRN: Iranian Elite Ecosystem (10 targets)
    # =========================================================================
    {"name": "IRGC Economic Empire", "target_type": "institution", "priority": 1,
     "metadata": {"campaign": "PKG-IRN", "phase": 1,
                  "description": "Controls 20-40% of Iranian economy — sectors, families, mechanisms"}},

    {"name": "Bonyad Foundations", "target_type": "institution", "priority": 1,
     "metadata": {"campaign": "PKG-IRN", "phase": 2,
                  "description": "Religious foundations controlling massive economic assets"}},

    {"name": "Iranian Clerical Dynasties", "target_type": "dynasty", "priority": 2,
     "metadata": {"campaign": "PKG-IRN", "phase": 3,
                  "description": "Rafsanjani, Larijani, Khamenei families — wealth, intermarriage, control"}},

    {"name": "Iran-Israel Covert Connections", "target_type": "network", "priority": 2,
     "metadata": {"campaign": "PKG-IRN", "phase": 4,
                  "description": "Iran-Contra, SAVAK-Mossad, post-1979 interactions, backchannels"}},

    {"name": "MOIS/Quds Force Network", "target_type": "institution", "priority": 2,
     "metadata": {"campaign": "PKG-IRN", "phase": 6,
                  "description": "External intelligence, proxy management, Western interactions"}},

    {"name": "Bazaari Merchant Class", "target_type": "network", "priority": 2,
     "metadata": {"campaign": "PKG-IRN", "phase": 5,
                  "description": "Traditional economic elite, IRGC/clerical relationship"}},

    {"name": "IRGC-Narcotics Nexus", "target_type": "network", "priority": 3,
     "metadata": {"campaign": "PKG-IRN", "phase": "context",
                  "description": "Drug trafficking revenue — Afghan/Turkish/European connections"}},

    {"name": "Iranian Nuclear Program (Leverage Analysis)", "target_type": "program", "priority": 3,
     "metadata": {"campaign": "PKG-IRN", "phase": "context",
                  "description": "Deterrent? Bargaining chip? Genuine weapon? Who controls it?"}},

    {"name": "Iranian Sanctions Evasion Networks", "target_type": "network", "priority": 3,
     "metadata": {"campaign": "PKG-IRN", "phase": 5,
                  "description": "Intermediaries, front companies, jurisdictions used",
                  "also_in": "PKG-XFIN Phase 4"}},

    {"name": "Shia Transnational Network", "target_type": "network", "priority": 3,
     "metadata": {"campaign": "PKG-IRN", "phase": 6,
                  "description": "Hezbollah, Iraqi militias, Houthis — coordination and financing"}},

    # =========================================================================
    # PKG-XFIN: Cross-Faction Financial Infrastructure (10 targets)
    # =========================================================================
    {"name": "Bank for International Settlements (BIS)", "target_type": "institution", "priority": 1,
     "metadata": {"campaign": "PKG-XFIN", "phase": 1,
                  "description": "Central bank of central banks — where adversarial bankers meet regularly"}},

    {"name": "Major Energy Trading Firms", "target_type": "network", "priority": 1,
     "metadata": {"campaign": "PKG-XFIN", "phase": 2,
                  "description": "Vitol, Glencore, Trafigura — serve ALL factions as intermediaries"}},

    {"name": "Offshore Financial Centers Network", "target_type": "network", "priority": 1,
     "metadata": {"campaign": "PKG-XFIN", "phase": 3,
                  "description": "City of London, Switzerland, Cayman, Dubai, Singapore — all factions park wealth"}},

    {"name": "Intermediary Jurisdictions (Sanctions)", "target_type": "network", "priority": 2,
     "metadata": {"campaign": "PKG-XFIN", "phase": 4,
                  "description": "UAE, Turkey, India, Singapore — sanctions evasion and cross-faction flows"}},

    {"name": "Arms Dealer Cross-Faction Networks", "target_type": "network", "priority": 2,
     "metadata": {"campaign": "PKG-XFIN", "phase": 5,
                  "description": "Who sells weapons to multiple sides? Financial channels?"}},

    {"name": "SWIFT and Alternatives", "target_type": "infrastructure", "priority": 2,
     "metadata": {"campaign": "PKG-XFIN", "phase": "context",
                  "description": "SWIFT as control; CIPS, SPFS as alternatives; interoperation?"}},

    {"name": "Cross-Faction Investment Bank Operations", "target_type": "network", "priority": 2,
     "metadata": {"campaign": "PKG-XFIN", "phase": 6,
                  "description": "Goldman, JPMorgan, HSBC operating in adversarial jurisdictions simultaneously"}},

    {"name": "Cryptocurrency as Cross-Faction Channel", "target_type": "infrastructure", "priority": 3,
     "metadata": {"campaign": "PKG-XFIN", "phase": "context",
                  "description": "Bitcoin/crypto as sanctions evasion and cross-faction transfer"}},

    {"name": "Cross-Faction Law Firms", "target_type": "network", "priority": 3,
     "metadata": {"campaign": "PKG-XFIN", "phase": "context",
                  "description": "Modern equivalents of Sullivan & Cromwell — firms across factional lines"}},

    {"name": "Insurance/Reinsurance Networks", "target_type": "network", "priority": 3,
     "metadata": {"campaign": "PKG-XFIN", "phase": "context",
                  "description": "Lloyd's, Swiss Re — serving all factions"}},
]


def register():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    added = 0
    skipped = 0

    for t in TARGETS:
        c.execute("SELECT target_id FROM targets WHERE name = ?", (t["name"],))
        if c.fetchone():
            print(f"SKIP: '{t['name']}'")
            skipped += 1
            continue

        c.execute("""
            INSERT INTO targets (name, target_type, priority, status, created_at, updated_at, metadata)
            VALUES (?, ?, ?, 'new', ?, ?, ?)
        """, (t["name"], t["target_type"], t["priority"], now, now, json.dumps(t["metadata"], indent=2)))
        tid = c.lastrowid
        campaign = t["metadata"]["campaign"]
        added += 1
        print(f"  {tid}: {t['name']} [{campaign}] P{t['priority']}")

    conn.commit()
    c.execute("SELECT COUNT(*) FROM targets")
    total = c.fetchone()[0]

    # Count by campaign
    for campaign in ["PKG-RESTRUCTURE", "PKG-RUS", "PKG-CHN", "PKG-IRN", "PKG-XFIN"]:
        c.execute("SELECT COUNT(*) FROM targets WHERE metadata LIKE ?", (f'%{campaign}%',))
        count = c.fetchone()[0]
        print(f"  {campaign}: {count} targets")

    conn.close()

    print(f"\n{'='*60}")
    print(f"ALL CAMPAIGN TARGETS REGISTERED")
    print(f"{'='*60}")
    print(f"  Added:   {added}")
    print(f"  Skipped: {skipped}")
    print(f"  Total targets in DB: {total}")
    print(f"{'='*60}")


if __name__ == "__main__":
    register()
