#!/usr/bin/env python3
"""
PKG-911 FOIA and Court Records Retriever
==========================================
Collects FOIA releases and court records for PKG-911 subjects via:

  - CourtListener / PACER public records: Blackwater/Xe/Academi civil and
    criminal litigation (Nisour Square manslaughter, Iraq war crimes, etc.)

  - MuckRock FOIA database: CIA investigation of Alex. Brown put options,
    SEC investigation documents, FBI records on pre-9/11 financial anomalies

  - CIA FOIA Reading Room: Krongard-related records, Alex. Brown put option
    investigation documents, pre-9/11 financial intelligence

  - FBI Vault: Epstein records that may reference Krongard; 9/11 financial
    investigation records

  - NSA FOIA portal: Any signals intelligence related to pre-9/11 financial
    foreknowledge

The combination of FOIA releases and court records provides the documentary
foundation for primary-source claims in the PKG-911 investigation.

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
logger = logging.getLogger("pkg911_foia")

PKG911_CAMPAIGN = "PKG-911"

SHERLOCK_ROOT = os.path.join(os.path.expanduser("~"), "Sherlock")
EVIDENCE_DIR = os.path.join(SHERLOCK_ROOT, "evidence")
OUTPUT_PATH = os.path.join(EVIDENCE_DIR, "pkg911_foia_index.json")

# ---------------------------------------------------------------------------
# Source definitions
# ---------------------------------------------------------------------------

# CourtListener / PACER public records
COURT_SOURCES = [
    {
        "source_name": "CourtListener - Blackwater litigation search",
        "url": "https://www.courtlistener.com/?q=blackwater&type=r&order_by=score+desc",
        "description": (
            "CourtListener RECAP archive search for Blackwater-related court records. "
            "Covers Nisour Square manslaughter (US v. Slough et al.), civil cases "
            "from Iraqi civilian victims, whistleblower suits, and contract disputes."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "CourtListener - Xe Services litigation",
        "url": "https://www.courtlistener.com/?q=%22Xe+Services%22&type=r&order_by=score+desc",
        "description": (
            "CourtListener RECAP search for Xe Services (Blackwater renamed) "
            "court records — covers post-2009 litigation under the renamed entity."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "CourtListener - Academi litigation",
        "url": "https://www.courtlistener.com/?q=Academi&type=r&order_by=score+desc",
        "description": (
            "CourtListener RECAP search for Academi (Blackwater/Xe's final name) "
            "court records — covers CONSTELLIS acquisition period litigation."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "CourtListener - Erik Prince litigation",
        "url": "https://www.courtlistener.com/?q=%22Erik+Prince%22&type=r&order_by=score+desc",
        "description": (
            "CourtListener RECAP search for Erik Prince personally — whistleblower "
            "affidavits, deposition transcripts, and civil suits naming Prince."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "CourtListener - Krongard CIA records",
        "url": "https://www.courtlistener.com/?q=Krongard&type=r&order_by=score+desc",
        "description": (
            "CourtListener RECAP search for Krongard — any civil or criminal "
            "records naming Buzzy Krongard (CIA) or A.B. Krongard (State Dept IG)."
        ),
        "expected_evidence_tier": "E2",
    },
    {
        "source_name": "CourtListener - Alex Brown September 11 put options",
        "url": (
            "https://www.courtlistener.com/?q=%22Alex+Brown%22+%22September+11%22"
            "&type=r&order_by=score+desc"
        ),
        "description": (
            "CourtListener search for 'Alex Brown' + 'September 11' in court records — "
            "any civil or SEC enforcement actions referencing the put option investigation."
        ),
        "expected_evidence_tier": "E2",
    },
    {
        "source_name": "CourtListener - US v. Slough (Nisour Square manslaughter)",
        "url": "https://www.courtlistener.com/docket/4202111/united-states-v-slough/",
        "description": (
            "US v. Slough et al. — the Nisour Square manslaughter case against "
            "Blackwater contractors. Covers prosecutorial history, appeals, and "
            "the Obama-era convictions later overturned on appeal."
        ),
        "expected_evidence_tier": "E1",
    },
]

# MuckRock FOIA database
MUCKROCK_SOURCES = [
    {
        "source_name": "MuckRock - Alex Brown put options September 11",
        "url": (
            "https://www.muckrock.com/foi/list/?q=Alex+Brown+put+options+September+11"
        ),
        "description": (
            "MuckRock FOIA request database search for 'Alex Brown put options "
            "September 11' — tracking any FOIA requests to SEC, CIA, FBI, or "
            "Treasury regarding the pre-9/11 put option investigation."
        ),
        "expected_evidence_tier": "E2",
    },
    {
        "source_name": "MuckRock - Blackwater FOIA requests",
        "url": "https://www.muckrock.com/foi/list/?q=Blackwater",
        "description": (
            "MuckRock FOIA database search for Blackwater — tracking FOIA requests "
            "to DOD, State Dept, CIA, and FBI regarding Blackwater operations."
        ),
        "expected_evidence_tier": "E2",
    },
    {
        "source_name": "MuckRock - Krongard CIA FOIA requests",
        "url": "https://www.muckrock.com/foi/list/?q=Krongard+CIA",
        "description": (
            "MuckRock search for Krongard CIA FOIA requests — any releases relating "
            "to Buzzy Krongard's tenure as CIA Executive Director 2001-2004."
        ),
        "expected_evidence_tier": "E2",
    },
    {
        "source_name": "MuckRock - 9/11 put options insider trading FOIA",
        "url": "https://www.muckrock.com/foi/list/?q=September+11+put+options+insider+trading",
        "description": (
            "MuckRock search for 9/11 put option FOIA requests — tracking any "
            "agency responses on the pre-attack securities trading investigation."
        ),
        "expected_evidence_tier": "E2",
    },
]

# CIA FOIA Reading Room
CIA_FOIA_SOURCES = [
    {
        "source_name": "CIA FOIA Reading Room - Krongard",
        "url": "https://www.cia.gov/readingroom/search/site/Krongard",
        "description": (
            "CIA FOIA Reading Room search for 'Krongard' — any declassified "
            "documents mentioning A.B. (Buzzy) Krongard, CIA Executive Director "
            "from March 2001 to November 2004. Krongard was former CEO of "
            "Alex. Brown & Sons (acquired by Deutsche Bank 1999)."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "CIA FOIA Reading Room - Alex Brown",
        "url": "https://www.cia.gov/readingroom/search/site/alex%20brown",
        "description": (
            "CIA FOIA Reading Room search for 'Alex Brown' — any CIA documents "
            "referencing Alex. Brown & Sons or Deutsche Bank Alex. Brown, "
            "potentially including pre-9/11 financial intelligence assessments."
        ),
        "expected_evidence_tier": "E2",
    },
    {
        "source_name": "CIA FOIA Reading Room - September 11 financial",
        "url": "https://www.cia.gov/readingroom/search/site/september%2011%20financial",
        "description": (
            "CIA FOIA Reading Room search for '9/11 financial' — declassified "
            "CIA assessments of pre-attack financial anomalies."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "CIA FOIA Reading Room - put options",
        "url": "https://www.cia.gov/readingroom/search/site/put%20options",
        "description": (
            "CIA FOIA Reading Room search for 'put options' — any CIA analysis "
            "of pre-9/11 option market activity as potential intelligence signal."
        ),
        "expected_evidence_tier": "E2",
    },
]

# FBI Vault FOIA releases
FBI_VAULT_SOURCES = [
    {
        "source_name": "FBI Vault - 9/11 Commission Inquiry",
        "url": "https://vault.fbi.gov/9-11-commission-inquiry",
        "description": (
            "FBI FOIA Vault release of 9/11 Commission Inquiry documents — "
            "includes FBI investigative records shared with the Commission, "
            "potentially covering financial foreknowledge investigation."
        ),
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "FBI Vault - Epstein FOIA releases",
        "url": "https://vault.fbi.gov/jeffrey-epstein",
        "description": (
            "FBI FOIA Vault releases on Jeffrey Epstein — searching for any "
            "references to Krongard or CIA connections in the FBI Epstein file."
        ),
        "expected_evidence_tier": "E2",
    },
    {
        "source_name": "FBI Vault - Blackwater / Iraq investigations",
        "url": "https://vault.fbi.gov/search?SearchableText=blackwater",
        "description": (
            "FBI FOIA Vault search for Blackwater-related releases — any FBI "
            "investigative records on Blackwater contractor conduct in Iraq."
        ),
        "expected_evidence_tier": "E2",
    },
    {
        "source_name": "FBI Vault - Financial Crimes 9/11 period",
        "url": "https://vault.fbi.gov/search?SearchableText=September+11+financial",
        "description": (
            "FBI Vault search for financial crimes / 9/11 period documents — "
            "FBI financial crimes division records on pre-attack securities trading."
        ),
        "expected_evidence_tier": "E2",
    },
]

# NSA FOIA portal
NSA_FOIA_SOURCES = [
    {
        "source_name": "NSA FOIA - September 11 financial intelligence",
        "url": "https://www.nsa.gov/foia/",
        "description": (
            "NSA FOIA portal — the NSA SIGINT mission would have captured any "
            "financial communications related to pre-9/11 put option activity. "
            "Most relevant NSA FOIA releases would be via mandatory declassification "
            "review; this source indexes available NSA FOIA releases."
        ),
        "expected_evidence_tier": "E3",
    },
]

# Treasury / FinCEN records
TREASURY_SOURCES = [
    {
        "source_name": "Treasury FinCEN - 9/11 financial suspicious activity",
        "url": "https://www.fincen.gov/resources/statutes-regulations/usa-patriot-act",
        "description": (
            "FinCEN (Financial Crimes Enforcement Network) — post-9/11 regulatory "
            "framework for suspicious activity reports. Pre-9/11 SARs on put option "
            "activity would have been filed through FinCEN predecessors."
        ),
        "expected_evidence_tier": "E3",
    },
    {
        "source_name": "Treasury FOIA - 9/11 financial investigation",
        "url": "https://home.treasury.gov/footer/freedom-of-information-act/",
        "description": (
            "Treasury FOIA portal — Office of Terrorism and Financial Intelligence "
            "records on pre-9/11 financial anomalies and post-9/11 investigation."
        ),
        "expected_evidence_tier": "E3",
    },
]

ALL_SOURCES = (
    COURT_SOURCES
    + MUCKROCK_SOURCES
    + CIA_FOIA_SOURCES
    + FBI_VAULT_SOURCES
    + NSA_FOIA_SOURCES
    + TREASURY_SOURCES
)

# Keywords for entity detection
ENTITY_KEYWORDS = [
    "Blackwater", "Xe Services", "Academi", "Erik Prince",
    "Krongard", "Buzzy", "A.B. Krongard",
    "Alex Brown", "Alex. Brown", "Deutsche Bank",
    "put option", "September 11", "9/11",
    "insider trading", "foreknowledge", "securities",
    "CIA", "FBI", "NSA", "SEC",
    "Epstein", "Nisour Square", "Iraq",
    "FOIA", "declassified", "reading room",
    "financial intelligence", "suspicious activity",
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


def _extract_document_links(html: str, base_url: str) -> List[Dict[str, str]]:
    """Extract PDF and document links from court/FOIA HTML pages."""
    links = []
    seen = set()
    patterns = [
        # PDF links
        (r'href="([^"]*\.pdf[^"]*)"', "pdf"),
        # CourtListener recap links
        (r'href="(/recap/[^"]*)"', "recap"),
        # CourtListener docket links
        (r'href="(/docket/[^"]*)"', "docket"),
        # CIA Reading Room document links
        (r'href="(https://www\.cia\.gov/readingroom/document/[^"]*)"', "cia_doc"),
        # FBI Vault document links
        (r'href="(https://vault\.fbi\.gov/[^"]*)"', "fbi_vault"),
        # MuckRock FOIA request links
        (r'href="(https://www\.muckrock\.com/foi/[^"]*)"', "muckrock_foi"),
    ]
    for pat, link_type in patterns:
        for match in re.finditer(pat, html, re.IGNORECASE):
            raw = match.group(1)
            full = urljoin(base_url, raw)
            if full not in seen:
                seen.add(full)
                links.append({"url": full, "type": link_type})
    return links[:30]


def _extract_court_metadata(html: str) -> Dict[str, Any]:
    """Extract basic court case metadata from CourtListener HTML."""
    meta = {}

    # Try to extract case names
    case_names = re.findall(
        r'class="case-name[^"]*"[^>]*>([^<]+)<', html, re.IGNORECASE
    )
    if case_names:
        meta["case_names"] = [n.strip() for n in case_names[:10]]

    # Try to extract result counts
    count_match = re.search(r'([\d,]+)\s+result', html, re.IGNORECASE)
    if count_match:
        meta["result_count_text"] = count_match.group(0)

    return meta


# ---------------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------------

def collect(dry_run: bool = False) -> List[Dict[str, Any]]:
    """
    Fetch all FOIA and court record sources and return structured result records.
    """
    logger.info("=== PKG-911 FOIA and Court Records Retriever ===")
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
            "court_metadata": {},
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

                # Extract document and case links
                doc_links = _extract_document_links(content, resp.url)
                record["extracted_links"] = doc_links
                if doc_links:
                    logger.info(f"    Found {len(doc_links)} document links")

                # For court sources, try to extract metadata
                if "courtlistener" in url:
                    record["court_metadata"] = _extract_court_metadata(content)

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
            "court_metadata": {},
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
            "PKG-911 FOIA and Court Records Retriever — CourtListener/PACER "
            "Blackwater litigation, MuckRock FOIA database, CIA Reading Room, "
            "FBI Vault, NSA FOIA, and Treasury FOIA records"
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

    logger.info("PKG-911 FOIA and Court Records Retriever — starting")
    logger.info(f"  Output: {args.output}")

    results = collect(dry_run=args.dry_run)

    output = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "pkg911_foia_retriever.py",
            "campaign": PKG911_CAMPAIGN,
            "dry_run": args.dry_run,
            "description": (
                "FOIA releases and court records for PKG-911: CourtListener/PACER "
                "Blackwater litigation, MuckRock FOIA (Alex. Brown put options, "
                "Blackwater, Krongard), CIA Reading Room (Krongard, put options), "
                "FBI Vault (9/11 Commission, Epstein), NSA FOIA, and Treasury FOIA."
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
        f"{stats['sources_with_entity_hits']} with keyword hits | "
        f"{stats['total_document_links']} document links discovered"
    )


if __name__ == "__main__":
    main()
