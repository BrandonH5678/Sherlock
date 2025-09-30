#!/bin/bash
# Install audible-cli in virtual environment for Operation Gladio processing

echo "🚀 Setting up audible-cli in virtual environment"
echo "================================================"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv gladio_env

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source gladio_env/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install audible-cli and dependencies
echo "📥 Installing audible-cli..."
pip install audible-cli

echo "📥 Installing audio processing dependencies..."
pip install pydub mutagen

# Test installation
echo "🧪 Testing installation..."
audible --version

if [ $? -eq 0 ]; then
    echo "✅ audible-cli installed successfully!"
    echo ""
    echo "🎯 NEXT STEPS:"
    echo "1. Activate environment: source gladio_env/bin/activate"
    echo "2. Authenticate: audible quickstart"
    echo "3. Download book: ./download_gladio_venv.sh"
    echo "4. Process: python3 batch_gladio_processor.py"
else
    echo "❌ Installation failed"
    exit 1
fi

# Create activation script
cat > activate_gladio.sh << 'EOF'
#!/bin/bash
# Activate Operation Gladio processing environment
echo "🔄 Activating Gladio processing environment..."
source /home/johnny5/Sherlock/gladio_env/bin/activate
echo "✅ Environment activated"
echo "Available commands:"
echo "  audible --help"
echo "  audible quickstart  (for first-time setup)"
echo "  audible library     (to see your books)"
EOF

chmod +x activate_gladio.sh

echo "📝 Created activation script: ./activate_gladio.sh"