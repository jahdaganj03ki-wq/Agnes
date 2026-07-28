import os
from functools import lru_cache

from backend.app.models.schemas import SkillInfo

EXTRACTED_PATH = os.path.join(os.path.dirname(__file__), "../../skills/extracted")


@lru_cache(maxsize=1)
def load_all() -> list[SkillInfo]:
    skills: list[SkillInfo] = []

    if not os.path.isdir(EXTRACTED_PATH):
        return skills

    for fname in sorted(os.listdir(EXTRACTED_PATH)):
        if not fname.endswith(".extracted.md"):
            continue
        fpath = os.path.join(EXTRACTED_PATH, fname)
        with open(fpath, encoding="utf-8") as f:
            content = f.read()
        name = fname.replace(".extracted.md", "")
        skills.append(SkillInfo(name=name, chars=len(content)))

    return skills


def get_content(name: str) -> str:
    fpath = os.path.join(EXTRACTED_PATH, f"{name}.extracted.md")
    if not os.path.isfile(fpath):
        return ""
    with open(fpath, encoding="utf-8") as f:
        return f.read()


def build_system_prompt(skills: list[SkillInfo]) -> str:
    parts: list[str] = []
    for s in skills:
        content = get_content(s.name)
        if content:
            parts.append(f"=== {s.name} ===\n{content}")
    parts.append(
        "\n\n=== ENHANCEMENT INSTRUCTION ===\n"
        "Enhance the user's image edit prompt following the format below. "
        "The output will be sent to an image-to-image model along with the original photo.\n\n"
        "FORMAT:\n"
        "ORIGINAL IMAGE DESCRIPTION: [describe what the original likely shows: subject, setting, clothing, lighting]\n"
        "EDIT INSTRUCTION: Change ONLY [precise description of what to edit]\n"
        "PRESERVE ALL OF THE FOLLOWING EXACTLY:\n"
        "- The person's identity, face, facial features, expression, skin tone\n"
        "- Hair style, color, and texture\n"
        "- Body pose, posture, hand position, body proportions\n"
        "- Background, setting, environment, location\n"
        "- Lighting direction, intensity, shadows, highlights\n"
        "- Image composition, framing, camera angle, perspective\n"
        "- ALL other clothing items NOT mentioned in the edit\n"
        "- Colors NOT mentioned in the edit\n"
        "- Image quality and style\n\n"
        "NEGATIVE INSTRUCTION: Do NOT change anything about the person's identity, face, pose, background, "
        "or any detail not explicitly mentioned in the EDIT INSTRUCTION.\n\n"
        "IMPORTANT: The enhanced prompt must make the image model understand that "
        "EVERYTHING except the specified change must remain 100% IDENTICAL to the original image."
    )
    return "\n\n".join(parts)
