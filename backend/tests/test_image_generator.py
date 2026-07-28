from unittest.mock import MagicMock, patch

import pytest

from backend.app.services import image_generator


def test_generate_no_api_key():
    with patch.object(image_generator, "settings") as mock_settings:
        mock_settings.agnes_api_key = ""
        with pytest.raises(RuntimeError, match="AGNES_API_KEY not configured"):
            image_generator.generate("prompt", "base64data")


@patch("backend.app.services.image_generator.httpx.Client")
def test_generate_success(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value.__enter__.return_value = mock_client
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "data": [{"url": "https://example.com/img.png", "revised_prompt": "Revised"}]
    }
    mock_client.post.return_value = mock_resp

    url, revised = image_generator.generate("test prompt", "base64img", "16:9")
    assert url == "https://example.com/img.png"
    assert revised == "Revised"
    mock_client.post.assert_called_once()


@patch("backend.app.services.image_generator.httpx.Client")
def test_generate_no_data(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value.__enter__.return_value = mock_client
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"data": []}
    mock_client.post.return_value = mock_resp

    url, revised = image_generator.generate("test", "img")
    assert url == ""
    assert revised is None
