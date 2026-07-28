from pydantic import BaseModel


class EditRequest(BaseModel):
    prompt: str
    image_base64: str
    aspect_ratio: str = "1:1"


class SkillInfo(BaseModel):
    name: str
    chars: int


class PromptEnhancement(BaseModel):
    original: str
    enhanced: str


class GenerationResult(BaseModel):
    image_url: str
    revised_prompt: str | None = None


class SSEEvent(BaseModel):
    event: str
    data: dict


class ErrorEvent(BaseModel):
    code: str
    message: str
    step: str | None = None
    retryable: bool = True
