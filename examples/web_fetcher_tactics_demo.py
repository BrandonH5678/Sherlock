#!/usr/bin/env python3
"""
Robust Web Fetcher - Tactics Demonstration
Shows all download strategies with real-world examples
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from robust_web_fetcher import RobustWebFetcher, DownloadStatus, filename_from_url

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def demo_basic_download():
    """Tactic 1: Basic multi-engine download"""
    print("\n" + "="*70)
    print("TACTIC 1: Multi-Engine Download (requests → curl → wget)")
    print("="*70)

    fetcher = RobustWebFetcher()

    # Direct PDF download
    result = fetcher.fetch(
        url="https://www.dni.gov/files/ODNI/documents/assessments/Prelimary-Assessment-UAP-20210625.pdf",
        output_path="demo_output/odni_uap_2021.pdf",
        try_mirrors=False,  # Disable for this demo
        try_wayback=False
    )

    print(f"\nResult: {result.status.value}")
    print(f"Local path: {result.local_path}")
    print(f"Engines attempted: {len(result.attempted_urls)}")

def demo_mirror_rotation():
    """Tactic 2: First-party mirror rotation"""
    print("\n" + "="*70)
    print("TACTIC 2: First-Party Mirror Rotation")
    print("="*70)

    fetcher = RobustWebFetcher()

    # Try ODNI report with mirror fallback
    result = fetcher.fetch(
        url="https://www.dni.gov/files/ODNI/documents/assessments/Unclassified-2022-Annual-Report-UAP.pdf",
        output_path="demo_output/odni_uap_2022.pdf",
        try_mirrors=True,  # Enable mirror rotation
        try_wayback=False
    )

    print(f"\nResult: {result.status.value}")
    print(f"Attempted URLs:")
    for url in result.attempted_urls:
        print(f"  - {url}")

def demo_arxiv_handling():
    """Tactic 3: arXiv special handling (/abs/ → /pdf/)"""
    print("\n" + "="*70)
    print("TACTIC 3: arXiv Content Negotiation")
    print("="*70)

    fetcher = RobustWebFetcher()

    # arXiv abstract page (should auto-redirect to PDF)
    result = fetcher.fetch(
        url="https://arxiv.org/abs/2502.06794",
        output_path="demo_output/arxiv_uap_science.pdf",
        try_mirrors=True,
        try_wayback=False
    )

    print(f"\nResult: {result.status.value}")
    print(f"Final content type: {result.content_type}")

def demo_wayback_fallback():
    """Tactic 4: Wayback Machine fallback"""
    print("\n" + "="*70)
    print("TACTIC 4: Wayback Machine Fallback")
    print("="*70)

    fetcher = RobustWebFetcher()

    # Intentionally use a URL that might be unavailable
    result = fetcher.fetch(
        url="https://example-gov-site.gov/old-report-2020.pdf",  # Hypothetical
        output_path="demo_output/wayback_test.pdf",
        try_mirrors=True,
        try_wayback=True  # Enable Wayback fallback
    )

    print(f"\nResult: {result.status.value}")
    if result.wayback_url:
        print(f"Wayback URL: {result.wayback_url}")
        print(f"Manual retrieval available at: {result.wayback_url}")

def demo_html_to_pdf():
    """Tactic 5: HTML → PDF conversion"""
    print("\n" + "="*70)
    print("TACTIC 5: HTML → PDF Conversion")
    print("="*70)

    fetcher = RobustWebFetcher()

    # Download HTML page
    result = fetcher.fetch(
        url="https://www.dni.gov/index.php/newsroom/reports-publications/reports-publications-2024/4020-uap-2024",
        output_path="demo_output/uap_2024_page.html",
        try_mirrors=False,
        try_wayback=False
    )

    if result.status == DownloadStatus.SUCCESS and result.local_path.endswith(".html"):
        print(f"\n✓ Downloaded HTML: {result.local_path}")

        # Convert to PDF
        pdf_path = result.local_path.replace(".html", ".pdf")
        print(f"\nAttempting HTML → PDF conversion...")

        if fetcher.html_to_pdf(result.local_path, pdf_path, engine="auto"):
            print(f"✓ Converted to PDF: {pdf_path}")
        else:
            print(f"⚠ Conversion failed (install wkhtmltopdf, playwright, or weasyprint)")

def demo_rate_limiting():
    """Tactic 6: Rate limiting and ToS compliance"""
    print("\n" + "="*70)
    print("TACTIC 6: Rate Limiting & ToS Compliance")
    print("="*70)

    # Create fetcher with custom rate limit
    fetcher = RobustWebFetcher(rate_limit_delay=3.0)  # 3 second delay between requests

    urls = [
        "https://www.dni.gov/files/ODNI/documents/assessments/Prelimary-Assessment-UAP-20210625.pdf",
        "https://www.dni.gov/files/ODNI/documents/assessments/Unclassified-2022-Annual-Report-UAP.pdf",
    ]

    print(f"\nDownloading {len(urls)} files with 3s rate limit...")
    import time
    start = time.time()

    for i, url in enumerate(urls, 1):
        filename = filename_from_url(url)
        result = fetcher.fetch(
            url=url,
            output_path=f"demo_output/{filename}",
            try_mirrors=False,
            try_wayback=False
        )
        print(f"  [{i}/{len(urls)}] {result.status.value}")

    elapsed = time.time() - start
    print(f"\nTotal time: {elapsed:.1f}s (respects rate limits)")

def demo_comprehensive_strategy():
    """Full demonstration of all tactics combined"""
    print("\n" + "="*70)
    print("COMPREHENSIVE STRATEGY: All Tactics Combined")
    print("="*70)

    fetcher = RobustWebFetcher(rate_limit_delay=2.0)

    # Difficult URLs that might need multiple tactics
    test_cases = [
        {
            "title": "AARO Historical Record",
            "url": "https://media.defense.gov/2024/Mar/08/2003409233/-1/-1/0/DOPSR-CLEARED-508-COMPLIANT-HRRV1-08-MAR-2024-FINAL.PDF",
        },
        {
            "title": "NASA UAP Study",
            "url": "https://science.nasa.gov/wp-content/uploads/2023/09/uap-independent-study-team-final-report.pdf",
        },
        {
            "title": "arXiv UAP Paper",
            "url": "https://arxiv.org/abs/2502.06794",
        },
    ]

    for test in test_cases:
        print(f"\n{'─'*70}")
        print(f"Testing: {test['title']}")
        print(f"URL: {test['url']}")

        filename = filename_from_url(test['url'], preferred_ext=".pdf")
        result = fetcher.fetch(
            url=test['url'],
            output_path=f"demo_output/{filename}",
            try_mirrors=True,   # Try mirrors on failure
            try_wayback=True,   # Fall back to Wayback
            timeout=90
        )

        print(f"\nStatus: {result.status.value}")
        print(f"Attempts: {len(result.attempted_urls)}")
        if result.local_path:
            print(f"✓ Success: {result.local_path}")
        else:
            print(f"✗ Failed: {result.error_msg}")
            if result.wayback_url:
                print(f"  Manual fallback: {result.wayback_url}")

def print_banner():
    """Print demo banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║         ROBUST WEB FETCHER - TACTICS DEMONSTRATION              ║
    ║                                                                  ║
    ║  Enhanced download strategies for stubborn sites and 403s       ║
    ║  Shared library: Sherlock • J5A • Squirt                        ║
    ╚══════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """Run all demonstrations"""
    import os
    os.makedirs("demo_output", exist_ok=True)

    print_banner()

    demos = [
        ("Basic Multi-Engine", demo_basic_download),
        ("Mirror Rotation", demo_mirror_rotation),
        ("arXiv Handling", demo_arxiv_handling),
        ("Wayback Fallback", demo_wayback_fallback),
        ("HTML→PDF", demo_html_to_pdf),
        ("Rate Limiting", demo_rate_limiting),
        ("Comprehensive", demo_comprehensive_strategy),
    ]

    print("\nAvailable demonstrations:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print(f"  0. Run all demos")

    try:
        choice = input("\nSelect demo (0-7): ").strip()
        choice = int(choice)

        if choice == 0:
            for name, demo_func in demos:
                demo_func()
        elif 1 <= choice <= len(demos):
            demos[choice - 1][1]()
        else:
            print("Invalid choice")

    except KeyboardInterrupt:
        print("\n\nDemo cancelled")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*70)
    print("Demo complete. Check demo_output/ for downloaded files.")
    print("="*70)

if __name__ == "__main__":
    main()
