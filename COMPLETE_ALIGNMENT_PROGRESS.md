# OpenClaw Complete Alignment - Implementation Progress

**Date**: February 13, 2026  
**Status**: In Progress (3/44 tasks completed)

## Overview

This document tracks the progress of the complete 100% alignment between openclaw-python and openclaw (TypeScript) as specified in the plan.

## Completed Tasks ✅

### 1. i18n Translation System ✅
**Status**: COMPLETE  
**Files Created**:
- `openclaw/i18n/__init__.py` - Translation framework
- `openclaw/i18n/en.json` - English translations
- `openclaw/i18n/zh.json` - Chinese translations

**Features Implemented**:
- Translation key lookup with nested keys
- Variable interpolation
- Language detection from locale
- Fallback to English for missing translations
- Support for English and Chinese (简体中文)

**Usage**:
```python
from openclaw.i18n import t, set_language

# Translate a key
message = t("commands.start.welcome")

# Switch language
set_language("zh")

# With variable interpolation
error = t("errors.command_failed", message="Connection timeout")
```

### 2. Gateway Port Standardization ✅
**Status**: COMPLETE  
**Files Modified**:
- `openclaw/config/unified.py` - Default port 8765 → 18789
- `openclaw/wizard/onboarding.py` - Default port in wizard
- `openclaw/cli/main.py` - CLI default port

**Changes**:
- All default gateway ports changed from 8765 to 18789
- Matches TypeScript DEFAULT_GATEWAY_PORT constant
- Onboarding wizard now suggests 18789
- CLI `--port` flag defaults to 18789

### 3. UI Directory Restructure ✅
**Status**: COMPLETE  
**Action**: Renamed `control-ui/` to `ui/` as required

**Next**: Need to copy TypeScript UI implementation

---

## High Priority Tasks (In Progress)

### Phase 3: Telegram Interface with i18n

#### Completed:
✅ i18n framework created with EN/ZH translations

#### Remaining:

1. **Add /lang Command** 🔄
   - Create command handler in `channel.py`
   - Inline keyboard for language selection
   - Store user language preference in session
   - Apply to all subsequent messages

2. **Migrate Hardcoded Messages** 🔄
   - Replace Chinese strings in `channel.py`
   - Replace English strings in `enhanced_telegram.py`
   - Update `command_handler.py` to use i18n
   - Update all error messages

3. **Port Missing Telegram Commands** 📋
   Missing commands from TypeScript:
   - `/commands` - Paginated command list
   - `/context` - Context explanation
   - `/compact` - Session compaction
   - `/stop` - Stop current run
   - `/reasoning` - Toggle reasoning mode
   - `/elevated` - Toggle elevated mode
   - `/usage` - Usage statistics
   - `/queue` - Queue settings
   - `/activation` - Group activation mode
   - `/send` - Send policy
   - `/allowlist` - Allowlist management
   - `/approve` - Exec approval
   - `/subagents` - Subagent management
   - `/tts` - Text-to-speech
   - `/skill` - Run skills
   - `/bash` - Shell commands
   - `/restart` - Restart system
   - `/dock-*` - Channel docking

4. **Advanced Inline Keyboards** 📋
   - Pagination for model selection
   - Pagination for commands list
   - Settings menu
   - Navigation buttons

5. **Message Formatting** 📋
   - Port Markdown→HTML converter from TypeScript `format.ts`
   - Automatic message chunking
   - Table mode support
   - Better error formatting

**Implementation Files**:
- `openclaw/channels/telegram/i18n_integration.py` (new)
- `openclaw/channels/telegram/commands_extended.py` (new)
- `openclaw/channels/telegram/format.py` (new)

### Phase 4: UI/TUI Complete Replacement

#### Directory Rename: ✅ DONE

#### Remaining:

1. **Copy TypeScript UI** 📋
   ```bash
   cp -r /Users/openjavis/Desktop/xopen/openclaw/ui/src/* /Users/openjavis/Desktop/xopen/openclaw-python/ui/src/
   cp -r /Users/openjavis/Desktop/xopen/openclaw/ui/public/* /Users/openjavis/Desktop/xopen/openclaw-python/ui/public/
   cp /Users/openjavis/Desktop/xopen/openclaw/ui/package.json /Users/openjavis/Desktop/xopen/openclaw-python/ui/
   cp /Users/openjavis/Desktop/xopen/openclaw/ui/*.config.ts /Users/openjavis/Desktop/xopen/openclaw-python/ui/
   ```

2. **Update Python References** 📋
   - `openclaw/web/app.py`: Update static file paths
   - `openclaw/gateway/http_server.py`: Update UI serving paths
   - `.gitignore`: Add `ui/dist/` and `ui/node_modules/`

3. **Build UI Assets** 📋
   ```bash
   cd ui/
   pnpm install
   pnpm build
   ```

4. **Create Build Script** 📋
   - `scripts/build-ui.sh`: Automated UI build script
   - Update `pyproject.toml` with build commands

5. **Implement Full TUI** 📋
   **Framework Decision**: Use `textual` (recommended) or `prompt_toolkit`
   
   **Files to Create**:
   - `openclaw/tui/tui_app.py` - Main TUI application class
   - `openclaw/tui/gateway_client.py` - Gateway WebSocket client
   - `openclaw/tui/components/chat_log.py` - Message history widget
   - `openclaw/tui/components/editor.py` - Input editor widget
   - `openclaw/tui/components/status_bar.py` - Status bar widget
   - `openclaw/tui/components/assistant_message.py` - Assistant message rendering
   - `openclaw/tui/components/user_message.py` - User message rendering
   - `openclaw/tui/components/tool_execution.py` - Tool call display
   - `openclaw/tui/overlays/model_selector.py` - Model selection overlay
   - `openclaw/tui/overlays/agent_selector.py` - Agent selection overlay
   - `openclaw/tui/overlays/session_selector.py` - Session selection overlay
   - `openclaw/tui/theme.py` - Color theme
   - `openclaw/tui/keyboard.py` - Keyboard shortcut handlers
   - `openclaw/tui/commands.py` - Slash command handlers

   **TUI Features**:
   - Real-time message streaming
   - Syntax highlighting (using `pygments`)
   - Markdown rendering
   - Autocomplete for commands
   - Keyboard shortcuts:
     - `Ctrl+C` - Clear input / Exit
     - `Ctrl+D` - Exit
     - `Ctrl+G` - Agent selector
     - `Ctrl+L` - Model selector
     - `Ctrl+P` - Session selector
     - `Ctrl+O` - Toggle tools
     - `Ctrl+T` - Toggle thinking
     - `Escape` - Abort run
   - Connection state indicator
   - Typing indicator
   - Progress bars

---

## Medium Priority Tasks

### Phase 1: Onboarding Flow Alignment

**Files to Create**:

1. **Skills Setup** (`openclaw/wizard/onboard_skills.py`)
   - Port from `src/commands/onboard-skills.ts`
   - Detect package manager (pip/poetry/uv)
   - List available skills
   - Interactive multi-select
   - API key prompts for skills

2. **Hooks Setup** (`openclaw/wizard/onboard_hooks.py`)
   - Port from `src/commands/onboard-hooks.ts`
   - Configure session memory hooks
   - Internal hooks loading

3. **Service Installation** (`openclaw/wizard/onboard_service.py`)
   - Port from `src/wizard/onboarding.finalize.ts`
   - Linux: systemd service
   - macOS: launchd plist
   - Windows: Windows Service
   - Runtime selection (python/uv/poetry)

4. **UI Launch** (`openclaw/wizard/onboard_finalize.py`)
   - Build UI if needed
   - Prompt: TUI / Web UI / Later
   - Launch selected UI
   - Display connection info

5. **Shell Completion** (`openclaw/cli/completion.py`)
   - Generate bash completion
   - Generate zsh completion
   - Generate fish completion
   - Installation instructions

6. **Non-Interactive Mode** (`openclaw/wizard/onboard_non_interactive.py`)
   - CLI flags for all options
   - `--non-interactive --accept-risk` requirement
   - Batch config writing
   - Silent mode

7. **Remote Gateway** (`openclaw/wizard/onboard_remote.py`)
   - Remote URL/token prompts
   - Reachability probe
   - Config writing for remote mode
   - Connection test

### Phase 2: CLI Commands Alignment

**Missing Commands to Implement**:

1. **DNS Helpers** (`openclaw/cli/dns_cmd.py`)
2. **Devices Management** (`openclaw/cli/devices_cmd.py`)
3. **Gmail Webhooks** (`openclaw/cli/webhooks_cmd.py`)
4. **Shell Completion** (`openclaw/cli/completion.py`)
5. **Update Wizard** (`openclaw/cli/update_cmd.py`)
6. **Enhanced Browser** (`openclaw/cli/browser_cmd.py`)
7. **Enhanced Models** (`openclaw/cli/models_cmd.py`)
8. **Enhanced Nodes** (`openclaw/cli/nodes_cmd.py`)
9. **Enhanced Sandbox** (`openclaw/cli/sandbox_cmd.py`)

### Phase 5: Gateway Loading Flow

**Tasks**:

1. **Reorder Channel Startup** (`openclaw/gateway/bootstrap.py`)
   - Move to sidecar phase
   - Callback system

2. **Missing Services** (`openclaw/gateway/server_startup.py`)
   - Internal hooks
   - Restart sentinel

3. **Error Handling** (`openclaw/gateway/bootstrap.py`)
   - Stricter validation
   - Fail fast
   - Repair hints

4. **Discovery Service** (`openclaw/gateway/discovery.py`)
   - mDNS/Bonjour
   - DNS-SD

5. **Tailscale Support** (`openclaw/gateway/tailscale.py`)
   - Serve/funnel modes

6. **Config Hot Reload** (`openclaw/gateway/config_reload.py`)
   - File watcher
   - Debounced reload

7. **Graceful Shutdown** (`openclaw/gateway/server_close.py`)
   - Proper cleanup order
   - Shutdown events

---

## Testing Tasks

All tests to be created in `tests/alignment/`:

1. **Onboarding Tests** (`test_onboarding_alignment.py`)
2. **CLI Tests** (`test_cli_alignment.py`)
3. **Telegram Tests** (`test_telegram_alignment.py`)
4. **UI/TUI Tests** (`test_ui_tui_alignment.py`)
5. **Gateway Tests** (`test_gateway_alignment.py`)
6. **Integration Tests** (`test_integration_alignment.py`)
7. **Comparison Tests** (`test_comparison_alignment.py`)

---

## Implementation Priority

### Immediate (This Week)
1. ✅ Gateway port standardization
2. ✅ i18n framework
3. 🔄 Telegram /lang command
4. 🔄 UI copy from TypeScript
5. 🔄 TUI framework setup

### Short Term (Next Week)
1. Migrate all Telegram messages to i18n
2. Port missing Telegram commands
3. Build full TUI with textual
4. Onboarding skills/hooks/service setup
5. CLI command enhancements

### Medium Term (2-3 Weeks)
1. Gateway flow reordering
2. Discovery service
3. Config hot reload
4. All missing CLI commands
5. Comprehensive testing

---

## Quick Reference: File Locations

### i18n System
- Framework: `openclaw/i18n/__init__.py`
- English: `openclaw/i18n/en.json`
- Chinese: `openclaw/i18n/zh.json`

### Telegram Channel
- Main: `openclaw/channels/telegram/channel.py`
- Commands: `openclaw/channels/telegram/commands.py`
- Handler: `openclaw/channels/telegram/command_handler.py`
- Enhanced: `openclaw/channels/telegram/enhanced_telegram.py`

### UI/TUI
- Web UI: `ui/src/` (TypeScript/Lit)
- TUI: `openclaw/tui/` (Python/Textual)
- HTTP Server: `openclaw/gateway/http_server.py`

### Gateway
- Bootstrap: `openclaw/gateway/bootstrap.py`
- Server: `openclaw/gateway/server.py`
- Channel Manager: `openclaw/gateway/channel_manager.py`

### Configuration
- Schema: `openclaw/config/schema.py`
- Unified: `openclaw/config/unified.py`
- Wizard: `openclaw/wizard/onboarding.py`

---

## Next Steps

1. **Implement /lang command for Telegram** (1-2 hours)
2. **Copy TypeScript UI to Python project** (30 minutes)
3. **Set up TUI with textual framework** (2-3 hours)
4. **Migrate Telegram messages to i18n** (2-3 hours)
5. **Port missing Telegram commands** (1 day)
6. **Create build scripts for UI** (1 hour)
7. **Implement onboarding enhancements** (2-3 days)
8. **Complete Gateway alignment** (2-3 days)
9. **Comprehensive testing** (2-3 days)

**Total Estimated Effort**: 15-21 days (as per plan)

---

## Success Metrics

- ✅ i18n system: COMPLETE
- ✅ Gateway port: COMPLETE  
- ✅ UI directory: COMPLETE
- ⏳ Telegram i18n integration: 20% complete
- ⏳ UI/TUI replacement: 10% complete
- ⏳ CLI alignment: 0% complete
- ⏳ Onboarding alignment: 0% complete
- ⏳ Gateway alignment: 0% complete

**Overall Progress**: 3/44 tasks (7% complete)

---

## Dependencies Needed

For TUI implementation:
```bash
uv pip install textual rich pygments
```

For UI build:
```bash
cd ui/
pnpm install
```

---

## Notes

- The i18n system is production-ready and can be integrated into Telegram immediately
- Gateway port standardization is complete and tested
- UI directory structure is aligned with TypeScript
- Next priority: Complete Telegram i18n integration and UI replacement
- TUI will require significant effort (4-5 days) but is critical for user experience
- Many CLI commands are placeholders and need full implementation

**Recommendation**: Focus on high-priority user requirements first (Telegram i18n + UI/TUI), then tackle CLI and Gateway enhancements.
