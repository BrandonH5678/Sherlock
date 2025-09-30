#!/bin/bash
# Monitor the high-resolution voice embedding analysis
# Run with: ./monitor_analysis.sh

echo "=== Sherlock Analysis Monitor ==="
echo "Started: $(date)"
echo

while true; do
    # Check if the process is still running
    if pgrep -f "diarize_embed.py" > /dev/null; then
        echo "[$(date '+%H:%M:%S')] Process running - Memory: $(ps -o pid,pcpu,pmem,cmd -C python3 | grep diarize_embed | awk '{print $3"%"}')"

        # Show current log output
        if [[ -f diarize_embed.log ]]; then
            tail -n 5 diarize_embed.log | sed 's/^/  LOG: /'
        fi

        # Check if output file exists and show size
        if [[ -f bench/diarize_embed_full.json ]]; then
            size=$(stat -c%s bench/diarize_embed_full.json 2>/dev/null || echo "0")
            echo "  OUTPUT: bench/diarize_embed_full.json (${size} bytes)"
        fi

    else
        echo "[$(date '+%H:%M:%S')] ✅ ANALYSIS COMPLETE!"

        if [[ -f bench/diarize_embed_full.json ]]; then
            size=$(stat -c%s bench/diarize_embed_full.json)
            echo "✅ Output: bench/diarize_embed_full.json (${size} bytes)"
        else
            echo "❌ No output file found - check diarize_embed.log for errors"
        fi

        echo "Final log:"
        tail -n 10 diarize_embed.log 2>/dev/null | sed 's/^/  /'
        break
    fi

    echo "---"
    sleep 300  # Check every 5 minutes
done

echo "Monitor finished: $(date)"