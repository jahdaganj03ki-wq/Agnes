import logging
import time

from openai import OpenAI

from backend.app.config import settings

logger = logging.getLogger("agnes.prompt_enhancer")

client = OpenAI(
    api_key=settings.agnes_api_key,
    base_url="https://apihub.agnes-ai.com/v1",
)


def enhance(system_prompt: str, user_prompt: str) -> str:
    if not settings.agnes_api_key:
        raise RuntimeError("AGNES_API_KEY not configured")

    start = time.time()
    response = client.chat.completions.create(
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
