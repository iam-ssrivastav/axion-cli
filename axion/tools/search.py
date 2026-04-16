"""
Grep/search tool for Axion CLI.
"""

import subprocess
import os
from axion.tools.base import BaseTool


class GrepSearchTool(BaseTool):

    @property
    def name(self) -> str:
        return "search_files"

    @property
    def description(self) -> str:
        return (
            "Search for a pattern in files using grep. "
            "Returns matching lines with file paths and line numbers. "
            "Use this to find code patterns, function definitions, usages, etc."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "The search pattern (supports regex).",
                },
                "path": {
                    "type": "string",
                    "description": "Directory or file to search in. Defaults to current directory.",
                },
                "include": {
                    "type": "string",
                    "description": "Glob pattern to filter files, e.g., '*.py', '*.js'. Optional.",
                },
                "case_insensitive": {
                    "type": "boolean",
                    "description": "Whether to perform case-insensitive search. Default: false.",
                },
            },
            "required": ["pattern"],
        }

    @property
    def requires_permission(self) -> bool:
        return False  # Searching is safe

    def execute(self, **kwargs) -> str:
        pattern = kwargs.get("pattern", "")
        path = kwargs.get("path", ".")
        include = kwargs.get("include", "")
        case_insensitive = kwargs.get("case_insensitive", False)

        if not pattern:
            return "Error: No search pattern provided."

        if not os.path.isabs(path):
            path = os.path.abspath(path)

        if not os.path.exists(path):
            return f"Error: Path not found: {path}"

        # Try ripgrep first, fall back to grep
        rg_available = _check_command("rg")

        if rg_available:
            cmd = ["rg", "--no-heading", "-n", "--max-count=50"]
            if case_insensitive:
                cmd.append("-i")
            if include:
                cmd.extend(["-g", include])
            # Exclude common non-code directories
            cmd.extend([
                "-g", "!node_modules",
                "-g", "!.git",
                "-g", "!__pycache__",
                "-g", "!*.pyc",
                "-g", "!.venv",
                "-g", "!venv",
            ])
            cmd.extend([pattern, path])
        else:
            cmd = ["grep", "-rnI"]
            if case_insensitive:
                cmd.append("-i")
            if include:
                cmd.extend(["--include", include])
            cmd.extend([
                "--exclude-dir=node_modules",
                "--exclude-dir=.git",
                "--exclude-dir=__pycache__",
                "--exclude-dir=.venv",
                "--exclude-dir=venv",
            ])
            cmd.extend([pattern, path])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 1:
                return "No matches found."

            if result.returncode > 1:
                error = result.stderr.strip()
                return f"Search error: {error}"

            output = result.stdout
            # Limit output lines
            lines = output.split("\n")
            if len(lines) > 50:
                output = "\n".join(lines[:50]) + "\n... (results truncated, try a more specific pattern)"

            if len(output) > 8000:
                output = output[:8000] + "\n... (results truncated)"

            match_count = min(len(lines), 50)
            return f"Found {match_count} matches:\n\n{output}"

        except subprocess.TimeoutExpired:
            return "Error: Search timed out. Try a more specific pattern or smaller directory."
        except FileNotFoundError:
            return "Error: Neither 'rg' (ripgrep) nor 'grep' found. Please install one."
        except Exception as e:
            return f"Error during search: {str(e)}"


def _check_command(cmd: str) -> bool:
    """Check if a command is available on PATH."""
    try:
        result = subprocess.run(
            ["which", cmd],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False
