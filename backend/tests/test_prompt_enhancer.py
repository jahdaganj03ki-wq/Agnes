from unittest.mock import MagicMock, patch

import pytest

from backend.app.services import prompt_enhancer


def test_enhance_no_api_key():
    with patch.object(prompt_enhancer, "settings") as mock_settings:
        mock_settings.agnes_api_key = ""
        with pytest.raises(RuntimeError, match="AGNES_API_KEY not configured"):
            prompt_enhancer.enhance("system", "user prompt")


@patch("backend.app.services.prompt_enhancer.client")
def test_enhance_success(mock_client):
    mock_msg = MagicMock()
    mock_msg.content = "Enhanced: [Subject] ... [Quality]"
    mock_choice = MagicMock()
    mock_choice.message = mock_msg
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response

    result = prompt_enhancer.enhance("system prompt", "my prompt")
    assert result == "Enhanced: [Subject] ... [Quality]"
    mock_client.chat.completions.create.assert_called_once()


@patch("backend.app.services.prompt_enhancer.client")
def test_enhance_empty_response(mock_client):
    mock_choice = MagicMock()
    mock_choice.message.content = None
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response

    result = prompt_enhancer.enhance("system", "user")
    assert result == ""
