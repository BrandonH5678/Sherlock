---
description: Refresh Sherlock system context and display current operational status
---

Read and summarize the current Sherlock system status, including:

1. **System Overview** from CLAUDE.md
2. **Current Mission Status** and active capabilities
3. **Key Operational Constraints**:
   - Memory limits (3.7GB total, 2.4GB available)
   - Processing protocols (VoiceEngineManager, IntelligentModelSelector)
   - Media retention policy (48-hour auto-delete)
4. **Active Evidence Database Status**
5. **Integration Points** (Squirt, Johny5Alive, external AI)
6. **Recent Git Status** and uncommitted changes
7. **Active Campaign Status**: Check MEMORY.md for any `## ACTIVE CAMPAIGN` section. If present, read the referenced campaign status file (e.g. `PKG911_CAMPAIGN_STATUS.md`) and summarize: current phase, last completed action, next action, and DB state at last save. This step is mandatory — do not skip even if other context is available.

Provide a concise summary that reorients the operator to the current system state and any pending work.
