"""
OpenAI-compatible provider for Axion CLI.
Works with Groq, Together, Fireworks, and any OpenAI-compatible API.
"""

from __future__ import annotations

import json
from typing import Generator, List, Optional

from openai import OpenAI, APIConnectionError, AuthenticationError

from axion.providers.base import BaseProvider, LLMResponse, ToolCall


class OpenAICompatProvider(BaseProvider):
    """Generic OpenAI-compatible provider (Groq, OpenAI, Together, etc.)."""

    def __init__(
        self,
        model: str,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        provider_label: str = "OpenAI-Compatible",
    ):
        self.model = model
        self._provider_label = provider_label
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    @property
    def provider_name(self) -> str:
        return self._provider_label

    def chat(
        self,
        messages: List[dict],
        tools: Optional[List[dict]] = None,
        temperature: float = 0.1,
        max_tokens: int = 8192,
    ) -> LLMResponse:
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        try:
            response = self.client.chat.completions.create(**kwargs)
            choice = response.choices[0]

            tool_calls = None
            if choice.message.tool_calls:
                tool_calls = []
                for tc in choice.message.tool_calls:
                    args = tc.function.arguments
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except json.JSONDecodeError:
                            args = {"raw": args}
                    tool_calls.append(
                        ToolCall(
                            id=tc.id,
                            name=tc.function.name,
                            arguments=args,
                        )
                    )

            return LLMResponse(
                content=choice.message.content,
                tool_calls=tool_calls,
                finish_reason=choice.finish_reason or "stop",
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                },
            )

        except AuthenticationError:
            raise ConnectionError(
                f"Authentication failed for {self._provider_label}. "
                "Check your API key."
            )
        except APIConnectionError:
            raise ConnectionError(
                f"Cannot connect to {self._provider_label}. "
                "Check the base URL and your internet connection."
            )

    def chat_stream(
        self,
        messages: List[dict],
        tools: Optional[List[dict]] = None,
        temperature: float = 0.1,
        max_tokens: int = 8192,
    ) -> Generator[str, None, Optional[LLMResponse]]:
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        try:
            stream = self.client.chat.completions.create(**kwargs)

            collected_content = ""
            collected_tool_calls = {}
            finish_reason = "stop"

            for chunk in stream:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta
                finish_reason = chunk.choices[0].finish_reason or finish_reason

                if delta.content:
                    collected_content += delta.content
                    yield delta.content

                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        idx = tc.index
                        if idx not in collected_tool_calls:
                            collected_tool_calls[idx] = {
                                "id": tc.id or f"call_{idx}",
                                "name": "",
                                "arguments": "",
                            }
                        if tc.function and tc.function.name:
                            collected_tool_calls[idx]["name"] = tc.function.name
                        if tc.id:
                            collected_tool_calls[idx]["id"] = tc.id
                        if tc.function and tc.function.arguments:
                            collected_tool_calls[idx]["arguments"] += tc.function.arguments

            tool_calls = None
            if collected_tool_calls:
                tool_calls = []
                for tc_data in collected_tool_calls.values():
                    args = tc_data["arguments"]
                    try:
                        args = json.loads(args) if args else {}
                    except json.JSONDecodeError:
                        args = {"raw": args}
                    tool_calls.append(
                        ToolCall(
                            id=tc_data["id"],
                            name=tc_data["name"],
                            arguments=args,
                        )
                    )

            return LLMResponse(
                content=collected_content if collected_content else None,
                tool_calls=tool_calls,
                finish_reason=finish_reason,
            )

        except AuthenticationError:
            raise ConnectionError(
                f"Authentication failed for {self._provider_label}."
            )
        except APIConnectionError:
            raise ConnectionError(
                f"Cannot connect to {self._provider_label}."
            )

    def test_connection(self) -> bool:
        try:
            self.client.models.list()
            return True
        except Exception:
            return False
