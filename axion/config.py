"""
Configuration management for Axion CLI.
"""

import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


DEFAULT_CONFIG_DIR = Path.home() / ".axion"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.yaml"

# Default models per provider
DEFAULT_MODELS = {
    "ollama": "llama3.1",
    "gemini": "gemini-2.0-flash",
    "groq": "llama-3.1-70b-versatile",
    "openai": "gpt-4o-mini",
}

# Base URLs per provider
DEFAULT_BASE_URLS = {
    "ollama": "http://localhost:11434/v1",
    "groq": "https://api.groq.com/openai/v1",
    "openai": "https://api.openai.com/v1",
}

# Environment variable names for API keys
ENV_KEY_MAP = {
    "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
    "groq": ["GROQ_API_KEY"],
    "openai": ["OPENAI_API_KEY"],
    "ollama": [],
}


@dataclass
class Config:
    """Axion CLI configuration."""

    provider: str = "ollama"
    model: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    working_dir: str = field(default_factory=os.getcwd)
    max_tokens: int = 8192
    temperature: float = 0.1
    theme: str = "dark"
    auto_approve_reads: bool = True  # Auto-approve non-destructive operations
    history_size: int = 50  # Number of conversation turns to keep

    def __post_init__(self):
        if self.model is None:
            self.model = DEFAULT_MODELS.get(self.provider, "llama3.1")
        if self.base_url is None and self.provider in DEFAULT_BASE_URLS:
            self.base_url = DEFAULT_BASE_URLS[self.provider]

    def resolve_api_key(self):
        """Resolve API key from environment variables if not explicitly set."""
        if self.api_key:
            return

        # Check AXION_API_KEY first (universal)
        axion_key = os.environ.get("AXION_API_KEY")
        if axion_key:
            self.api_key = axion_key
            return

        # Check provider-specific env vars
        env_vars = ENV_KEY_MAP.get(self.provider, [])
        for var in env_vars:
            key = os.environ.get(var)
            if key:
                self.api_key = key
                return

        # Ollama doesn't need an API key
        if self.provider == "ollama":
            self.api_key = "ollama"  # Placeholder, not used

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Config":
        """Load config from YAML file, falling back to defaults."""
        path = Path(config_path) if config_path else DEFAULT_CONFIG_FILE

        if path.exists():
            try:
                with open(path, "r") as f:
                    data = yaml.safe_load(f) or {}
                return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
            except Exception:
                pass

        return cls()

    def save(self, config_path: Optional[str] = None):
        """Save current config to YAML file."""
        path = Path(config_path) if config_path else DEFAULT_CONFIG_FILE
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "theme": self.theme,
            "auto_approve_reads": self.auto_approve_reads,
            "history_size": self.history_size,
        }

        # Don't save sensitive data
        if self.base_url and self.provider not in DEFAULT_BASE_URLS:
            data["base_url"] = self.base_url

        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
