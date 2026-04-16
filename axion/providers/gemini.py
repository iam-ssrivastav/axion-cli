"""
Google Gemini provider for Axion CLI — generous free tier.
Uses the google-generativeai SDK directly for best tool calling support.
"""

from __future__ import annotations

import json
from typing import Generator, List, Optional

from axion.providers.base import BaseProvider, LLMResponse, ToolCall


class GeminiProvider(BaseProvider):
    """Google Gemini provider."""

    def __init__(self, model: str = "gemini-2.0-flash", api_key: str = ""):
        self.model = model
        self.api_key = api_key
        self._client = None

    def _get_client(self):
        """Lazy-initialize the Gemini client."""
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai
            except ImportError:
                raise ImportError(
                    "google-generativeai package not installed. Run:\n"
                    "  pip install google-generativeai"
                )
        return self._client

    @property
    def provider_name(self) -> str:
        return "Google Gemini"

    def _convert_tools_to_gemini(self, tools: List[dict]) -> list:
        """Convert OpenAI tool format to Gemini function declarations."""
        import google.generativeai as genai
        from google.generativeai.types import FunctionDeclaration, Tool

        declarations = []
        for tool in tools:
            func = tool.get("function", {})
            params = func.get("parameters", {})
            cleaned_params = self._clean_params_for_gemini(params)

            declarations.append(
                FunctionDeclaration(
                    name=func["name"],
                    description=func.get("description", ""),
                    parameters=cleaned_params,
                )
            )

        return [Tool(function_declarations=declarations)]

    def _clean_params_for_gemini(self, params: dict) -> dict:
        """Clean parameter schema for Gemini compatibility."""
        cleaned = {}
        if "type" in params:
            cleaned["type_"] = params["type"].upper()
        if "properties" in params:
            cleaned_props = {}
            for k, v in params["properties"].items():
                prop = {}
                if "type" in v:
                    prop["type_"] = v["type"].upper()
                if "description" in v:
                    prop["description"] = v["description"]
                cleaned_props[k] = prop
            cleaned["properties"] = cleaned_props
        if "required" in params:
            cleaned["required"] = params["required"]
        return cleaned

    def chat(
        self,
        messages: List[dict],
        tools: Optional[List[dict]] = None,
        temperature: float = 0.1,
        max_tokens: int = 8192,
    ) -> LLMResponse:
        genai = self._get_client()

        gemini_messages = self._convert_messages(messages)
        system_instruction = self._extract_system(messages)

        config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }

        model_kwargs = {"model_name": self.model}
        if system_instruction:
            model_kwargs["system_instruction"] = system_instruction

        model = genai.GenerativeModel(
            **model_kwargs,
            generation_config=config,
        )

        gemini_tools = None
        if tools:
            gemini_tools = self._convert_tools_to_gemini(tools)

        try:
            response = model.generate_content(
                gemini_messages,
                tools=gemini_tools,
            )

            content = None
            tool_calls = None

            if response.candidates:
                candidate = response.candidates[0]
                parts = candidate.content.parts

                text_parts = []
                tc_list = []

                for i, part in enumerate(parts):
                    if part.text:
                        text_parts.append(part.text)
                    if part.function_call:
                        fc = part.function_call
                        args = dict(fc.args) if fc.args else {}
                        tc_list.append(
                            ToolCall(
                                id=f"call_{i}",
                                name=fc.name,
                                arguments=args,
                            )
                        )

                if text_parts:
                    content = "".join(text_parts)
                if tc_list:
                    tool_calls = tc_list

            return LLMResponse(
                content=content,
                tool_calls=tool_calls,
                finish_reason="stop",
            )

        except Exception as e:
            error_msg = str(e)
            if "API_KEY" in error_msg.upper() or "401" in error_msg:
                raise ConnectionError(
                    "Invalid or missing Gemini API key. Get one free at:\n"
                    "  https://ai.google.dev/\n"
                    "Then set: export GEMINI_API_KEY='your-key'"
                )
            raise

    def chat_stream(
        self,
        messages: List[dict],
        tools: Optional[List[dict]] = None,
        temperature: float = 0.1,
        max_tokens: int = 8192,
    ) -> Generator[str, None, Optional[LLMResponse]]:
        genai = self._get_client()

        gemini_messages = self._convert_messages(messages)
        system_instruction = self._extract_system(messages)

        config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }

        model_kwargs = {"model_name": self.model}
        if system_instruction:
            model_kwargs["system_instruction"] = system_instruction

        model = genai.GenerativeModel(
            **model_kwargs,
            generation_config=config,
        )

        gemini_tools = None
        if tools:
            gemini_tools = self._convert_tools_to_gemini(tools)

        try:
            response = model.generate_content(
                gemini_messages,
                tools=gemini_tools,
                stream=True,
            )

            collected_content = ""
            collected_tool_calls = []

            for chunk in response:
                if chunk.candidates:
                    for part in chunk.candidates[0].content.parts:
                        if part.text:
                            collected_content += part.text
                            yield part.text
                        if part.function_call:
                            fc = part.function_call
                            collected_tool_calls.append(
                                ToolCall(
                                    id=f"call_{len(collected_tool_calls)}",
                                    name=fc.name,
                                    arguments=dict(fc.args) if fc.args else {},
                                )
                            )

            return LLMResponse(
                content=collected_content if collected_content else None,
                tool_calls=collected_tool_calls if collected_tool_calls else None,
                finish_reason="stop",
            )

        except Exception as e:
            error_msg = str(e)
            if "API_KEY" in error_msg.upper():
                raise ConnectionError(
                    "Invalid Gemini API key. Get one free at https://ai.google.dev/"
                )
            raise

    def _convert_messages(self, messages: List[dict]) -> list:
        """Convert OpenAI-format messages to Gemini format."""
        gemini_msgs = []

        for msg in messages:
            role = msg["role"]
            if role == "system":
                continue
            elif role == "assistant":
                gemini_msgs.append({
                    "role": "model",
                    "parts": [msg.get("content", "")],
                })
            elif role == "tool":
                gemini_msgs.append({
                    "role": "user",
                    "parts": [f"Tool result for {msg.get('name', 'tool')}: {msg.get('content', '')}"],
                })
            else:
                gemini_msgs.append({
                    "role": "user",
                    "parts": [msg.get("content", "")],
                })

        return gemini_msgs

    def _extract_system(self, messages: List[dict]) -> Optional[str]:
        """Extract system message content."""
        for msg in messages:
            if msg["role"] == "system":
                return msg["content"]
        return None

    def test_connection(self) -> bool:
        try:
            genai = self._get_client()
            model = genai.GenerativeModel(model_name=self.model)
            response = model.generate_content("Say hello in one word.")
            return bool(response.text)
        except Exception:
            return False
