"""
Axion CLI entry point.
Usage: python -m axion  OR  axion (after pip install)
"""

import click
import sys
import os

from axion import __version__
from axion.config import Config
from axion.cli import InteractiveSession


@click.command()
@click.option(
    "--provider", "-p",
    type=click.Choice(["ollama", "gemini", "groq", "openai"], case_sensitive=False),
    default=None,
    help="LLM provider to use (default: from config or ollama)",
)
@click.option(
    "--model", "-m",
    default=None,
    help="Model name to use (e.g., llama3.1, gemini-2.0-flash, llama-3.1-70b-versatile)",
)
@click.option(
    "--api-key", "-k",
    default=None,
    help="API key for the provider (or set via env: AXION_API_KEY, GEMINI_API_KEY, GROQ_API_KEY)",
)
@click.option(
    "--base-url",
    default=None,
    help="Custom base URL for OpenAI-compatible APIs",
)
@click.option(
    "--version", "-v",
    is_flag=True,
    help="Show version and exit",
)
@click.option(
    "--config-path",
    default=None,
    help="Path to config file",
)
@click.argument("prompt", nargs=-1, required=False)
def main(provider, model, api_key, base_url, version, config_path, prompt):
    """🚀 Axion — Free, open-source AI coding assistant for your terminal.

    Run without arguments for interactive mode, or pass a prompt directly:

        axion "explain this codebase"
        axion -p gemini -m gemini-2.0-flash "fix the bug in main.py"
    """
    if version:
        click.echo(f"Axion CLI v{__version__}")
        sys.exit(0)

    # Load config
    config = Config.load(config_path)

    # CLI args override config
    if provider:
        config.provider = provider.lower()
    if model:
        config.model = model
    if api_key:
        config.api_key = api_key
    if base_url:
        config.base_url = base_url

    # Resolve API key from env if not set
    config.resolve_api_key()

    # Set working directory context
    config.working_dir = os.getcwd()

    # Join prompt args if provided
    initial_prompt = " ".join(prompt) if prompt else None

    # Start interactive session
    session = InteractiveSession(config)
    session.run(initial_prompt)


if __name__ == "__main__":
    main()
