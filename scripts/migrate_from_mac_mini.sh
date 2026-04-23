#!/bin/bash
# Mac Mini → J5A Server Migration Script
# Transfers critical Sherlock assets using rsync with phased approach
#
# Usage: ./migrate_from_mac_mini.sh [phase]
#   phase: all, 1, 2, 3, or verify

set -euo pipefail

# Configuration
MAC_MINI_HOST="johnny5-macmini"  # Tailscale hostname
J5A_SHERLOCK="/home/johnny5/Sherlock"
LOG_FILE="$J5A_SHERLOCK/migration_$(date +%Y%m%d_%H%M%S).log"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $*" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $*" | tee -a "$LOG_FILE"
}

# Banner
echo "========================================================================================================="
echo "                       MAC MINI → J5A SERVER MIGRATION"
echo "========================================================================================================="
echo ""
log "Starting Mac Mini → J5A Server migration"
log "Mac Mini host: $MAC_MINI_HOST"
log "J5A Sherlock: $J5A_SHERLOCK"
log "Log file: $LOG_FILE"
echo ""

# Phase 1: Critical Evidence (Transcripts, Diarization, Databases)
migrate_phase1() {
    log "========== PHASE 1: Migrating critical evidence =========="
    log "This phase transfers: transcripts, diarization outputs, databases"
    log "Estimated time: 5-30 minutes"
    echo ""

    # Create target directories
    mkdir -p "$J5A_SHERLOCK/nightshift_processing"

    # Migrate nightshift_processing (transcripts, diarization)
    log "Migrating nightshift_processing directory (transcripts, JSON, logs)..."
    rsync -avz --progress --partial --append-verify \
        --include="*/" \
        --include="*.txt" \
        --include="*.json" \
        --include="*.log" \
        --include="*.srt" \
        --include="*.vtt" \
        --include="*.tsv" \
        --exclude="*.mp3" \
        --exclude="*.m4a" \
        --exclude="*.wav" \
        "${MAC_MINI_HOST}:~/Sherlock/nightshift_processing/" \
        "$J5A_SHERLOCK/nightshift_processing/" \
        2>&1 | tee -a "$LOG_FILE" || {
            log_warning "nightshift_processing directory may not exist on Mac Mini"
        }

    # Migrate database files
    log "Migrating database files..."
    rsync -avz --progress --partial --append-verify \
        "${MAC_MINI_HOST}:~/Sherlock/*.db" \
        "$J5A_SHERLOCK/" \
        2>&1 | tee -a "$LOG_FILE" || {
            log_warning "Some database files may not exist on Mac Mini"
        }

    log "✅ Phase 1 complete: Critical evidence migrated"
    echo ""
}

# Phase 2: Raw Media (Large Files)
migrate_phase2() {
    log "========== PHASE 2: Migrating raw media =========="
    log "This phase transfers: MP3 files, audio chunks, video files"
    log "Estimated time: 4-6 hours (depends on data size)"
    log "This will run in background - safe to close terminal"
    echo ""

    # Create target directory
    mkdir -p "$J5A_SHERLOCK/nightshift_downloads"

    # Migrate nightshift_downloads (raw podcast/media files)
    log "Migrating nightshift_downloads directory (raw media)..."
    rsync -avz --progress --partial --append-verify \
        --include="*/" \
        --include="*.mp3" \
        --include="*.m4a" \
        --include="*.mp4" \
        --include="*.wav" \
        "${MAC_MINI_HOST}:~/Sherlock/nightshift_downloads/" \
        "$J5A_SHERLOCK/nightshift_downloads/" \
        2>&1 | tee -a "$LOG_FILE" || {
            log_warning "nightshift_downloads directory may not exist on Mac Mini"
        }

    # Also migrate any audio chunks in nightshift_processing
    log "Migrating audio chunks from nightshift_processing..."
    rsync -avz --progress --partial --append-verify \
        --include="*/" \
        --include="*.mp3" \
        --include="*.m4a" \
        --include="*.wav" \
        "${MAC_MINI_HOST}:~/Sherlock/nightshift_processing/" \
        "$J5A_SHERLOCK/nightshift_processing/" \
        2>&1 | tee -a "$LOG_FILE" || {
            log_warning "No audio chunks found or directory does not exist"
        }

    log "✅ Phase 2 complete: Raw media migrated"
    echo ""
}

# Phase 3: Complete Operation Gladio Audiobook
migrate_phase3() {
    log "========== PHASE 3: Migrating Operation Gladio audiobook =========="
    log "This phase transfers: Complete Operation Gladio processing outputs"
    log "Estimated time: 5-15 minutes"
    echo ""

    # Create target directory
    mkdir -p "$J5A_SHERLOCK/audiobooks/operation_gladio"

    # Migrate Operation Gladio complete directory
    log "Migrating Operation Gladio audiobook directory..."
    rsync -avz --progress --partial --append-verify \
        "${MAC_MINI_HOST}:~/Sherlock/audiobooks/operation_gladio/" \
        "$J5A_SHERLOCK/audiobooks/operation_gladio/" \
        2>&1 | tee -a "$LOG_FILE" || {
            log_warning "Operation Gladio directory may not exist on Mac Mini"
        }

    log "✅ Phase 3 complete: Operation Gladio migrated"
    echo ""
}

# Verification Phase
verify_migration() {
    log "========== VERIFICATION: Post-migration checks =========="
    echo ""

    # Verify nightshift_processing
    if [ -d "$J5A_SHERLOCK/nightshift_processing" ]; then
        TRANSCRIPT_COUNT=$(find "$J5A_SHERLOCK/nightshift_processing" -name "*.txt" -type f 2>/dev/null | wc -l)
        DIARIZATION_COUNT=$(find "$J5A_SHERLOCK/nightshift_processing" -name "*diarization*.json" -type f 2>/dev/null | wc -l)
        log "✅ nightshift_processing: $TRANSCRIPT_COUNT transcripts, $DIARIZATION_COUNT diarization files"
    else
        log_warning "nightshift_processing directory not created (may not exist on Mac Mini)"
    fi

    # Verify nightshift_downloads
    if [ -d "$J5A_SHERLOCK/nightshift_downloads" ]; then
        MEDIA_COUNT=$(find "$J5A_SHERLOCK/nightshift_downloads" -name "*.mp3" -type f 2>/dev/null | wc -l)
        log "✅ nightshift_downloads: $MEDIA_COUNT MP3 files"
    else
        log_warning "nightshift_downloads directory not created (may not exist on Mac Mini)"
    fi

    # Verify databases
    log "Checking database files..."
    for db in sherlock.db nightshift_queue.db speaker_database.db evidence.db phoenix_audit.db; do
        if [ -f "$J5A_SHERLOCK/$db" ]; then
            SIZE=$(du -h "$J5A_SHERLOCK/$db" 2>/dev/null | cut -f1)
            log "✅ Database migrated: $db ($SIZE)"
        else
            log_warning "Database not found: $db (may not exist on Mac Mini)"
        fi
    done

    # Verify Operation Gladio
    if [ -d "$J5A_SHERLOCK/audiobooks/operation_gladio" ]; then
        GLADIO_SIZE=$(du -sh "$J5A_SHERLOCK/audiobooks/operation_gladio" 2>/dev/null | cut -f1)
        log "✅ Operation Gladio: $GLADIO_SIZE"
    else
        log_warning "Operation Gladio directory not created (may not exist on Mac Mini)"
    fi

    # Calculate total migrated size
    TOTAL_SIZE=$(du -sh "$J5A_SHERLOCK" 2>/dev/null | cut -f1)
    log "Total Sherlock directory size: $TOTAL_SIZE"

    echo ""
    log "========================================================================================================="
    log "Migration verification complete!"
    log "Full migration log: $LOG_FILE"
    log "========================================================================================================="
}

# Main execution
PHASE="${1:-all}"

case "$PHASE" in
    all)
        log "Running full migration (all 3 phases + verification)"
        migrate_phase1
        migrate_phase2
        migrate_phase3
        verify_migration
        ;;
    1)
        log "Running Phase 1 only (critical evidence)"
        migrate_phase1
        verify_migration
        ;;
    2)
        log "Running Phase 2 only (raw media)"
        migrate_phase2
        verify_migration
        ;;
    3)
        log "Running Phase 3 only (Operation Gladio)"
        migrate_phase3
        verify_migration
        ;;
    verify)
        log "Running verification only"
        verify_migration
        ;;
    *)
        log_error "Invalid phase: $PHASE"
        echo ""
        echo "Usage: $0 [phase]"
        echo "  phase: all, 1, 2, 3, or verify"
        echo ""
        echo "Phase 1: Critical evidence (transcripts, diarization, databases) - 5-30 min"
        echo "Phase 2: Raw media (MP3 files, audio chunks) - 4-6 hours"
        echo "Phase 3: Operation Gladio audiobook - 5-15 min"
        echo "verify: Run verification checks only"
        echo ""
        exit 1
        ;;
esac

log "Migration script complete!"
