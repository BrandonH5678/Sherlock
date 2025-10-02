# Sherlock: Local-First Deep Research System - Makefile
# Build automation for ingest, diarization, targets, packages, and analysis

SHELL := /bin/bash
PYTHON := python3
VENV := venv
ACTIVATE := source $(VENV)/bin/activate
DB := evidence.db

.PHONY: help
help:
	@echo "Sherlock Build Targets"
	@echo "======================"
	@echo ""
	@echo "Setup:"
	@echo "  make setup          - Create venv and install dependencies"
	@echo "  make install        - Install dependencies only"
	@echo "  make clean          - Remove venv and cached files"
	@echo ""
	@echo "Database:"
	@echo "  make db-init        - Initialize database schema"
	@echo "  make db-migrate     - Run database migrations"
	@echo "  make db-reset       - Reset database (DANGER: deletes all data)"
	@echo "  make db-stats       - Show database statistics"
	@echo ""
	@echo "Ingest:"
	@echo "  make yt URL=<url>   - Ingest YouTube video"
	@echo "  make yt-auto URL=<url> - Ingest YouTube with auto-diarization"
	@echo "  make media FILE=<path> - Ingest local media file"
	@echo "  make doc FILE=<path>   - Ingest PDF document"
	@echo ""
	@echo "Diarization:"
	@echo "  make diarize MEDIA=<media_id> - Run unsupervised diarization"
	@echo "  make diarize-supervised MEDIA=<media_id> ANCHORS=<anchors> - Run supervised diarization"
	@echo ""
	@echo "Targets & Packages:"
	@echo "  make target-add NAME=<name> TYPE=<type> PRIORITY=<1-5> - Add target"
	@echo "  make target-list    - List all targets"
	@echo "  make pkg-create TARGET=<target_id> - Create targeting package"
	@echo "  make pkg-validate PKG=<pkg_id> LEVEL=<0|1|2> - Validate package"
	@echo "  make pkg-submit PKG=<pkg_id> - Submit package to J5A"
	@echo "  make pkg-status PKG=<pkg_id> - Check package status"
	@echo "  make pkg-list       - List all packages"
	@echo ""
	@echo "Targeting Officer:"
	@echo "  make officer-run    - Run Targeting Officer once"
	@echo "  make officer-daemon - Run Targeting Officer daemon"
	@echo "  make officer-report - Generate daily report"
	@echo ""
	@echo "Query & Analysis:"
	@echo "  make search QUERY=<query> - Full-text search"
	@echo "  make query-speaker SPEAKER=<speaker_id> - Query by speaker"
	@echo "  make report OP=<operation> - Generate intelligence report"
	@echo "  make cross-ref OP1=<op1> OP2=<op2> - Cross-reference analysis"
	@echo ""
	@echo "Testing & Lint:"
	@echo "  make test           - Run all tests"
	@echo "  make lint           - Run ruff linter"
	@echo "  make format         - Format code with ruff"

# ============================================================================
# Setup
# ============================================================================

.PHONY: setup
setup: venv install db-init
	@echo "✅ Sherlock setup complete"

$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)

venv: $(VENV)/bin/activate

.PHONY: install
install: venv
	$(ACTIVATE) && pip install --upgrade pip
	$(ACTIVATE) && pip install -r requirements.txt

.PHONY: clean
clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# ============================================================================
# Database
# ============================================================================

.PHONY: db-init
db-init:
	$(ACTIVATE) && sherlock db init

.PHONY: db-migrate
db-migrate:
	$(ACTIVATE) && sherlock db migrate

.PHONY: db-reset
db-reset:
	@echo "⚠️  WARNING: This will delete all data in $(DB)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(ACTIVATE) && sherlock db reset --confirm; \
	fi

.PHONY: db-stats
db-stats:
	$(ACTIVATE) && sherlock db stats

# ============================================================================
# Ingest
# ============================================================================

.PHONY: yt
yt:
	@if [ -z "$(URL)" ]; then \
		echo "❌ Error: URL required. Usage: make yt URL=https://youtube.com/watch?v=..."; \
		exit 1; \
	fi
	$(ACTIVATE) && sherlock ingest youtube "$(URL)"

.PHONY: yt-auto
yt-auto:
	@if [ -z "$(URL)" ]; then \
		echo "❌ Error: URL required. Usage: make yt-auto URL=https://youtube.com/watch?v=..."; \
		exit 1; \
	fi
	$(ACTIVATE) && sherlock ingest youtube "$(URL)" --auto-diarize

.PHONY: media
media:
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Error: FILE required. Usage: make media FILE=/path/to/file.mp4"; \
		exit 1; \
	fi
	$(ACTIVATE) && sherlock ingest media "$(FILE)"

.PHONY: doc
doc:
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Error: FILE required. Usage: make doc FILE=/path/to/file.pdf"; \
		exit 1; \
	fi
	$(ACTIVATE) && sherlock ingest document "$(FILE)"

# ============================================================================
# Diarization
# ============================================================================

.PHONY: diarize
diarize:
	@if [ -z "$(MEDIA)" ]; then \
		echo "❌ Error: MEDIA required. Usage: make diarize MEDIA=media_001"; \
		exit 1; \
	fi
	$(ACTIVATE) && sherlock diarize "$(MEDIA)"

.PHONY: diarize-supervised
diarize-supervised:
	@if [ -z "$(MEDIA)" ] || [ -z "$(ANCHORS)" ]; then \
		echo "❌ Error: MEDIA and ANCHORS required. Usage: make diarize-supervised MEDIA=media_001 ANCHORS=speaker1.json,speaker2.json"; \
		exit 1; \
	fi
	$(ACTIVATE) && sherlock diarize "$(MEDIA)" --anchors "$(ANCHORS)"

# ============================================================================
# Targets & Packages
# ============================================================================

.PHONY: target-add
target-add:
	@if [ -z "$(NAME)" ] || [ -z "$(TYPE)" ] || [ -z "$(PRIORITY)" ]; then \
		echo "❌ Error: NAME, TYPE, PRIORITY required. Usage: make target-add NAME=AARO TYPE=org PRIORITY=1"; \
		exit 1; \
	fi
	$(ACTIVATE) && sherlock targets add "$(NAME)" --type "$(TYPE)" --priority "$(PRIORITY)"

.PHONY: target-list
target-list:
	$(ACTIVATE) && sherlock targets list

.PHONY: pkg-create
pkg-create:
	@if [ -z "$(TARGET)" ]; then \
		echo "❌ Error: TARGET required. Usage: make pkg-create TARGET=aaro"; \
		exit 1; \
	fi
	$(ACTIVATE) && sherlock pkg create --target "$(TARGET)" --version 1

.PHONY: pkg-validate
pkg-validate:
	@if [ -z "$(PKG)" ] || [ -z "$(LEVEL)" ]; then \
		echo "❌ Error: PKG and LEVEL required. Usage: make pkg-validate PKG=pkg_aaro_v1 LEVEL=0"; \
		exit 1; \
	fi
	$(ACTIVATE) && sherlock pkg validate --package "$(PKG)" --level "$(LEVEL)"

.PHONY: pkg-submit
pkg-submit:
	@if [ -z "$(PKG)" ]; then \
		echo "❌ Error: PKG required. Usage: make pkg-submit PKG=pkg_aaro_v1"; \
		exit 1; \
	fi
	$(ACTIVATE) && sherlock pkg submit --package "$(PKG)"

.PHONY: pkg-status
pkg-status:
	@if [ -z "$(PKG)" ]; then \
		echo "❌ Error: PKG required. Usage: make pkg-status PKG=pkg_aaro_v1"; \
		exit 1; \
	fi
	$(ACTIVATE) && sherlock pkg status "$(PKG)"

.PHONY: pkg-list
pkg-list:
	$(ACTIVATE) && sherlock pkg list

# ============================================================================
# Targeting Officer
# ============================================================================

.PHONY: officer-run
officer-run:
	$(ACTIVATE) && sherlock officer run --once

.PHONY: officer-daemon
officer-daemon:
	$(ACTIVATE) && sherlock officer run --daemon --interval 3600

.PHONY: officer-report
officer-report:
	$(ACTIVATE) && sherlock officer report --daily --output "targeting_report_$$(date +%Y-%m-%d).md"

# ============================================================================
# Query & Analysis
# ============================================================================

.PHONY: search
search:
	@if [ -z "$(QUERY)" ]; then \
		echo "❌ Error: QUERY required. Usage: make search QUERY='operation mockingbird'"; \
		exit 1; \
	fi
	$(ACTIVATE) && sherlock search "$(QUERY)"

.PHONY: query-speaker
query-speaker:
	@if [ -z "$(SPEAKER)" ]; then \
		echo "❌ Error: SPEAKER required. Usage: make query-speaker SPEAKER=frank_wisner"; \
		exit 1; \
	fi
	$(ACTIVATE) && sherlock query speaker "$(SPEAKER)"

.PHONY: report
report:
	@if [ -z "$(OP)" ]; then \
		echo "❌ Error: OP required. Usage: make report OP=mockingbird"; \
		exit 1; \
	fi
	$(ACTIVATE) && sherlock analyze report "$(OP)" --output "$(OP)_report.md"

.PHONY: cross-ref
cross-ref:
	@if [ -z "$(OP1)" ] || [ -z "$(OP2)" ]; then \
		echo "❌ Error: OP1 and OP2 required. Usage: make cross-ref OP1=mockingbird OP2=mkultra"; \
		exit 1; \
	fi
	$(ACTIVATE) && sherlock analyze cross-ref "$(OP1)" "$(OP2)" --output "$(OP1)_$(OP2)_cross_ref.md"

# ============================================================================
# Testing & Lint
# ============================================================================

.PHONY: test
test:
	$(ACTIVATE) && pytest tests/ -v

.PHONY: lint
lint:
	$(ACTIVATE) && ruff check src/

.PHONY: format
format:
	$(ACTIVATE) && ruff format src/

# ============================================================================
# Integration Workflows
# ============================================================================

.PHONY: integrate-operation
integrate-operation:
	@if [ -z "$(SCRIPT)" ]; then \
		echo "❌ Error: SCRIPT required. Usage: make integrate-operation SCRIPT=integrate_mockingbird_evidence.py"; \
		exit 1; \
	fi
	$(ACTIVATE) && $(PYTHON) "$(SCRIPT)"

# Example: Complete workflow for new target
.PHONY: workflow-target
workflow-target:
	@echo "📋 Example: Complete targeting workflow"
	@echo "1. Add target: make target-add NAME=AARO TYPE=org PRIORITY=1"
	@echo "2. Create package: make pkg-create TARGET=aaro"
	@echo "3. Edit package: sherlock pkg edit pkg_aaro_v1"
	@echo "4. Validate: make pkg-validate PKG=pkg_aaro_v1 LEVEL=0"
	@echo "5. Submit: make pkg-submit PKG=pkg_aaro_v1"
	@echo "6. Monitor: make officer-run"
	@echo "7. Check status: make pkg-status PKG=pkg_aaro_v1"

# ============================================================================
# Development Shortcuts
# ============================================================================

.PHONY: dev-setup
dev-setup: setup
	@echo "🔧 Installing development dependencies..."
	$(ACTIVATE) && pip install pytest ruff ipython

.PHONY: shell
shell:
	$(ACTIVATE) && ipython

.PHONY: dev-reset
dev-reset: db-reset
	@echo "🔧 Resetting development environment..."
	rm -rf media/ diarization/ checkpoints/
	@echo "✅ Development environment reset complete"

# ============================================================================
# CI/CD (Future)
# ============================================================================

.PHONY: ci
ci: lint test
	@echo "✅ CI checks passed"

# ============================================================================
# Maintenance
# ============================================================================

.PHONY: backup
backup:
	@mkdir -p backups
	@cp $(DB) "backups/$(DB)_$$(date +%Y%m%d_%H%M%S).backup"
	@echo "✅ Database backed up to backups/"

.PHONY: restore
restore:
	@if [ -z "$(BACKUP)" ]; then \
		echo "❌ Error: BACKUP required. Usage: make restore BACKUP=backups/evidence.db_20251001_120000.backup"; \
		exit 1; \
	fi
	@cp "$(BACKUP)" $(DB)
	@echo "✅ Database restored from $(BACKUP)"
