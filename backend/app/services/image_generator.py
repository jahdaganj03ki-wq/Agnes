import json
import logging
import time

import httpx

from backend.app.config import settings

logger = logging.getLogger("agnes.image_generator")

BASE_URL = "https://apihub.agnes-ai.com/v1"


def generate(
    prompt: str,
    image_base64: str,
    aspect_ratio: str = "1:1",
) -> tuple[str, str | None]:
    if not settings.agnes_api_key:
        raise RuntimeError("AGNES_API_KEY not configured")

    # Image strength: 0.0 = max preservation (barely change), 1.0 = full regeneration
    # 0.6-0.8 offers a balance: edits targeted areas while mostly preserving the original
    image_strength = 0.65

    body: dict = {
        "model": "agnes-image-2.1-flash",
        "prompt": prompt,
        "ratio": aspect_ratio,
        "strength": image_strength,
        "extra_body": {
            "response_format": "url",
        },
    }
    if image_base64:
        body["extra_body"]["image"] = [image_base64]

    start = time.time()
    with httpx.Client() as client:
        resp = client.post(
            f"{BASE_URL}/images/generations",
            headers={
                "Authorization": f"Bearer {settings.agnes_api_key}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=120.0,
        )
        resp.raise_for_status()
        data = resp.json()
    elapsed = time.time() - start

    image_url = ""
    revised_prompt = None
    if data.get("data"):
        item = data["data"][0]
        image_url = item.get("url", "")
        revised_prompt = item.get("revised_prompt")

    logger.info(
        "Generated image in %.2fs (url=%s)",
        elapsed,
        image_url[:60] if image_url else "none",
    )
    return image_url, revised_prompt
