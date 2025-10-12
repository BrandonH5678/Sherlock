# fetch_uap_reading_list.py - Enhanced with robust_web_fetcher
import os, json, sys, logging
from pathlib import Path

# Import enhanced fetcher from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))
from robust_web_fetcher import RobustWebFetcher, filename_from_url, DownloadStatus

OUTDIR = os.environ.get("OUTDIR", "uap_reading_list")
CONVERT_HTML = os.environ.get("CONVERT_HTML_TO_PDF", "0") == "1"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DOCS = [
  {
    "title": "FY2024 Consolidated Annual Report on UAP (Unclassified)",
    "url": "https://www.dni.gov/index.php/newsroom/reports-publications/reports-publications-2024/4020-uap-2024",
    "pdf_hint": True  # page links to the PDF
  },
  {
    "title": "AARO Historical Record Report, Volume I (Mar 8, 2024)",
    "url": "https://media.defense.gov/2024/Mar/08/2003409233/-1/-1/0/DOPSR-CLEARED-508-COMPLIANT-HRRV1-08-MAR-2024-FINAL.PDF",
  },
  {
    "title": "NASA UAP Independent Study Team – Final Report (2023)",
    "url": "https://science.nasa.gov/wp-content/uploads/2023/09/uap-independent-study-team-final-report.pdf",
  },
  {
    "title": "Starlink Misidentification Case Study (Buettner et al., 2024, PDF)",
    "url": "https://arxiv.org/pdf/2403.08155",
  },
  {
    "title": "ODNI Preliminary Assessment of UAP (2021)",
    "url": "https://www.dni.gov/files/ODNI/documents/assessments/Prelimary-Assessment-UAP-20210625.pdf",
  },
  {
    "title": "2022 Annual Report on UAP (ODNI)",
    "url": "https://www.dni.gov/files/ODNI/documents/assessments/Unclassified-2022-Annual-Report-UAP.pdf",
  },
  {
    "title": "Project Condign – UAP in the UK Air Defence Region (Volumes 1–3) (archive.org index)",
    "url": "https://archive.org/details/condign-vol-2-1-258",
  },
  {
    "title": "Knuth et al. The New Science of UAP (arXiv record)",
    "url": "https://arxiv.org/abs/2502.06794",
  },
  {
    "title": "Schulze-Makuch & Reichhardt (2025) Reliability Scale for UAP (MDPI)",
    "url": "https://www.mdpi.com/2218-1997/11/10/326",
  },
  {
    "title": "Daghbouche (2025) Computational Complexity of UAP Reverse Engineering (arXiv PDF)",
    "url": "https://arxiv.org/pdf/2505.00051",
  },
]

os.makedirs(OUTDIR, exist_ok=True)
manifest = []

# Initialize enhanced fetcher
fetcher = RobustWebFetcher(cache_dir=os.path.join(OUTDIR, ".cache"), rate_limit_delay=2.0)

def fetch_doc(entry):
    """Fetch document using enhanced multi-tactic downloader"""
    url = entry["url"]
    print(f"\n{'='*70}")
    print(f"Fetching: {entry['title']}")
    print(f"URL: {url}")
    print(f"{'='*70}")

    # Determine file extension from URL
    is_pdf = url.lower().endswith(".pdf") or "/pdf/" in url.lower()
    preferred_ext = ".pdf" if is_pdf else ".html"
    filename = filename_from_url(url, preferred_ext=preferred_ext)
    output_path = os.path.join(OUTDIR, filename)

    # Use robust fetcher with all tactics enabled
    result = fetcher.fetch(
        url=url,
        output_path=output_path,
        try_mirrors=True,  # Enable first-party mirror rotation
        try_wayback=True,  # Enable Wayback fallback
        timeout=90
    )

    # Handle download result
    if result.status in (DownloadStatus.SUCCESS, DownloadStatus.WAYBACK_SUCCESS):
        print(f"✓ Download successful: {result.local_path}")
        print(f"  Content-Type: {result.content_type}")
        print(f"  Attempts: {len(result.attempted_urls)}")

        # Convert HTML to PDF if requested
        if CONVERT_HTML and result.local_path.endswith(".html"):
            pdf_path = result.local_path.replace(".html", ".pdf")
            print(f"  Converting HTML → PDF...")
            if fetcher.html_to_pdf(result.local_path, pdf_path):
                print(f"  ✓ Converted to PDF: {pdf_path}")
                return pdf_path, result.content_type, result.wayback_url
            else:
                print(f"  ⚠ HTML→PDF conversion skipped (no engine available)")

        return result.local_path, result.content_type, result.wayback_url

    # Download failed - return None with wayback reference
    print(f"✗ Download failed after {len(result.attempted_urls)} attempts")
    print(f"  Status: {result.status.value}")
    if result.error_msg:
        print(f"  Error: {result.error_msg}")
    if result.wayback_url:
        print(f"  Wayback URL: {result.wayback_url}")

    return None, None, result.wayback_url

for e in DOCS:
    path, mtype, wayback = fetch_doc(e)

    if not path:
        # Download failed - record with wayback reference
        manifest.append({
            "title": e["title"],
            "source_url": e["url"],
            "local_path": None,
            "status": "FAILED_DOWNLOAD",
            "wayback": wayback or f"https://web.archive.org/web/*/{e['url']}",
            "type": "unknown",
            "tags": ["UAP", "debunk", "constraints", "failed"]
        })
        continue

    # Download successful
    entry = {
        "title": e["title"],
        "source_url": e["url"],
        "local_path": path,
        "status": "OK",
        "type": "pdf" if path.lower().endswith(".pdf") else "html",
        "content_type": mtype,
        "tags": ["UAP", "debunk", "constraints"]
    }

    # Add wayback reference if retrieved from archive
    if wayback and "web.archive.org" in wayback:
        entry["wayback_source"] = wayback
        entry["tags"].append("wayback_retrieved")

    manifest.append(entry)

# Write manifest for Sherlock ingestion
manifest_path = os.path.join(OUTDIR, "manifest.json")
with open(manifest_path, "w") as f:
    json.dump(manifest, f, indent=2)

# Summary report
success_count = len([m for m in manifest if m['status'] == 'OK'])
failed_count = len([m for m in manifest if m['status'] == 'FAILED_DOWNLOAD'])
wayback_count = len([m for m in manifest if 'wayback_retrieved' in m.get('tags', [])])

print(f"\n{'='*70}")
print(f"DOWNLOAD SUMMARY")
print(f"{'='*70}")
print(f"✓ Successful: {success_count}/{len(DOCS)}")
print(f"✗ Failed: {failed_count}/{len(DOCS)}")
print(f"📚 Retrieved from Wayback: {wayback_count}")
print(f"\nManifest: {manifest_path}")
print(f"Output directory: {OUTDIR}")
print(f"{'='*70}")

# List failed downloads for manual review
if failed_count > 0:
    print(f"\nFAILED DOWNLOADS (manual retrieval required):")
    for m in manifest:
        if m['status'] == 'FAILED_DOWNLOAD':
            print(f"\n  Title: {m['title']}")
            print(f"  Original: {m['source_url']}")
            print(f"  Wayback: {m['wayback']}")
