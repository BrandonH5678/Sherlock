#!/bin/bash
# External Browser Authentication for Audible
echo "🌐 AUDIBLE EXTERNAL BROWSER AUTHENTICATION"
echo "=========================================="
echo ""
echo "This will solve the CVF visibility issue by using your web browser."
echo ""

# Activate environment
source /home/johnny5/Sherlock/gladio_env/bin/activate

echo "📝 Please provide your Audible login details:"
echo ""
read -p "Enter your Audible username/email: " AUDIBLE_USERNAME
echo ""

echo "🔄 Starting external browser authentication..."
echo "This will open a browser window where you can complete the login with CVF visibility."
echo ""

# Use external login with provided username
audible manage auth-file add \
    --external-login \
    --country-code us \
    --auth-file gladio_auth \
    --audible-username "$AUDIBLE_USERNAME"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Authentication successful!"
    echo ""
    echo "🧪 Testing authentication..."
    audible library | head -5

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Library access confirmed!"
        echo ""
        echo "🚀 Ready to download Operation Gladio!"
        echo "Next command: ./download_gladio_venv.sh"
    else
        echo "⚠️  Authentication succeeded but library access failed"
        echo "Try: audible activation"
    fi
else
    echo ""
    echo "❌ Authentication failed"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "1. Make sure you completed the browser login"
    echo "2. Check your internet connection"
    echo "3. Verify your Audible account credentials"
    echo ""
    echo "💡 Alternative: Use the cookie import method"
    echo "Run: ./audible_browser_auth.sh"
fi