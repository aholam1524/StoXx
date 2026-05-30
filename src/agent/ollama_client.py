"""Minimal Ollama HTTP client for local, free proposal generation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class OllamaClient:
    model: str = "qwen2.5:0.5b"
    base_url: str = "http://localhost:11434"
    timeout_seconds: int = 300

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
        except requests.RequestException:
            return False
        models = response.json().get("models", [])
        return any(model.get("name") == self.model for model in models)

    def generate(self, prompt: str) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "system": (
                "You write strictly fact-based short-term stock research notes. "
                "Never invent indicators, news, moving averages, price levels, "
                "support/resistance, catalysts, or thresholds that are not provided."
            ),
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9,
                "num_predict": 320,
            },
        }
        response = requests.post(
            f"{self.base_url}/api/generate",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return str(response.json().get("response", "")).strip()
