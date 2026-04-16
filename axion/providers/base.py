"""
Base LLM provider interface for Axion CLI.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generator, List, Optional, Dict
from dataclasses import dataclass, field


@dataclass
class ToolCall:
    """Represents a tool call from the LLM."""
    id: str
    name: str
    arguments: dict


@dataclass
class LLMResponse:
    """Response from an LLM provider."""
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    finish_reason: str = "stop"
    usage: Optional[Dict] = None


class BaseProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def chat(
        self,
        messages: List[dict],
        tools: Optional[List[dict]] = None,
        temperature: float = 0.1,
        max_tokens: int = 8192,
    ) -> LLMResponse:
        """Send a chat request and return the response."""
        ...

    @abstractmethod
    def chat_stream(
        self,
        messages: List[dict],
        tools: Optional[List[dict]] = None,
        temperature: float = 0.1,
        max_tokens: int = 8192,
    ) -> Generator[str, None, Optional[LLMResponse]]:
        """Stream a chat response, yielding text chunks."""
        ...

    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the provider connection works."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider name."""
        ...
