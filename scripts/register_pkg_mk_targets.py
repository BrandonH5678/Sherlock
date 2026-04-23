#!/usr/bin/env python3
"""Register 17 PKG-MK campaign targets in sherlock.db.

Targets span MK behavioral control programs, key figures, organizations,
and social movement intersection points.
"""
import sqlite3
import json
from datetime import datetime, timezone

DB_PATH = "/home/johnny5/Sherlock/sherlock.db"

TARGETS = [
    # Tier 1 — CRITICAL
    {
        "name": "Charles Dederich",
        "target_type": "person",
        "priority": 1,
        "metadata": {
            "campaign": "PKG-MK",
            "role": "Synanon founder, MKULTRA-LSD recipient Aug 28 1957",
            "born": 1913, "died": 1997,
            "key_event": "Received LSD from Dr. Keith Dittman and Dr. Sidney Cohen (MKULTRA-connected) on Aug 28, 1957 — catalyst for Synanon ego-destruction philosophy",
        },
    },
    {
        "name": "Synanon",
        "target_type": "organization",
        "priority": 1,
        "metadata": {
            "campaign": "PKG-MK",
            "role": "Attack therapy cult with documented MKULTRA-researcher origins",
            "founded": 1958, "dissolved": 1991,
            "key_methods": ["the Game (attack therapy)", "ego destruction", "forced head shaving", "sleep deprivation", "family separation", "confession rituals"],
            "assets_peak": "$30M+ by mid-1970s",
        },
    },
    {
        "name": "Dr. Louis Jolyon West",
        "target_type": "person",
        "priority": 1,
        "metadata": {
            "campaign": "PKG-MK",
            "role": "MKULTRA contractor appearing at Ruby, Manson, Hearst, McVeigh, Synanon FOIA link",
            "born": 1924, "died": 1999,
            "key_cases": ["Jack Ruby (JFK)", "Charles Manson (counterculture)", "Patty Hearst (SLA)", "Timothy McVeigh (OKC)", "Synanon-Oswald FOIA link"],
            "extends": "MKULTRA_INTELLIGENCE_REPORT.md, MKULTRA_JFK_CROSS_REFERENCE.md",
        },
    },
    {
        "name": "Cesar Chavez / United Farm Workers",
        "target_type": "person",
        "priority": 1,
        "metadata": {
            "campaign": "PKG-MK",
            "role": "Primary investigation axis — intelligence and secret society activities from MK program angle",
            "born": 1927, "died": 1993,
            "investigation_axes": [
                "MK behavioral techniques infiltrating UFW (Synanon Game at La Paz?)",
                "1970s purges: organic vs COINTELPRO-induced vs MK-method-influenced",
                "Catholic organizational connections (Opus Dei, Knights of Columbus)",
                "Intelligence connections around Chavez (handlers, advisors)",
            ],
        },
    },
    {
        "name": "COINTELPRO",
        "target_type": "program",
        "priority": 1,
        "metadata": {
            "campaign": "PKG-MK",
            "role": "FBI counterintelligence program — relationship to MK programs is core research question",
            "active": "1956-1971 (official), continued informally",
            "key_question": "Separate bureaucratic program or operationally coordinated with CIA MK programs?",
        },
    },
    # Tier 2 — HIGH
    {
        "name": "Dr. Sidney Cohen",
        "target_type": "person",
        "priority": 2,
        "metadata": {
            "campaign": "PKG-MK",
            "role": "UCLA psychiatrist, MKULTRA-connected, administered LSD to both Dederich AND Bill Wilson (AA)",
            "born": 1910, "died": 1987,
            "key_event": "Nexus figure connecting CIA behavioral research to two major addiction treatment movements",
        },
    },
    {
        "name": "Esalen Institute",
        "target_type": "organization",
        "priority": 2,
        "metadata": {
            "campaign": "PKG-MK",
            "role": "Center of Human Potential Movement, CIA/DOD connections documented",
            "founded": 1962,
            "location": "Big Sur, California",
            "key_connections": ["Soviet exchange program (CIA interest)", "SRI remote viewing overlap", "Military officer seminars"],
        },
    },
    {
        "name": "Peoples Temple / Jim Jones",
        "target_type": "organization",
        "priority": 2,
        "metadata": {
            "campaign": "PKG-MK",
            "role": "Cross-pollination with Synanon documented; Jonestown as behavioral control endpoint",
            "key_connections": [
                "Synanon drink mix donation used at Jonestown",
                "Shared personnel between organizations",
                "NBC journalist Pat Lynch investigated both, was killed",
                "Jones in Brazil 1961-63 alongside CIA-connected Dan Mitrione",
            ],
        },
    },
    {
        "name": "Straight Inc.",
        "target_type": "organization",
        "priority": 2,
        "metadata": {
            "campaign": "PKG-MK",
            "role": "Direct Synanon → federal drug policy pipeline",
            "founded": 1976, "closed": 1993,
            "key_connections": ["Drug Czar Robert DuPont endorsement", "CIA subcontractor Ruth Fox", "Nancy Reagan endorsement"],
            "successor": "Drug-Free America Foundation",
            "founder": "Mel Sembler (later Ambassador to Australia and Italy)",
        },
    },
    {
        "name": "Sidney Gottlieb",
        "target_type": "person",
        "priority": 2,
        "metadata": {
            "campaign": "PKG-MK",
            "role": "MK-Ultra program director, CIA Technical Services Division",
            "born": 1918, "died": 1999,
            "extends": "MKULTRA_INTELLIGENCE_REPORT.md (existing content, zero DB claims)",
        },
    },
    {
        "name": "Werner Erhard / est",
        "target_type": "person",
        "priority": 2,
        "metadata": {
            "campaign": "PKG-MK",
            "role": "Human Potential Movement commercial arm, Synanon-adjacent",
            "born": 1935,
            "key_connections": ["Former Scientologist", "Visited Synanon", "est = mass-market behavioral technology (1M+ people)"],
        },
    },
    # Tier 3 — MEDIUM
    {
        "name": "Human Potential Movement",
        "target_type": "concept",
        "priority": 3,
        "metadata": {
            "campaign": "PKG-MK",
            "role": "Umbrella concept linking Esalen, est, Gestalt, Synanon — aggregation target",
            "period": "1960s-present",
            "key_question": "Was HPM a vector for deploying behavioral control techniques into civilian culture?",
        },
    },
    {
        "name": "Robert DuPont",
        "target_type": "person",
        "priority": 3,
        "metadata": {
            "campaign": "PKG-MK",
            "role": "Nixon Drug Czar who endorsed Straight Inc., pipeline from MK methods to federal policy",
            "key_connection": "Federal grant ~$2M to start The Seed (Synanon-derived program)",
            "revolving_door": "Later became private drug testing industry consultant",
        },
    },
    {
        "name": "Dr. Keith Dittman",
        "target_type": "person",
        "priority": 3,
        "metadata": {
            "campaign": "PKG-MK",
            "role": "MKULTRA researcher who co-administered LSD to Dederich alongside Cohen, Aug 28 1957",
        },
    },
    {
        "name": "Abraham Maslow",
        "target_type": "person",
        "priority": 3,
        "metadata": {
            "campaign": "PKG-MK",
            "role": "'Unsilenced' testimony places him at Synanon designing brainwashing program",
            "born": 1908, "died": 1970,
            "evidence_tier": "E2/E3 — single source ('Unsilenced' testimony from Mark), specific and testable but unconfirmed",
        },
    },
    {
        "name": "MK-SEARCH",
        "target_type": "program",
        "priority": 3,
        "metadata": {
            "campaign": "PKG-MK",
            "role": "MK-Ultra successor program 1964-1972, behavioral modification focus",
            "active": "1964-1972",
            "parent_program": "MK-Ultra (target ID 13)",
        },
    },
    {
        "name": "Operation CHAOS",
        "target_type": "program",
        "priority": 3,
        "metadata": {
            "campaign": "PKG-MK",
            "role": "CIA domestic surveillance 1967-1974, overlap with both MK and COINTELPRO",
            "active": "1967-1974",
            "key_question": "Operational bridge between CIA MK programs and FBI COINTELPRO?",
        },
    },
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
            print(f"SKIP target '{t['name']}': already exists")
            skipped += 1
            continue

        c.execute("""
            INSERT INTO targets (name, target_type, priority, status, created_at, updated_at, metadata)
            VALUES (?, ?, ?, 'new', ?, ?, ?)
        """, (
            t["name"],
            t["target_type"],
            t["priority"],
            now, now,
            json.dumps(t["metadata"], indent=2),
        ))
        tid = c.lastrowid
        added += 1
        print(f"Added target {tid}: {t['name']} ({t['target_type']}, P{t['priority']})")

    conn.commit()

    c.execute("SELECT COUNT(*) FROM targets")
    total = c.fetchone()[0]
    conn.close()

    print(f"\n{'='*60}")
    print(f"PKG-MK TARGET REGISTRATION COMPLETE")
    print(f"{'='*60}")
    print(f"  Added:   {added}")
    print(f"  Skipped: {skipped}")
    print(f"  Total targets in DB: {total}")
    print(f"{'='*60}")


if __name__ == "__main__":
    register()
