#!/bin/bash
# Monitor Sherlock transcription progress

echo "====================================================================="
echo "SHERLOCK TRANSCRIPTION PIPELINE - PROGRESS MONITOR"
echo "====================================================================="
echo ""

echo "📊 PROCESSING STATUS:"
echo ""

# Count total episodes
echo "Target Episodes: 50 (1 test + 49 production)"
echo ""

# Count completed transcriptions
completed=$(find /home/johnny5/Sherlock/freelance_transcripts -name "audio.json" 2>/dev/null | wc -l)
echo "✅ Completed Transcriptions: $completed"

# Count audio files downloaded
downloaded=$(find /home/johnny5/Sherlock/freelance_transcripts -name "audio.mp3" 2>/dev/null | wc -l)
echo "📥 Audio Files Downloaded: $downloaded"

# Check active processes
active=$(ps aux | grep "process_sherlock_transcription.py" | grep -v grep | wc -l)
echo "🔄 Active Processing Jobs: $active"

# GPU status
echo ""
echo "🎮 GPU STATUS:"
nvidia-smi --query-gpu=temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv,noheader

echo ""
echo "====================================================================="
echo "DIRECTORY STRUCTURE:"
echo "====================================================================="
find /home/johnny5/Sherlock/freelance_transcripts -type d | head -20

echo ""
echo "====================================================================="
echo "RECENT RESULTS FILES:"
echo "====================================================================="
ls -lht /home/johnny5/Sherlock/transcription_results_*.json 2>/dev/null | head -5

echo ""
echo "====================================================================="
