import asyncio
import json
import logging
import random
from typing import AsyncGenerator

from backend.app.models.schemas import EditRequest, ErrorEvent, SSEEvent
from backend.app.services import image_generator, prompt_enhancer
from backend.app.services.skill_loader import build_system_prompt, load_all, get_content

logger = logging.getLogger("agnes.pipeline")


async def edit_image_pipeline(
    request: EditRequest,
) -> AsyncGenerator[str, None]:
    try:
        skills = load_all()
        if not skills:
            yield _sse("error", ErrorEvent(
                code="config_error", message="No skills loaded", step="skills", retryable=False
            ).model_dump())
            return

        for s in skills:
            content = get_content(s.name)
            yield _sse("skill_loading", {"skill": s.name})
            await asyncio.sleep(random.uniform(0.05, 0.2))
            yield _sse("skill_loaded", {"skill": s.name, "chars": len(content)})
            logger.info("Skill loaded: %s (%d chars)", s.name, len(content))

        yield _sse("enhancing", {})
        system_prompt = build_system_prompt(skills)
        try:
            enhanced = await asyncio.wait_for(
                asyncio.to_thread(prompt_enhancer.enhance, system_prompt, request.prompt),
                timeout=60.0,
            )
        except asyncio.TimeoutError:
            yield _sse("error", ErrorEvent(
                code="timeout", message="Prompt enhancement timed out", step="enhance"
            ).model_dump())
            return
        except Exception as e:
            yield _sse("error", ErrorEvent(
                code="server_error", message=str(e), step="enhance", retryable=True
            ).model_dump())
            return

        yield _sse("prompt_enhanced", {
            "original": request.prompt,
            "enhanced": enhanced,
        })

        yield _sse("generating", {})
        try:
            image_url, revised_prompt = await asyncio.wait_for(
                asyncio.to_thread(
                    image_generator.generate,
                    enhanced,
                    request.image_base64,
                    request.aspect_ratio,
                ),
                timeout=120.0,
            )
        except asyncio.TimeoutError:
            yield _sse("error", ErrorEvent(
                code="timeout", message="Image generation timed out", step="generate"
            ).model_dump())
            return
        except Exception as e:
            yield _sse("error", ErrorEvent(
                code="server_error", message=str(e), step="generate", retryable=True
            ).model_dump())
            return

        yield _sse("result", {
            "image_url": image_url,
            "revised_prompt": revised_prompt,
        })
        logger.info("Pipeline complete: %s", image_url[:60] if image_url else "")

    except Exception as e:
        logger.exception("Unexpected pipeline error")
        yield _sse("error", ErrorEvent(
            code="server_error", message=str(e), step=None, retryable=True
        ).model_dump())


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"
