#!/usr/bin/env python3
"""
Epstein FOIA Document Collector
================================
Searches public government archives for Epstein-related documents using
the Retriever RobustWebFetcher. Targets DOJ, FBI Vault, and CIA CREST
reading room. Collects document listings and metadata into a structured
index for downstream analysis.

Part of PKG-EP (Epstein Investigation) campaign for Sherlock.
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

# Add Retriever to sys.path
RETRIEVER_BASE = os.path.join(
    os.path.expanduser("~"),
    "Johny5Alive", "j5a-nightshift", "ops", "fetchers", "retriever"
)
if RETRIEVER_BASE not in sys.path:
    sys.path.insert(0, RETRIEVER_BASE)

from retriever.rwf import RobustWebFetcher

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("epstein_foia_collector")

SHERLOCK_ROOT = os.path.join(os.path.expanduser("~"), "Sherlock")
OUTPUT_PATH = os.path.join(SHERLOCK_ROOT, "evidence", "epstein_foia_document_index.json")

# Archive targets with entry points and search strategies
ARCHIVE_TARGETS = [
    {
        "name": "DOJ Epstein Library",
        "base_url": "https://www.justice.gov/epstein",
        "description": "Department of Justice Jeffrey Epstein investigation documents",
        "search_strategy": "index_page",
        "link_patterns": [
            r'href="([^"]*\.pdf)"',
            r'href="(/epstein/[^"]*)"',
            r'href="(/media/[^"]*)"',
        ],
        "document_types": ["pdf", "court_filing", "press_release"],
        "priority": 1,
    },
    {
        "name": "FBI Vault - Epstein",
        "base_url": "https://vault.fbi.gov/",
        "search_url": "https://vault.fbi.gov/search?SearchableText=epstein",
        "description": "FBI FOIA Vault electronic reading room",
        "search_strategy": "search_page",
        "link_patterns": [
            r'href="(https://vault\.fbi\.gov/[^"]*)"',
            r'href="(/[^"]*epstein[^"]*)"',
        ],
        "document_types": ["fbi_record", "pdf", "investigation_file"],
        "priority": 1,
    },
    {
        "name": "CIA CREST Reading Room",
        "base_url": "https://www.cia.gov/readingroom/",
        "search_url": "https://www.cia.gov/readingroom/search/site/epstein",
        "description": "CIA FOIA Electronic Reading Room (CREST)",
        "search_strategy": "search_page",
        "link_patterns": [
            r'href="(https://www\.cia\.gov/readingroom/document/[^"]*)"',
            r'href="(/readingroom/document/[^"]*)"',
        ],
        "document_types": ["cia_record", "declassified", "pdf"],
        "priority": 2,
    },
]

# Additional keyword searches to run against archives that support it
SUPPLEMENTARY_SEARCHES = [
    "Jeffrey Epstein",
    "Ghislaine Maxwell",
    "Epstein blackmail",
    "Epstein intelligence",
    "Les Wexner Epstein",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_links_from_html(html: str, base_url: str, patterns: List[str]) -> List[Dict[str, str]]:
    """
    Extract document links from HTML using the provided regex patterns.
    Returns list of dicts with 'url' and 'text' keys.
    """
    links = []
    seen_urls = set()

    for pattern in patterns:
        for match in re.finditer(pattern, html, re.IGNORECASE):
            raw_url = match.group(1)
            full_url = urljoin(base_url, raw_url)
            if full_url not in seen_urls:
                seen_urls.add(full_url)
                links.append({
                    "url": full_url,
                    "raw_href": raw_url,
                })

    # Also extract link text for context
    for link_match in re.finditer(
        r'<a\s+[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
        html,
        re.IGNORECASE | re.DOTALL,
    ):
        href = link_match.group(1)
        text = re.sub(r"<[^>]+>", "", link_match.group(2)).strip()
        full_url = urljoin(base_url, href)
        # Update existing entries with link text
        for link in links:
            if link["url"] == full_url:
                link["text"] = text
                break

    return links


def extract_page_title(html: str) -> str:
    """Extract the <title> from HTML."""
    match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if match:
        return re.sub(r"\s+", " ", match.group(1)).strip()
    return ""


def collect_archive_documents(
    target: Dict[str, Any],
    fetcher: RobustWebFetcher,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Collect document metadata from a single archive target.
    Returns a result dict with documents list and status info.
    """
    name = target["name"]
    base_url = target["base_url"]
    search_url = target.get("search_url")
    strategy = target["search_strategy"]

    logger.info(f"Collecting from: {name}")

    result = {
        "source": name,
        "base_url": base_url,
        "description": target["description"],
        "priority": target["priority"],
        "status": "pending",
        "documents": [],
        "errors": [],
    }

    if dry_run:
        logger.info(f"  [DRY RUN] Would fetch {base_url}")
        result["status"] = "dry_run"
        result["documents"] = _generate_dry_run_documents(target)
        return result

    # Determine which URL to fetch
    fetch_url = search_url if (strategy == "search_page" and search_url) else base_url

    try:
        logger.info(f"  Fetching: {fetch_url}")
        resp = fetcher.get(fetch_url)

        if resp.status_code >= 400:
            error_msg = f"HTTP {resp.status_code} from {fetch_url}"
            logger.warning(f"  {error_msg}")
            result["status"] = "http_error"
            result["errors"].append(error_msg)
            return result

        page_title = extract_page_title(resp.text)
        logger.info(f"  Page title: {page_title}")

        # Extract document links
        links = extract_links_from_html(resp.text, resp.url, target["link_patterns"])
        logger.info(f"  Found {len(links)} document links")

        for link in links:
            doc = {
                "url": link["url"],
                "title": link.get("text", ""),
                "source_archive": name,
                "document_types": target["document_types"],
                "discovered_at": datetime.now(timezone.utc).isoformat(),
                "verified": False,
            }
            result["documents"].append(doc)

        result["status"] = "success"
        result["page_title"] = page_title

    except Exception as exc:
        error_msg = f"Fetch failed for {name}: {exc}"
        logger.error(f"  {error_msg}")
        result["status"] = "error"
        result["errors"].append(error_msg)

    # Run supplementary keyword searches if the archive has a search URL template
    if search_url and strategy == "search_page":
        for keyword in SUPPLEMENTARY_SEARCHES:
            try:
                # Build search URL with keyword
                kw_url = _build_search_url(target, keyword)
                if kw_url and kw_url != fetch_url:
                    logger.info(f"  Supplementary search: {keyword}")

                    if dry_run:
                        continue

                    kw_resp = fetcher.get(kw_url)
                    if kw_resp.status_code < 400:
                        kw_links = extract_links_from_html(
                            kw_resp.text, kw_resp.url, target["link_patterns"]
                        )
                        existing_urls = {d["url"] for d in result["documents"]}
                        new_count = 0
                        for link in kw_links:
                            if link["url"] not in existing_urls:
                                existing_urls.add(link["url"])
                                result["documents"].append({
                                    "url": link["url"],
                                    "title": link.get("text", ""),
                                    "source_archive": name,
                                    "search_keyword": keyword,
                                    "document_types": target["document_types"],
                                    "discovered_at": datetime.now(timezone.utc).isoformat(),
                                    "verified": False,
                                })
                                new_count += 1
                        if new_count:
                            logger.info(f"    +{new_count} new documents from '{keyword}'")

            except Exception as exc:
                logger.debug(f"  Supplementary search error ({keyword}): {exc}")

    logger.info(f"  Total documents collected from {name}: {len(result['documents'])}")
    return result


def _build_search_url(target: Dict[str, Any], keyword: str) -> Optional[str]:
    """Build a search URL for the given archive and keyword."""
    name = target["name"]
    encoded = quote_plus(keyword)

    if "FBI Vault" in name:
        return f"https://vault.fbi.gov/search?SearchableText={encoded}"
    elif "CIA CREST" in name:
        return f"https://www.cia.gov/readingroom/search/site/{encoded}"
    elif "DOJ" in name:
        # DOJ Epstein page is a static index; no search endpoint
        return None

    return None


def _generate_dry_run_documents(target: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate placeholder documents for dry-run mode."""
    name = target["name"]
    placeholders = []
    sample_titles = [
        "Epstein Investigation Report - Part 1",
        "Jeffrey Epstein - Related Correspondence",
        "Maxwell-Epstein Financial Records Summary",
    ]
    for i, title in enumerate(sample_titles, start=1):
        placeholders.append({
            "url": f"{target['base_url']}sample_document_{i}.pdf",
            "title": f"[DRY RUN] {title}",
            "source_archive": name,
            "document_types": target["document_types"],
            "discovered_at": datetime.now(timezone.utc).isoformat(),
            "verified": False,
        })
    return placeholders


# ---------------------------------------------------------------------------
# Verification pass
# ---------------------------------------------------------------------------

def verify_document_urls(
    documents: List[Dict[str, Any]],
    fetcher: RobustWebFetcher,
    max_verify: int = 50,
) -> int:
    """
    HEAD-check a sample of document URLs to verify they are reachable.
    Updates documents in place. Returns count of verified documents.
    """
    verified_count = 0
    to_check = documents[:max_verify]

    logger.info(f"Verifying up to {len(to_check)} document URLs...")

    for doc in to_check:
        try:
            ok = fetcher.head_ok(doc["url"])
            doc["verified"] = ok
            if ok:
                verified_count += 1
        except Exception:
            doc["verified"] = False

    logger.info(f"Verification complete: {verified_count}/{len(to_check)} URLs reachable")
    return verified_count


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_collection(dry_run: bool = False, skip_verify: bool = False) -> Dict[str, Any]:
    """
    Run full FOIA document collection across all archive targets.
    Returns the complete index dict.
    """
    fetcher = RobustWebFetcher(timeout=30, max_retries=3)

    index = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "epstein_foia_collector.py",
            "campaign": "PKG-EP",
            "dry_run": dry_run,
            "archives_scanned": len(ARCHIVE_TARGETS),
            "supplementary_keywords": SUPPLEMENTARY_SEARCHES,
        },
        "archives": [],
        "documents": [],
        "statistics": {
            "total_documents": 0,
            "verified_documents": 0,
            "by_archive": {},
        },
    }

    for target in ARCHIVE_TARGETS:
        archive_name = target["name"]
        logger.info(f"=== Processing archive: {archive_name} ===")

        result = collect_archive_documents(target, fetcher, dry_run=dry_run)

        index["archives"].append({
            "name": archive_name,
            "base_url": target["base_url"],
            "status": result["status"],
            "document_count": len(result["documents"]),
            "errors": result.get("errors", []),
        })

        index["documents"].extend(result["documents"])
        index["statistics"]["by_archive"][archive_name] = len(result["documents"])

    index["statistics"]["total_documents"] = len(index["documents"])

    # Optional verification pass
    if not dry_run and not skip_verify and index["documents"]:
        verified = verify_document_urls(index["documents"], fetcher)
        index["statistics"]["verified_documents"] = verified

    return index


def main():
    parser = argparse.ArgumentParser(
        description="Collect Epstein-related FOIA documents from public government archives"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making network calls; generate placeholder index",
    )
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="Skip URL verification pass (faster, less thorough)",
    )
    parser.add_argument(
        "--output",
        default=OUTPUT_PATH,
        help=f"Output path for document index JSON (default: {OUTPUT_PATH})",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug-level logging",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("Epstein FOIA Document Collector - starting")
    logger.info(f"  Dry run:      {args.dry_run}")
    logger.info(f"  Skip verify:  {args.skip_verify}")
    logger.info(f"  Output:       {args.output}")

    index = run_collection(dry_run=args.dry_run, skip_verify=args.skip_verify)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    with open(args.output, "w") as f:
        json.dump(index, f, indent=2, default=str)

    logger.info(f"Document index written to {args.output}")
    logger.info(
        f"Summary: {index['statistics']['total_documents']} documents "
        f"from {len(ARCHIVE_TARGETS)} archives"
    )

    for archive, count in index["statistics"]["by_archive"].items():
        logger.info(f"  {archive}: {count} documents")

    if index["statistics"]["verified_documents"] > 0:
        logger.info(
            f"  Verified: {index['statistics']['verified_documents']} URLs reachable"
        )


if __name__ == "__main__":
    main()
