#!/usr/bin/env python3
"""
PKG-911 Congressional Records Retriever
==========================================
Collects Congressional hearing records, testimony transcripts, and official
investigation documents for PKG-911 target entities, including:

  - Waxman Committee (House Oversight) hearings on A.B. Krongard (2007):
    Howard "Buzzy" Krongard (former CEO Alex. Brown, CIA Exec. Director 2001-2004),
    his brother's (Howard Krongard, State Dept IG) alleged obstruction of
    Blackwater investigations.

  - Senate Finance Committee: Leon Black / Apollo Global / Epstein testimony
    (post-2019 revelations of Black's $158M+ payments to Epstein)

  - Senate Intelligence Committee Joint Inquiry (2002): 9/11 financial
    foreknowledge section — SEC referrals on pre-attack put option trading

  - House Oversight Committee: Blackwater hearings 2007-2008, Erik Prince
    testimony, WPPS contract oversight

  - Congress.gov search: Krongard + Blackwater + Inspector General

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
logger = logging.getLogger("pkg911_congressional")

PKG911_CAMPAIGN = "PKG-911"

SHERLOCK_ROOT = os.path.join(os.path.expanduser("~"), "Sherlock")
EVIDENCE_DIR = os.path.join(SHERLOCK_ROOT, "evidence")
OUTPUT_PATH = os.path.join(EVIDENCE_DIR, "pkg911_congressional_index.json")

# ---------------------------------------------------------------------------
# Source definitions
# ---------------------------------------------------------------------------

# Waxman Committee / Krongard / Blackwater (House Oversight 2007)
WAXMAN_KRONGARD_SOURCES = [
    {
        "source_name": "Congress.gov - Krongard Blackwater Inspector General search",
        "url": (
            "https://www.congress.gov/search?q=%7B%22source%22%3A%22hearings%22%2C"
            "%22search%22%3A%22Krongard+Blackwater+inspector+general%22%7D"
        ),
        "description": (
            "Congress.gov hearing search for 'Krongard Blackwater inspector general' — "
            "A.B. Krongard (Howard Krongard) was State Department Inspector General "
            "who allegedly blocked Blackwater investigation while his brother 'Buzzy' "
            "Krongard (ex-CEO Alex. Brown, ex-CIA Executive Director) held Blackwater "
            "advisory board seat. Waxman Committee (House Oversight) investigated 2007."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "Congress.gov search - Krongard Blackwater hearing records",
        "url": (
            "https://www.congress.gov/search?q=Krongard+Blackwater+inspector+general"
            "&searchResultViewType=expanded"
        ),
        "expected_evidence_tier": "E1",
        "description": (
            "Congress.gov general search for Krongard / Blackwater hearing records "
            "including testimony and committee reports."
        ),
    },
    {
        "source_name": "House Oversight Committee - Blackwater Hearings 2007",
        "url": "https://oversight.house.gov/investigations/",
        "description": (
            "House Committee on Oversight and Government Reform — investigations archive. "
            "Waxman chaired 2007-2009; Blackwater hearings generated public testimony "
            "from Erik Prince and Krongard recusal revelation."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "GPO - Krongard Blackwater Hearing Transcript",
        "url": (
            "https://www.govinfo.gov/content/pkg/CHRG-110hhrg45097/html/CHRG-110hhrg45097.htm"
        ),
        "description": (
            "GPO record of House Oversight hearing on Blackwater / Krongard — "
            "110th Congress, transcript of Waxman Committee proceedings where "
            "A.B. Krongard disclosed brother's Blackwater advisory board position."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "GPO - GovInfo search Krongard",
        "url": "https://www.govinfo.gov/search/#advanced?query=Krongard&collection=CHRG&dateRange=custom&startDate=2007-01-01&endDate=2008-12-31",
        "description": (
            "GovInfo.gov advanced search for 'Krongard' in Congressional Hearings "
            "(CHRG) collection, 2007-2008 — the Waxman Committee investigation period."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "GPO - GovInfo search Erik Prince Blackwater",
        "url": "https://www.govinfo.gov/search/#advanced?query=Blackwater+Erik+Prince&collection=CHRG&dateRange=custom&startDate=2007-01-01&endDate=2009-12-31",
        "description": (
            "GovInfo.gov search for Blackwater / Erik Prince Congressional hearings "
            "2007-2009 — covers WPPS contract oversight and Nisour Square aftermath."
        ),
        "expected_evidence_tier": "E1",
    },
]

# Senate Finance / Apollo / Leon Black
APOLLO_SENATE_SOURCES = [
    {
        "source_name": "Senate Finance Committee - Leon Black Apollo Epstein",
        "url": (
            "https://www.finance.senate.gov/search?query=Leon+Black+Apollo+Epstein"
        ),
        "description": (
            "Senate Finance Committee search for Leon Black / Apollo / Epstein "
            "— Senate Finance investigated Apollo's tax practices and the Black-Epstein "
            "financial relationship after 2019 revelations of $158M+ in payments."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "Congress.gov - Leon Black Epstein hearings",
        "url": (
            "https://www.congress.gov/search?q=Leon+Black+Epstein+Apollo"
            "&searchResultViewType=expanded"
        ),
        "description": (
            "Congress.gov search for all Congressional records mentioning "
            "Leon Black + Epstein + Apollo."
        ),
        "expected_evidence_tier": "E1",
    },
]

# Senate Intelligence / Joint Inquiry / 9/11 Financial Foreknowledge
INTEL_INQUIRY_SOURCES = [
    {
        "source_name": "Senate Intelligence - 9/11 Joint Inquiry Report",
        "url": (
            "https://www.intelligence.senate.gov/publications/"
            "report-joint-inquiry-intelligence-community-activities-and-conduct-"
            "prior-and-immediately"
        ),
        "description": (
            "Senate Select Committee on Intelligence Joint Inquiry into 9/11 — "
            "the primary Congressional investigation covering pre-attack financial "
            "foreknowledge, SEC referrals on put option activity, and intelligence "
            "failures. Contains the classified 28 pages on Saudi funding."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "Senate Intelligence - 9/11 Joint Inquiry PDF direct",
        "url": "https://www.intelligence.senate.gov/sites/default/files/publications/9-11report.pdf",
        "description": (
            "Direct PDF of the Senate Joint Inquiry final report (2002). "
            "Checking for Alex. Brown, Deutsche Bank, UAL/AAL put option, "
            "and financial foreknowledge references."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "GovInfo - Senate Joint Inquiry 2002",
        "url": "https://www.govinfo.gov/content/pkg/GPO-911REPORT/pdf/GPO-911REPORT.pdf",
        "description": (
            "GovInfo version of the 9/11 Commission Final Report — cross-reference "
            "for financial foreknowledge findings vs. Senate Joint Inquiry."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "Congress.gov - 9/11 put options insider trading hearings",
        "url": (
            "https://www.congress.gov/search?q=September+11+put+options+insider+trading"
            "&searchResultViewType=expanded"
        ),
        "description": (
            "Congress.gov search for all hearing records mentioning September 11 "
            "put options or insider trading investigations."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "Declassified 28 Pages - FBI Summary",
        "url": "https://vault.fbi.gov/9-11-commission-inquiry/9-11-commission-inquiry-part-01",
        "description": (
            "FBI FOIA Vault — 9/11 Commission Inquiry records. The 28 pages on "
            "Saudi funding were declassified July 2016. Searching for any financial "
            "foreknowledge / securities trading references."
        ),
        "expected_evidence_tier": "E1",
    },
]

# House Oversight / Blackwater
BLACKWATER_OVERSIGHT_SOURCES = [
    {
        "source_name": "GovInfo - House Oversight Blackwater Hearing Oct 2007",
        "url": (
            "https://www.govinfo.gov/content/pkg/CHRG-110hhrg38326/html/CHRG-110hhrg38326.htm"
        ),
        "description": (
            "GPO/GovInfo record of House Oversight Committee hearing on Blackwater "
            "October 2007 (Erik Prince testimony). 110th Congress hearing."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "GovInfo - Congressional Records search Blackwater 2007-2008",
        "url": (
            "https://www.govinfo.gov/search/#advanced?query=Blackwater&collection=CHRG"
            "&dateRange=custom&startDate=2007-01-01&endDate=2009-01-01"
        ),
        "description": (
            "GovInfo CHRG collection search for all Blackwater-related Congressional "
            "hearing records from 2007-2009."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "Congress.gov - Blackwater hearings search",
        "url": (
            "https://www.congress.gov/search?q=Blackwater+hearing"
            "&searchResultViewType=expanded"
        ),
        "description": (
            "Congress.gov search for all Blackwater-related hearing records."
        ),
        "expected_evidence_tier": "E1",
    },
]

ALL_SOURCES = (
    WAXMAN_KRONGARD_SOURCES
    + APOLLO_SENATE_SOURCES
    + INTEL_INQUIRY_SOURCES
    + BLACKWATER_OVERSIGHT_SOURCES
)

# Keywords for entity detection
ENTITY_KEYWORDS = [
    "Krongard", "Buzzy", "Howard Krongard", "A.B. Krongard",
    "Blackwater", "Erik Prince", "WPPS", "Academi", "Xe Services",
    "Alex Brown", "Alex. Brown", "Deutsche Bank",
    "CIA", "inspector general", "obstruction",
    "Leon Black", "Apollo", "Epstein",
    "put option", "September 11", "9/11", "insider trading",
    "foreknowledge", "UAL", "United Airlines", "American Airlines",
    "Waxman", "Joint Inquiry", "Senate Intelligence",
    "financial foreknowledge", "SEC investigation",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_preview(content: str, max_chars: int = 600) -> str:
    """Strip HTML tags and return a clean text preview."""
    text = re.sub(r'<(script|style)[^>]*>.*?</(script|style)>', '', content, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:max_chars]


def _extract_document_links(html: str, base_url: str) -> List[str]:
    """Extract PDF and document links from HTML pages."""
    links = []
    seen = set()
    patterns = [
        r'href="([^"]*\.pdf[^"]*)"',
        r'href="([^"]*\.htm[^"]*)"',
        r'href="([^"]*CHRG[^"]*)"',
        r'href="([^"]*hearing[^"]*)"',
        r'href="([^"]*testimony[^"]*)"',
    ]
    for pat in patterns:
        for match in re.finditer(pat, html, re.IGNORECASE):
            raw = match.group(1)
            full = urljoin(base_url, raw)
            if full not in seen:
                seen.add(full)
                links.append(full)
    return links[:25]


# ---------------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------------

def collect(dry_run: bool = False) -> List[Dict[str, Any]]:
    """
    Fetch all Congressional sources and return structured result records.
    """
    logger.info("=== PKG-911 Congressional Records Retriever ===")
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

                # Extract document links
                doc_links = _extract_document_links(content, resp.url)
                record["extracted_links"] = doc_links
                if doc_links:
                    logger.info(f"    Found {len(doc_links)} document links")

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
            "PKG-911 Congressional Records Retriever — Waxman/Krongard/Blackwater "
            "hearings, Senate Intelligence Joint Inquiry, Apollo/Leon Black testimony, "
            "and 9/11 financial foreknowledge Congressional records"
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

    logger.info("PKG-911 Congressional Records Retriever — starting")
    logger.info(f"  Output: {args.output}")

    results = collect(dry_run=args.dry_run)

    output = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "pkg911_congressional_retriever.py",
            "campaign": PKG911_CAMPAIGN,
            "dry_run": args.dry_run,
            "description": (
                "Congressional hearing records for PKG-911: Waxman Committee on "
                "Krongard/Blackwater (2007), Senate Intelligence 9/11 Joint Inquiry "
                "(2002), Senate Finance on Apollo/Leon Black, and House Oversight "
                "Blackwater hearings (2007-2008)."
            ),
        },
        "results": results,
        "statistics": {
            "total_sources": len(results),
            "successful_fetches": sum(1 for r in results if r["status"] == "SUCCESS"),
            "errors": sum(1 for r in results if r["status"] not in ("SUCCESS", "DRY_RUN")),
            "sources_with_entity_hits": sum(1 for r in results if r.get("entity_mentions")),
            "total_document_links": sum(len(r.get("extracted_links", [])) for r in results),
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
        f"{stats['total_document_links']} document links found"
    )


if __name__ == "__main__":
    main()
