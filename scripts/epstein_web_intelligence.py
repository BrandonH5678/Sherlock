#!/usr/bin/env python3
"""
Epstein Web Intelligence Collector
====================================
Multi-step web intelligence collection pipeline:
  Step 1: Collect and index court filing metadata from public Epstein case dockets
  Step 2: Cross-reference against existing Sherlock evidence files
  Step 3: Build a searchable index of all collected intelligence

Uses Retriever v2 agents (WebScraperAgent, IndexAgent, FSAgent) where available,
with RobustWebFetcher as the HTTP backbone.

Part of PKG-EP (Epstein Investigation) campaign for Sherlock.
"""

import sys
import os
import json
import logging
import argparse
import re
import glob as globmod
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, quote_plus
from pathlib import Path

# Add Retriever to sys.path
RETRIEVER_BASE = os.path.join(
    os.path.expanduser("~"),
    "Johny5Alive", "j5a-nightshift", "ops", "fetchers", "retriever"
)
if RETRIEVER_BASE not in sys.path:
    sys.path.insert(0, RETRIEVER_BASE)

from retriever.rwf import RobustWebFetcher
from retriever.index_agent import IndexAgent
from retriever.fs_agent import FSAgent

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("epstein_web_intelligence")

SHERLOCK_ROOT = os.path.join(os.path.expanduser("~"), "Sherlock")
EVIDENCE_DIR = os.path.join(SHERLOCK_ROOT, "evidence")
OUTPUT_PATH = os.path.join(EVIDENCE_DIR, "epstein_web_intelligence_index.json")

# Court docket and public filing sources
COURT_SOURCES = [
    {
        "name": "SDNY Epstein Criminal Case",
        "case_id": "1:19-cr-00490",
        "description": "U.S. v. Jeffrey Epstein - Southern District of New York criminal case",
        "urls": [
            "https://www.justice.gov/usao-sdny/united-states-v-jeffrey-epstein",
            "https://www.justice.gov/epstein",
        ],
        "link_patterns": [
            r'href="([^"]*\.pdf)"',
            r'href="(/usao-sdny/[^"]*epstein[^"]*)"',
            r'href="(/epstein/[^"]*)"',
        ],
    },
    {
        "name": "Giuffre v. Maxwell Civil Case",
        "case_id": "1:15-cv-07433",
        "description": "Virginia Giuffre v. Ghislaine Maxwell - SDNY civil case (unsealed documents)",
        "urls": [
            "https://www.courtlistener.com/docket/4355835/giuffre-v-maxwell/",
        ],
        "link_patterns": [
            r'href="(/docket/4355835/[^"]*)"',
            r'href="(https://storage\.courtlistener\.com/[^"]*)"',
            r'href="(/recap/[^"]*)"',
        ],
    },
    {
        "name": "US Virgin Islands v. JPMorgan",
        "case_id": "USVI-JPM",
        "description": "Government of the USVI v. JPMorgan Chase - Epstein banking relationship",
        "urls": [
            "https://www.courtlistener.com/docket/66665083/government-of-the-united-states-virgin-islands-v-jpmorgan-chase-bank-na/",
        ],
        "link_patterns": [
            r'href="(/docket/66665083/[^"]*)"',
            r'href="(https://storage\.courtlistener\.com/[^"]*)"',
        ],
    },
    {
        "name": "Epstein Doe Unsealing",
        "case_id": "DOE-UNSEAL",
        "description": "Doe v. Epstein - Documents unsealed in January 2024",
        "urls": [
            "https://www.courtlistener.com/docket/6111516/doe-v-epstein/",
        ],
        "link_patterns": [
            r'href="(/docket/6111516/[^"]*)"',
            r'href="(https://storage\.courtlistener\.com/[^"]*)"',
        ],
    },
]

# Key entities to track across all sources
ENTITY_KEYWORDS = [
    "Epstein", "Maxwell", "Wexner", "Brunel", "Dubin", "Black",
    "JPMorgan", "Deutsche Bank", "Bear Stearns", "Cantor Fitzgerald",
    "Lutnick", "Clinton", "Gates", "Dershowitz", "Staley",
    "Mossad", "CIA", "FBI", "intelligence", "blackmail",
    "PROMIS", "BCCI", "Mega Group",
]


# ---------------------------------------------------------------------------
# Step 1: Court Filing Metadata Collection
# ---------------------------------------------------------------------------

def collect_court_filings(
    fetcher: RobustWebFetcher,
    dry_run: bool = False,
) -> List[Dict[str, Any]]:
    """
    Step 1: Collect court filing metadata from public docket sources.
    """
    logger.info("=== STEP 1: Court Filing Metadata Collection ===")
    all_filings = []

    for source in COURT_SOURCES:
        name = source["name"]
        logger.info(f"Processing: {name} ({source['case_id']})")

        if dry_run:
            filings = _generate_dry_run_filings(source)
            all_filings.extend(filings)
            logger.info(f"  [DRY RUN] Generated {len(filings)} placeholder filings")
            continue

        for url in source["urls"]:
            try:
                logger.info(f"  Fetching: {url}")
                resp = fetcher.get(url)

                if resp.status_code >= 400:
                    logger.warning(f"  HTTP {resp.status_code} from {url}")
                    continue

                # Extract filing links
                filings_from_page = _extract_filing_metadata(
                    resp.text, resp.url, source
                )
                all_filings.extend(filings_from_page)
                logger.info(f"  Found {len(filings_from_page)} filings from {url}")

            except Exception as exc:
                logger.error(f"  Error fetching {url}: {exc}")

    logger.info(f"Step 1 complete: {len(all_filings)} total filings collected")
    return all_filings


def _extract_filing_metadata(
    html: str, base_url: str, source: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Extract filing metadata from an HTML page."""
    filings = []
    seen_urls = set()

    # Extract links matching patterns
    for pattern in source["link_patterns"]:
        for match in re.finditer(pattern, html, re.IGNORECASE):
            raw_url = match.group(1)
            full_url = urljoin(base_url, raw_url)
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            filings.append({
                "url": full_url,
                "case_id": source["case_id"],
                "case_name": source["name"],
                "title": "",
                "discovered_at": datetime.now(timezone.utc).isoformat(),
                "entity_mentions": [],
            })

    # Try to enrich with link text and detect entity mentions
    link_text_map = {}
    for link_match in re.finditer(
        r'<a\s+[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
        html,
        re.IGNORECASE | re.DOTALL,
    ):
        href = link_match.group(1)
        text = re.sub(r"<[^>]+>", "", link_match.group(2)).strip()
        full_url = urljoin(base_url, href)
        link_text_map[full_url] = text

    for filing in filings:
        text = link_text_map.get(filing["url"], "")
        filing["title"] = text

        # Scan for entity mentions in the title
        if text:
            for keyword in ENTITY_KEYWORDS:
                if keyword.lower() in text.lower():
                    filing["entity_mentions"].append(keyword)

    return filings


def _generate_dry_run_filings(source: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate placeholder filings for dry-run mode."""
    samples = [
        f"{source['name']} - Motion to Unseal Documents",
        f"{source['name']} - Exhibit A: Financial Records",
        f"{source['name']} - Deposition Transcript Excerpt",
        f"{source['name']} - Government Response Brief",
    ]
    filings = []
    for i, title in enumerate(samples, start=1):
        filings.append({
            "url": f"https://example.com/filing/{source['case_id']}/doc_{i}.pdf",
            "case_id": source["case_id"],
            "case_name": source["name"],
            "title": f"[DRY RUN] {title}",
            "discovered_at": datetime.now(timezone.utc).isoformat(),
            "entity_mentions": ["Epstein"],
        })
    return filings


# ---------------------------------------------------------------------------
# Step 2: Cross-Reference Against Existing Evidence
# ---------------------------------------------------------------------------

def cross_reference_evidence(
    filings: List[Dict[str, Any]],
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Step 2: Cross-reference collected filings against existing Sherlock
    evidence files in the evidence/ directory.
    """
    logger.info("=== STEP 2: Cross-Reference Against Existing Evidence ===")

    cross_ref = {
        "existing_evidence_files": [],
        "entity_overlap": {},
        "new_entities_from_filings": [],
        "coverage_gaps": [],
    }

    # Scan existing evidence files
    evidence_files = _scan_evidence_directory()
    cross_ref["existing_evidence_files"] = [
        {"filename": ef["filename"], "entities": ef["entities"]}
        for ef in evidence_files
    ]
    logger.info(f"  Found {len(evidence_files)} existing evidence files")

    # Build entity sets from existing evidence
    existing_entities = set()
    for ef in evidence_files:
        existing_entities.update(ef["entities"])

    # Build entity set from new filings
    filing_entities = set()
    for f in filings:
        filing_entities.update(f.get("entity_mentions", []))

    # Compute overlap
    overlap = existing_entities & filing_entities
    new_entities = filing_entities - existing_entities
    uncovered = existing_entities - filing_entities

    cross_ref["entity_overlap"] = {
        "shared_entities": sorted(overlap),
        "shared_count": len(overlap),
    }
    cross_ref["new_entities_from_filings"] = sorted(new_entities)

    # Identify coverage gaps: entities in existing evidence not found in filings
    cross_ref["coverage_gaps"] = sorted(uncovered)

    logger.info(f"  Entity overlap: {len(overlap)} shared entities")
    logger.info(f"  New from filings: {len(new_entities)} entities")
    logger.info(f"  Coverage gaps: {len(uncovered)} entities in evidence but not filings")

    return cross_ref


def _scan_evidence_directory() -> List[Dict[str, Any]]:
    """
    Scan the Sherlock evidence/ directory for existing files.
    Extract entity names from filenames and (where possible) file content.
    """
    evidence_files = []
    evidence_path = Path(EVIDENCE_DIR)

    if not evidence_path.exists():
        logger.warning(f"Evidence directory not found: {EVIDENCE_DIR}")
        return evidence_files

    # Scan JSON claim files
    for filepath in sorted(evidence_path.glob("*_claims.json")):
        entities = _extract_entities_from_filename(filepath.name)
        file_entities = _extract_entities_from_json(filepath)
        entities.extend(file_entities)

        evidence_files.append({
            "filename": filepath.name,
            "path": str(filepath),
            "type": "claims_json",
            "entities": list(set(entities)),
        })

    # Scan markdown evidence files
    for filepath in sorted(evidence_path.glob("*.md")):
        entities = _extract_entities_from_filename(filepath.name)

        evidence_files.append({
            "filename": filepath.name,
            "path": str(filepath),
            "type": "markdown",
            "entities": list(set(entities)),
        })

    return evidence_files


def _extract_entities_from_filename(filename: str) -> List[str]:
    """Extract entity names from a filename by matching against ENTITY_KEYWORDS."""
    entities = []
    name_lower = filename.lower()
    for keyword in ENTITY_KEYWORDS:
        if keyword.lower() in name_lower:
            entities.append(keyword)
    return entities


def _extract_entities_from_json(filepath: Path) -> List[str]:
    """Try to extract entity mentions from a JSON evidence file."""
    entities = []
    try:
        with open(filepath, "r") as f:
            data = json.load(f)

        # Handle list of claims
        claims = data if isinstance(data, list) else data.get("claims", [])
        text_blob = json.dumps(claims).lower()

        for keyword in ENTITY_KEYWORDS:
            if keyword.lower() in text_blob:
                entities.append(keyword)

    except Exception:
        pass  # Non-critical; skip files that cannot be parsed

    return entities


# ---------------------------------------------------------------------------
# Step 3: Build Searchable Index
# ---------------------------------------------------------------------------

def build_searchable_index(
    filings: List[Dict[str, Any]],
    cross_ref: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Step 3: Build a searchable index using the Retriever IndexAgent.
    Indexes all filings and cross-reference data for fast keyword lookup.
    """
    logger.info("=== STEP 3: Build Searchable Index ===")

    index_agent = IndexAgent(
        index_path=os.path.join(EVIDENCE_DIR, ".epstein_search_index.json"),
        min_term_length=2,
        max_results=200,
    )

    # Index each filing as a document
    for i, filing in enumerate(filings):
        doc_id = f"filing_{i:04d}"
        doc_text = " ".join([
            filing.get("title", ""),
            filing.get("case_name", ""),
            filing.get("case_id", ""),
            " ".join(filing.get("entity_mentions", [])),
        ])

        index_agent.documents[doc_id] = {
            "id": doc_id,
            "text": doc_text,
            "url": filing.get("url", ""),
            "case_id": filing.get("case_id", ""),
            "case_name": filing.get("case_name", ""),
            "title": filing.get("title", ""),
        }

        # Simple term indexing
        terms = set(re.findall(r'\b\w{2,}\b', doc_text.lower()))
        for term in terms:
            if isinstance(index_agent.term_index[term], list):
                index_agent.term_index[term] = set(index_agent.term_index[term])
            index_agent.term_index[term].add(doc_id)
            index_agent.term_freq[term][doc_id] += 1
        index_agent.doc_lengths[doc_id] = len(terms)

    # Index existing evidence files from cross-reference
    for j, ef in enumerate(cross_ref.get("existing_evidence_files", [])):
        doc_id = f"evidence_{j:04d}"
        doc_text = " ".join([ef["filename"]] + ef.get("entities", []))

        index_agent.documents[doc_id] = {
            "id": doc_id,
            "text": doc_text,
            "filename": ef["filename"],
            "type": "existing_evidence",
        }

        terms = set(re.findall(r'\b\w{2,}\b', doc_text.lower()))
        for term in terms:
            if isinstance(index_agent.term_index[term], list):
                index_agent.term_index[term] = set(index_agent.term_index[term])
            index_agent.term_index[term].add(doc_id)
            index_agent.term_freq[term][doc_id] += 1
        index_agent.doc_lengths[doc_id] = len(terms)

    # Save the index
    try:
        _save_index(index_agent)
        logger.info(f"  Index saved with {len(index_agent.documents)} documents")
    except Exception as exc:
        logger.warning(f"  Index save failed: {exc}")

    # Generate index summary
    summary = {
        "total_indexed_documents": len(index_agent.documents),
        "total_unique_terms": len(index_agent.term_index),
        "filing_documents": sum(1 for d in index_agent.documents if d.startswith("filing_")),
        "evidence_documents": sum(1 for d in index_agent.documents if d.startswith("evidence_")),
        "sample_searches": {},
    }

    # Run sample searches against key entities
    for keyword in ["Epstein", "Maxwell", "JPMorgan", "intelligence", "BCCI"]:
        kw_lower = keyword.lower()
        matching_docs = index_agent.term_index.get(kw_lower, set())
        summary["sample_searches"][keyword] = {
            "hits": len(matching_docs),
            "doc_ids": sorted(matching_docs)[:10],  # First 10
        }

    logger.info(f"  Sample search results:")
    for kw, res in summary["sample_searches"].items():
        logger.info(f"    '{kw}': {res['hits']} hits")

    return summary


def _save_index(index_agent: IndexAgent):
    """Persist the index to disk."""
    if index_agent.index_path:
        data = {
            "documents": index_agent.documents,
            "term_index": {k: list(v) for k, v in index_agent.term_index.items()},
            "doc_lengths": index_agent.doc_lengths,
        }
        with open(index_agent.index_path, "w") as f:
            json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_pipeline(dry_run: bool = False) -> Dict[str, Any]:
    """
    Run the full 3-step web intelligence pipeline.
    Returns the complete intelligence index.
    """
    fetcher = RobustWebFetcher(timeout=30, max_retries=3)

    # Step 1: Collect court filings
    filings = collect_court_filings(fetcher, dry_run=dry_run)

    # Step 2: Cross-reference with existing evidence
    cross_ref = cross_reference_evidence(filings, dry_run=dry_run)

    # Step 3: Build searchable index
    index_summary = build_searchable_index(filings, cross_ref)

    # Assemble final output
    intelligence_index = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "epstein_web_intelligence.py",
            "campaign": "PKG-EP",
            "dry_run": dry_run,
            "pipeline_steps": [
                "court_filing_collection",
                "evidence_cross_reference",
                "searchable_index_build",
            ],
        },
        "court_filings": filings,
        "cross_reference": cross_ref,
        "index_summary": index_summary,
        "statistics": {
            "total_filings": len(filings),
            "cases_covered": list({f["case_id"] for f in filings}),
            "entities_tracked": ENTITY_KEYWORDS,
            "existing_evidence_files": len(cross_ref.get("existing_evidence_files", [])),
            "entity_overlap_count": cross_ref.get("entity_overlap", {}).get("shared_count", 0),
            "new_entities_discovered": len(cross_ref.get("new_entities_from_filings", [])),
            "indexed_documents": index_summary.get("total_indexed_documents", 0),
        },
    }

    return intelligence_index


def main():
    parser = argparse.ArgumentParser(
        description="Multi-step Epstein web intelligence collection and indexing pipeline"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making network calls; generate placeholder data",
    )
    parser.add_argument(
        "--output",
        default=OUTPUT_PATH,
        help=f"Output path for intelligence index JSON (default: {OUTPUT_PATH})",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug-level logging",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("Epstein Web Intelligence Collector - starting")
    logger.info(f"  Dry run: {args.dry_run}")
    logger.info(f"  Output:  {args.output}")

    intelligence_index = run_pipeline(dry_run=args.dry_run)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    with open(args.output, "w") as f:
        json.dump(intelligence_index, f, indent=2, default=str)

    logger.info(f"Intelligence index written to {args.output}")
    stats = intelligence_index["statistics"]
    logger.info(f"Summary:")
    logger.info(f"  Total filings:           {stats['total_filings']}")
    logger.info(f"  Cases covered:           {len(stats['cases_covered'])}")
    logger.info(f"  Existing evidence files: {stats['existing_evidence_files']}")
    logger.info(f"  Entity overlap:          {stats['entity_overlap_count']}")
    logger.info(f"  New entities:            {stats['new_entities_discovered']}")
    logger.info(f"  Indexed documents:       {stats['indexed_documents']}")


if __name__ == "__main__":
    main()
