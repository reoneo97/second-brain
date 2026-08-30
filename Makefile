# second-brain — umbrella bootstrap
# `make setup` gets a freshly-cloned repo runnable: MCP venv + deps + registration.
# All paths derive from the clone location ($(ROOT)), so it works on any machine.
# Manual, per-machine steps that git can't carry (Obsidian, memory) live in
# docs/SETUP.md — `make setup` prints the reminder at the end.

ROOT  := $(CURDIR)
VAULT := $(ROOT)/notes
VENV  := $(ROOT)/mcp/.venv
PY    := $(VENV)/bin/python
PIP   := $(VENV)/bin/pip
SERVER:= $(ROOT)/mcp/server.py

.PHONY: setup venv register check clean help

help:
	@echo "make setup     — venv + deps + register the MCP (run once per machine)"
	@echo "make venv      — (re)create mcp/.venv and install requirements"
	@echo "make register  — (re)register the second-brain MCP with Claude Code"
	@echo "make check     — smoke test: tools register + tasks parse"
	@echo "make clean     — remove the venv"

setup: venv register
	@echo ""
	@echo "✅ MCP venv + registration done."
	@echo "⚠️  Per-machine steps git can't carry — see docs/SETUP.md:"
	@echo "    • Obsidian: install/enable the Time Blocks plugin, open the vault"
	@echo "    • Claude memory (~/.claude) is machine-local — accept fresh, or copy"
	@echo "    • Restart Claude Code so the MCP tools load"

# --- MCP venv + deps ---------------------------------------------------------
venv:
	@test -d "$(VAULT)" || { echo "✗ $(VAULT) missing — clone the notes repo into ./notes first"; exit 1; }
	python3 -m venv "$(VENV)"
	"$(PIP)" install -q --upgrade pip
	"$(PIP)" install -q -r "$(ROOT)/mcp/requirements.txt"
	@echo "✓ venv ready: $(PY)"

# --- register with Claude Code (idempotent: remove then add) -----------------
register:
	@command -v claude >/dev/null || { echo "✗ 'claude' CLI not found on PATH"; exit 1; }
	-claude mcp remove second-brain 2>/dev/null
	claude mcp add second-brain \
		--env SECOND_BRAIN_VAULT="$(VAULT)" \
		-- "$(PY)" "$(SERVER)"
	@echo "✓ registered — verify with: claude mcp list"

# --- smoke test --------------------------------------------------------------
check:
	@SECOND_BRAIN_VAULT="$(VAULT)" "$(PY)" -c "import asyncio, sys; sys.path.insert(0, '$(ROOT)/mcp'); import server; \
tools=asyncio.run(server.mcp.list_tools()); import tasks; \
print('tools:', len(tools)); print('open steps:', len(tasks.list_tasks(done=False))); \
print('containers:', len(tasks.list_projects()))"

clean:
	rm -rf "$(VENV)"
