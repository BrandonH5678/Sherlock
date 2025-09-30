#!/bin/bash
# Keep system awake during Gladio processing
echo "🛡️ Keeping system awake for Operation Gladio processing..."
echo "This will prevent sleep until processing completes."

# Use caffeinate to prevent sleep
caffeinate -d -i -m -s -w $(pgrep -f "autonomous_gladio_processing")

echo "✅ Processing complete - sleep prevention ended"