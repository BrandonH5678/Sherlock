#!/bin/bash
# Autonomous Operation Gladio Processing Script
# Runs unattended for the full day while you're away

LOG_FILE="/home/johnny5/Sherlock/gladio_processing.log"
RESULT_FILE="/home/johnny5/Sherlock/gladio_results.txt"

echo "🚀 AUTONOMOUS OPERATION GLADIO PROCESSING STARTED" | tee -a "$LOG_FILE"
echo "Start Time: $(date)" | tee -a "$LOG_FILE"
echo "=================================================" | tee -a "$LOG_FILE"

# Function to log with timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Activate virtual environment
log_message "🔄 Activating virtual environment..."
source /home/johnny5/Sherlock/gladio_env/bin/activate

# Install CPU-only PyTorch for compatibility
log_message "🔧 Installing CPU-optimized dependencies..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu >> "$LOG_FILE" 2>&1

# Test dependencies
log_message "🧪 Testing dependencies..."
python3 -c "
import whisper
import faster_whisper
import torch
print('✅ All dependencies working')
" >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    log_message "✅ Dependencies verified successfully"
else
    log_message "❌ Dependency test failed, using fallback processing"
fi

# Start processing
log_message "🎯 Starting Operation Gladio audiobook processing..."
log_message "📁 Audio file: audiobooks/operation_gladio/Operation_Gladio_The_Unholy_Alliance_Between_the_Vatican_the_CIA_and_the_Mafia-AAX_22_64.aaxc"
log_message "⏱️  Expected duration: 2-4 hours"

# Process the audiobook
python3 batch_gladio_processor.py "audiobooks/operation_gladio/Operation_Gladio_The_Unholy_Alliance_Between_the_Vatican_the_CIA_and_the_Mafia-AAX_22_64.aaxc" >> "$LOG_FILE" 2>&1

# Check results
if [ $? -eq 0 ]; then
    log_message "✅ Processing completed successfully!"

    # Generate summary report
    log_message "📊 Generating summary report..."
    python3 -c "
import sqlite3
import json
from pathlib import Path

# Check if database was created
db_path = 'gladio_intelligence.db'
if Path(db_path).exists():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Count entities
    cursor.execute('SELECT COUNT(*) FROM people')
    people_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM organizations')
    org_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM relationships')
    relationship_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM resource_flows')
    flow_count = cursor.fetchone()[0]

    summary = f'''
🎯 OPERATION GLADIO INTELLIGENCE EXTRACTION COMPLETE
===============================================

📊 EXTRACTED ENTITIES:
• People: {people_count:,} individuals
• Organizations: {org_count:,} entities
• Relationships: {relationship_count:,} connections
• Resource Flows: {flow_count:,} transactions

📁 DATABASE: {db_path}
⏰ Completion Time: $(date)

🔍 READY FOR ANALYSIS:
• Search any person, organization, or event
• Query relationships and connections
• Analyze resource flows and timelines
• Export data for further research

✅ MISSION ACCOMPLISHED
'''

    print(summary)
    conn.close()
else:
    print('❌ Database not found - processing may have failed')
" | tee -a "$RESULT_FILE"

else
    log_message "❌ Processing failed - check logs for details"
    echo "❌ Processing failed - check $LOG_FILE for details" > "$RESULT_FILE"
fi

# Final status
log_message "🏁 Autonomous processing session completed"
log_message "End Time: $(date)"
log_message "================================================="

echo "
🎯 AUTONOMOUS PROCESSING STATUS
================================

📁 Processing Log: $LOG_FILE
📊 Results Summary: $RESULT_FILE
🗄️ Database: gladio_intelligence.db

Check these files for complete results when you return.
" | tee -a "$RESULT_FILE"