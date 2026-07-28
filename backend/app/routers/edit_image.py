import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.app.models.schemas import EditRequest
from backend.app.services.pipeline import edit_image_pipeline

logger = logging.getLogger("agnes.router")
router = APIRouter()


@router.post("/edit-image")
async def edit_image(request: EditRequest):
    logger.info(
        "Edit image request: prompt=%s, ratio=%s, img_size=%d",
        request.prompt[:50],
        request.aspect_ratio,
        len(request.image_base64),
    )
    return StreamingResponse(
        edit_image_pipeline(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
