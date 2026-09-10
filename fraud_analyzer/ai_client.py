from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()


def _first_env(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value is not None and value.strip() != "":
            return value
    return None


@dataclass
class FreeAIConfig:
    provider: str = "openrouter"
    model: str | None = None
    api_key: str | None = None
    base_url: str | None = None

    @classmethod
    def from_env(cls) -> "FreeAIConfig":
        provider = (os.getenv("FRAUD_ANALYZER_PROVIDER", "openrouter") or "openrouter").lower()
        provider_prefix = provider.upper().replace("-", "_")
        return cls(
            provider=provider,
            model=_first_env(
                f"FRAUD_ANALYZER_{provider_prefix}_MODEL",
                "FRAUD_ANALYZER_MODEL",
                f"{provider_prefix}_MODEL",
            ),
            api_key=_first_env(
                f"FRAUD_ANALYZER_{provider_prefix}_API_KEY",
                "FRAUD_ANALYZER_API_KEY",
                f"{provider_prefix}_API_KEY",
            ),
            base_url=_first_env(
                f"FRAUD_ANALYZER_{provider_prefix}_BASE_URL",
                "FRAUD_ANALYZER_BASE_URL",
                f"{provider_prefix}_BASE_URL",
            ),
        )


def _build_headers(config: FreeAIConfig) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"
    return headers


def ai_extract_structured_json(prompt: str, input_text: str, config: FreeAIConfig | None = None) -> dict[str, Any]:
    config = config or FreeAIConfig.from_env()
    provider = (config.provider or "openrouter").lower()
    if not config.model:
        config.model = {
            "openrouter": "openai/gpt-oss-20b",
            "groq": "llama-3.1-8b-instant",
            "gemini": "gemini-2.0-flash",
            "ollama": "llama3.1:8b",
        }.get(provider, "openai/gpt-oss-20b")

    if provider == "gemini":
        if not config.api_key:
            raise ValueError("Gemini requires FRAUD_ANALYZER_GEMINI_API_KEY or FRAUD_ANALYZER_API_KEY.")
        url = f"{config.base_url or 'https://generativelanguage.googleapis.com/v1beta'}/models/{config.model}:generateContent?key={config.api_key}"
        payload = {
            "contents": [{"parts": [{"text": f"{prompt}\n\n{input_text}"}]}],
            "generationConfig": {"responseMimeType": "application/json"},
        }
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        raw = response.json()
        try:
            return json.loads(raw["candidates"][0]["content"]["parts"][0]["text"])  # type: ignore[index]
        except (KeyError, TypeError, ValueError):
            return {"raw_response": raw}

    if provider == "ollama":
        url = f"{config.base_url or 'http://localhost:11434'}/api/chat"
        payload = {
            "model": config.model,
            "messages": [{"role": "user", "content": f"{prompt}\n\n{input_text}"}],
            "stream": False,
        }
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        raw = response.json()
        content = raw.get("message", {}).get("content", "")
        try:
            return json.loads(content)
        except ValueError:
            return {"raw_response": content}

    url = f"{config.base_url or 'https://openrouter.ai/api/v1'}/chat/completions"
    payload = {
        "model": config.model,
        "messages": [{"role": "user", "content": f"{prompt}\n\n{input_text}"}],
        "temperature": 0.1,
    }
    response = requests.post(url, headers=_build_headers(config), json=payload, timeout=60)
    response.raise_for_status()
    raw = response.json()
    content = raw["choices"][0]["message"]["content"]
    try:
        return json.loads(content)
    except ValueError:
        return {"raw_response": content}
