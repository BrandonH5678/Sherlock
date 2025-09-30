#!/bin/bash
# Keep system awake during processing - Linux version

echo "🛡️ Keeping system awake for Operation Gladio processing..."

# Method 1: Use systemd-inhibit if available
if command -v systemd-inhibit >/dev/null 2>&1; then
    echo "Using systemd-inhibit to prevent sleep..."
    systemd-inhibit --what=sleep:idle --who="Operation Gladio" --why="Processing audiobook" sleep infinity &
    INHIBIT_PID=$!
    echo "Sleep inhibitor started with PID: $INHIBIT_PID"
fi

# Method 2: Keep CPU active with lightweight tasks
echo "Starting CPU keep-alive..."
while pgrep -f "direct_aaxc_processor" > /dev/null; do
    # Light CPU activity every 5 minutes
    sleep 300
    echo "$(date): Keeping system active..." >> /tmp/keepalive.log
done

# Clean up
if [ ! -z "$INHIBIT_PID" ]; then
    kill $INHIBIT_PID 2>/dev/null
fi

echo "✅ Processing complete - sleep prevention ended"