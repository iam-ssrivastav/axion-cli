"""
File editing tool for Axion CLI — search-and-replace within files.
"""

import os
from axion.tools.base import BaseTool


class FileEditTool(BaseTool):

    @property
    def name(self) -> str:
        return "edit_file"

    @property
    def description(self) -> str:
        return (
            "Edit an existing file by replacing a specific string/block of text with new content. "
            "The target_content must exactly match text in the file (including whitespace). "
            "Use this for surgical edits instead of rewriting entire files."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to edit.",
                },
                "target_content": {
                    "type": "string",
                    "description": "The exact text to find and replace. Must match the file content exactly.",
                },
                "replacement_content": {
                    "type": "string",
                    "description": "The new text to replace the target with.",
                },
            },
            "required": ["path", "target_content", "replacement_content"],
        }

    @property
    def requires_permission(self) -> bool:
        return True

    @property
    def permission_message(self) -> str:
        return "Edit file content (search and replace)"

    def execute(self, **kwargs) -> str:
        path = kwargs.get("path", "")
        target = kwargs.get("target_content", "")
        replacement = kwargs.get("replacement_content", "")

        if not path:
            return "Error: No file path provided."
        if not target:
            return "Error: No target content provided."

        if not os.path.isabs(path):
            path = os.path.abspath(path)

        if not os.path.exists(path):
            return f"Error: File not found: {path}"

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            if target not in content:
                return (
                    f"Error: Target content not found in {path}. "
                    "Make sure the text matches exactly (including whitespace and indentation)."
                )

            count = content.count(target)
            if count > 1:
                return (
                    f"Warning: Found {count} occurrences of the target text. "
                    "Please provide more context to make the match unique."
                )

            new_content = content.replace(target, replacement, 1)

            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)

            target_lines = target.count("\n") + 1
            replacement_lines = replacement.count("\n") + 1
            return (
                f"Edited {path}: replaced {target_lines} lines with {replacement_lines} lines."
            )

        except PermissionError:
            return f"Error: Permission denied: {path}"
        except Exception as e:
            return f"Error editing file: {str(e)}"
