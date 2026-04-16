"""
Base tool interface and registry for Axion CLI.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseTool(ABC):
    """Abstract base class for all Axion tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool name."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this tool does."""
        ...

    @property
    @abstractmethod
    def parameters(self) -> dict:
        """JSON Schema for tool parameters."""
        ...

    @property
    def requires_permission(self) -> bool:
        """Whether this tool needs user confirmation before running."""
        return False

    @property
    def permission_message(self) -> str:
        """Message to show when asking for permission."""
        return f"Execute tool: {self.name}"

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Execute the tool with given parameters. Returns result as string."""
        ...

    def get_openai_schema(self) -> dict:
        """Get the OpenAI function-calling compatible schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def get_gemini_schema(self) -> dict:
        """Get Google Gemini function declaration schema."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


class ToolRegistry:
    """Registry of all available tools."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        """Register a tool."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def all_tools(self) -> List[BaseTool]:
        """Get all registered tools."""
        return list(self._tools.values())

    def get_openai_schemas(self) -> List[dict]:
        """Get all tool schemas in OpenAI format."""
        return [tool.get_openai_schema() for tool in self._tools.values()]

    def get_gemini_declarations(self) -> List[dict]:
        """Get all tool schemas in Gemini format."""
        return [tool.get_gemini_schema() for tool in self._tools.values()]


def create_tool_registry() -> ToolRegistry:
    """Create and populate the default tool registry."""
    from axion.tools.file_read import FileReadTool
    from axion.tools.file_write import FileWriteTool
    from axion.tools.file_edit import FileEditTool
    from axion.tools.command import CommandTool
    from axion.tools.search import GrepSearchTool
    from axion.tools.list_dir import ListDirectoryTool

    registry = ToolRegistry()
    registry.register(FileReadTool())
    registry.register(FileWriteTool())
    registry.register(FileEditTool())
    registry.register(CommandTool())
    registry.register(GrepSearchTool())
    registry.register(ListDirectoryTool())

    return registry
