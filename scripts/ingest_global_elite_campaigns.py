#!/usr/bin/env python3
"""Ingest all 5 Global Elite Ecosystem campaign reports into sherlock.db.

Parses structured intelligence reports from evidence/ directory,
extracts claims and cross-references, and inserts into the database.

Campaigns: PKG-RESTRUCTURE, PKG-RUS, PKG-CHN, PKG-IRN, PKG-XFIN
"""
import sqlite3
import re
import os
import json
from datetime import datetime

DB_PATH = "/home/johnny5/Sherlock/sherlock.db"
EVIDENCE_DIR = "/home/johnny5/Sherlock/evidence"

# Campaign definitions: (prefix, file_prefix, campaign_name, source_id_prefix)
CAMPAIGNS = [
    ("RST", "rst_phase", "PKG-RESTRUCTURE", "RST_GLOBAL_ELITE"),
    ("RUS", "rus_phase", "PKG-RUS", "RUS_GLOBAL_ELITE"),
    ("CHN", "chn_phase", "PKG-CHN", "CHN_GLOBAL_ELITE"),
    ("IRN", "irn_phase", "PKG-IRN", "IRN_GLOBAL_ELITE"),
    ("XFN", "xfn_phase", "PKG-XFIN", "XFN_GLOBAL_ELITE"),
]


def parse_claims_from_report(filepath, claim_prefix):
    """Extract claims from a markdown report's Claims Register table."""
    with open(filepath, 'r') as f:
        content = f.read()

    claims = []
    # Match claim rows in markdown tables
    # Format: | RST-001 | description | E1 | 0.80 | source |
    # Handle various formats: E1, E1/E2, E1-E2, E1-E4, and confidence ranges like 0.80-0.85
    pattern = rf'\|\s*({claim_prefix}-\d+)\s*\|\s*(.*?)\s*\|\s*(E[1-4](?:[/-]E?[1-4])?)\s*\|\s*([\d.]+(?:\s*-\s*[\d.]+)?)\s*\|\s*(.*?)\s*\|'

    for match in re.finditer(pattern, content):
        claim_id = match.group(1).strip()
        description = match.group(2).strip()
        evidence_tier = match.group(3).strip()
        conf_str = match.group(4).strip()
        # For confidence ranges like "0.80-0.85", take the average
        if '-' in conf_str:
            parts = conf_str.split('-')
            confidence = (float(parts[0].strip()) + float(parts[1].strip())) / 2
        else:
            confidence = float(conf_str)
        source = match.group(5).strip()

        claims.append({
            'claim_id': claim_id,
            'text': description,
            'evidence_tier': evidence_tier,
            'confidence': confidence,
            'source_ref': source,
        })

    return claims


def parse_xrefs_from_report(filepath):
    """Extract cross-references from a markdown report."""
    with open(filepath, 'r') as f:
        content = f.read()

    xrefs = []
    # Match xref rows: | xref_rst_001 | entity1 | entity2 | relationship | 0.XX |
    pattern = r'\|\s*(xref_\w+_\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*([\d.]+)\s*\|'

    for match in re.finditer(pattern, content):
        xref_id = match.group(1).strip()
        entity1 = match.group(2).strip()
        entity2 = match.group(3).strip()
        relationship = match.group(4).strip()
        confidence = float(match.group(5).strip())

        xrefs.append({
            'xref_id': xref_id,
            'entity1': entity1,
            'entity2': entity2,
            'relationship_type': relationship,
            'confidence': confidence,
        })

    return xrefs


def get_phase_from_filename(filename):
    """Extract phase number from filename like rst_phase1_xxx.md"""
    match = re.search(r'phase(\d+)', filename)
    return int(match.group(1)) if match else 0


def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    now = datetime.utcnow().isoformat()

    total_sources = 0
    total_claims = 0
    total_xrefs = 0
    total_dupes = 0

    for claim_prefix, file_prefix, campaign_name, source_id_base in CAMPAIGNS:
        # Find all report files for this campaign
        files = sorted([
            f for f in os.listdir(EVIDENCE_DIR)
            if f.startswith(file_prefix) and f.endswith('.md')
        ])

        if not files:
            print(f"⚠️  No files found for {campaign_name}")
            continue

        print(f"\n{'='*60}")
        print(f"Campaign: {campaign_name} ({len(files)} files)")
        print(f"{'='*60}")

        campaign_claims = 0
        campaign_xrefs = 0

        for filename in files:
            filepath = os.path.join(EVIDENCE_DIR, filename)
            phase = get_phase_from_filename(filename)

            # Register source
            source_id = f"{source_id_base}_P{phase:02d}"

            # Extract title from first line
            with open(filepath, 'r') as f:
                first_line = f.readline().strip().lstrip('# ')

            try:
                cursor.execute("""
                    INSERT INTO evidence_sources
                    (source_id, title, file_path, evidence_type, created_at, ingested_at, processing_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    source_id,
                    first_line,
                    f"evidence/{filename}",
                    "intelligence_report",
                    now,
                    now,
                    "completed"
                ))
                total_sources += 1
            except sqlite3.IntegrityError:
                print(f"  Source {source_id} already exists, skipping")

            # Parse and insert claims
            claims = parse_claims_from_report(filepath, claim_prefix)
            file_claims = 0
            file_dupes = 0

            for claim in claims:
                tags = json.dumps([
                    claim['evidence_tier'],
                    campaign_name,
                    f"phase_{phase}",
                    "global_elite_ecosystem"
                ])

                try:
                    cursor.execute("""
                        INSERT INTO evidence_claims
                        (claim_id, source_id, claim_type, text, confidence, tags, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        claim['claim_id'],
                        source_id,
                        "factual",
                        claim['text'],
                        claim['confidence'],
                        tags,
                        now,
                    ))
                    file_claims += 1
                except sqlite3.IntegrityError:
                    file_dupes += 1

            # Parse and insert cross-references
            xrefs = parse_xrefs_from_report(filepath)
            file_xrefs = 0

            for xref in xrefs:
                source_claims_json = json.dumps({source_id: 1})
                try:
                    cursor.execute("""
                        INSERT INTO cross_references
                        (xref_id, entity1, entity2, relationship_type, source_claims, confidence, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        xref['xref_id'],
                        xref['entity1'],
                        xref['entity2'],
                        xref['relationship_type'],
                        source_claims_json,
                        xref['confidence'],
                        now,
                    ))
                    file_xrefs += 1
                except sqlite3.IntegrityError:
                    pass  # Skip duplicate xrefs

            campaign_claims += file_claims
            campaign_xrefs += file_xrefs
            total_dupes += file_dupes

            status = "✅" if file_claims > 0 else "⚠️"
            print(f"  {status} Phase {phase}: {file_claims} claims, {file_xrefs} xrefs{f', {file_dupes} dupes' if file_dupes else ''} — {filename}")

        total_claims += campaign_claims
        total_xrefs += campaign_xrefs
        print(f"  Campaign total: {campaign_claims} claims, {campaign_xrefs} xrefs")

    conn.commit()

    # Final DB stats
    cursor.execute("SELECT COUNT(*) FROM evidence_claims")
    db_claims = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM cross_references")
    db_xrefs = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM evidence_sources")
    db_sources = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM targets")
    db_targets = cursor.fetchone()[0]

    conn.close()

    print(f"\n{'='*60}")
    print(f"INGESTION COMPLETE")
    print(f"{'='*60}")
    print(f"New sources:  {total_sources}")
    print(f"New claims:   {total_claims}")
    print(f"New xrefs:    {total_xrefs}")
    print(f"Duplicates:   {total_dupes}")
    print(f"\nDB TOTALS:")
    print(f"  Claims:  {db_claims}")
    print(f"  XRefs:   {db_xrefs}")
    print(f"  Sources: {db_sources}")
    print(f"  Targets: {db_targets}")


if __name__ == "__main__":
    main()
