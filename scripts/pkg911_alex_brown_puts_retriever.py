#!/usr/bin/env python3
"""
PKG-911 Alex. Brown / Deutsche Bank Put Options Retriever
==========================================================
Documents Alex. Brown & Sons / Deutsche Bank Alex. Brown as the primary
institutional conduit for anomalous pre-9/11 put option activity on American
Airlines (AAL) and United Airlines (UAL).

Key evidentiary threads:
  - A.B. Brown (Deutsche Bank's U.S. equity arm) was the single largest
    purchaser of UAL put options in the days before 9/11 per contemporaneous
    press reporting and the 9/11 Commission financial investigation.
  - A.B. Krongard (Buzzy Krongard) was CEO of Alex. Brown & Sons until its
    1999 acquisition by Deutsche Bank; he became Executive Director of CIA in
    2001. The timing of his role transition is central to the foreknowledge
    hypothesis.
  - The SEC conducted a formal investigation; findings were transmitted to the
    9/11 Commission but never publicly released in full.

Sources targeted:
  - 9/11 Commission Staff Statement No. 3 (Finances of 9/11)
  - Senate Joint Inquiry (2002) financial foreknowledge section
  - IOSCO 2003 report on securities market integrity post-9/11
  - Contemporaneous WSJ / Bloomberg / Reuters coverage (2001-2002)
  - SEC formal investigation public records

Part of PKG-911 campaign for Sherlock — Phase 7, Priority 2.
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
logger = logging.getLogger("pkg911_alex_brown_puts")

PKG911_CAMPAIGN = "PKG-911"

SHERLOCK_ROOT = os.path.join(os.path.expanduser("~"), "Sherlock")
EVIDENCE_DIR = os.path.join(SHERLOCK_ROOT, "evidence")
OUTPUT_PATH = os.path.join(EVIDENCE_DIR, "pkg911_alex_brown_puts_index.json")

# ---------------------------------------------------------------------------
# Source definitions
# ---------------------------------------------------------------------------

# 9/11 Commission official records
COMMISSION_SOURCES = [
    {
        "source_name": "9/11 Commission Staff Statement 3 - Finances",
        "url": "https://9-11commission.gov/staff_statements/staff_statement_3.pdf",
        "description": (
            "9/11 Commission Staff Statement No. 3: Finances of the 9/11 Plot. "
            "Official record of Commission's financial investigation, including "
            "SEC referrals on put option activity. Primary source document."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "9/11 Commission - Staff Statements Index",
        "url": "https://9-11commission.gov/staff_statements/",
        "description": (
            "Index of all 9/11 Commission staff statements — scanning for any "
            "additional financial investigation records beyond Statement 3."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "National Archives - 9/11 Commission Records",
        "url": "https://www.archives.gov/research/9-11",
        "description": (
            "National Archives 9/11 Commission records repository — financial "
            "investigation materials and SEC referral documentation."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "9/11 Commission Final Report - Chapter 5 Notes",
        "url": "https://www.9-11commission.gov/report/911Report_Ch5.pdf",
        "description": (
            "9/11 Commission Final Report Chapter 5 — includes footnotes referencing "
            "SEC and FBI investigation of pre-attack securities trading."
        ),
        "expected_evidence_tier": "E1",
    },
]

# Senate Joint Inquiry (2002)
SENATE_SOURCES = [
    {
        "source_name": "Senate Joint Inquiry 2002 - Full Report",
        "url": (
            "https://www.intelligence.senate.gov/publications/"
            "report-joint-inquiry-intelligence-community-activities-and-conduct-"
            "prior-and-immediately"
        ),
        "description": (
            "Senate Select Committee on Intelligence / House Permanent Select "
            "Committee on Intelligence Joint Inquiry into Intelligence Community "
            "Activities Before and After 9/11 (2002). Contains financial "
            "foreknowledge section."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "Senate Intelligence Committee - 9/11 Joint Inquiry PDF",
        "url": "https://www.intelligence.senate.gov/sites/default/files/publications/9-11report.pdf",
        "description": (
            "Direct PDF of the Senate Joint Inquiry report — checking for "
            "Alex. Brown, Deutsche Bank, and put option references."
        ),
        "expected_evidence_tier": "E1",
    },
]

# IOSCO Report
IOSCO_SOURCES = [
    {
        "source_name": "IOSCO 9/11 Securities Investigation Report",
        "url": "https://www.iosco.org/library/pubdocs/pdf/IOSCOPD121.pdf",
        "description": (
            "International Organization of Securities Commissions (IOSCO) report "
            "on securities market integrity post-9/11, 2002. Covers cross-border "
            "investigation of pre-attack put option activity across exchanges."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "IOSCO Publications Search - 9/11",
        "url": "https://www.iosco.org/library/pubdocs/",
        "description": (
            "IOSCO publications library — searching for September 11 securities "
            "market investigation documents published 2001-2003."
        ),
        "expected_evidence_tier": "E2",
    },
]

# Contemporaneous press coverage
PRESS_SOURCES = [
    {
        "source_name": "WSJ Archive - Alex Brown Deutsche Bank 9/11 Puts",
        "url": (
            "https://www.wsj.com/search?query=Alex+Brown+Deutsche+Bank+"
            "September+11+put+options+SEC&isToggleOn=true&operator=AND"
            "&sort=date-desc&duration=custom&startDate=2001/09/01&endDate=2002/12/31"
        ),
        "description": (
            "Wall Street Journal archive search for 'Alex Brown Deutsche Bank "
            "September 11 put options SEC' coverage from 2001-2002. WSJ was "
            "the primary outlet for SEC investigation reporting."
        ),
        "expected_evidence_tier": "E2",
    },
    {
        "source_name": "Reuters - 9/11 put options investigation archive",
        "url": (
            "https://www.reuters.com/search/news?query=Alex+Brown+put+options+"
            "September+11+insider+trading+SEC"
        ),
        "description": (
            "Reuters archive search for Alex. Brown / put options / SEC "
            "investigation coverage from the 2001-2002 period."
        ),
        "expected_evidence_tier": "E2",
    },
    {
        "source_name": "Bloomberg - Deutsche Bank Alex Brown 9/11 puts",
        "url": (
            "https://www.bloomberg.com/search?query=Alex+Brown+Deutsche+Bank+"
            "put+options+September+11+SEC+investigation"
        ),
        "description": (
            "Bloomberg archive search for Deutsche Bank Alex. Brown put option "
            "coverage in the immediate post-9/11 period."
        ),
        "expected_evidence_tier": "E2",
    },
    {
        "source_name": "SF Chronicle 2001 - Krongard CIA Alex Brown",
        "url": (
            "https://www.sfgate.com/news/article/Mystery-of-terror-insider-trading-"
            "2874789.php"
        ),
        "description": (
            "San Francisco Chronicle reporting on Krongard / Alex. Brown / CIA "
            "connection and pre-9/11 put option investigation."
        ),
        "expected_evidence_tier": "E2",
    },
    {
        "source_name": "The Independent 2001 - City Insiders Sep 11 Trades",
        "url": "https://www.independent.co.uk/money/markets/city-insiders-made-a-killing-9176661.html",
        "description": (
            "UK Independent contemporaneous reporting on financial insiders "
            "profiting from September 11 attacks through put options."
        ),
        "expected_evidence_tier": "E2",
    },
]

# SEC investigation records
SEC_SOURCES = [
    {
        "source_name": "SEC EDGAR - Alex Brown / Deutsche Bank 1999 filings",
        "url": (
            "https://efts.sec.gov/LATEST/search-index?q=%22Alex.+Brown%22"
            "&dateRange=custom&startdt=1999-01-01&enddt=2002-01-01"
        ),
        "description": (
            "SEC EDGAR full-text search for 'Alex. Brown' filings 1999-2001 — "
            "acquisition filings, form 4s, and any investigation-related disclosures."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "SEC EDGAR full-text search - put options September 11",
        "url": (
            "https://efts.sec.gov/LATEST/search-index?q=%22put+options%22+"
            "%22September+11%22&dateRange=custom&startdt=2001-09-01&enddt=2003-01-01"
        ),
        "description": (
            "SEC EDGAR full-text search for 'put options' AND 'September 11' "
            "in filings from the investigation period."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "SEC FOIA - 9/11 trading investigation",
        "url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=alex+brown&CIK=&type=&dateb=&owner=include&count=40&search_text=",
        "description": (
            "SEC EDGAR company search for Alex. Brown entities — to identify "
            "all registered entities under the Alex. Brown name for investigation tracking."
        ),
        "expected_evidence_tier": "E2",
    },
]

ALL_SOURCES = COMMISSION_SOURCES + SENATE_SOURCES + IOSCO_SOURCES + PRESS_SOURCES + SEC_SOURCES

# Keywords for entity detection
ENTITY_KEYWORDS = [
    "Alex Brown", "Alex. Brown", "Deutsche Bank", "Krongard", "Buzzy",
    "put option", "UAL", "United Airlines", "American Airlines", "AMR",
    "SEC", "insider trading", "foreknowledge",
    "September 11", "9/11",
    "CIA", "executive director", "intelligence",
    "IOSCO", "securities commission",
    "Poteshman", "informed trading",
]


# ---------------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------------

def collect(dry_run: bool = False) -> List[Dict[str, Any]]:
    """
    Fetch all Alex. Brown / put options sources and return structured records.
    """
    logger.info("=== PKG-911 Alex. Brown / Put Options Retriever ===")
    logger.info(f"  Campaign: {PKG911_CAMPAIGN}")
    logger.info(f"  Dry run: {dry_run}")
    logger.info(f"  Sources to fetch: {len(ALL_SOURCES)}")

    if dry_run:
        return _generate_dry_run_results()

    fetcher = RobustWebFetcher(timeout=30, max_retries=3)
    results = []

    for source in ALL_SOURCES:
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
            "extracted_links": [],
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
                record["content_preview"] = _make_preview(content)

                # Extract PDF links from HTML pages
                if "text/html" in resp.headers.get("content-type", ""):
                    pdf_links = _extract_pdf_links(content, resp.url)
                    record["extracted_links"] = pdf_links[:20]  # cap at 20
                    if pdf_links:
                        logger.info(f"    Found {len(pdf_links)} PDF links")

                # Scan for entity mentions
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


def _make_preview(content: str, max_chars: int = 500) -> str:
    """Strip HTML tags and return a clean text preview."""
    text = re.sub(r'<(script|style)[^>]*>.*?</(script|style)>', '', content, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:max_chars]


def _extract_pdf_links(html: str, base_url: str) -> List[str]:
    """Extract PDF links from an HTML page."""
    links = []
    seen = set()
    patterns = [
        r'href="([^"]*\.pdf[^"]*)"',
        r"href='([^']*\.pdf[^']*)'",
        r'href="([^"]*staff_statement[^"]*)"',
        r'href="([^"]*financial[^"]*)"',
    ]
    for pat in patterns:
        for match in re.finditer(pat, html, re.IGNORECASE):
            raw = match.group(1)
            full = urljoin(base_url, raw)
            if full not in seen:
                seen.add(full)
                links.append(full)
    return links


def _generate_dry_run_results() -> List[Dict[str, Any]]:
    """Return placeholder results for dry-run mode."""
    results = []
    for source in ALL_SOURCES:
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
            "extracted_links": [],
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
            "PKG-911 Alex. Brown / Deutsche Bank Put Options Retriever — collect "
            "documentation of pre-9/11 put option activity and the Alex. Brown / "
            "Krongard / CIA foreknowledge hypothesis"
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

    logger.info("PKG-911 Alex. Brown / Put Options Retriever — starting")
    logger.info(f"  Output: {args.output}")

    results = collect(dry_run=args.dry_run)

    output = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "pkg911_alex_brown_puts_retriever.py",
            "campaign": PKG911_CAMPAIGN,
            "dry_run": args.dry_run,
            "description": (
                "Documentation of Alex. Brown / Deutsche Bank Alex. Brown as "
                "primary institutional conduit for pre-9/11 put option activity "
                "on UAL and AAL. Covers 9/11 Commission, Senate Joint Inquiry, "
                "IOSCO, press coverage, and SEC records."
            ),
        },
        "results": results,
        "statistics": {
            "total_sources": len(results),
            "successful_fetches": sum(1 for r in results if r["status"] == "SUCCESS"),
            "errors": sum(1 for r in results if r["status"] not in ("SUCCESS", "DRY_RUN")),
            "sources_with_entity_hits": sum(1 for r in results if r.get("entity_mentions")),
            "total_pdf_links_found": sum(len(r.get("extracted_links", [])) for r in results),
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
        f"{stats['sources_with_entity_hits']} with keyword hits | "
        f"{stats['total_pdf_links_found']} PDF links discovered"
    )


if __name__ == "__main__":
    main()
