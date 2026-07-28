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
        "\n\nEnhance the following image edit prompt using the structures and best practices defined above. "
        "Follow the exact format: [Subject] + [Scene/Environment] + [Style] + [Lighting] + "
        "[Composition] + [Quality Requirements]. "
        "For image-to-image, also include: [What to change] + [What to preserve]."
    )
    return "\n\n".join(parts)
