#!/bin/bash
# Robust Web Fetcher - Quick Setup Script
# For deploying to J5A and Squirt systems

set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║       Robust Web Fetcher - Installation & Test Script          ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

SHERLOCK_DIR="/home/johnny5/Sherlock"

# Check Python version
echo "[1/6] Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found"
    exit 1
fi
echo "✓ Python OK"
echo ""

# Check dependencies
echo "[2/6] Checking required dependencies..."
python3 -c "import requests" 2>/dev/null && echo "✓ requests library installed" || echo "⚠ Install: pip install requests"
which curl >/dev/null 2>&1 && echo "✓ curl available" || echo "⚠ curl not found (optional)"
which wget >/dev/null 2>&1 && echo "✓ wget available" || echo "⚠ wget not found (optional)"
which wkhtmltopdf >/dev/null 2>&1 && echo "✓ wkhtmltopdf available" || echo "⚠ Install: sudo apt install wkhtmltopdf (for HTML→PDF)"
echo ""

# Verify core files exist
echo "[3/6] Verifying core files..."
if [ -f "$SHERLOCK_DIR/robust_web_fetcher.py" ]; then
    echo "✓ robust_web_fetcher.py found ($(wc -l < "$SHERLOCK_DIR/robust_web_fetcher.py") lines)"
else
    echo "❌ robust_web_fetcher.py not found"
    exit 1
fi

if [ -f "$SHERLOCK_DIR/uap_reading_list_fetcher/fetch_uap_reading_list.py" ]; then
    echo "✓ fetch_uap_reading_list.py found ($(wc -l < "$SHERLOCK_DIR/uap_reading_list_fetcher/fetch_uap_reading_list.py") lines)"
else
    echo "❌ fetch_uap_reading_list.py not found"
    exit 1
fi
echo ""

# Run basic syntax check
echo "[4/6] Running Python syntax check..."
python3 -m py_compile "$SHERLOCK_DIR/robust_web_fetcher.py"
if [ $? -eq 0 ]; then
    echo "✓ Syntax check passed"
else
    echo "❌ Syntax errors found"
    exit 1
fi
echo ""

# Quick import test
echo "[5/6] Testing imports..."
python3 << 'PYTEST'
import sys
sys.path.insert(0, '/home/johnny5/Sherlock')

try:
    from robust_web_fetcher import RobustWebFetcher, DownloadStatus, filename_from_url
    print("✓ All imports successful")
    
    # Test instantiation
    fetcher = RobustWebFetcher()
    print("✓ RobustWebFetcher instantiated")
    
    # Test filename generation
    fn = filename_from_url("https://example.gov/report.pdf")
    print(f"✓ filename_from_url() working: {fn}")
    
except Exception as e:
    print(f"❌ Import test failed: {e}")
    sys.exit(1)
PYTEST

if [ $? -ne 0 ]; then
    echo "❌ Import test failed"
    exit 1
fi
echo ""

# Summary and next steps
echo "[6/6] Installation Summary"
echo "══════════════════════════════════════════════════════════════════"
echo "✅ Core library: $SHERLOCK_DIR/robust_web_fetcher.py"
echo "✅ Enhanced fetcher: $SHERLOCK_DIR/uap_reading_list_fetcher/fetch_uap_reading_list.py"
echo "✅ Documentation:"
echo "   - Integration: ROBUST_WEB_FETCHER_INTEGRATION.md"
echo "   - Quick Ref: ROBUST_WEB_FETCHER_QUICK_REF.md"
echo "   - Summary: ROBUST_WEB_FETCHER_SUMMARY.md"
echo "✅ Demo: examples/web_fetcher_tactics_demo.py"
echo ""
echo "📋 NEXT STEPS:"
echo ""
echo "1. Test the enhanced UAP fetcher:"
echo "   cd $SHERLOCK_DIR/uap_reading_list_fetcher"
echo "   OUTDIR=\"test_output\" python3 fetch_uap_reading_list.py"
echo ""
echo "2. Run interactive demo:"
echo "   cd $SHERLOCK_DIR/examples"
echo "   python3 web_fetcher_tactics_demo.py"
echo ""
echo "3. Deploy to J5A (when ready):"
echo "   cp $SHERLOCK_DIR/robust_web_fetcher.py /path/to/j5a/"
echo ""
echo "4. Deploy to Squirt (when ready):"
echo "   cp $SHERLOCK_DIR/robust_web_fetcher.py /path/to/squirt/"
echo ""
echo "══════════════════════════════════════════════════════════════════"
echo "✅ Setup complete! Ready for production use."
echo "══════════════════════════════════════════════════════════════════"
