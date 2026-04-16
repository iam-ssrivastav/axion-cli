"""
Terminal UI rendering for Axion CLI.
Uses Rich library for beautiful terminal output.
"""

import os
import sys
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.table import Table
from rich.live import Live
from rich.spinner import Spinner
from rich.rule import Rule
from rich import box

from axion.ui.themes import get_theme
from axion import __version__


class TerminalUI:
    """Handles all terminal rendering for Axion CLI."""

    def __init__(self, theme_name: str = "dark"):
        self.console = Console()
        self.theme = get_theme(theme_name)
        self.width = min(self.console.width, 120)

    def show_banner(self):
        """Display the startup banner."""
        banner_text = Text()
        banner_text.append("  ⚛  ", style=f"bold {self.theme['primary']}")
        banner_text.append("A", style=f"bold {self.theme['primary']}")
        banner_text.append("X", style=f"bold {self.theme['secondary']}")
        banner_text.append("I", style=f"bold {self.theme['accent']}")
        banner_text.append("O", style=f"bold {self.theme['success']}")
        banner_text.append("N", style=f"bold {self.theme['info']}")
        banner_text.append(f"  v{__version__}", style=f"{self.theme['muted']}")

        self.console.print()
        self.console.print(
            Panel(
                banner_text,
                subtitle=f"[{self.theme['muted']}]Free & Open Source AI Coding Assistant[/]",
                border_style=self.theme["primary"],
                box=box.DOUBLE_EDGE,
                padding=(0, 2),
            )
        )

    def show_config_info(self, provider: str, model: str, working_dir: str):
        """Show current configuration summary."""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column(style=f"{self.theme['muted']}")
        table.add_column(style=f"bold {self.theme['secondary']}")

        table.add_row("  Provider", provider.upper())
        table.add_row("  Model", model)
        table.add_row("  Directory", self._truncate_path(working_dir))

        self.console.print(table)
        self.console.print(
            f"\n  [{self.theme['muted']}]Type your message to chat. "
            f"Commands: /help, /config, /clear, /exit[/]"
        )
        self.console.print(
            Rule(style=self.theme["border"])
        )

    def show_help(self):
        """Display help information."""
        help_table = Table(
            title="⚛ Axion Commands",
            title_style=f"bold {self.theme['primary']}",
            box=box.ROUNDED,
            border_style=self.theme["border"],
            show_lines=True,
        )
        help_table.add_column("Command", style=f"bold {self.theme['secondary']}", min_width=20)
        help_table.add_column("Description", style=self.theme["text"])

        commands = [
            ("/help", "Show this help message"),
            ("/config", "Show current configuration"),
            ("/config set <key> <value>", "Update a config value"),
            ("/clear", "Clear conversation history"),
            ("/theme <dark|light>", "Switch color theme"),
            ("/model <name>", "Switch to a different model"),
            ("/provider <name>", "Switch LLM provider"),
            ("/exit, /quit, Ctrl+C", "Exit Axion"),
        ]

        for cmd, desc in commands:
            help_table.add_row(cmd, desc)

        self.console.print()
        self.console.print(help_table)
        self.console.print()

    def get_user_input(self) -> str:
        """Get input from the user with a styled prompt."""
        try:
            self.console.print()
            prompt_text = f"[bold {self.theme['user_prompt']}]  ❯ You:[/] "
            user_input = self.console.input(prompt_text)
            return user_input.strip()
        except (EOFError, KeyboardInterrupt):
            return "/exit"

    def show_thinking(self):
        """Show a thinking indicator."""
        return self.console.status(
            f"[bold {self.theme['secondary']}]  ⚛ Thinking...[/]",
            spinner="dots",
            spinner_style=self.theme["primary"],
        )

    def show_ai_message(self, content: str):
        """Render an AI response with markdown formatting."""
        self.console.print()
        self.console.print(
            f"  [bold {self.theme['secondary']}]⚛ Axion:[/]"
        )
        self.console.print()

        # Render as markdown for rich formatting
        md = Markdown(content, code_theme="monokai")
        self.console.print(md, width=self.width - 4)

    def show_ai_message_streaming(self, content: str):
        """Update the streaming AI response."""
        self.console.print()
        self.console.print(
            f"  [bold {self.theme['secondary']}]⚛ Axion:[/]"
        )
        self.console.print()
        md = Markdown(content, code_theme="monokai")
        self.console.print(md, width=self.width - 4)

    def show_tool_call(self, tool_name: str, args: dict):
        """Display a tool being called."""
        self.console.print()

        # Tool name header
        tool_text = Text()
        tool_text.append("  🔧 ", style="bold")
        tool_text.append(f"Tool: ", style=f"{self.theme['muted']}")
        tool_text.append(f"{tool_name}", style=f"bold {self.theme['tool_name']}")

        self.console.print(tool_text)

        # Tool arguments
        for key, value in args.items():
            val_display = str(value)
            if len(val_display) > 200:
                val_display = val_display[:200] + "..."
            self.console.print(
                f"    [{self.theme['tool_arg']}]{key}:[/] {val_display}"
            )

    def show_tool_result(self, result: str, is_error: bool = False):
        """Display tool execution result."""
        if is_error:
            style = self.theme["error"]
            icon = "✗"
        else:
            style = self.theme["success"]
            icon = "✓"

        result_display = result
        if len(result_display) > 1000:
            result_display = result_display[:1000] + "\n... (truncated)"

        self.console.print(
            Panel(
                result_display,
                title=f"[bold {style}]{icon} Result[/]",
                border_style=style,
                box=box.ROUNDED,
                padding=(0, 1),
            )
        )

    def ask_permission(self, action: str, details: str = "") -> bool:
        """Ask user for permission to execute a potentially dangerous action."""
        self.console.print()
        self.console.print(
            Panel(
                f"[bold {self.theme['warning']}]⚠ Permission Required[/]\n\n"
                f"{action}\n"
                f"[{self.theme['muted']}]{details}[/]" if details else
                f"[bold {self.theme['warning']}]⚠ Permission Required[/]\n\n{action}",
                border_style=self.theme["warning"],
                box=box.ROUNDED,
            )
        )

        try:
            response = self.console.input(
                f"  [{self.theme['warning']}]Allow? (y/n):[/] "
            ).strip().lower()
            return response in ("y", "yes")
        except (EOFError, KeyboardInterrupt):
            return False

    def show_error(self, message: str):
        """Display an error message."""
        self.console.print(
            f"\n  [{self.theme['error']}]✗ Error: {message}[/]\n"
        )

    def show_warning(self, message: str):
        """Display a warning."""
        self.console.print(
            f"\n  [{self.theme['warning']}]⚠ {message}[/]"
        )

    def show_info(self, message: str):
        """Display an info message."""
        self.console.print(
            f"\n  [{self.theme['info']}]ℹ {message}[/]"
        )

    def show_success(self, message: str):
        """Display a success message."""
        self.console.print(
            f"\n  [{self.theme['success']}]✓ {message}[/]"
        )

    def show_goodbye(self):
        """Show exit message."""
        self.console.print(
            f"\n  [{self.theme['primary']}]⚛ Goodbye! Happy coding! 👋[/]\n"
        )

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system("cls" if os.name == "nt" else "clear")

    def _truncate_path(self, path: str, max_len: int = 60) -> str:
        """Truncate a path for display."""
        if len(path) <= max_len:
            return path
        return "..." + path[-(max_len - 3):]
