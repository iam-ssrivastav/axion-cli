"""
Main interactive CLI session for Axion CLI.
This is the brain — orchestrating LLM calls, tool execution, and the conversation loop.
"""

from __future__ import annotations

import json
import os
import sys
import traceback
from typing import Generator, List, Optional

from axion.config import Config, DEFAULT_MODELS, DEFAULT_BASE_URLS
from axion.ui.terminal import TerminalUI
from axion.tools.base import create_tool_registry, ToolRegistry
from axion.providers.base import BaseProvider, LLMResponse, ToolCall


# System prompt that defines Axion's behavior
SYSTEM_PROMPT = """You are Axion, a powerful AI coding assistant running in the user's terminal.

You help users with:
- Understanding and navigating codebases
- Writing, editing, and debugging code
- Running commands and interpreting results
- Answering technical questions

## Guidelines
1. Be concise and direct. Terminal space is precious.
2. Use tools when you need to read files, write code, or run commands. Don't guess file contents.
3. When editing files, read the file first to understand the current content.
4. Always explain what you're doing and why before making changes.
5. For destructive operations (writing files, running commands), be careful and precise.
6. Format code blocks with the appropriate language identifier.
7. If unsure, ask the user rather than guessing.

## Current Context
- Working Directory: {working_dir}
- Operating System: {os_info}

You have these tools available:
- read_file: Read file contents
- write_file: Create or overwrite files
- edit_file: Make surgical edits to existing files
- run_command: Execute shell commands
- search_files: Search for patterns in code (grep/ripgrep)
- list_directory: List directory contents

Always use tools when you need to interact with the filesystem. Do NOT make up file contents."""


class InteractiveSession:
    """The main interactive session that runs the conversation loop."""

    def __init__(self, config: Config):
        self.config = config
        self.ui = TerminalUI(config.theme)
        self.tools = create_tool_registry()
        self.provider = self._create_provider()
        self.messages: List[dict] = []
        self.max_tool_iterations = 10  # Safety limit for tool call loops

    def _create_provider(self) -> BaseProvider:
        """Create the appropriate LLM provider based on config."""
        provider = self.config.provider.lower()

        if provider == "ollama":
            from axion.providers.ollama import OllamaProvider
            return OllamaProvider(
                model=self.config.model,
                base_url=self.config.base_url or "http://localhost:11434/v1",
            )
        elif provider == "gemini":
            from axion.providers.gemini import GeminiProvider
            if not self.config.api_key:
                self.ui.show_error(
                    "Gemini requires an API key. Set GEMINI_API_KEY environment variable\n"
                    "  or use: axion -p gemini -k YOUR_KEY\n"
                    "  Get a free key at: https://ai.google.dev/"
                )
                sys.exit(1)
            return GeminiProvider(
                model=self.config.model,
                api_key=self.config.api_key,
            )
        elif provider in ("groq", "openai"):
            from axion.providers.openai_compat import OpenAICompatProvider
            if not self.config.api_key:
                self.ui.show_error(
                    f"{provider.upper()} requires an API key. "
                    f"Set {provider.upper()}_API_KEY environment variable."
                )
                sys.exit(1)

            base_url = self.config.base_url or DEFAULT_BASE_URLS.get(
                provider, "https://api.openai.com/v1"
            )
            labels = {"groq": "Groq", "openai": "OpenAI"}

            return OpenAICompatProvider(
                model=self.config.model,
                api_key=self.config.api_key,
                base_url=base_url,
                provider_label=labels.get(provider, provider.upper()),
            )
        else:
            self.ui.show_error(f"Unknown provider: {provider}")
            sys.exit(1)

    def _build_system_prompt(self) -> str:
        """Build the system prompt with current context."""
        return SYSTEM_PROMPT.format(
            working_dir=self.config.working_dir,
            os_info=f"{os.uname().sysname} {os.uname().machine}",
        )

    def run(self, initial_prompt: Optional[str] = None):
        """Run the interactive session."""
        self.ui.show_banner()
        self.ui.show_config_info(
            self.config.provider,
            self.config.model,
            self.config.working_dir,
        )

        # Initialize system message
        self.messages = [
            {"role": "system", "content": self._build_system_prompt()}
        ]

        # If an initial prompt was provided, process it
        if initial_prompt:
            self._process_user_message(initial_prompt)

        # Main interaction loop
        while True:
            try:
                user_input = self.ui.get_user_input()

                if not user_input:
                    continue

                # Handle slash commands
                if user_input.startswith("/"):
                    should_continue = self._handle_command(user_input)
                    if not should_continue:
                        break
                    continue

                # Process the message
                self._process_user_message(user_input)

            except KeyboardInterrupt:
                self.ui.show_goodbye()
                break
            except Exception as e:
                self.ui.show_error(f"Unexpected error: {str(e)}")
                if os.environ.get("AXION_DEBUG"):
                    traceback.print_exc()

    def _handle_command(self, command: str) -> bool:
        """Handle slash commands. Returns False if should exit."""
        parts = command.strip().split(maxsplit=2)
        cmd = parts[0].lower()

        if cmd in ("/exit", "/quit", "/q"):
            self.ui.show_goodbye()
            return False

        elif cmd == "/help":
            self.ui.show_help()

        elif cmd == "/clear":
            self.messages = [
                {"role": "system", "content": self._build_system_prompt()}
            ]
            self.ui.clear_screen()
            self.ui.show_banner()
            self.ui.show_success("Conversation cleared.")

        elif cmd == "/config":
            if len(parts) >= 3 and parts[1].lower() == "set":
                self._handle_config_set(parts[2] if len(parts) > 2 else "")
            else:
                self.ui.show_config_info(
                    self.config.provider,
                    self.config.model,
                    self.config.working_dir,
                )

        elif cmd == "/theme":
            if len(parts) > 1:
                theme = parts[1].lower()
                if theme in ("dark", "light"):
                    self.config.theme = theme
                    self.ui = TerminalUI(theme)
                    self.ui.show_success(f"Theme changed to {theme}.")
                else:
                    self.ui.show_error("Available themes: dark, light")
            else:
                self.ui.show_info(f"Current theme: {self.config.theme}")

        elif cmd == "/model":
            if len(parts) > 1:
                self.config.model = parts[1]
                self.provider = self._create_provider()
                self.ui.show_success(f"Model changed to {parts[1]}.")
            else:
                self.ui.show_info(f"Current model: {self.config.model}")

        elif cmd == "/provider":
            if len(parts) > 1:
                new_provider = parts[1].lower()
                if new_provider in ("ollama", "gemini", "groq", "openai"):
                    self.config.provider = new_provider
                    if self.config.model in DEFAULT_MODELS.values():
                        self.config.model = DEFAULT_MODELS.get(new_provider, "llama3.1")
                    if new_provider in DEFAULT_BASE_URLS:
                        self.config.base_url = DEFAULT_BASE_URLS[new_provider]
                    self.config.resolve_api_key()
                    self.provider = self._create_provider()
                    self.ui.show_success(
                        f"Provider changed to {new_provider} (model: {self.config.model})"
                    )
                else:
                    self.ui.show_error("Available providers: ollama, gemini, groq, openai")
            else:
                self.ui.show_info(f"Current provider: {self.config.provider}")

        else:
            self.ui.show_warning(f"Unknown command: {cmd}. Type /help for available commands.")

        return True

    def _handle_config_set(self, args: str):
        """Handle /config set commands."""
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            self.ui.show_error("Usage: /config set <key> <value>")
            return

        key, value = parts[0], parts[1]
        valid_keys = ["temperature", "max_tokens", "auto_approve_reads"]

        if key not in valid_keys:
            self.ui.show_error(f"Valid config keys: {', '.join(valid_keys)}")
            return

        try:
            if key == "temperature":
                self.config.temperature = float(value)
            elif key == "max_tokens":
                self.config.max_tokens = int(value)
            elif key == "auto_approve_reads":
                self.config.auto_approve_reads = value.lower() in ("true", "1", "yes")
            self.ui.show_success(f"Set {key} = {value}")
        except ValueError:
            self.ui.show_error(f"Invalid value for {key}: {value}")

    def _process_user_message(self, user_input: str):
        """Process a user message through the LLM and handle tool calls."""
        self.messages.append({"role": "user", "content": user_input})

        # Trim history if too long
        self._trim_history()

        iteration = 0

        while iteration < self.max_tool_iterations:
            iteration += 1

            try:
                # Call the LLM
                response = self._call_llm()

                if response is None:
                    break

                # If we got text content, display it
                if response.content:
                    self.ui.show_ai_message(response.content)
                    self.messages.append({
                        "role": "assistant",
                        "content": response.content,
                    })

                # If we got tool calls, execute them
                if response.tool_calls:
                    # Add assistant message with tool calls for context
                    assistant_msg = {"role": "assistant", "content": response.content or ""}
                    if self.config.provider != "gemini":
                        # OpenAI format: include tool_calls in assistant message
                        assistant_msg["tool_calls"] = [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.name,
                                    "arguments": json.dumps(tc.arguments),
                                },
                            }
                            for tc in response.tool_calls
                        ]
                    if response.content is None:
                        # Only add if we didn't already add content above
                        self.messages.append(assistant_msg)

                    # Execute each tool call
                    all_results = self._execute_tool_calls(response.tool_calls)

                    if all_results is None:
                        # User denied permission, break the loop
                        self.messages.append({
                            "role": "user",
                            "content": "The user denied permission for the tool operation. Please suggest an alternative or explain what you were trying to do.",
                        })
                        continue

                    # Continue the loop to let LLM process tool results
                    continue
                else:
                    # No tool calls, we're done
                    break

            except ConnectionError as e:
                self.ui.show_error(str(e))
                # Remove the user message since we failed
                if self.messages and self.messages[-1]["role"] == "user":
                    self.messages.pop()
                break
            except Exception as e:
                self.ui.show_error(f"LLM error: {str(e)}")
                if os.environ.get("AXION_DEBUG"):
                    traceback.print_exc()
                break

        if iteration >= self.max_tool_iterations:
            self.ui.show_warning("Reached maximum tool call iterations. Stopping.")

    def _call_llm(self) -> Optional[LLMResponse]:
        """Call the LLM and handle streaming."""
        tool_schemas = self.tools.get_openai_schemas()

        with self.ui.show_thinking():
            try:
                response = self.provider.chat(
                    messages=self.messages,
                    tools=tool_schemas if tool_schemas else None,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                )
                return response
            except Exception:
                raise

    def _execute_tool_calls(self, tool_calls: List[ToolCall]) -> Optional[List[dict]]:
        """Execute tool calls and add results to messages.
        
        Returns list of results, or None if user denied permission.
        """
        results = []

        for tc in tool_calls:
            tool = self.tools.get(tc.name)

            if tool is None:
                self.ui.show_error(f"Unknown tool: {tc.name}")
                result = f"Error: Unknown tool '{tc.name}'"
                self._add_tool_result(tc, result)
                results.append({"name": tc.name, "result": result})
                continue

            # Show what tool is being called
            self.ui.show_tool_call(tc.name, tc.arguments)

            # Check if permission is needed
            if tool.requires_permission:
                # Always ask for destructive ops
                if tc.name in ("write_file", "edit_file", "run_command"):
                    allowed = self.ui.ask_permission(
                        tool.permission_message,
                        f"Tool: {tc.name}\nArgs: {json.dumps(tc.arguments, indent=2)}"
                    )
                    if not allowed:
                        self.ui.show_warning("Operation denied by user.")
                        return None

            # Execute the tool
            try:
                result = tool.execute(**tc.arguments)
                self.ui.show_tool_result(result, is_error=result.startswith("Error"))
            except Exception as e:
                result = f"Error executing {tc.name}: {str(e)}"
                self.ui.show_tool_result(result, is_error=True)

            self._add_tool_result(tc, result)
            results.append({"name": tc.name, "result": result})

        return results

    def _add_tool_result(self, tc: ToolCall, result: str):
        """Add a tool result to the message history."""
        if self.config.provider == "gemini":
            # Gemini uses a different format for tool results
            self.messages.append({
                "role": "user",
                "content": f"[Tool Result for {tc.name}]:\n{result}",
            })
        else:
            # OpenAI format
            self.messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "name": tc.name,
                "content": result,
            })

    def _trim_history(self):
        """Trim conversation history to stay within limits."""
        max_messages = self.config.history_size * 2 + 1  # +1 for system prompt

        if len(self.messages) > max_messages:
            # Keep system prompt + recent messages
            system = self.messages[0]
            recent = self.messages[-(max_messages - 1):]
            self.messages = [system] + recent
