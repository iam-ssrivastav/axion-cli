"""
Ollama provider for Axion CLI — 100% free, local LLM.
Uses the OpenAI-compatible API that Ollama exposes.
"""

from __future__ import annotations

import json
from typing import Generator, List, Optional

from openai import OpenAI, APIConnectionError

from axion.providers.base import BaseProvider, LLMResponse, ToolCall


class OllamaProvider(BaseProvider):
    """Ollama provider using its OpenAI-compatible API."""

    def __init__(self, model: str = "llama3.1", base_url: str = "http://localhost:11434/v1"):
        self.model = model
        self.client = OpenAI(
            base_url=base_url,
            api_key="ollama",  # Ollama doesn't require an API key
        )

    @property
    def provider_name(self) -> str:
        return "Ollama (Local)"

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
        except APIConnectionError:
            raise ConnectionError(
                "Cannot connect to Ollama. Make sure Ollama is running:\n"
                "  brew install ollama\n"
                "  ollama serve\n"
                f"  ollama pull {self.model}"
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
                                "name": tc.function.name if tc.function and tc.function.name else "",
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

        except APIConnectionError:
            raise ConnectionError(
                "Cannot connect to Ollama. Make sure Ollama is running:\n"
                "  ollama serve\n"
                f"  ollama pull {self.model}"
            )

    def test_connection(self) -> bool:
        try:
            self.client.models.list()
            return True
        except Exception:
            return False
