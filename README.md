# OpenClaw Python 🦞

> **A Python port of OpenClaw - Your personal AI assistant platform**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

OpenClaw Python is a complete Python implementation of the OpenClaw personal AI assistant platform. Currently supports Telegram with additional channels under active development.

## 🚧 Current Status

**✅ Working:**
- Telegram channel integration
- Core agent runtime with tool execution
- 24 built-in tools (file operations, web search, bash, etc.)
- 56+ skills for specialized tasks
- Workspace management with personality files (SOUL.md, AGENTS.md, etc.)
- Multi-model support (Claude, GPT, Gemini)

**🔨 In Development:**
- Discord, Slack, and WhatsApp channels
- Web Control UI
- Cron scheduler
- Additional automation features

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (3.12+ recommended)
- **uv** package manager
- At least one LLM API key (Anthropic, OpenAI, or Google Gemini)
- **For Telegram:** A bot token from [@BotFather](https://t.me/botfather)

### Installation

```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone https://github.com/openjavis/openclaw-python.git
cd openclaw-python

# Install dependencies
uv sync
```

### Configuration

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Add your API keys:**
   ```bash
   # Required: At least one AI model provider
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   # OR
   OPENAI_API_KEY=sk-your-key-here
   # OR
   GOOGLE_API_KEY=your-google-key-here

   # Required for Telegram
   TELEGRAM_BOT_TOKEN=your-telegram-bot-token
   ```

3. **Run initial setup:**
   ```bash
   uv run openclaw onboard
   ```
   
   This creates your configuration file at `~/.openclaw/config.json` and sets up your workspace at `~/.openclaw/workspace/`.

## 📝 Command Reference

### Starting the Gateway

```bash
# Start with Telegram (foreground)
uv run openclaw start --port 18789 --telegram

# The gateway will create workspace files on first run:
# ~/.openclaw/workspace/SOUL.md    - Agent personality
# ~/.openclaw/workspace/AGENTS.md  - Operating instructions
# ~/.openclaw/workspace/TOOLS.md   - Local tool configurations
# ~/.openclaw/workspace/USER.md    - User profile
# ~/.openclaw/workspace/IDENTITY.md - Agent identity
```

### Managing the Gateway

```bash
# Check status
uv run openclaw gateway status

# Stop the gateway
# Press Ctrl+C in the terminal, or use:
uv run openclaw cleanup --kill-all

# View logs (if running as service)
uv run openclaw gateway logs

# Clean up stuck ports
uv run openclaw cleanup
uv run openclaw cleanup --ports 18789,8080
```

### Channel Management

```bash
# List available channels
uv run openclaw channels list

# Currently only Telegram is operational
# Other channels are in development
```

### Cron Jobs (Coming Soon)

```bash
# List cron jobs
uv run openclaw cron list

# Note: Cron functionality is under development
```

### Configuration

```bash
# View current configuration
cat ~/.openclaw/config.json

# Edit workspace files
nano ~/.openclaw/workspace/SOUL.md
nano ~/.openclaw/workspace/AGENTS.md
```

### Troubleshooting

```bash
# If ports are stuck (error: address already in use)
uv run openclaw cleanup --kill-all

# Run diagnostics
uv run openclaw doctor

# Check gateway bootstrap logs
uv run openclaw start --port 18789 --telegram
# Look for: "Bootstrap complete: X steps, 0 errors"
```

## 🏗️ Architecture

OpenClaw Python follows a modular architecture:

```
openclaw/
├── agents/          # Core agent runtime and system prompt
│   ├── templates/   # Workspace file templates (SOUL.md, etc.)
│   └── tools/       # Built-in tools (24 tools)
├── channels/        # Communication channels
│   └── telegram/    # ✅ Ready
├── gateway/         # Gateway server and bootstrap
├── skills/          # Modular skills (56+ available)
├── config/          # Configuration management
└── cli/             # Command-line interface
```

### Workspace Structure

Your workspace at `~/.openclaw/workspace/` contains:

- **SOUL.md** - Defines your agent's personality and values
- **AGENTS.md** - Operating instructions and conventions
- **TOOLS.md** - Tool-specific configurations
- **USER.md** - Your profile and preferences
- **IDENTITY.md** - Agent identity (name, emoji, avatar)
- **HEARTBEAT.md** - Periodic task checklist
- **BOOTSTRAP.md** - First-run initialization guide (auto-created, delete after use)

These files are injected into the agent's system prompt on each session start.

## 🤖 Using with Telegram

1. **Create a bot:**
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Send `/newbot` and follow the prompts
   - Copy your bot token to `.env`

2. **Start the gateway:**
   ```bash
   uv run openclaw start --port 18789 --telegram
   ```

3. **Chat with your bot:**
   - Find your bot on Telegram (search for the username you created)
   - Send a message to start chatting
   - The agent has access to tools and can execute commands

## 🛠️ Development

```bash
# Run tests
uv run pytest

# Run specific test
uv run pytest tests/test_agent.py

# Format code
uv run ruff format .

# Lint
uv run ruff check .
```

## 📚 Documentation

For detailed documentation, see the [docs/](./docs/) directory:

- [Gateway Architecture](./docs/gateway/)
- [Channel Implementation](./docs/channels/)
- [Agent System](./docs/agents/)
- [Skills Development](./docs/skills/)

## 🤝 Contributing

Contributions are welcome! This is an active development project. Please:

1. Check existing issues or create a new one
2. Fork the repository
3. Create a feature branch
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Credits

This is a Python port of the original [OpenClaw](https://github.com/openjavis/openclaw) TypeScript project. Built with Python for clarity, maintainability, and ecosystem compatibility.

## ⚠️ Important Notes

- **Telegram Only**: Currently only the Telegram channel is fully functional. Other channels are under active development.
- **Active Development**: This project is rapidly evolving. Expect frequent updates.
- **Security**: Review the SOUL.md and AGENTS.md files in your workspace to understand your agent's boundaries and permissions.
- **API Costs**: Be aware of API usage costs from your chosen LLM provider.

## 🔗 Links

- [OpenClaw (TypeScript)](https://github.com/openjavis/openclaw)
- [Issue Tracker](https://github.com/openjavis/openclaw-python/issues)
- [Telegram BotFather](https://t.me/botfather)

---

Built with 🦞 by the OpenClaw community
