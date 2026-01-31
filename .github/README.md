# OpenClaw Python

> 🦞 Personal AI assistant platform - Python implementation of [OpenClaw](https://github.com/openclaw/openclaw)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Production-ready Python implementation with Gemini 3, enhanced security, and complete testing.**

---

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/zhaoyuong/openclaw-python.git
cd openclaw-python

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Configure
cp .env.example .env
# Add your API keys to .env

# Test Gemini 3
uv run python tests/manual/test_gemini_3_flash.py
```

---

## ✨ Features

### Core (v0.4.0)
- ✅ Multi-provider LLM (Anthropic, OpenAI, Google, AWS, Ollama)
- ✅ 24+ tools with permissions
- ✅ Multi-channel support (Telegram, Discord, Slack, WebChat)
- ✅ REST API + OpenAI compatibility

### Advanced (v0.5.0)
- ✅ Thinking Mode
- ✅ Auth Rotation
- ✅ Model Fallback
- ✅ Session Queuing
- ✅ Context Compaction
- ✅ Tool Formatting

### Enterprise (v0.6.0)
- ✅ **Gemini 3 Flash/Pro** with Thinking Mode
- ✅ Settings Manager
- ✅ Message Summarization
- ✅ Enhanced Tool Policies
- ✅ WebSocket Streaming

---

## 📚 Documentation

- **[Quick Start](docs/guides/QUICKSTART.md)** - Get started in 5 minutes
- **[Gemini Setup](docs/setup/GEMINI_SETUP_GUIDE.md)** - Gemini 3 configuration
- **[Migration Guide](docs/guides/MIGRATION_GUIDE.md)** - Migrate from ClawdBot
- **[Full Documentation](docs/README.md)** - Complete docs

---

## 🎯 Status

| Component | Completion | Tests |
|-----------|-----------|-------|
| Agent Runtime | 100% | 309 passing |
| Gemini 3 Integration | 100% | ✅ Verified |
| Tools System | 90% | ✅ 24+ tools |
| Channels | 70% | ✅ 4 production |
| Documentation | 100% | ✅ Complete |

**Status**: ✅ Production Ready - v0.6.0

---

## 🔗 Links

- **Main Project**: https://github.com/openclaw/openclaw (TypeScript)
- **Python Port**: https://github.com/zhaoyuong/openclaw-python
- **Website**: https://openclaw.ai

---

## 📝 License

MIT License - see [LICENSE](LICENSE)

---

**🦞 OpenClaw - Your personal AI assistant, any OS, any platform.**
