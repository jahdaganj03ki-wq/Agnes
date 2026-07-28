import os
import tempfile

import pytest

from backend.app.services import skill_loader


def test_load_all_empty_dir():
    skills = skill_loader.load_all()
    assert isinstance(skills, list)


def test_load_all_returns_skills():
    skills = skill_loader.load_all()
    names = {s.name for s in skills}
    assert "AgnesGenerationSkill" in names
    assert "AgnesCliSkill" in names
    assert "VisionCraftPromptGuide" in names


def test_load_all_chars_positive():
    skills = skill_loader.load_all()
    for s in skills:
        assert s.chars > 0


def test_get_content_known():
    content = skill_loader.get_content("AgnesGenerationSkill")
    assert "Prompt Structure" in content
    assert len(content) > 0


def test_get_content_unknown():
    content = skill_loader.get_content("nonexistent")
    assert content == ""


def test_build_system_prompt_contains_all_skills():
    skills = skill_loader.load_all()
    prompt = skill_loader.build_system_prompt(skills)
    for s in skills:
        assert s.name in prompt
    assert "Enhance the following" in prompt
