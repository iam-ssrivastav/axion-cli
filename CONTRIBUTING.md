# Axion CLI - Contribution Guidelines

Thanks for your interest in contributing to Axion CLI! 🎉

## Development Setup

```bash
# Clone the repo
git clone https://github.com/your-username/axion-cli.git
cd axion-cli

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux

# Install in development mode
pip install -e ".[dev]"

# Run linting
ruff check axion/

# Run tests
pytest
```

## Adding a New LLM Provider

1. Create `axion/providers/your_provider.py`
2. Extend `BaseProvider` from `axion/providers/base.py`
3. Implement `chat()`, `chat_stream()`, and `test_connection()`
4. Register it in `axion/providers/__init__.py`
5. Add it to the provider factory in `axion/cli.py`
6. Update the CLI options in `axion/__main__.py`

## Adding a New Tool

1. Create `axion/tools/your_tool.py`
2. Extend `BaseTool` from `axion/tools/base.py`
3. Implement `name`, `description`, `parameters`, and `execute()`
4. Register it in `axion/tools/base.py` → `create_tool_registry()`
5. Set `requires_permission = True` for destructive operations

## Code Style

- Use `ruff` for linting
- Follow PEP 8
- Add type hints
- Write docstrings for public methods
