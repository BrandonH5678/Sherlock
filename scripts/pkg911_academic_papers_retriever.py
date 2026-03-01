#!/usr/bin/env python3
"""
PKG-911 Academic Papers Retriever
===================================
Collects and indexes peer-reviewed statistical analyses of pre-9/11 put options,
focusing on:
  - Poteshman (2006), "Unusual Option Market Activity and the Terrorist Attacks
    of September 11, 2001," Journal of Business vol 79(4). DOI: 10.1086/503645
  - Chesney, Crameri & Mancini (2015), "Detecting Informed Trading Activities
    in the Options Markets," Journal of Financial Stability, and the earlier
    Swiss Finance Institute working paper (2011/2012).
  - Any additional peer-reviewed analyses or rebuttals.

These papers are primary academic evidence for pre-9/11 financial foreknowledge
via option market activity. They form the evidentiary backbone for the
Alex. Brown / Deutsche Bank Alex. Brown put-option hypothesis.

Part of PKG-911 campaign for Sherlock — Phase 7, Priority 1.
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
logger = logging.getLogger("pkg911_academic_papers")

PKG911_CAMPAIGN = "PKG-911"

SHERLOCK_ROOT = os.path.join(os.path.expanduser("~"), "Sherlock")
EVIDENCE_DIR = os.path.join(SHERLOCK_ROOT, "evidence")
OUTPUT_PATH = os.path.join(EVIDENCE_DIR, "pkg911_academic_papers_index.json")

# ---------------------------------------------------------------------------
# Source definitions
# ---------------------------------------------------------------------------

# Poteshman (2006) sources
POTESHMAN_SOURCES = [
    {
        "source_name": "Poteshman 2006 - JSTOR",
        "url": "https://www.jstor.org/stable/10.1086/503645",
        "description": (
            "Poteshman (2006) 'Unusual Option Market Activity and the Terrorist "
            "Attacks of September 11, 2001,' Journal of Business vol 79(4). "
            "Primary academic evidence of statistically anomalous put option activity "
            "before 9/11 using proprietary CBOE data."
        ),
        "doi": "10.1086/503645",
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "Poteshman 2006 - Scholar Google",
        "url": (
            "https://scholar.google.com/scholar?q=Poteshman+2006+unusual+option+"
            "market+activity+terrorist+attacks+September+11"
        ),
        "description": "Google Scholar search for Poteshman 2006 paper and citing articles.",
        "doi": "10.1086/503645",
        "expected_evidence_tier": "E2",
    },
    {
        "source_name": "Poteshman 2006 - SSRN search",
        "url": (
            "https://papers.ssrn.com/sol3/results.cfm?RequestTimeout=50000000"
            "&txtSearch=Poteshman+September+11+options&rd=1"
        ),
        "description": "SSRN search for Poteshman 2006 pre-print or working paper.",
        "doi": "10.1086/503645",
        "expected_evidence_tier": "E2",
    },
    {
        "source_name": "Poteshman 2006 - CrossRef metadata",
        "url": "https://api.crossref.org/works/10.1086/503645",
        "description": (
            "CrossRef API metadata for Poteshman 2006 DOI — returns structured JSON "
            "with full citation details, abstract link, and citation count."
        ),
        "doi": "10.1086/503645",
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "Poteshman 2006 - Semantic Scholar",
        "url": (
            "https://api.semanticscholar.org/graph/v1/paper/search"
            "?query=Poteshman+unusual+option+market+activity+September+11"
            "&fields=title,authors,year,abstract,externalIds,citationCount,url"
        ),
        "description": "Semantic Scholar API search for Poteshman 2006 and related papers.",
        "doi": "10.1086/503645",
        "expected_evidence_tier": "E1",
    },
]

# Chesney, Crameri & Mancini (2015) sources
CHESNEY_SOURCES = [
    {
        "source_name": "Chesney et al. 2015 - SSRN working paper",
        "url": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1522157",
        "description": (
            "Chesney, Crameri & Mancini — Swiss Finance Institute working paper "
            "on detecting informed trading in options markets around 9/11. "
            "This SSRN ID is to be verified — may be the correct identifier."
        ),
        "doi": None,
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "Chesney et al. - Swiss Finance Institute",
        "url": "https://www.swissfinanceinstitute.ch/research/publications",
        "description": (
            "Swiss Finance Institute publications page — search for Chesney, "
            "Crameri & Mancini informed trading / 9/11 working paper series."
        ),
        "doi": None,
        "expected_evidence_tier": "E2",
    },
    {
        "source_name": "Chesney et al. 2015 - Scholar Google",
        "url": (
            "https://scholar.google.com/scholar?q=Chesney+Crameri+Mancini+"
            "detecting+informed+trading+options+September+11"
        ),
        "description": "Google Scholar search for Chesney et al. paper and citing articles.",
        "doi": None,
        "expected_evidence_tier": "E2",
    },
    {
        "source_name": "Chesney et al. - Semantic Scholar",
        "url": (
            "https://api.semanticscholar.org/graph/v1/paper/search"
            "?query=Chesney+Crameri+detecting+informed+trading+options+September+11"
            "&fields=title,authors,year,abstract,externalIds,citationCount,url"
        ),
        "description": (
            "Semantic Scholar API search for Chesney et al. and all related "
            "informed trading / 9/11 put option papers."
        ),
        "doi": None,
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "Chesney et al. - Journal of Financial Stability DOI lookup",
        "url": (
            "https://api.crossref.org/works"
            "?query=Chesney+Crameri+Mancini+detecting+informed+trading+options"
            "&filter=container-title:Journal+of+Financial+Stability&rows=5"
        ),
        "description": (
            "CrossRef API search for Chesney et al. 2015 Journal of Financial "
            "Stability paper — retrieves DOI, abstract link, and full citation."
        ),
        "doi": None,
        "expected_evidence_tier": "E1",
    },
]

# Additional rebuttal and context papers
ADDITIONAL_SOURCES = [
    {
        "source_name": "Terrorist Finance Working Group - 9/11 Commission",
        "url": "https://9-11commission.gov/staff_statements/staff_statement_3.pdf",
        "description": (
            "9/11 Commission Staff Statement No. 3 — Finances of the 9/11 Plot. "
            "Official record of the Commission's financial investigation findings, "
            "including SEC referrals on put option activity."
        ),
        "doi": None,
        "expected_evidence_tier": "E1",
    },
    {
        "source_name": "Semantic Scholar - broader 9/11 option trading academic search",
        "url": (
            "https://api.semanticscholar.org/graph/v1/paper/search"
            "?query=September+11+put+options+insider+trading+financial+markets"
            "&fields=title,authors,year,abstract,externalIds,citationCount,url&limit=10"
        ),
        "description": (
            "Broad Semantic Scholar search for all academic papers on 9/11 "
            "put option / insider trading / financial foreknowledge — intended to "
            "capture rebuttals, meta-analyses, and related work."
        ),
        "doi": None,
        "expected_evidence_tier": "E2",
    },
    {
        "source_name": "CrossRef broad search - 9/11 options foreknowledge",
        "url": (
            "https://api.crossref.org/works"
            "?query=September+11+put+options+insider+trading+terrorist+attacks"
            "&rows=10&sort=relevance"
        ),
        "description": (
            "CrossRef API broad search to find peer-reviewed papers on 9/11 "
            "options foreknowledge hypothesis, including any published rebuttals."
        ),
        "doi": None,
        "expected_evidence_tier": "E2",
    },
]

ALL_SOURCES = POTESHMAN_SOURCES + CHESNEY_SOURCES + ADDITIONAL_SOURCES

# Keywords relevant to this investigation
ENTITY_KEYWORDS = [
    "Poteshman", "Chesney", "Crameri", "Mancini",
    "put option", "call option", "implied volatility",
    "September 11", "9/11", "terrorist",
    "Alex Brown", "Deutsche Bank", "CBOE",
    "informed trading", "insider trading", "foreknowledge",
    "American Airlines", "United Airlines",
    "Journal of Business", "Journal of Financial Stability",
    "Swiss Finance Institute",
]


# ---------------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------------

def collect(dry_run: bool = False) -> List[Dict[str, Any]]:
    """
    Fetch all academic paper sources and return structured result records.
    Each record captures: source_name, url, status, content_preview,
    retrieved_at, evidence_tier, and any extracted metadata.
    """
    logger.info("=== PKG-911 Academic Papers Retriever ===")
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
            "doi": source.get("doi"),
            "status": None,
            "http_status_code": None,
            "content_preview": None,
            "content_length": None,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "evidence_tier": source.get("expected_evidence_tier", "E3"),
            "campaign": PKG911_CAMPAIGN,
            "entity_mentions": [],
            "extracted_metadata": {},
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

                # Try to parse JSON responses (Semantic Scholar, CrossRef)
                if "json" in resp.headers.get("content-type", "").lower() or url.startswith("https://api."):
                    try:
                        parsed = json.loads(content)
                        record["extracted_metadata"] = _extract_api_metadata(parsed, name)
                    except json.JSONDecodeError:
                        pass

                # Scan for entity mentions in content
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
    # Remove script/style blocks
    text = re.sub(r'<(script|style)[^>]*>.*?</(script|style)>', '', content, flags=re.DOTALL | re.IGNORECASE)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:max_chars]


def _extract_api_metadata(data: Any, source_name: str) -> Dict[str, Any]:
    """
    Extract structured metadata from API responses (Semantic Scholar, CrossRef).
    Returns a dict with title, authors, year, abstract, doi, citation_count, etc.
    """
    meta = {}

    if isinstance(data, dict):
        # Semantic Scholar single paper or search results
        if "data" in data and isinstance(data["data"], list):
            papers = data["data"]
            meta["result_count"] = len(papers)
            meta["papers"] = []
            for p in papers[:5]:  # top 5
                paper_meta = {
                    "title": p.get("title"),
                    "year": p.get("year"),
                    "authors": [a.get("name") for a in p.get("authors", [])],
                    "abstract": (p.get("abstract") or "")[:300],
                    "citation_count": p.get("citationCount"),
                    "url": p.get("url"),
                    "external_ids": p.get("externalIds", {}),
                }
                meta["papers"].append(paper_meta)

        # CrossRef works endpoint
        elif "message" in data:
            msg = data["message"]
            if "items" in msg:
                items = msg["items"]
                meta["result_count"] = len(items)
                meta["papers"] = []
                for item in items[:5]:
                    paper_meta = {
                        "title": " ".join(item.get("title", [])),
                        "year": item.get("published", {}).get("date-parts", [[None]])[0][0],
                        "doi": item.get("DOI"),
                        "journal": " ".join(item.get("container-title", [])),
                        "url": item.get("URL"),
                        "abstract": (item.get("abstract") or "")[:300],
                    }
                    meta["papers"].append(paper_meta)
            else:
                # Single CrossRef work
                meta["title"] = " ".join(msg.get("title", []))
                meta["doi"] = msg.get("DOI")
                meta["journal"] = " ".join(msg.get("container-title", []))
                meta["year"] = msg.get("published", {}).get("date-parts", [[None]])[0][0]
                meta["abstract"] = (msg.get("abstract") or "")[:300]
                meta["publisher"] = msg.get("publisher")
                meta["volume"] = msg.get("volume")
                meta["issue"] = msg.get("issue")
                meta["page"] = msg.get("page")

    return meta


def _generate_dry_run_results() -> List[Dict[str, Any]]:
    """Return placeholder results for dry-run mode."""
    results = []
    for source in ALL_SOURCES:
        results.append({
            "source_name": source["source_name"],
            "url": source["url"],
            "description": source.get("description", ""),
            "doi": source.get("doi"),
            "status": "DRY_RUN",
            "http_status_code": None,
            "content_preview": f"[DRY RUN] Would fetch: {source['url']}",
            "content_length": None,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "evidence_tier": source.get("expected_evidence_tier", "E3"),
            "campaign": PKG911_CAMPAIGN,
            "entity_mentions": [],
            "extracted_metadata": {},
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
            "PKG-911 Academic Papers Retriever — collect peer-reviewed analyses "
            "of pre-9/11 put option activity (Poteshman 2006; Chesney et al. 2015)"
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

    logger.info("PKG-911 Academic Papers Retriever — starting")
    logger.info(f"  Output: {args.output}")

    results = collect(dry_run=args.dry_run)

    output = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "pkg911_academic_papers_retriever.py",
            "campaign": PKG911_CAMPAIGN,
            "dry_run": args.dry_run,
            "description": (
                "Peer-reviewed academic analyses of pre-9/11 put option anomalies. "
                "Primary sources: Poteshman (2006) Journal of Business; "
                "Chesney, Crameri & Mancini (2015) Journal of Financial Stability."
            ),
        },
        "results": results,
        "statistics": {
            "total_sources": len(results),
            "successful_fetches": sum(1 for r in results if r["status"] == "SUCCESS"),
            "errors": sum(1 for r in results if r["status"] not in ("SUCCESS", "DRY_RUN")),
            "sources_with_entity_hits": sum(1 for r in results if r.get("entity_mentions")),
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
        f"{stats['sources_with_entity_hits']} with keyword hits"
    )


if __name__ == "__main__":
    main()
