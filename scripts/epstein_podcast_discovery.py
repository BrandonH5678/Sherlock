#!/usr/bin/env python3
"""
Epstein Podcast Discovery Script
=================================
Uses Retriever v1 discovery cascade to scan podcast homepages for episodes
matching Epstein-investigation search terms. Builds a source catalog of
relevant episodes across multiple independent media outlets.

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
from urllib.parse import urljoin

# Add Retriever to sys.path
RETRIEVER_BASE = os.path.join(
    os.path.expanduser("~"),
    "Johny5Alive", "j5a-nightshift", "ops", "fetchers", "retriever"
)
if RETRIEVER_BASE not in sys.path:
    sys.path.insert(0, RETRIEVER_BASE)

from retriever.discovery import (
    discover_audio_from_homepage,
    DiscoveryError,
    DiscoveryRetryConfig,
    _find_rss_links,
    _parse_rss_enclosures,
)
from retriever.rwf import RobustWebFetcher

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("epstein_podcast_discovery")

SHERLOCK_ROOT = os.path.join(os.path.expanduser("~"), "Sherlock")
OUTPUT_PATH = os.path.join(SHERLOCK_ROOT, "evidence", "epstein_podcast_source_catalog.json")

# Target podcast sources
PODCAST_SOURCES = [
    {
        "name": "Unlimited Hangout",
        "homepage": "https://unlimitedhangout.com/",
        "description": "Whitney Webb investigative journalism - primary Epstein/intelligence analysis",
        "priority": 1,
    },
    {
        "name": "The Corbett Report",
        "homepage": "https://www.corbettreport.com/",
        "description": "Independent investigative journalism on intelligence, finance, geopolitics",
        "priority": 2,
    },
    {
        "name": "TrueAnon",
        "homepage": "https://soundcloud.com/trueanonpod",
        "description": "Podcast focused on Epstein case, intelligence operations, and power structures",
        "rss_fallback": "https://feeds.soundcloud.com/users/soundcloud:users:693677498/sounds.rss",
        "priority": 1,
    },
]

# Search terms for filtering relevant episodes
SEARCH_TERMS = [
    "Epstein",
    "Maxwell",
    "Mossad",
    "PROMIS",
    "intelligence",
    "BCCI",
    "Lutnick",
    "Cantor Fitzgerald",
]

# Compile case-insensitive patterns for matching
SEARCH_PATTERNS = [re.compile(re.escape(term), re.IGNORECASE) for term in SEARCH_TERMS]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def matches_search_terms(text: str) -> List[str]:
    """Return list of search terms that appear in the given text."""
    if not text:
        return []
    matched = []
    for term, pattern in zip(SEARCH_TERMS, SEARCH_PATTERNS):
        if pattern.search(text):
            matched.append(term)
    return matched


def discover_rss_episodes(
    source: Dict[str, Any],
    fetcher: RobustWebFetcher,
    dry_run: bool = False,
) -> List[Dict[str, Any]]:
    """
    Discover all episodes from a podcast source via RSS, then filter by
    search terms. Returns list of matching episode metadata dicts.
    """
    name = source["name"]
    homepage = source["homepage"]
    rss_fallback = source.get("rss_fallback")

    logger.info(f"Discovering episodes for: {name} ({homepage})")

    if dry_run:
        logger.info(f"  [DRY RUN] Would fetch homepage and RSS feeds for {name}")
        return _generate_dry_run_episodes(source)

    # Step 1 - Fetch homepage and locate RSS feeds
    rss_urls = []
    try:
        home_resp = fetcher.get(homepage)
        if home_resp.status_code < 400:
            rss_urls = _find_rss_links(home_resp.text, home_resp.url)
            logger.info(f"  Found {len(rss_urls)} RSS candidates from homepage")
        else:
            logger.warning(f"  Homepage returned HTTP {home_resp.status_code}")
    except Exception as exc:
        logger.warning(f"  Failed to fetch homepage: {exc}")

    # Add fallback RSS if provided and not already found
    if rss_fallback and rss_fallback not in rss_urls:
        rss_urls.insert(0, rss_fallback)
        logger.info(f"  Added RSS fallback URL: {rss_fallback}")

    if not rss_urls:
        logger.warning(f"  No RSS feeds found for {name}")
        return []

    # Step 2 - Parse all RSS feeds and collect episodes
    all_episodes = []
    seen_urls = set()

    for rss_url in rss_urls:
        try:
            rss_resp = fetcher.get(rss_url)
            if rss_resp.status_code >= 400:
                logger.debug(f"  RSS feed returned {rss_resp.status_code}: {rss_url}")
                continue

            episodes = _parse_rss_enclosures(rss_resp.text, rss_url)
            logger.info(f"  Parsed {len(episodes)} episodes from {rss_url}")

            for ep in episodes:
                url = ep.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_episodes.append(ep)

        except Exception as exc:
            logger.debug(f"  RSS parse error for {rss_url}: {exc}")
            continue

    logger.info(f"  Total unique episodes found: {len(all_episodes)}")

    # Step 3 - Filter by search terms
    matching = []
    for ep in all_episodes:
        title = ep.get("title", "") or ""
        matched_terms = matches_search_terms(title)
        if matched_terms:
            matching.append({
                "source": name,
                "title": title,
                "pub_date": ep.get("pubDate"),
                "audio_url": ep.get("url"),
                "rss_feed": ep.get("rss"),
                "matched_terms": matched_terms,
                "match_count": len(matched_terms),
            })

    logger.info(f"  Episodes matching search terms: {len(matching)}")
    return matching


def _generate_dry_run_episodes(source: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate placeholder episode entries for dry-run mode."""
    name = source["name"]
    placeholders = []
    for i, term in enumerate(SEARCH_TERMS[:3], start=1):
        placeholders.append({
            "source": name,
            "title": f"[DRY RUN] Sample episode about {term}",
            "pub_date": None,
            "audio_url": f"https://example.com/{name.lower().replace(' ', '_')}/episode_{i}.mp3",
            "rss_feed": f"https://example.com/{name.lower().replace(' ', '_')}/feed.xml",
            "matched_terms": [term],
            "match_count": 1,
        })
    return placeholders


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_discovery(dry_run: bool = False) -> Dict[str, Any]:
    """
    Run full discovery cascade across all podcast sources.
    Returns the complete catalog dict.
    """
    fetcher = RobustWebFetcher(timeout=30, max_retries=3)
    retry_config = DiscoveryRetryConfig(
        max_cascade_retries=2,
        max_stage_retries=2,
        retry_delay=2.0,
        exponential_backoff=True,
    )

    catalog = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "epstein_podcast_discovery.py",
            "campaign": "PKG-EP",
            "search_terms": SEARCH_TERMS,
            "dry_run": dry_run,
            "sources_scanned": len(PODCAST_SOURCES),
        },
        "sources": [],
        "episodes": [],
        "statistics": {
            "total_episodes_found": 0,
            "total_matching_episodes": 0,
            "by_source": {},
            "by_search_term": {t: 0 for t in SEARCH_TERMS},
        },
    }

    for source in PODCAST_SOURCES:
        source_name = source["name"]
        logger.info(f"=== Processing source: {source_name} ===")

        catalog["sources"].append({
            "name": source_name,
            "homepage": source["homepage"],
            "description": source["description"],
            "priority": source["priority"],
        })

        try:
            matches = discover_rss_episodes(source, fetcher, dry_run=dry_run)
        except Exception as exc:
            logger.error(f"Discovery failed for {source_name}: {exc}")
            matches = []

        # Sort by match count (most relevant first)
        matches.sort(key=lambda x: x["match_count"], reverse=True)

        catalog["episodes"].extend(matches)
        catalog["statistics"]["by_source"][source_name] = len(matches)

        for ep in matches:
            for term in ep.get("matched_terms", []):
                catalog["statistics"]["by_search_term"][term] += 1

    catalog["statistics"]["total_matching_episodes"] = len(catalog["episodes"])

    return catalog


def main():
    parser = argparse.ArgumentParser(
        description="Discover Epstein-related podcast episodes across investigative media sources"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making network calls; generate placeholder catalog",
    )
    parser.add_argument(
        "--output",
        default=OUTPUT_PATH,
        help=f"Output path for catalog JSON (default: {OUTPUT_PATH})",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug-level logging",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("Epstein Podcast Discovery - starting")
    logger.info(f"  Dry run: {args.dry_run}")
    logger.info(f"  Output:  {args.output}")

    catalog = run_discovery(dry_run=args.dry_run)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    with open(args.output, "w") as f:
        json.dump(catalog, f, indent=2, default=str)

    logger.info(f"Catalog written to {args.output}")
    logger.info(
        f"Summary: {catalog['statistics']['total_matching_episodes']} matching episodes "
        f"across {len(PODCAST_SOURCES)} sources"
    )

    # Print per-source breakdown
    for src, count in catalog["statistics"]["by_source"].items():
        logger.info(f"  {src}: {count} matches")

    # Print per-term breakdown
    logger.info("Search term hits:")
    for term, count in sorted(
        catalog["statistics"]["by_search_term"].items(),
        key=lambda x: x[1],
        reverse=True,
    ):
        if count > 0:
            logger.info(f"  {term}: {count}")


if __name__ == "__main__":
    main()
