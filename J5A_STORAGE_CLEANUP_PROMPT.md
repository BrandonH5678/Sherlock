# J5A Task: /home Partition Storage Cleanup

## Problem
The `/home` partition is at 82% capacity (39GB used / 49GB total, 8.4GB free). Sherlock has 5 new intelligence campaigns queued (PKG-RESTRUCTURE, PKG-RUS, PKG-CHN, PKG-IRN, PKG-XFIN) that will generate ~40 research reports and roughly double the evidence database. While the new reports themselves are small (~3-5MB text), the partition needs headroom and the current usage includes large artifacts that may no longer be needed.

## What's Consuming Space in /home/johnny5/Sherlock/ (7.7GB total)

| Directory | Size | Description | Likely Action |
|-----------|------|-------------|---------------|
| `freelance_transcripts/` | **4.6GB** | Transcribed audio/text from freelance processing pipeline | Archive or delete if evidence has been extracted to `evidence/` |
| `downloads/` | **2.3GB** | Downloaded media files | Should have been caught by 48-hour auto-delete timer (`j5a-media-cleanup.timer`). Investigate why these persist. |
| `geo_env/` | 493MB | Python venv for geology processing | Delete if geology pipeline is inactive |
| `primevideo_env/` | 175MB | Python venv for Prime Video capture | Delete if Prime Video pipeline is inactive |
| `evidence/` | 25MB | Intelligence reports and structured data | **DO NOT TOUCH** — this is the permanent evidence store |
| `scripts/` | 740KB | Ingestion and processing scripts | **DO NOT TOUCH** |
| `nightshift_inbox/` | 312KB | 74 queued NightShift packages | Review — process or archive |

## Also Check Other /home Consumers
- Other projects under `/home/johnny5/` (Squirt, Prism, J5A itself)
- `~/.cache/` (pip, huggingface models, etc.)
- Any other large directories

## Recommended Actions

### Quick Wins (Operator Decision Required)
1. **`downloads/`** (2.3GB): Check if the media-cleanup timer is running (`systemctl status j5a-media-cleanup.timer`). If media has been here >48 hours, the timer may be broken. Fix timer and/or manually clean.
2. **`freelance_transcripts/`** (4.6GB): Check if all transcripts have been processed into evidence claims. If so, archive to external storage or `/home/johnny5/Sherlock/archives/` (excluded from cleanup) or delete.
3. **`geo_env/` + `primevideo_env/`** (668MB): Check if these venvs are actively used. If not, delete — they can be recreated from requirements files.

### Structural Options (If Quick Wins Aren't Enough)
4. **Expand the partition**: If the NVMe has unallocated space or another partition can be resized.
5. **Move large artifacts to `/var/lib/johnny5/`**: If that mount has more space.
6. **Set up automated archiving**: Move processed transcripts to cold storage after evidence extraction.

## Target
Get `/home` below 70% utilization (~34GB used) to provide comfortable headroom for the 5 new campaigns. That means freeing ~5GB minimum, ideally ~7-8GB.

## Context
- Sherlock DB: 1,021 claims, 439 cross-references, 140 targets across completed campaigns (PKG-EP, PKG-911, PKG-MK) and 5 new campaigns in setup
- The 48-hour media retention policy is documented in Sherlock's CLAUDE.md
- Cleanup script: `/var/lib/johnny5/scripts/media-cleanup.sh`
- Cleanup timer: `j5a-media-cleanup.timer` (runs every 6 hours)
- Archives directory (excluded from cleanup): `/home/johnny5/Sherlock/archives/`
