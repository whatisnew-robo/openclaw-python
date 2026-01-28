# Contributing to ClawdBot Python

Thank you for your interest in contributing to ClawdBot Python!

## Development Status

> **Note**: This project is under active development. APIs may change frequently.

## Getting Started

### Prerequisites

- Python 3.11+
- Poetry
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/zhaoyuong/clawdbot-python.git
cd clawdbot-python

# Install dependencies (including dev dependencies)
poetry install --with dev

# Run tests to verify setup
poetry run pytest
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Follow the existing code style
- Add tests for new functionality
- Update documentation if needed

### 3. Run Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=clawdbot

# Run specific tests
poetry run pytest tests/test_runtime.py -v
```

### 4. Code Quality

```bash
# Format code
poetry run black clawdbot/ tests/

# Lint
poetry run ruff check clawdbot/ tests/

# Type check
poetry run mypy clawdbot/
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: description of your changes"
```

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `test:` - Tests
- `refactor:` - Code refactoring

### 6. Submit Pull Request

Push your branch and create a pull request on GitHub.

## Code Style

- Use [Black](https://black.readthedocs.io/) for formatting
- Use [Ruff](https://docs.astral.sh/ruff/) for linting
- Use type hints wherever possible
- Write docstrings for public functions and classes

## Testing

- Write tests for all new features
- Maintain or improve test coverage
- Use pytest fixtures for common setup
- Use async tests for async code

## Project Structure

```
clawdbot/
├── agents/        # Agent runtime and tools
├── api/           # REST API
├── channels/      # Channel plugins
├── config/        # Configuration
├── gateway/       # WebSocket gateway
└── monitoring/    # Health and metrics
```

## Areas for Contribution

### High Priority
- Improving test coverage
- Bug fixes
- Documentation improvements
- Channel plugin testing

### Medium Priority
- New tools
- Performance improvements
- Error handling improvements

### Low Priority
- New channel plugins
- New skills

## Questions?

If you have questions, please open an issue on GitHub.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
