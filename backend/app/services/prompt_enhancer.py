import logging
import os
import threading
import time

from openai import OpenAI

from backend.app.config import settings

logger = logging.getLogger("agnes.prompt_enhancer")

_client: OpenAI | None = None
_client_lock = threading.Lock()


def _get_client() -> OpenAI:
    """Lazy-Initialized OpenAI-Client (nicht mehr auf Modulebene)."""
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                api_key = settings.agnes_api_key or os.environ.get("OPENAI_API_KEY")
                if not api_key:
                    raise RuntimeError("AGNES_API_KEY not configured")
                _client = OpenAI(
                    api_key=api_key,
                    base_url="https://apihub.agnes-ai.com/v1",
                )
    return _client


def enhance(system_prompt: str, user_prompt: str) -> str:
    if not settings.agnes_api_key and not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("AGNES_API_KEY not configured")

    start = time.time()
    response = _get_client().chat.completions.create(
        model="agnes-2.0-flash",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
    )
    elapsed = time.time() - start
    enhanced = response.choices[0].message.content or ""

    logger.info(
        "Enhanced prompt (%d → %d chars) in %.2fs",
        len(user_prompt),
        len(enhanced),
        elapsed,
    )
    return enhanced
