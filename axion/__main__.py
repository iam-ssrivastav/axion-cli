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


@click.group(invoke_without_command=True)
@click.option("--version", "-v", is_flag=True, help="Show version and exit")
@click.pass_context
def cli(ctx, version):
    """🚀 Axion — Free, open-source AI coding assistant for your terminal."""
    if version:
        click.echo(f"Axion CLI v{__version__}")
        sys.exit(0)
    
    # If no subcommand was provided, run the chat command
    if ctx.invoked_subcommand is None:
        ctx.invoke(chat)

@cli.command()
@click.option("--provider", "-p", type=click.Choice(["ollama", "gemini", "groq", "openai"], case_sensitive=False), help="LLM provider to use")
@click.option("--model", "-m", help="Model name to use")
@click.option("--api-key", "-k", help="API key for the provider")
@click.option("--base-url", help="Custom base URL")
@click.argument("prompt", nargs=-1, required=False)
def chat(provider, model, api_key, base_url, prompt):
    """Start an interactive chat session (Default)."""
    config = Config.load()

    if provider:
        config.provider = provider.lower()
    if model:
        config.model = model
    if api_key:
        config.api_key = api_key
    if base_url:
        config.base_url = base_url

    config.resolve_api_key()
    config.working_dir = os.getcwd()

    initial_prompt = " ".join(prompt) if prompt else None
    session = InteractiveSession(config)
    session.run(initial_prompt)

@cli.group(name="config")
def config_cmd():
    """Manage Axion configuration."""
    pass

@config_cmd.command(name="set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    """Set a configuration value (e.g. axion config set provider ollama)."""
    config = Config.load()
    if not hasattr(config, key):
        click.echo(f"❌ Unknown config key: {key}")
        return
    
    # Simple type conversion
    if key in ["max_tokens", "history_size"]:
        value = int(value)
    elif key in ["temperature"]:
        value = float(value)
    elif key in ["auto_approve_reads"]:
        value = value.lower() in ("true", "1", "yes")

    setattr(config, key, value)
    config.save()
    click.echo(f"✅ Set {key} = {value}")

@config_cmd.command(name="show")
def config_show():
    """Show current configuration."""
    config = Config.load()
    click.echo("Current Axion Configuration:")
    for key, value in config.__dict__.items():
        if key == "api_key" and value:
            value = "*****" + value[-4:] if len(value) > 8 else "***"
        click.echo(f"  {key}: {value}")

def main():
    cli()

if __name__ == "__main__":
    main()
