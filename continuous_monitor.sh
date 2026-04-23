#!/bin/bash
# Continuous monitoring of Sherlock transcription pipeline
# Runs in background, updates status every 5 minutes

LOG_FILE="/home/johnny5/Sherlock/processing_monitor.log"

echo "==================================================================" >> $LOG_FILE
echo "CONTINUOUS MONITORING STARTED: $(date)" >> $LOG_FILE
echo "==================================================================" >> $LOG_FILE

while true; do
    echo "" >> $LOG_FILE
    echo "[$(date)] Checking progress..." >> $LOG_FILE

    # Count completions
    completed=$(find /home/johnny5/Sherlock/freelance_transcripts -name "audio.json" 2>/dev/null | wc -l)
    downloaded=$(find /home/johnny5/Sherlock/freelance_transcripts -name "audio.mp3" 2>/dev/null | wc -l)
    active=$(ps aux | grep "process_sherlock_transcription.py" | grep -v grep | wc -l)

    echo "  Completed: $completed/50" >> $LOG_FILE
    echo "  Downloaded: $downloaded" >> $LOG_FILE
    echo "  Active Jobs: $active" >> $LOG_FILE

    # GPU status
    gpu_temp=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader)
    gpu_util=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader)
    echo "  GPU: ${gpu_temp}°C, ${gpu_util} utilization" >> $LOG_FILE

    # Check if all jobs completed
    if [ $active -eq 0 ]; then
        echo "" >> $LOG_FILE
        echo "[$(date)] ALL PROCESSING JOBS COMPLETED!" >> $LOG_FILE
        echo "  Final Count: $completed/50 transcriptions" >> $LOG_FILE
        echo "==================================================================" >> $LOG_FILE
        break
    fi

    # Wait 5 minutes before next check
    sleep 300
done

echo "Monitoring loop exited. See $LOG_FILE for full history."
