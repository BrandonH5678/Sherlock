#!/usr/bin/env python3
"""
Ingest Buhler/Exodus Propulsion intelligence into Sherlock DB.
Source: American Alchemy episode — Dr. Charles Buhler interview (2026-03-30)
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = "sherlock.db"

def ingest():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.now().isoformat()

    # 1. Register evidence source
    source_id = "EP_EXODUS_001"
    cur.execute("""
        INSERT INTO evidence_sources (source_id, title, url, file_path, evidence_type, duration, created_at, ingested_at, metadata, processing_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        source_id,
        "American Alchemy: Dr. Charles Buhler — NASA Electrostatics Lead / Exodus Propulsion CEO",
        "https://youtu.be/mOWwdIuyaQA",
        "freelance_transcripts/american_alchemy/buhler_exodus_mOWwdIuyaQA/audio_transcription/alignment_audio_enhanced/diarization_audio_aligned/audio_diarized_enhanced_READABLE.txt",
        "podcast_transcript",
        9208.0,
        "2026-03-30",
        now,
        json.dumps({
            "channel": "Jesse Michels (American Alchemy)",
            "guest": "Dr. Charles Buhler",
            "secondary_guest": "David Chester",
            "confidence": 0.883,
            "word_count": 27331,
            "segments": 4850,
            "pipeline": "FT Premium",
            "reliability": 0.80
        }),
        "complete"
    ))
    print(f"Source registered: {source_id}")

    # 2. Register targets
    targets = [
        ("Dr. Charles Buhler", "person", 2, "active", {"role": "Lead Scientist NASA Electrostatics Lab, CEO Exodus Propulsion Technologies, incoming President ESA", "credentials": "PhD theoretical condensed matter physics, Florida State University"}),
        ("Exodus Propulsion Technologies", "organization", 2, "active", {"type": "propulsion R&D company", "website": "exoduspropulsion.space", "experiments": "~2000 variations", "patent": "USPTO granted after 2-year national security hold"}),
        ("Thomas Townsend Brown", "person", 3, "historical", {"era": "1920s-1960s", "field": "electrogravitics", "connections": "Curtis LeMay, Edward Teller, Navy, Martin Corp"}),
    ]

    for name, ttype, priority, status, meta in targets:
        cur.execute("SELECT target_id FROM targets WHERE name = ?", (name,))
        existing = cur.fetchone()
        if existing:
            print(f"  Target exists: {name} (ID: {existing[0]})")
        else:
            cur.execute("""
                INSERT INTO targets (name, target_type, priority, status, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, ttype, priority, status, now, now, json.dumps(meta)))
            print(f"  Target added: {name} (ID: {cur.lastrowid})")

    # 3. Ingest claims
    claims = [
        ("EXP-001", "Dr. Charles Buhler", "experimental", "Propellantless thrust measured in ~2,000 experiment variations at Exodus Propulsion Technologies. Force in 5-10 millinewton range. High vacuum chamber testing eliminates ion wind.", 0.80, 32.0, 39.0, "propellantless_thrust,vacuum_testing,electrostatics", "2000 experiment variations, millinewton range, high vacuum"),
        ("EXP-002", "Dr. Charles Buhler", "experimental", "Thrust persists after power-off (~200 micronewtons residual). Device would continue accelerating in zero-gravity without power. Violates classical energy conservation — suggests quantum vacuum effect.", 0.75, 47.0, 53.0, "residual_thrust,quantum_vacuum,energy_conservation", "Power-off persistence, 200 micronewtons"),
        ("EXP-003", "Dr. Charles Buhler", "experimental", "Weight reduction demonstrated on scale. Flipping device reverses effect. Videos on exoduspropulsion.space. Second patent under USPTO peer review.", 0.75, 4181.0, 4207.0, "weight_reduction,patent,replication", "Scale demonstration, directional"),
        ("EXP-004", "Dr. Charles Buhler", "testimonial", "First force observation in 2010 at NASA lab using laser displacement. Witnessed by Dr. Sid Clements (senior electrostatics expert/mentor) who became fully engaged after initial skepticism.", 0.85, 1930.0, 2034.0, "first_observation,witness,nasa_lab", "2010, laser displacement, Dr. Sid Clements witness"),
        ("EXP-005", "Dr. Charles Buhler", "factual", "NASA Electrodynamic Dust Shield successfully tested on lunar surface. Nine EDS payloads. Thermal radiator, glass, and camera variants all successful. 25 years of development.", 0.95, 1080.0, 1126.0, "nasa,lunar_surface,dust_shield,operational", "Flight-qualified hardware, establishes credibility"),
        ("EXP-006", "Dr. Charles Buhler", "factual", "USPTO patent granted after 2-year national security hold. Second patent undergoing examiner review with affidavit witnesses confirming independent reproduction.", 0.70, 4209.0, 4232.0, "patent,national_security,reproduction", "2-year hold implies government sensitivity assessment"),
        ("EXP-007", "Jacques Cornillon / Jesse Michels", "historical", "Townsend Brown 1956 Paris vacuum experiment confirmed by Jacques Cornillon deathbed confession (2009). Force exceeded atmospheric results at 10^-6 torr. 120-page report available.", 0.65, 340.0, 403.0, "townsend_brown,vacuum,historical,deathbed_confession", "1956 Paris, 2009 confession, 120-page report"),
        ("EXP-008", "Dr. Charles Buhler", "anecdotal", "Aerospace insiders from Lockheed, Northrop give wink-wink confirmation: 'you're on the right path.' Cannot officially confirm due to classification.", 0.30, 5361.0, 5390.0, "classified,aerospace,lockheed,northrop,compartmentalization", "E3 — anecdotal, unnamed sources"),
        ("EXP-009", "Dr. Charles Buhler", "analytical", "Spacecraft momentum anomalies through Van Allen belts (speed up/slow down from charge pickup) possibly attributable to same electrostatic force. NASA adds extra fuel to compensate.", 0.40, 5503.0, 5533.0, "spacecraft_anomaly,van_allen,momentum", "Testable hypothesis linking lab to known engineering problem"),
        ("EXP-010", "Dr. Charles Buhler / David Chester", "theoretical", "QED theoretical framework under development for thrust mechanism. Starting from two charges, exploring quantum electrodynamics tools. David Chester (MIT/UCLA) stress-testing theory.", 0.50, 6819.0, 6898.0, "qed,theoretical,david_chester", "Theory in progress, not published"),
        ("EXP-011", "Jesse Michels / peer-reviewed", "factual", "Beatrice Villarroel (Stockholm) found 68% increase in pre-Sputnik Palomar plate transients following nuclear detonations (11% baseline vs 19% post-test). Peer-reviewed.", 0.85, 3951.0, 4031.0, "nuclear_uap,palomar,villarroel,peer_reviewed,transients", "Independent confirmation of nuclear-transient correlation"),
        ("EXP-012", "Dr. Charles Buhler", "testimonial", "Childhood UFO sighting: six bright white lights in formation, no sound, SE New York mid-1980s (Hudson Valley wave). Cars following lights for several days. Local newspaper coverage.", 0.70, 4240.0, 4334.0, "ufo_sighting,hudson_valley,childhood,motivation", "Contextualizes career motivation"),
        ("EXP-013", "Dr. Charles Buhler", "experimental", "Ion wind elimination: (1) high vacuum, (2) enclosure testing. Lifter-in-box shows scale unchanged — ion wind is Newton's 3rd law. Anomalous force moves WITH 'wind' direction (opposite to ion wind).", 0.80, 2641.0, 2942.0, "methodology,ion_wind,vacuum,control_experiment", "Key methodological distinction"),
        ("EXP-014", "Dr. Charles Buhler", "theoretical", "Two force components: surface force (electrostatic pressure) and volume force (E-field divergence). Classical description approximate; full explanation requires QED.", 0.70, 5533.0, 5557.0, "force_components,electrostatic_pressure,qed", "Mathematically structured framework"),
        ("EXP-015", "Dr. Charles Buhler", "self-assessment", "Explicitly rejects anti-gravity and warp drive labels. Does not believe 2,000V experiments bend spacetime. Co-founder Drew uses 'warp drive' but Buhler disagrees. Acknowledges interferometry could test.", 0.95, 5764.0, 5839.0, "intellectual_honesty,anti_gravity_rejected,credibility", "Increases credibility vs typical fringe claims"),
        ("EXP-016", "Dr. Charles Buhler", "assessment", "Peer review acceptance estimated 20-30 years due to century of stigmatization. Plans live demo at ESA conference Cocoa Beach FL June 2026. Pursuing USPTO patent as parallel validation.", 0.85, 3868.0, 3907.0, "peer_review,stigmatization,esa_conference,demo", "Documents institutional resistance"),
    ]

    for cid, speaker, ctype, text, conf, start, end, tags, context in claims:
        cur.execute("""
            INSERT INTO evidence_claims (claim_id, source_id, speaker_id, claim_type, text, confidence, start_time, end_time, tags, context, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (cid, source_id, speaker, ctype, text, conf, start, end, tags, context, now))

    print(f"Claims ingested: {len(claims)}")

    # 4. Cross-references
    xrefs = [
        ("xref_exp_001", "Villarroel nuclear transients (EXP-011)", "Thread 3 POSS-I nuclear-UAP study", "validates", "EXP-011", 0.85),
        ("xref_exp_002", "Exodus residual thrust (EXP-002)", "Casimir effect / quantum vacuum", "parallels", "EXP-002", 0.50),
        ("xref_exp_003", "Townsend Brown military connections (EXP-007)", "classified aerospace programs", "structural_link", "EXP-007", 0.45),
        ("xref_exp_004", "Aerospace wink-wink (EXP-008)", "PKG-MK compartmentalization patterns", "parallels", "EXP-008", 0.35),
        ("xref_exp_005", "Hudson Valley sighting (EXP-012)", "1982-1986 documented mass sighting wave", "contextualizes", "EXP-012", 0.80),
        ("xref_exp_006", "USPTO national security hold (EXP-006)", "Salvatore Pais Navy patents", "parallels", "EXP-006", 0.55),
    ]

    for xid, e1, e2, rtype, src_claims, conf in xrefs:
        cur.execute("""
            INSERT INTO cross_references (xref_id, entity1, entity2, relationship_type, source_claims, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (xid, e1, e2, rtype, src_claims, conf, now))

    print(f"Cross-references ingested: {len(xrefs)}")

    conn.commit()

    # Verify
    cur.execute("SELECT COUNT(*) FROM evidence_claims")
    total_claims = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM cross_references")
    total_xrefs = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM evidence_sources")
    total_sources = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM targets")
    total_targets = cur.fetchone()[0]

    print(f"\n{'='*50}")
    print(f"DB TOTALS AFTER INGESTION:")
    print(f"  Claims: {total_claims}")
    print(f"  Cross-references: {total_xrefs}")
    print(f"  Sources: {total_sources}")
    print(f"  Targets: {total_targets}")
    print(f"{'='*50}")

    conn.close()

if __name__ == "__main__":
    ingest()
