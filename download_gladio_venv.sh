#!/bin/bash
# Operation Gladio Audiobook Download Script (Virtual Environment Version)
# Downloads and prepares audiobook for Sherlock processing

echo "🚀 Operation Gladio Audiobook Download (Virtual Environment)"
echo "============================================================="

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source /home/johnny5/Sherlock/gladio_env/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    echo "Run: ./install_audible_venv.sh first"
    exit 1
fi

echo "✅ Virtual environment activated"

# Check audible-cli is available
if ! command -v audible &> /dev/null; then
    echo "❌ audible-cli not found in virtual environment"
    echo "Run: ./install_audible_venv.sh"
    exit 1
fi

echo "🔍 Searching for Operation Gladio in library..."

# Search for the book (flexible search patterns)
BOOK_INFO=$(audible library | grep -i "gladio\|operation.*gladio" | head -1)

if [ -z "$BOOK_INFO" ]; then
    echo "❌ Operation Gladio not found in library"
    echo ""
    echo "📋 Troubleshooting:"
    echo "1. Verify book is purchased: https://audible.com/library"
    echo "2. Check authentication: audible activation"
    echo "3. View all books: audible library"
    echo "4. Search manually: audible library | grep -i gladio"
    echo ""
    echo "If the book has a different title, you can download manually:"
    echo "audible library  # Find the correct title/ASIN"
    echo "audible download <ASIN> --output-dir audiobooks/operation_gladio --decrypt"
    exit 1
fi

echo "✅ Found: $BOOK_INFO"

# Extract ASIN (first field in audible library output)
ASIN=$(echo "$BOOK_INFO" | awk '{print $1}')
echo "📖 Book ASIN: $ASIN"

# Create download directory
mkdir -p /home/johnny5/Sherlock/audiobooks/operation_gladio
cd /home/johnny5/Sherlock/audiobooks/operation_gladio

echo "⬇️  Downloading Operation Gladio..."
echo "   ASIN: $ASIN"
echo "   Output: $(pwd)"

# Download the audiobook with decryption
audible download "$ASIN" --output-dir . --decrypt

# Check if download was successful
if [ $? -eq 0 ]; then
    echo "✅ Download completed successfully"

    # List downloaded files
    echo ""
    echo "📁 Downloaded files:"
    ls -la *.mp3 *.m4a *.wav *.aax *.aaxc 2>/dev/null || echo "No audio files found"

    # Convert files to MP3 if needed (for consistency)
    echo ""
    echo "🔧 Preparing for Sherlock processing..."

    # Convert any .m4a files to .mp3
    for file in *.m4a; do
        if [ -f "$file" ]; then
            echo "🔄 Converting $file to MP3..."
            ffmpeg -i "$file" -codec:a libmp3lame -b:a 128k "${file%.m4a}.mp3" -y
            if [ $? -eq 0 ]; then
                echo "✅ Converted: ${file%.m4a}.mp3"
            fi
        fi
    done

    # Convert any .aax files (if decryption resulted in .aax instead of direct MP3)
    for file in *.aax; do
        if [ -f "$file" ]; then
            echo "🔄 Converting $file to MP3..."
            ffmpeg -i "$file" -codec:a libmp3lame -b:a 128k "${file%.aax}.mp3" -y
            if [ $? -eq 0 ]; then
                echo "✅ Converted: ${file%.aax}.mp3"
            fi
        fi
    done

    # Find the main audio file
    MAIN_FILE=$(ls -1 *.mp3 2>/dev/null | head -1)

    if [ -n "$MAIN_FILE" ]; then
        echo ""
        echo "🎯 Ready for Sherlock processing!"
        echo "📁 Audio file: $MAIN_FILE"
        echo "📊 File size: $(du -h "$MAIN_FILE" | cut -f1)"
        echo ""
        echo "🚀 Next step:"
        echo "   cd /home/johnny5/Sherlock"
        echo "   source gladio_env/bin/activate"
        echo "   python3 batch_gladio_processor.py \"audiobooks/operation_gladio/$MAIN_FILE\""
        echo ""
        echo "⏱️  Estimated processing time: 2-4 hours"
        echo "📊 Expected output: Complete Operation Gladio fact library"
    else
        echo "⚠️  No MP3 files found after conversion"
        echo "Check downloaded files manually"
    fi

else
    echo "❌ Download failed"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "1. Check authentication: audible activation"
    echo "2. Verify book ownership: audible library"
    echo "3. Check download quota: audible quota"
    echo "4. Verify ASIN: $ASIN"
    echo ""
    echo "For manual download:"
    echo "audible download $ASIN --output-dir . --decrypt"
    exit 1
fi

echo ""
echo "✅ Operation Gladio download process complete!"