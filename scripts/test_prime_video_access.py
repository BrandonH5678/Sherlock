#!/usr/bin/env python3
"""
Test Amazon Prime Video Access
Verifies that Prime Video can be accessed and captures browser profile for automation

Usage: python3 test_prime_video_access.py [--url URL]
"""

import sys
import os
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
import time

def find_firefox_profile():
    """Find the default Firefox profile directory"""
    # Check for snap Firefox first (common on Ubuntu)
    snap_firefox = Path.home() / "snap" / "firefox" / "common" / ".mozilla" / "firefox"
    if snap_firefox.exists():
        firefox_dir = snap_firefox
    else:
        # Fall back to standard location
        firefox_dir = Path.home() / ".mozilla" / "firefox"
        if not firefox_dir.exists():
            return None

    # Look for profiles.ini
    profiles_ini = firefox_dir / "profiles.ini"
    if not profiles_ini.exists():
        return None

    # Parse profiles.ini to find default profile
    with open(profiles_ini) as f:
        lines = f.readlines()

    current_profile_path = None
    is_default = False

    for line in lines:
        line = line.strip()
        if line.startswith("Path="):
            current_profile_path = line.split("=", 1)[1]
        elif line.startswith("Default=1"):
            is_default = True
            if current_profile_path:
                break

    if current_profile_path:
        if "/" in current_profile_path or "\\" in current_profile_path:
            return Path(current_profile_path)
        else:
            return firefox_dir / current_profile_path

    return None

def test_prime_video_access(url: str = None):
    """
    Test Prime Video access and capture session

    Args:
        url: Optional Prime Video URL to test
    """
    print("=" * 80)
    print("PRIME VIDEO ACCESS TEST")
    print("=" * 80)
    print()

    # Find Firefox profile
    profile_path = find_firefox_profile()

    if profile_path and profile_path.exists():
        print(f"✅ Found Firefox profile: {profile_path}")
    else:
        print("⚠️  No Firefox profile found")
        print("   Please open Firefox manually first to create a profile")
        print("   Command: DISPLAY=:0 firefox")
        return False

    print()
    print("Launching Firefox with automation...")
    print("(This will open a browser window on the server)")
    print()

    # Set display
    os.environ["DISPLAY"] = ":0"

    try:
        with sync_playwright() as p:
            # Launch Firefox with existing profile
            print("Starting browser...")
            browser = p.firefox.launch(
                headless=False,  # Show browser window
                args=[f"--profile", str(profile_path)]
            )

            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/145.0"
            )

            page = context.new_page()

            # Navigate to Prime Video or provided URL
            test_url = url if url else "https://www.amazon.com/Prime-Video/b?ie=UTF8&node=2676882011"

            print(f"Navigating to: {test_url}")
            page.goto(test_url, wait_until="networkidle", timeout=30000)

            # Wait for page to load
            time.sleep(3)

            # Check if we're logged in
            page_content = page.content().lower()

            if "sign in" in page_content or "sign-in" in page_content:
                print()
                print("=" * 80)
                print("⚠️  NOT LOGGED IN")
                print("=" * 80)
                print()
                print("Please:")
                print("1. Log into Amazon Prime Video in the browser window")
                print("2. Navigate to 'Age of Disclosure'")
                print("3. Copy the URL from the address bar")
                print("4. Press Enter here when ready...")
                print()
                input("Press Enter after logging in...")

                # Get current URL
                current_url = page.url
                print()
                print("Current URL:", current_url)

            else:
                print()
                print("=" * 80)
                print("✅ LOGGED IN TO PRIME VIDEO")
                print("=" * 80)
                print()

                if url:
                    print(f"Testing playback at: {url}")
                    print()
                    print("Please verify the video loads correctly in the browser window.")
                    print("Press Enter when ready to continue...")
                    input()

                    current_url = page.url
                else:
                    print("Please navigate to 'Age of Disclosure' in the browser")
                    print("Then copy the URL from the address bar")
                    print()
                    print("Press Enter when you're on the video page...")
                    input()

                    current_url = page.url
                    print()
                    print("Video URL:", current_url)

            # Save configuration
            config = {
                "firefox_profile": str(profile_path),
                "age_of_disclosure_url": current_url if "gp/video" in current_url else None,
                "verified_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "display": ":0"
            }

            config_file = Path("/home/johnny5/Sherlock/prime_video_config.json")
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)

            print()
            print("=" * 80)
            print("✅ CONFIGURATION SAVED")
            print("=" * 80)
            print()
            print(f"Config file: {config_file}")
            print(f"Firefox profile: {profile_path}")
            if config["age_of_disclosure_url"]:
                print(f"Video URL: {config['age_of_disclosure_url']}")
            print()

            print("Browser will close in 5 seconds...")
            time.sleep(5)

            browser.close()

            return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    url = None

    if len(sys.argv) > 2 and sys.argv[1] == "--url":
        url = sys.argv[2]

    success = test_prime_video_access(url)

    if success:
        print()
        print("✅ Prime Video access verified!")
        print()
        print("Next step: Run the automated documentary processor")
        sys.exit(0)
    else:
        print()
        print("❌ Prime Video access test failed")
        print()
        print("Please:")
        print("1. Make sure you're logged into the server GUI")
        print("2. Run: DISPLAY=:0 firefox")
        print("3. Enable DRM content in Firefox preferences")
        print("4. Log into Amazon Prime Video")
        print("5. Try this test again")
        sys.exit(1)

if __name__ == "__main__":
    main()
