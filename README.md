# ClawdBot Python

> **⚠️ WORK IN PROGRESS**: This project is under active development. APIs may change without notice.

A Python implementation of the ClawdBot personal AI assistant platform. This is a port of the [TypeScript version](https://github.com/badlogic/clawdbot), designed to provide a more accessible Python-based alternative.

## Status

| Component | Status | Notes |
|-----------|--------|-------|
| Agent Runtime | ✅ Working | Claude & OpenAI support |
| Tools System | ✅ Working | 24+ tools implemented |
| Channel Plugins | 🚧 In Progress | Framework ready, needs testing |
| REST API | ✅ Working | Full FastAPI implementation |
| Monitoring | ✅ Working | Health checks & metrics |
| CLI | ✅ Working | Full command-line interface |

**Current Development Stage**: Alpha - Core functionality works, but not production-ready.

## Quick Start

### Prerequisites

- Python 3.11+
- Poetry (package manager)
- An API key (Anthropic or OpenAI)

### Installation

```bash
# Clone repository
git clone https://github.com/zhaoyuong/clawdbot-python.git
cd clawdbot-python

# Install dependencies
poetry install

# Copy environment template
cp .env.example .env

# Add your API key
echo "ANTHROPIC_API_KEY=your-key-here" >> .env
```

### Basic Usage

```bash
# Chat with agent (one-shot)
poetry run python -m clawdbot agent chat "Hello, who are you?"

# Start API server
poetry run python -m clawdbot api start

# Check health
poetry run python -m clawdbot health check

# View configuration
poetry run python -m clawdbot config show
```

### Run Examples

```bash
# Basic agent usage
poetry run python examples/01_basic_agent.py

# Agent with tools
poetry run python examples/02_with_tools.py

# API server
poetry run python examples/04_api_server.py
```

## Project Structure

```
clawdbot-python/
├── clawdbot/              # Main package
│   ├── agents/            # Agent runtime & tools
│   ├── api/               # REST API server
│   ├── channels/          # Channel plugins
│   ├── config/            # Configuration
│   ├── gateway/           # WebSocket gateway
│   └── monitoring/        # Health & metrics
├── examples/              # Usage examples
├── extensions/            # Channel extensions
├── skills/                # Skill templates
├── tests/                 # Test suite
└── docs/                  # Documentation
```

## Features

### Agent Runtime
- Streaming responses from Claude and OpenAI
- Context window management
- Automatic error handling and retry
- Tool calling support

### Tools
- File operations (read, write, glob, grep)
- Shell command execution
- Web browsing (Playwright)
- Image generation
- And more...

### REST API
- Health check endpoints (`/health`, `/health/live`, `/health/ready`)
- Metrics endpoint (`/metrics`, `/metrics/prometheus`)
- Agent chat API
- Session management
- Channel management

### CLI
- `clawdbot agent chat` - Chat with agent
- `clawdbot api start` - Start API server
- `clawdbot health check` - Run health checks
- `clawdbot config show` - View configuration

## API Documentation

Start the API server and visit:
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Run Tests

```bash
# All tests
poetry run pytest

# With coverage
poetry run pytest --cov=clawdbot --cov-report=html

# Specific test file
poetry run pytest tests/test_runtime.py -v
```

### Code Quality

```bash
# Format code
poetry run black clawdbot/

# Lint
poetry run ruff check clawdbot/

# Type check
poetry run mypy clawdbot/
```

## Docker

```bash
# Build image
docker build -t clawdbot-python .

# Run with docker-compose
docker-compose up

# Run tests in container
./test-docker-safe.sh
```

See [docs/guides/](docs/guides/) for detailed Docker documentation.

## Configuration

Configuration can be set via:
1. Environment variables (`CLAWDBOT_*`)
2. `.env` file
3. JSON config file

Example environment variables:
```bash
CLAWDBOT_AGENT__MODEL=anthropic/claude-sonnet-4-20250514
CLAWDBOT_API__PORT=8000
CLAWDBOT_DEBUG=true
```

## Documentation

- [Quick Start Guide](docs/guides/QUICKSTART.md)
- [Installation](docs/guides/INSTALLATION.md)
- [Architecture](docs/development/ARCHITECTURE.md)
- [Agent Implementation](docs/development/AGENT_IMPLEMENTATION.md)
- [Docker Guide](docs/guides/DOCKER_QUICKSTART.md)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

This project is a Python port of [ClawdBot](https://github.com/badlogic/clawdbot) by Mario Zechner.

---

**Note**: This is an independent implementation and not affiliated with Anthropic or OpenAI.
