"""Shared utilities used across agents.

The most important helper here is :func:`call_llm_json`, which wraps the OpenAI
SDK with the JSON-parsing-and-retry behaviour required by the spec's
error-handling section: if the model returns non-JSON, we retry once with an
explicit reminder, then fall back to a caller-supplied default.
"""

import os
import json
import re
from typing import Any, Optional

from openai import OpenAI

from utils.logger import get_logger

log = get_logger("helpers")

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# A single shared client. Reads OPENAI_API_KEY from the environment.
_client: Optional[OpenAI] = None


def get_client() -> OpenAI:
    """Lazily construct and cache the OpenAI client."""
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


def _extract_json(text: str) -> Any:
    """Best-effort extraction of a JSON object/array from a model response.

    Handles bare JSON, JSON wrapped in fenced code blocks, and JSON with leading
    or trailing prose by locating the outermost braces/brackets.
    """
    text = text.strip()

    # Strip Markdown code fences if present.
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()

    # Fast path: the whole thing is JSON.
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fall back: grab the first {...} or [...] span.
    for open_ch, close_ch in (("{", "}"), ("[", "]")):
        start = text.find(open_ch)
        end = text.rfind(close_ch)
        if start != -1 and end != -1 and end > start:
            candidate = text[start : end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue
    raise json.JSONDecodeError("No JSON object found", text, 0)


def call_llm_text(
    system: str,
    user: str,
    *,
    model: Optional[str] = None,
    max_tokens: int = 4096,
    temperature: float = 0.2,
    json_mode: bool = False,
) -> str:
    """Call the LLM and return the raw text of the response.

    When ``json_mode`` is True, OpenAI's native JSON response format is requested
    so the model is constrained to emit a valid JSON object.
    """
    client = get_client()
    kwargs = dict(
        model=model or DEFAULT_MODEL,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    resp = client.chat.completions.create(**kwargs)
    return (resp.choices[0].message.content or "").strip()


def call_llm_json(
    system: str,
    user: str,
    *,
    default: Any,
    model: Optional[str] = None,
    max_tokens: int = 4096,
    temperature: float = 0.2,
) -> Any:
    """Call the LLM expecting JSON. Retry once on parse failure, then fall back.

    Per the spec error-handling requirements:
      * If the LLM call itself raises, log and return ``default``.
      * If JSON parsing fails, retry once with a hard "respond ONLY with JSON"
        reminder appended to the user message.
      * If it still fails, return ``default``.
    """
    try:
        text = call_llm_text(
            system, user, model=model, max_tokens=max_tokens,
            temperature=temperature, json_mode=True,
        )
    except Exception as exc:  # network / API failure
        log.error("LLM call failed: %s", exc)
        return default

    try:
        return _extract_json(text)
    except json.JSONDecodeError:
        log.warning("First response was not valid JSON; retrying with reminder.")

    # Retry once with an explicit reminder.
    reminder = (
        user
        + "\n\nIMPORTANT: Respond ONLY with a single valid JSON object. "
        "No markdown, no code fences, no preamble, no trailing text."
    )
    try:
        text = call_llm_text(
            system, reminder, model=model, max_tokens=max_tokens,
            temperature=0.0, json_mode=True,
        )
        return _extract_json(text)
    except Exception as exc:
        log.error("JSON retry failed (%s); falling back to default.", exc)
        return default


# Backwards-compatible aliases (earlier the pipeline targeted a different SDK).
call_claude_text = call_llm_text
call_claude_json = call_llm_json


def truncate(text: str, max_chars: int) -> str:
    """Truncate a string to ``max_chars`` with an ellipsis marker."""
    if text is None:
        return ""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + " ...[truncated]"
