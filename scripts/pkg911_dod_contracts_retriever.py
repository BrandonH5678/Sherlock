#!/usr/bin/env python3
"""
PKG-911 DOD / Federal Contracts Retriever
==========================================
Collects DOD and federal contract records for Blackwater / Xe Services /
Academi and affiliated entities via USASpending.gov, USAID, and State
Department contract databases.

Key PKG-911 targets:
  - Blackwater USA / Xe Services / Academi — Erik Prince PMC network
  - Greystone Ltd — international (Barbados) Blackwater affiliate
  - Presidential Airways — Blackwater aviation subsidiary
  - Triple Canopy — competing PMC with Blackwater contract award history
  - State Department WPPS (Worldwide Personal Protective Services) contracts
  - USAID contracts for Blackwater and affiliated entities

The Blackwater network's federal contracting history documents:
  1. How a private intelligence/paramilitary capability was state-funded
  2. The Krongard family nexus (Buzzy Krongard CIA, Howard Krongard State IG)
  3. Contract scale of the "outsourced intelligence" model post-9/11

Part of PKG-911 campaign for Sherlock — Phase 7.
"""

import sys
import os
import json
import logging
import argparse
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, quote_plus, urlencode
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
logger = logging.getLogger("pkg911_dod_contracts")

PKG911_CAMPAIGN = "PKG-911"

SHERLOCK_ROOT = os.path.join(os.path.expanduser("~"), "Sherlock")
EVIDENCE_DIR = os.path.join(SHERLOCK_ROOT, "evidence")
OUTPUT_PATH = os.path.join(EVIDENCE_DIR, "pkg911_dod_contracts_index.json")

USASPENDING_API = "https://api.usaspending.gov/api/v2"

# ---------------------------------------------------------------------------
# USASpending.gov API searches
# These use the public REST API — no authentication required.
# ---------------------------------------------------------------------------

USASPENDING_SEARCHES = [
    {
        "source_name": "USASpending - Blackwater USA awards",
        "vendor": "Blackwater USA",
        "description": (
            "USASpending.gov award search for Blackwater USA — primary entity "
            "for Blackwater federal contracts including State Dept WPPS."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "USASpending - Xe Services awards",
        "vendor": "Xe Services",
        "description": (
            "USASpending.gov award search for Xe Services — Blackwater's renamed "
            "entity (renamed after Nisour Square massacre and congressional pressure)."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "USASpending - Academi awards",
        "vendor": "Academi",
        "description": (
            "USASpending.gov award search for Academi — Blackwater/Xe's final "
            "corporate name, acquired by CONSTELLIS Holdings."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "USASpending - Greystone Ltd awards",
        "vendor": "Greystone",
        "description": (
            "USASpending.gov award search for Greystone Ltd — Blackwater's "
            "international (Barbados-registered) affiliate for overseas operations."
        ),
        "expected_evidence_tier": "E2",
    },
    {
        "source_name": "USASpending - Presidential Airways",
        "vendor": "Presidential Airways",
        "description": (
            "USASpending.gov award search for Presidential Airways — Blackwater's "
            "aviation subsidiary that operated aircraft under DOD contracts."
        ),
        "expected_evidence_tier": "E2",
    },
]

# ---------------------------------------------------------------------------
# Direct URL sources (contract databases, news, official records)
# ---------------------------------------------------------------------------

DIRECT_SOURCES = [
    # USASpending.gov keyword search pages
    {
        "source_name": "USASpending.gov - Blackwater keyword search",
        "url": "https://www.usaspending.gov/search/?hash=4acc77c2d3c41e7e8bad461069e00de8",
        "description": (
            "USASpending.gov advanced search for Blackwater contract awards — "
            "provides total obligated amounts, agency breakdown, and contract types."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "State Department - WPPS contract overview",
        "url": "https://www.state.gov/worldwide-protective-services/",
        "description": (
            "State Department WPPS (Worldwide Personal Protective Services) program — "
            "the primary vehicle for Blackwater/Xe/Academi State Dept contracts. "
            "Covers Embassy and diplomatic protection in Iraq and Afghanistan."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "GAO - Blackwater WPPS contract oversight reports",
        "url": "https://www.gao.gov/products/GAO-08-966T",
        "description": (
            "GAO report GAO-08-966T on private security contractors in Iraq — "
            "covers Blackwater WPPS contract administration and oversight failures."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "GAO - Private Security Contractors Iraq Afghanistan",
        "url": "https://www.gao.gov/assets/gao-10-928.pdf",
        "description": (
            "GAO-10-928: 'Afghanistan and Iraq — DOD and State Department Have "
            "Taken Steps to Improve Oversight of Private Security Contractors.' "
            "Documents the full scale of Blackwater/PMC contracting."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "SIGIR - Blackwater Iraq contract reports",
        "url": "https://www.sigir.mil/reports/quarterlyreports/",
        "description": (
            "Special Inspector General for Iraq Reconstruction (SIGIR) quarterly "
            "reports — covers Blackwater contract performance and oversight gaps."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "CRS Report - Private Security Contractors",
        "url": "https://sgp.fas.org/crs/natsec/R40835.pdf",
        "description": (
            "Congressional Research Service report on Private Security Contractors "
            "in Iraq — comprehensive overview of Blackwater contract history, "
            "WPPS awards, and Congressional oversight context."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "USAID - Blackwater contract database search",
        "url": (
            "https://www.usaid.gov/results-and-data/data-resources/partner-contracts-and-grants"
        ),
        "description": (
            "USAID partner contracts and grants database — searching for Blackwater "
            "USAID contracts in Iraq and Afghanistan reconstruction programs."
        ),
        "expected_evidence_tier": "E2",
    },
    {
        "source_name": "Federal Procurement Data System - Blackwater search",
        "url": (
            "https://www.fpds.gov/ezsearch/search.do?q=Blackwater"
            "&MAIN_SEARCH_SELECTION=ALL&SEARCH_INDEX=MAIN&templateName=1.5.1"
            "&indexName=awardfull&x=0&y=0&sortBy=SIGNED_DATE&desc=Y"
        ),
        "description": (
            "FPDS (Federal Procurement Data System) search for Blackwater — "
            "the primary federal contract award database covering all agency awards."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "USASpending.gov API - recipient search Blackwater",
        "url": f"{USASPENDING_API}/recipient/",
        "description": (
            "USASpending.gov recipient endpoint — will be queried for Blackwater, "
            "Xe Services, and Academi UEI/DUNS records."
        ),
        "expected_evidence_tier": "E1",
        "method": "API",
    },
    {
        "source_name": "OpenSecrets - Blackwater lobbying and political contributions",
        "url": "https://www.opensecrets.org/orgs/blackwater-usa/summary?id=D000034178",
        "description": (
            "OpenSecrets profile for Blackwater USA — lobbying expenditures and "
            "political contribution history contextualizes the political protection "
            "that allowed Blackwater to escape accountability post-Nisour Square."
        ),
        "expected_evidence_tier": "E2",
    },
]

# Keywords for entity detection
ENTITY_KEYWORDS = [
    "Blackwater", "Xe Services", "Academi", "CONSTELLIS",
    "Greystone", "Presidential Airways",
    "Erik Prince", "Krongard",
    "WPPS", "protective services", "security contractor",
    "Iraq", "Afghanistan", "State Department",
    "DOD", "Department of Defense", "USAID",
    "private military", "PMC",
    "Nisour Square", "CIA",
    "contract award", "obligated", "FPDS",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_preview(content: str, max_chars: int = 500) -> str:
    """Strip HTML tags and return a clean text preview."""
    text = re.sub(r'<(script|style)[^>]*>.*?</(script|style)>', '', content, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:max_chars]


def _build_usaspending_payload(vendor_name: str) -> Dict[str, Any]:
    """
    Build a USASpending.gov spending_by_award POST payload for a vendor name search.
    """
    return {
        "filters": {
            "recipient_search_text": [vendor_name],
            "award_type_codes": ["A", "B", "C", "D"],  # Contracts only
        },
        "fields": [
            "Award ID", "Recipient Name", "Award Amount", "Awarding Agency",
            "Awarding Sub Agency", "Award Type", "Start Date", "End Date",
            "Description", "Place of Performance State Code",
        ],
        "page": 1,
        "limit": 25,
        "sort": "Award Amount",
        "order": "desc",
    }


def _parse_usaspending_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse USASpending API response into a structured summary."""
    results = data.get("results", [])
    page_metadata = data.get("page_metadata", {})
    summary = {
        "total_count": page_metadata.get("count", len(results)),
        "total_pages": page_metadata.get("total", 1),
        "awards": [],
    }
    for award in results[:10]:
        summary["awards"].append({
            "award_id": award.get("Award ID"),
            "recipient": award.get("Recipient Name"),
            "amount": award.get("Award Amount"),
            "agency": award.get("Awarding Agency"),
            "sub_agency": award.get("Awarding Sub Agency"),
            "type": award.get("Award Type"),
            "start_date": award.get("Start Date"),
            "end_date": award.get("End Date"),
            "description": award.get("Description"),
        })
    return summary


# ---------------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------------

def collect(dry_run: bool = False) -> List[Dict[str, Any]]:
    """
    Fetch DOD/federal contract sources and USASpending API results.
    Returns structured result records.
    """
    logger.info("=== PKG-911 DOD Contracts Retriever ===")
    logger.info(f"  Campaign: {PKG911_CAMPAIGN}")
    logger.info(f"  Dry run: {dry_run}")

    total_sources = len(USASPENDING_SEARCHES) + len(DIRECT_SOURCES)
    logger.info(f"  Total sources: {total_sources} ({len(USASPENDING_SEARCHES)} API + {len(DIRECT_SOURCES)} direct)")

    if dry_run:
        return _generate_dry_run_results()

    fetcher = RobustWebFetcher(timeout=30, max_retries=3)
    results = []

    # --- USASpending POST API calls ---
    for search in USASPENDING_SEARCHES:
        name = search["source_name"]
        vendor = search["vendor"]
        api_url = f"{USASPENDING_API}/search/spending_by_award/"
        logger.info(f"  API: {name} (vendor: {vendor})")

        record = {
            "source_name": name,
            "url": api_url,
            "vendor_query": vendor,
            "description": search.get("description", ""),
            "status": None,
            "http_status_code": None,
            "content_preview": None,
            "content_length": None,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "evidence_tier": search.get("expected_evidence_tier", "E3"),
            "campaign": PKG911_CAMPAIGN,
            "entity_mentions": [],
            "parsed_awards": {},
            "error": None,
        }

        try:
            payload = _build_usaspending_payload(vendor)
            resp = fetcher.post(api_url, json=payload)
            record["http_status_code"] = resp.status_code

            if resp.status_code >= 400:
                record["status"] = f"HTTP_ERROR_{resp.status_code}"
                logger.warning(f"    HTTP {resp.status_code}")
            else:
                record["status"] = "SUCCESS"
                content = resp.text
                record["content_length"] = len(content)

                try:
                    data = json.loads(content)
                    record["parsed_awards"] = _parse_usaspending_response(data)
                    award_count = record["parsed_awards"].get("total_count", 0)
                    record["content_preview"] = (
                        f"Found {award_count} contract awards for '{vendor}'"
                    )
                    logger.info(f"    OK — {award_count} awards for '{vendor}'")
                except json.JSONDecodeError:
                    record["content_preview"] = _make_preview(content)
                    logger.info(f"    OK — non-JSON response ({len(content)} chars)")

        except Exception as exc:
            record["status"] = "FETCH_ERROR"
            record["error"] = str(exc)
            logger.error(f"    Error: {exc}")

        results.append(record)

    # --- Direct URL fetches ---
    for source in DIRECT_SOURCES:
        name = source["source_name"]
        url = source["url"]
        logger.info(f"  Fetching: {name}")
        logger.info(f"    URL: {url}")

        record = {
            "source_name": name,
            "url": url,
            "description": source.get("description", ""),
            "status": None,
            "http_status_code": None,
            "content_preview": None,
            "content_length": None,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "evidence_tier": source.get("expected_evidence_tier", "E3"),
            "campaign": PKG911_CAMPAIGN,
            "entity_mentions": [],
            "parsed_awards": {},
            "error": None,
        }

        try:
            resp = fetcher.get(url)
            record["http_status_code"] = resp.status_code

            if resp.status_code >= 400:
                record["status"] = f"HTTP_ERROR_{resp.status_code}"
                logger.warning(f"    HTTP {resp.status_code} from {url}")
            else:
                record["status"] = "SUCCESS"
                content = resp.text
                record["content_length"] = len(content)

                ct = resp.headers.get("content-type", "")
                if "json" in ct:
                    try:
                        data = json.loads(content)
                        record["parsed_awards"] = data
                        record["content_preview"] = json.dumps(data)[:500]
                    except Exception:
                        record["content_preview"] = _make_preview(content)
                else:
                    record["content_preview"] = _make_preview(content)

                content_lower = content.lower()
                for kw in ENTITY_KEYWORDS:
                    if kw.lower() in content_lower:
                        record["entity_mentions"].append(kw)

                logger.info(
                    f"    OK — {record['content_length']} chars, "
                    f"{len(record['entity_mentions'])} keyword hits"
                )

        except Exception as exc:
            record["status"] = "FETCH_ERROR"
            record["error"] = str(exc)
            logger.error(f"    Error: {exc}")

        results.append(record)

    logger.info(f"Collection complete: {len(results)} sources processed")
    successes = sum(1 for r in results if r["status"] == "SUCCESS")
    logger.info(f"  Successes: {successes} / {len(results)}")

    return results


def _generate_dry_run_results() -> List[Dict[str, Any]]:
    """Return placeholder results for dry-run mode."""
    results = []
    for search in USASPENDING_SEARCHES:
        results.append({
            "source_name": search["source_name"],
            "url": f"{USASPENDING_API}/search/spending_by_award/",
            "vendor_query": search["vendor"],
            "description": search.get("description", ""),
            "status": "DRY_RUN",
            "http_status_code": None,
            "content_preview": f"[DRY RUN] Would POST to USASpending API for vendor: {search['vendor']}",
            "content_length": None,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "evidence_tier": search.get("expected_evidence_tier", "E3"),
            "campaign": PKG911_CAMPAIGN,
            "entity_mentions": [],
            "parsed_awards": {},
            "error": None,
        })
    for source in DIRECT_SOURCES:
        results.append({
            "source_name": source["source_name"],
            "url": source["url"],
            "description": source.get("description", ""),
            "status": "DRY_RUN",
            "http_status_code": None,
            "content_preview": f"[DRY RUN] Would fetch: {source['url']}",
            "content_length": None,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "evidence_tier": source.get("expected_evidence_tier", "E3"),
            "campaign": PKG911_CAMPAIGN,
            "entity_mentions": [],
            "parsed_awards": {},
            "error": None,
        })
    logger.info(f"  [DRY RUN] Generated {len(results)} placeholder results")
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=(
            "PKG-911 DOD Contracts Retriever — collect USASpending.gov and federal "
            "contract records for Blackwater/Xe/Academi and affiliated entities"
        )
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

    logger.info("PKG-911 DOD Contracts Retriever — starting")
    logger.info(f"  Output: {args.output}")

    results = collect(dry_run=args.dry_run)

    # Summarize award totals from USASpending
    total_awards_found = 0
    for r in results:
        parsed = r.get("parsed_awards", {})
        if isinstance(parsed, dict):
            total_awards_found += parsed.get("total_count", 0)

    output = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "pkg911_dod_contracts_retriever.py",
            "campaign": PKG911_CAMPAIGN,
            "dry_run": args.dry_run,
            "description": (
                "DOD and federal contract records for Blackwater/Xe/Academi, "
                "Greystone, Presidential Airways. Uses USASpending.gov API plus "
                "GAO, SIGIR, CRS, FPDS, State Dept, and USAID contract databases."
            ),
        },
        "results": results,
        "statistics": {
            "total_sources": len(results),
            "successful_fetches": sum(1 for r in results if r["status"] == "SUCCESS"),
            "errors": sum(1 for r in results if r["status"] not in ("SUCCESS", "DRY_RUN")),
            "sources_with_entity_hits": sum(1 for r in results if r.get("entity_mentions")),
            "total_contract_awards_found": total_awards_found,
        },
    }

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(output, f, indent=2, default=str)

    logger.info(f"Output written to {args.output}")
    stats = output["statistics"]
    logger.info(
        f"Summary: {stats['total_sources']} sources | "
        f"{stats['successful_fetches']} OK | "
        f"{stats['errors']} errors | "
        f"{stats['total_contract_awards_found']} contract awards found"
    )


if __name__ == "__main__":
    main()
