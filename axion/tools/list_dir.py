"""
Directory listing tool for Axion CLI.
"""

import os
from axion.tools.base import BaseTool


class ListDirectoryTool(BaseTool):

    @property
    def name(self) -> str:
        return "list_directory"

    @property
    def description(self) -> str:
        return (
            "List the contents of a directory, showing files and subdirectories "
            "with their sizes. Use this to explore project structure."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path to list. Defaults to current directory.",
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Whether to list recursively (default: false). Be careful with large directories.",
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum recursion depth (default: 3). Only used if recursive is true.",
                },
            },
            "required": [],
        }

    @property
    def requires_permission(self) -> bool:
        return False

    def execute(self, **kwargs) -> str:
        path = kwargs.get("path", ".")
        recursive = kwargs.get("recursive", False)
        max_depth = kwargs.get("max_depth", 3)

        if not os.path.isabs(path):
            path = os.path.abspath(path)

        if not os.path.exists(path):
            return f"Error: Path not found: {path}"

        if not os.path.isdir(path):
            return f"Error: Not a directory: {path}"

        try:
            if recursive:
                return self._list_recursive(path, max_depth)
            else:
                return self._list_flat(path)
        except PermissionError:
            return f"Error: Permission denied: {path}"
        except Exception as e:
            return f"Error listing directory: {str(e)}"

    def _list_flat(self, path: str) -> str:
        """List directory contents non-recursively."""
        entries = []
        skip_dirs = {
            "node_modules", ".git", "__pycache__", ".venv", "venv",
            ".next", ".tox", "dist", "build", ".eggs",
        }

        try:
            items = sorted(os.listdir(path))
        except PermissionError:
            return f"Error: Permission denied: {path}"

        dirs = []
        files = []

        for item in items:
            if item in skip_dirs:
                continue

            full_path = os.path.join(path, item)

            if os.path.isdir(full_path):
                try:
                    child_count = len(os.listdir(full_path))
                except PermissionError:
                    child_count = "?"
                dirs.append(f"  📁 {item}/ ({child_count} items)")
            else:
                size = os.path.getsize(full_path)
                size_str = self._format_size(size)
                files.append(f"  📄 {item} ({size_str})")

        output = f"Directory: {path}\n\n"
        if dirs:
            output += "Directories:\n" + "\n".join(dirs) + "\n\n"
        if files:
            output += "Files:\n" + "\n".join(files) + "\n"
        if not dirs and not files:
            output += "(empty directory)\n"

        output += f"\nTotal: {len(dirs)} directories, {len(files)} files"
        return output

    def _list_recursive(self, path: str, max_depth: int, current_depth: int = 0) -> str:
        """List directory contents recursively as a tree."""
        lines = []
        if current_depth == 0:
            lines.append(f"{os.path.basename(path)}/")

        skip_dirs = {
            "node_modules", ".git", "__pycache__", ".venv", "venv",
            ".next", ".tox", "dist", "build", ".eggs",
        }

        try:
            items = sorted(os.listdir(path))
        except PermissionError:
            return f"Error: Permission denied: {path}"

        # Separate dirs and files
        dirs = []
        files = []
        for item in items:
            if item.startswith(".") and item not in (".env",):
                continue
            if item in skip_dirs:
                continue
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                dirs.append(item)
            else:
                files.append(item)

        all_items = dirs + files
        total_items = len(all_items)

        for idx, item in enumerate(all_items):
            is_last = idx == total_items - 1
            prefix = "  " * current_depth
            connector = "└── " if is_last else "├── "
            full_path = os.path.join(path, item)

            if os.path.isdir(full_path):
                lines.append(f"{prefix}{connector}📁 {item}/")
                if current_depth < max_depth - 1:
                    sub_result = self._list_recursive(
                        full_path, max_depth, current_depth + 1
                    )
                    if sub_result:
                        lines.append(sub_result)
            else:
                size = self._format_size(os.path.getsize(full_path))
                lines.append(f"{prefix}{connector}📄 {item} ({size})")

            # Cap total output
            if len(lines) > 200:
                lines.append(f"{prefix}    ... (truncated, too many files)")
                break

        return "\n".join(lines)

    def _format_size(self, size: int) -> str:
        """Format file size in human-readable form."""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"
