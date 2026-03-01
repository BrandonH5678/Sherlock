#!/usr/bin/env python3
"""
PKG-911 SEC Filings Retriever
================================
Collects SEC EDGAR filings for key PKG-911 entities:
  - Alex. Brown & Sons / Deutsche Bank Alex. Brown (1999 acquisition)
  - Apollo Global Management (Leon Black — Epstein financier; IPO 2011
    and early filings containing Epstein disclosures)
  - Blackwater USA / Xe Services / Academi (any public entity filings)
  - Edmond de Rothschild entities (SEC registrations if any)
  - Cantor Fitzgerald (Lutnick / 9-11 nexus, bond market disruption)
  - Bear Stearns (Epstein-Bear Stearns financial relationship)

Uses EDGAR full-text search (EFTS) and EDGAR company search API endpoints
to collect structured filing metadata without requiring browser rendering.

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
logger = logging.getLogger("pkg911_sec_filings")

PKG911_CAMPAIGN = "PKG-911"

SHERLOCK_ROOT = os.path.join(os.path.expanduser("~"), "Sherlock")
EVIDENCE_DIR = os.path.join(SHERLOCK_ROOT, "evidence")
OUTPUT_PATH = os.path.join(EVIDENCE_DIR, "pkg911_sec_filings_index.json")

EDGAR_BASE = "https://www.sec.gov"
EFTS_BASE = "https://efts.sec.gov/LATEST/search-index"
EDGAR_COMPANY_SEARCH = "https://www.sec.gov/cgi-bin/browse-edgar"
EDGAR_API_BASE = "https://data.sec.gov"

# ---------------------------------------------------------------------------
# Entity definitions and their EDGAR search parameters
# ---------------------------------------------------------------------------

EDGAR_ENTITIES = [
    {
        "entity_name": "Alex. Brown & Sons / Deutsche Bank Alex. Brown",
        "rationale": (
            "Alex. Brown was the primary conduit for pre-9/11 UAL/AAL put options. "
            "Deutsche Bank acquired Alex. Brown in 1999. Filing records from 1999-2002 "
            "may contain SEC investigation disclosures or unusual trading disclosures."
        ),
        "searches": [
            {
                "source_name": "EDGAR EFTS - Alex. Brown full-text 1999-2003",
                "url": (
                    f"{EFTS_BASE}?q=%22Alex.+Brown%22"
                    "&dateRange=custom&startdt=1999-01-01&enddt=2003-01-01"
                    "&forms=S-4,8-K,10-K,SC 13G"
                ),
                "expected_evidence_tier": "E1",
            },
            {
                "source_name": "EDGAR Company Search - Alex Brown",
                "url": (
                    f"{EDGAR_COMPANY_SEARCH}?action=getcompany&company=alex+brown"
                    "&CIK=&type=&dateb=&owner=include&count=40&search_text="
                ),
                "expected_evidence_tier": "E1",
            },
            {
                "source_name": "EDGAR EFTS - Deutsche Bank Alex Brown acquisition S-4",
                "url": (
                    f"{EFTS_BASE}?q=%22Deutsche+Bank%22+%22Alex.+Brown%22"
                    "&dateRange=custom&startdt=1998-01-01&enddt=2000-12-31"
                    "&forms=S-4,SC TO-T"
                ),
                "expected_evidence_tier": "E1",
            },
        ],
    },
    {
        "entity_name": "Apollo Global Management (Leon Black)",
        "rationale": (
            "Leon Black paid Jeffrey Epstein $158M+ in fees (2012-2017) post-conviction. "
            "Apollo IPO'd in 2011; early 10-K filings may contain Epstein-related "
            "disclosures after relationship became public. Black resigned as CEO in 2021 "
            "following Epstein revelations."
        ),
        "searches": [
            {
                "source_name": "EDGAR EFTS - Apollo Global Epstein references",
                "url": (
                    f"{EFTS_BASE}?q=%22Epstein%22+%22Apollo%22"
                    "&dateRange=custom&startdt=2019-01-01&enddt=2022-12-31"
                ),
                "expected_evidence_tier": "E1",
            },
            {
                "source_name": "EDGAR Company Search - Apollo Global Management",
                "url": (
                    f"{EDGAR_COMPANY_SEARCH}?action=getcompany&company=apollo+global"
                    "&CIK=&type=10-K&dateb=&owner=include&count=20&search_text="
                ),
                "expected_evidence_tier": "E1",
            },
            {
                "source_name": "EDGAR EFTS - Leon Black references 2019-2022",
                "url": (
                    f"{EFTS_BASE}?q=%22Leon+Black%22+%22Epstein%22"
                    "&dateRange=custom&startdt=2019-01-01&enddt=2022-01-01"
                ),
                "expected_evidence_tier": "E1",
            },
        ],
    },
    {
        "entity_name": "Blackwater USA / Xe Services / Academi",
        "rationale": (
            "Blackwater (later Xe Services, then Academi) is a private military "
            "contractor founded by Erik Prince. Congressional investigation 2007-2008 "
            "examined Iraq war profiteering and oversight failures. Howard Krongard "
            "(former CEO of Alex. Brown's parent; brother of CIA's Buzzy Krongard) "
            "served as State Dept Inspector General while blocking Blackwater investigations."
        ),
        "searches": [
            {
                "source_name": "EDGAR Company Search - Blackwater",
                "url": (
                    f"{EDGAR_COMPANY_SEARCH}?action=getcompany&company=blackwater"
                    "&CIK=&type=&dateb=&owner=include&count=40&search_text="
                ),
                "expected_evidence_tier": "E2",
            },
            {
                "source_name": "EDGAR Company Search - Academi",
                "url": (
                    f"{EDGAR_COMPANY_SEARCH}?action=getcompany&company=academi"
                    "&CIK=&type=&dateb=&owner=include&count=40&search_text="
                ),
                "expected_evidence_tier": "E2",
            },
            {
                "source_name": "EDGAR Company Search - Xe Services",
                "url": (
                    f"{EDGAR_COMPANY_SEARCH}?action=getcompany&company=xe+services"
                    "&CIK=&type=&dateb=&owner=include&count=40&search_text="
                ),
                "expected_evidence_tier": "E2",
            },
            {
                "source_name": "EDGAR Company Search - Erik Prince",
                "url": (
                    f"{EDGAR_COMPANY_SEARCH}?action=getcompany&company=&CIK=erik+prince"
                    "&type=&dateb=&owner=include&count=40&search_text="
                ),
                "expected_evidence_tier": "E2",
            },
        ],
    },
    {
        "entity_name": "Edmond de Rothschild",
        "rationale": (
            "Edmond de Rothschild entities appear in Epstein financial network analysis "
            "through European banking connections. SEC registration status and US "
            "entity filings are relevant for mapping the network."
        ),
        "searches": [
            {
                "source_name": "EDGAR Company Search - Edmond de Rothschild",
                "url": (
                    f"{EDGAR_COMPANY_SEARCH}?action=getcompany&company=edmond+de+rothschild"
                    "&CIK=&type=&dateb=&owner=include&count=40&search_text="
                ),
                "expected_evidence_tier": "E3",
            },
            {
                "source_name": "EDGAR EFTS - Rothschild 9/11 references",
                "url": (
                    f"{EFTS_BASE}?q=%22Rothschild%22+%22September+11%22"
                    "&dateRange=custom&startdt=2001-09-01&enddt=2003-01-01"
                ),
                "expected_evidence_tier": "E3",
            },
        ],
    },
    {
        "entity_name": "Cantor Fitzgerald / Howard Lutnick",
        "rationale": (
            "Cantor Fitzgerald lost 658 employees on 9/11 (floors 101-105 of WTC1). "
            "Howard Lutnick was absent that day (his son's first day of school). "
            "Cantor controlled ~25% of US Treasury bond market; its destruction "
            "disrupted the US government securities clearing system. WTC7 housed SEC "
            "files on active market investigations. Lutnick testimony contradiction "
            "re: Epstein ties documented at 0.95 confidence."
        ),
        "searches": [
            {
                "source_name": "EDGAR Company Search - Cantor Fitzgerald",
                "url": (
                    f"{EDGAR_COMPANY_SEARCH}?action=getcompany&company=cantor+fitzgerald"
                    "&CIK=&type=&dateb=&owner=include&count=40&search_text="
                ),
                "expected_evidence_tier": "E2",
            },
            {
                "source_name": "EDGAR EFTS - Cantor Fitzgerald 9/11 period",
                "url": (
                    f"{EFTS_BASE}?q=%22Cantor+Fitzgerald%22"
                    "&dateRange=custom&startdt=2001-09-01&enddt=2003-01-01"
                ),
                "expected_evidence_tier": "E1",
            },
            {
                "source_name": "EDGAR EFTS - Lutnick references",
                "url": (
                    f"{EFTS_BASE}?q=%22Lutnick%22"
                    "&dateRange=custom&startdt=2001-09-01&enddt=2010-01-01"
                ),
                "expected_evidence_tier": "E2",
            },
        ],
    },
    {
        "entity_name": "Bear Stearns",
        "rationale": (
            "Bear Stearns was 40% owner of Liquid Funding Ltd (LFL), a $6.7B Bermuda "
            "vehicle where Epstein served as chairman. Bear Stearns collapsed March 2008 "
            "and was acquired by JPMorgan. LFL was wound down April 2008 (3 weeks after "
            "collapse). Sandstorm Report (Price Waterhouse 1991) names Bear Stearns as "
            "BCCI-connected institution."
        ),
        "searches": [
            {
                "source_name": "EDGAR Company Search - Bear Stearns",
                "url": (
                    f"{EDGAR_COMPANY_SEARCH}?action=getcompany&company=bear+stearns"
                    "&CIK=&type=&dateb=&owner=include&count=40&search_text="
                ),
                "expected_evidence_tier": "E1",
            },
            {
                "source_name": "EDGAR EFTS - Bear Stearns Epstein references",
                "url": (
                    f"{EFTS_BASE}?q=%22Bear+Stearns%22+%22Epstein%22"
                ),
                "expected_evidence_tier": "E1",
            },
            {
                "source_name": "EDGAR EFTS - Liquid Funding Ltd",
                "url": (
                    f"{EFTS_BASE}?q=%22Liquid+Funding%22"
                ),
                "expected_evidence_tier": "E1",
            },
        ],
    },
]

# Keywords for entity detection in content
ENTITY_KEYWORDS = [
    "Alex Brown", "Alex. Brown", "Deutsche Bank",
    "Apollo", "Leon Black", "Epstein",
    "Blackwater", "Academi", "Erik Prince", "Krongard",
    "Cantor Fitzgerald", "Lutnick",
    "Bear Stearns", "Liquid Funding",
    "Rothschild",
    "put option", "September 11", "9/11",
    "SEC investigation", "BCCI",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_preview(content: str, max_chars: int = 500) -> str:
    """Strip HTML/XML tags and return a clean text preview."""
    text = re.sub(r'<(script|style)[^>]*>.*?</(script|style)>', '', content, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:max_chars]


def _extract_edgar_links(html: str, base_url: str) -> List[Dict[str, str]]:
    """Extract filing links from EDGAR HTML pages."""
    links = []
    seen = set()
    # Match EDGAR filing index links
    patterns = [
        r'href="(/Archives/edgar/data/[^"]+\.(?:htm|html|pdf|txt))"',
        r'href="(/cgi-bin/browse-edgar[^"]*)"',
    ]
    for pat in patterns:
        for match in re.finditer(pat, html, re.IGNORECASE):
            raw = match.group(1)
            full = urljoin(base_url, raw)
            if full not in seen:
                seen.add(full)
                links.append({"url": full, "type": "edgar_filing"})
    return links[:30]


def _parse_edgar_json(content: str) -> Dict[str, Any]:
    """Try to parse JSON from EDGAR API responses."""
    try:
        data = json.loads(content)
        # Summarize hits from EFTS search
        if "hits" in data:
            hits = data["hits"]
            total = hits.get("total", {})
            entries = hits.get("hits", [])
            papers = []
            for e in entries[:10]:
                src = e.get("_source", {})
                papers.append({
                    "entity_name": src.get("entity_name"),
                    "file_date": src.get("file_date"),
                    "form_type": src.get("form_type"),
                    "file_num": src.get("file_num"),
                    "display_date_filed": src.get("display_date_filed"),
                    "description": src.get("description"),
                    "url": (
                        f"https://www.sec.gov/Archives/edgar/data/"
                        f"{src.get('entity_id', '')}/{src.get('file_date', '').replace('-','')}"
                    ),
                })
            return {
                "total_results": total.get("value", 0),
                "filings": papers,
            }
        return {"raw_keys": list(data.keys())}
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------------

def collect(dry_run: bool = False) -> List[Dict[str, Any]]:
    """
    Fetch all SEC EDGAR sources and return structured result records.
    """
    logger.info("=== PKG-911 SEC Filings Retriever ===")
    logger.info(f"  Campaign: {PKG911_CAMPAIGN}")
    logger.info(f"  Dry run: {dry_run}")

    # Flatten searches across all entities
    all_searches = []
    for entity in EDGAR_ENTITIES:
        for search in entity["searches"]:
            all_searches.append({**search, "entity_name": entity["entity_name"]})

    logger.info(f"  Total searches: {len(all_searches)}")

    if dry_run:
        return _generate_dry_run_results(all_searches)

    fetcher = RobustWebFetcher(timeout=30, max_retries=3)
    results = []

    for search in all_searches:
        name = search["source_name"]
        url = search["url"]
        logger.info(f"  Fetching: {name}")
        logger.info(f"    URL: {url}")

        record = {
            "source_name": name,
            "entity_name": search.get("entity_name", ""),
            "url": url,
            "status": None,
            "http_status_code": None,
            "content_preview": None,
            "content_length": None,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "evidence_tier": search.get("expected_evidence_tier", "E3"),
            "campaign": PKG911_CAMPAIGN,
            "entity_mentions": [],
            "extracted_filings": [],
            "parsed_results": {},
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
                if "json" in ct or "efts.sec.gov" in url:
                    record["parsed_results"] = _parse_edgar_json(content)
                    record["content_preview"] = json.dumps(record["parsed_results"])[:500]
                else:
                    record["content_preview"] = _make_preview(content)
                    record["extracted_filings"] = _extract_edgar_links(content, resp.url)

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

    logger.info(f"Collection complete: {len(results)} searches processed")
    successes = sum(1 for r in results if r["status"] == "SUCCESS")
    logger.info(f"  Successes: {successes} / {len(results)}")

    return results


def _generate_dry_run_results(all_searches: List[Dict]) -> List[Dict[str, Any]]:
    """Return placeholder results for dry-run mode."""
    results = []
    for search in all_searches:
        results.append({
            "source_name": search["source_name"],
            "entity_name": search.get("entity_name", ""),
            "url": search["url"],
            "status": "DRY_RUN",
            "http_status_code": None,
            "content_preview": f"[DRY RUN] Would fetch: {search['url']}",
            "content_length": None,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "evidence_tier": search.get("expected_evidence_tier", "E3"),
            "campaign": PKG911_CAMPAIGN,
            "entity_mentions": [],
            "extracted_filings": [],
            "parsed_results": {},
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
            "PKG-911 SEC Filings Retriever — collect EDGAR filings for Alex. Brown, "
            "Apollo/Leon Black, Blackwater, Cantor Fitzgerald, Bear Stearns, "
            "and Edmond de Rothschild"
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

    logger.info("PKG-911 SEC Filings Retriever — starting")
    logger.info(f"  Output: {args.output}")

    results = collect(dry_run=args.dry_run)

    output = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "pkg911_sec_filings_retriever.py",
            "campaign": PKG911_CAMPAIGN,
            "dry_run": args.dry_run,
            "entities_covered": [e["entity_name"] for e in EDGAR_ENTITIES],
            "description": (
                "SEC EDGAR filings for PKG-911 key entities: Alex. Brown, "
                "Apollo/Leon Black, Blackwater/Academi, Cantor Fitzgerald, "
                "Bear Stearns, and Edmond de Rothschild."
            ),
        },
        "results": results,
        "statistics": {
            "total_searches": len(results),
            "successful_fetches": sum(1 for r in results if r["status"] == "SUCCESS"),
            "errors": sum(1 for r in results if r["status"] not in ("SUCCESS", "DRY_RUN")),
            "sources_with_entity_hits": sum(1 for r in results if r.get("entity_mentions")),
            "total_filings_found": sum(len(r.get("extracted_filings", [])) for r in results),
        },
    }

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(output, f, indent=2, default=str)

    logger.info(f"Output written to {args.output}")
    stats = output["statistics"]
    logger.info(
        f"Summary: {stats['total_searches']} searches | "
        f"{stats['successful_fetches']} OK | "
        f"{stats['errors']} errors | "
        f"{stats['total_filings_found']} filings discovered"
    )


if __name__ == "__main__":
    main()
