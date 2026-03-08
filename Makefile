# ============================================================
# MNDA Automation — Makefile
# Common development and operations commands.
# ============================================================

.PHONY: install test review watch-email watch-slack clean help

# Default target
help:
	@echo ""
	@echo "MNDA Automation — available commands:"
	@echo ""
	@echo "  make install        First-time setup (creates venv, installs deps, creates .env)"
	@echo "  make test           Run unit tests"
	@echo "  make review         Review a file  (FILE=path/to/nda.pdf)"
	@echo "  make watch-email    Start email inbox watcher daemon"
	@echo "  make watch-slack    Start Slack bot daemon"
	@echo "  make clean          Remove venv and cached files"
	@echo ""

install:
	bash install.sh

test:
	@source .venv/bin/activate && pytest tests/ -v

review:
	@source .venv/bin/activate && mnda review --file $(FILE)

watch-email:
	@source .venv/bin/activate && mnda watch-email

watch-slack:
	@source .venv/bin/activate && mnda watch-slack

clean:
	rm -rf .venv __pycache__ mnda_automation/__pycache__ .pytest_cache
	find . -name "*.pyc" -delete
	@echo "Cleaned."
