import json
from unittest.mock import patch

import pytest

from backend.app.models.schemas import EditRequest, SkillInfo
from backend.app.services.pipeline import edit_image_pipeline


@pytest.mark.asyncio
async def test_pipeline_full_success():
    request = EditRequest(
        prompt="Recolor to red",
        image_base64="data:image/png;base64,abc",
        aspect_ratio="1:1",
    )

    with (
        patch("backend.app.services.pipeline.load_all") as mock_load,
        patch("backend.app.services.pipeline.get_content") as mock_content,
        patch("backend.app.services.pipeline.build_system_prompt") as mock_build,
        patch("backend.app.services.pipeline.prompt_enhancer.enhance") as mock_enhance,
        patch("backend.app.services.pipeline.image_generator.generate") as mock_gen,
    ):
        mock_load.return_value = [
            SkillInfo(name="TestSkill", chars=100),
        ]
        mock_content.return_value = "test content"
        mock_build.return_value = "system prompt"
        mock_enhance.return_value = "Enhanced: [Subject] + [Quality]"
        mock_gen.return_value = ("https://example.com/result.png", "Revised prompt")

        events = []
        async for sse_str in edit_image_pipeline(request):
            events.append(_parse_sse(sse_str))

        event_types = [e["event"] for e in events]
        assert event_types == [
            "skill_loading",
            "skill_loaded",
            "enhancing",
            "prompt_enhanced",
            "generating",
            "result",
        ]
        assert events[-1]["data"]["image_url"] == "https://example.com/result.png"


@pytest.mark.asyncio
async def test_pipeline_enhance_error():
    request = EditRequest(prompt="test", image_base64="data:image/png;base64,x")

    with (
        patch("backend.app.services.pipeline.load_all") as mock_load,
        patch("backend.app.services.pipeline.get_content") as mock_content,
        patch("backend.app.services.pipeline.prompt_enhancer.enhance") as mock_enhance,
    ):
        mock_load.return_value = [SkillInfo(name="S", chars=10)]
        mock_content.return_value = "c"
        mock_enhance.side_effect = RuntimeError("API error")

        events = []
        async for sse_str in edit_image_pipeline(request):
            events.append(_parse_sse(sse_str))

        assert events[-1]["event"] == "error"
        assert events[-1]["data"]["step"] == "enhance"


@pytest.mark.asyncio
async def test_pipeline_no_skills():
    request = EditRequest(prompt="test", image_base64="data:image/png;base64,x")

    with patch("backend.app.services.pipeline.load_all") as mock_load:
        mock_load.return_value = []

        events = []
        async for sse_str in edit_image_pipeline(request):
            events.append(_parse_sse(sse_str))

        assert events[0]["event"] == "error"
        assert events[0]["data"]["code"] == "config_error"


def _parse_sse(sse_str: str) -> dict:
    lines = sse_str.strip().split("\n")
    event = ""
    data = {}
    for line in lines:
        if line.startswith("event: "):
            event = line[7:]
        elif line.startswith("data: "):
            data = json.loads(line[6:])
    return {"event": event, "data": data}
