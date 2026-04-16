"""
File writing tool for Axion CLI.
"""

import os
from pathlib import Path
from axion.tools.base import BaseTool


class FileWriteTool(BaseTool):

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return (
            "Create a new file or overwrite an existing file with the given content. "
            "Parent directories will be created automatically if they don't exist. "
            "Use this to create new code files, configs, etc."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative path for the file to create/write.",
                },
                "content": {
                    "type": "string",
                    "description": "The complete file content to write.",
                },
            },
            "required": ["path", "content"],
        }

    @property
    def requires_permission(self) -> bool:
        return True  # Writing files is destructive

    @property
    def permission_message(self) -> str:
        return "Write to file (this will create or overwrite)"

    def execute(self, **kwargs) -> str:
        path = kwargs.get("path", "")
        content = kwargs.get("content", "")

        if not path:
            return "Error: No file path provided."

        # Resolve relative paths
        if not os.path.isabs(path):
            path = os.path.abspath(path)

        try:
            # Create parent directories
            Path(path).parent.mkdir(parents=True, exist_ok=True)

            existed = os.path.exists(path)

            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            action = "Updated" if existed else "Created"
            lines = content.count("\n") + (1 if content and not content.endswith("\n") else 0)
            return f"{action} file: {path} ({lines} lines, {len(content)} bytes)"

        except PermissionError:
            return f"Error: Permission denied: {path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"
