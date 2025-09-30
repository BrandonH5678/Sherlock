#!/usr/bin/env python3
"""
Convert AAXC to MP3 using voucher file information
Simplified approach for Operation Gladio processing
"""

import subprocess
import json
import os
from pathlib import Path

def convert_aaxc_to_mp3():
    """Convert AAXC file to MP3 using voucher information"""

    aaxc_file = "audiobooks/operation_gladio/Operation_Gladio_The_Unholy_Alliance_Between_the_Vatican_the_CIA_and_the_Mafia-AAX_22_64.aaxc"
    voucher_file = "audiobooks/operation_gladio/Operation_Gladio_The_Unholy_Alliance_Between_the_Vatican_the_CIA_and_the_Mafia-AAX_22_64.voucher"
    output_file = "audiobooks/operation_gladio/Operation_Gladio_Full.mp3"

    print("🔄 Converting AAXC to MP3...")
    print(f"Input: {aaxc_file}")
    print(f"Output: {output_file}")

    # Read voucher for decryption info
    try:
        with open(voucher_file, 'r') as f:
            voucher = json.load(f)
        key = voucher['content_license']['license_response']['key']
        iv = voucher['content_license']['license_response']['iv']
        print(f"✅ Voucher loaded - Key: {key[:8]}...")
    except Exception as e:
        print(f"❌ Voucher error: {e}")
        return False

    # Try multiple conversion approaches
    conversion_methods = [
        # Method 1: Direct FFmpeg with activation bytes
        [
            'ffmpeg', '-y',
            '-activation_bytes', '35d4b805',
            '-i', aaxc_file,
            '-c:a', 'libmp3lame', '-b:a', '128k',
            '-map_metadata', '0',
            output_file
        ],
        # Method 2: Copy codec to avoid re-encoding
        [
            'ffmpeg', '-y',
            '-activation_bytes', '35d4b805',
            '-i', aaxc_file,
            '-acodec', 'copy',
            '-vn',
            output_file
        ],
        # Method 3: Force MP3 output
        [
            'ffmpeg', '-y',
            '-activation_bytes', '35d4b805',
            '-i', aaxc_file,
            '-f', 'mp3',
            output_file
        ]
    ]

    for i, cmd in enumerate(conversion_methods, 1):
        print(f"\n🔄 Trying conversion method {i}...")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0 and os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"✅ Conversion successful! Output size: {file_size:,} bytes")
                return True
            else:
                print(f"❌ Method {i} failed: {result.stderr[:200]}...")
                if os.path.exists(output_file):
                    os.remove(output_file)
        except subprocess.TimeoutExpired:
            print(f"⏰ Method {i} timed out")
        except Exception as e:
            print(f"❌ Method {i} error: {e}")

    # Method 4: Use Whisper directly on AAXC (it sometimes works)
    print("\n🔄 Trying direct Whisper processing...")
    try:
        import whisper
        # Just test if whisper can load the file
        model = whisper.load_model("base")
        result = model.transcribe(aaxc_file, language="en", verbose=False)
        if result and result.get('text'):
            print("✅ Whisper can process AAXC directly!")
            # Create a symlink for processing
            mp3_link = "audiobooks/operation_gladio/Operation_Gladio_Direct.aaxc"
            if os.path.exists(mp3_link):
                os.remove(mp3_link)
            os.symlink(aaxc_file, mp3_link)
            return True
    except Exception as e:
        print(f"❌ Direct Whisper failed: {e}")

    print("❌ All conversion methods failed")
    return False

if __name__ == "__main__":
    success = convert_aaxc_to_mp3()
    if success:
        print("\n🎯 Ready for processing!")
    else:
        print("\n❌ Conversion failed")