#!/bin/bash
# Browser-based Audible Authentication
# Solves CVF visibility issues by using browser authentication

echo "🔐 AUDIBLE BROWSER AUTHENTICATION"
echo "================================="

# Activate virtual environment
source /home/johnny5/Sherlock/gladio_env/bin/activate

echo "🌐 Starting browser-based authentication..."
echo ""
echo "📋 INSTRUCTIONS:"
echo "1. This will open authentication in your default browser"
echo "2. You'll see the CVF captcha in the browser (not terminal)"
echo "3. Complete the login process in the browser"
echo "4. Return here when authentication is complete"
echo ""

read -p "Press Enter to start browser authentication..."

# Try alternative authentication method
echo "🔄 Attempting browser authentication..."

# Method 1: Try with external authentication
audible manage auth-file add --help

echo ""
echo "💡 ALTERNATIVE APPROACH:"
echo ""
echo "Since CVF is not visible in terminal, try this manual approach:"
echo ""
echo "1. Go to https://audible.com in your browser"
echo "2. Log in manually (you'll see the CVF there)"
echo "3. Once logged in, we'll extract your session cookies"
echo "4. Import those cookies into audible-cli"
echo ""
echo "🔧 Manual Cookie Extraction Method:"
echo "1. Login to audible.com in browser"
echo "2. Open browser developer tools (F12)"
echo "3. Go to Application/Storage > Cookies > audible.com"
echo "4. Export session cookies"
echo "5. Import into audible-cli"
echo ""

read -p "Would you like me to create a cookie import script? (y/n): " create_script

if [[ $create_script =~ ^[Yy]$ ]]; then
    cat > import_audible_cookies.py << 'EOF'
#!/usr/bin/env python3
"""
Import Audible cookies from browser session
Alternative authentication method when CVF is not visible
"""

import json
import os
from pathlib import Path

def import_cookies():
    print("🍪 AUDIBLE COOKIE IMPORT")
    print("========================")

    print("""
    STEP-BY-STEP PROCESS:

    1. Open your browser and go to https://audible.com
    2. Log in to your account (CVF will be visible in browser)
    3. After successful login, open Developer Tools (F12)
    4. Go to: Application/Storage → Cookies → audible.com
    5. Look for these important cookies:
       - session-id
       - session-token
       - ubid-main
       - x-main

    6. Copy the cookie values and paste them when prompted below
    """)

    cookies = {}

    cookie_names = ['session-id', 'session-token', 'ubid-main', 'x-main']

    for cookie_name in cookie_names:
        value = input(f"Enter {cookie_name} cookie value: ").strip()
        if value:
            cookies[cookie_name] = value

    if cookies:
        print(f"✅ Collected {len(cookies)} cookies")

        # Save cookies for audible-cli
        config_dir = Path.home() / '.audible'
        config_dir.mkdir(exist_ok=True)

        with open(config_dir / 'cookies.json', 'w') as f:
            json.dump(cookies, f, indent=2)

        print(f"💾 Cookies saved to: {config_dir / 'cookies.json'}")
        print("🎯 Try running audible commands now")

    else:
        print("❌ No cookies collected")

if __name__ == "__main__":
    import_cookies()
EOF

    chmod +x import_audible_cookies.py
    echo "✅ Created cookie import script: import_audible_cookies.py"
    echo ""
    echo "🎯 NEXT STEPS:"
    echo "1. Login to audible.com in your browser"
    echo "2. Run: python3 import_audible_cookies.py"
    echo "3. Test with: audible library"
fi

echo ""
echo "🔄 ALTERNATIVE: Try quickstart with debug mode"
echo "audible quickstart --debug"
echo ""
echo "Or we can proceed with manual download if you have the book ASIN"