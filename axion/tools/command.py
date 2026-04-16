"""
Command execution tool for Axion CLI.
"""

import subprocess
import os
from axion.tools.base import BaseTool


class CommandTool(BaseTool):

    @property
    def name(self) -> str:
        return "run_command"

    @property
    def description(self) -> str:
        return (
            "Execute a shell command and return its output. "
            "Use this to run build tools, tests, git commands, install packages, etc. "
            "Commands run in the current working directory. "
            "IMPORTANT: Do not run interactive commands that require user input."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute.",
                },
                "working_dir": {
                    "type": "string",
                    "description": "Optional working directory. Defaults to current directory.",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 60, max: 300).",
                },
            },
            "required": ["command"],
        }

    @property
    def requires_permission(self) -> bool:
        return True  # Always ask for command execution

    @property
    def permission_message(self) -> str:
        return "Execute shell command"

    def execute(self, **kwargs) -> str:
        command = kwargs.get("command", "")
        working_dir = kwargs.get("working_dir", os.getcwd())
        timeout = min(kwargs.get("timeout", 60), 300)

        if not command:
            return "Error: No command provided."

        if not os.path.isabs(working_dir):
            working_dir = os.path.abspath(working_dir)

        if not os.path.isdir(working_dir):
            return f"Error: Working directory not found: {working_dir}"

        # Block obviously dangerous commands
        dangerous_patterns = [
            "rm -rf /", "rm -rf /*", "mkfs", ":(){ :|:& };:",
            "> /dev/sd", "dd if=/dev/zero", "chmod -R 777 /",
        ]
        for pattern in dangerous_patterns:
            if pattern in command:
                return f"Error: Blocked dangerous command pattern: {pattern}"

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=working_dir,
                env={**os.environ, "PAGER": "cat"},
            )

            output_parts = []

            if result.stdout:
                stdout = result.stdout
                if len(stdout) > 10000:
                    stdout = stdout[:10000] + "\n... (output truncated)"
                output_parts.append(stdout)

            if result.stderr:
                stderr = result.stderr
                if len(stderr) > 5000:
                    stderr = stderr[:5000] + "\n... (stderr truncated)"
                output_parts.append(f"STDERR:\n{stderr}")

            output_parts.append(f"\nExit code: {result.returncode}")

            return "\n".join(output_parts)

        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {timeout} seconds."
        except Exception as e:
            return f"Error executing command: {str(e)}"
