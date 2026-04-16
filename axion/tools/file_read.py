"""
File reading tool for Axion CLI.
"""

import os
from axion.tools.base import BaseTool


class FileReadTool(BaseTool):

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return (
            "Read the contents of a file at the given path. "
            "Returns the file content as a string. "
            "Use this to understand code, configs, and other text files."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative path to the file to read.",
                },
                "start_line": {
                    "type": "integer",
                    "description": "Optional start line number (1-indexed). If not specified, reads from beginning.",
                },
                "end_line": {
                    "type": "integer",
                    "description": "Optional end line number (1-indexed, inclusive). If not specified, reads to end.",
                },
            },
            "required": ["path"],
        }

    @property
    def requires_permission(self) -> bool:
        return False  # Reading is safe

    def execute(self, **kwargs) -> str:
        path = kwargs.get("path", "")
        start_line = kwargs.get("start_line")
        end_line = kwargs.get("end_line")

        if not path:
            return "Error: No file path provided."

        # Resolve relative paths
        if not os.path.isabs(path):
            path = os.path.abspath(path)

        if not os.path.exists(path):
            return f"Error: File not found: {path}"

        if not os.path.isfile(path):
            return f"Error: Not a file: {path}"

        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            total_lines = len(lines)

            if start_line is not None or end_line is not None:
                start = max(1, start_line or 1) - 1  # Convert to 0-indexed
                end = min(total_lines, end_line or total_lines)
                lines = lines[start:end]
                header = f"[Lines {start + 1}-{end} of {total_lines}]\n"
            else:
                # Cap at 500 lines for very large files
                if total_lines > 500:
                    lines = lines[:500]
                    header = f"[Showing first 500 of {total_lines} lines. Use start_line/end_line for more.]\n"
                else:
                    header = f"[{total_lines} lines]\n"

            content = "".join(lines)
            return header + content

        except PermissionError:
            return f"Error: Permission denied: {path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"
