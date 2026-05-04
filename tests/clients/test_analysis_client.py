import pytest
import requests
import json
from unittest.mock import MagicMock
from clients.analysis_client import AnalysisClient
from exceptions.model_api_error import ModelAPIError


@pytest.fixture
def mock_env(monkeypatch):
    """Fixture to inject predictable environment variables."""
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")
    monkeypatch.setenv("OLLAMA_API_URL", "http://test-url/api/generate")
    monkeypatch.setenv("OLLAMA_USER", "testuser")
    monkeypatch.setenv("OLLAMA_PASSWORD", "testpass")


@pytest.fixture
def client(mock_env):
    return AnalysisClient()


def test_get_response_success(mocker, client):
    # Arrange
    mock_post = mocker.patch("requests.post")
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "Mocked LLM output"}
    mock_post.return_value = mock_response

    # Act
    result = client.get_response("Test prompt")

    # Assert
    assert result == "Mocked LLM output"
    mock_post.assert_called_once()

    # Verify payload format
    call_kwargs = mock_post.call_args[1]
    assert call_kwargs["json"]["model"] == "test-model"
    assert call_kwargs["json"]["prompt"] == "Test prompt"
    assert call_kwargs["json"]["format"] == "json"

    # Verify auth was configured
    assert call_kwargs["auth"] is not None


def test_get_response_http_error(mocker, client):
    # Arrange
    mock_post = mocker.patch("requests.post")
    mock_response = MagicMock()
    # Simulate a 404 Not Found or 500 Internal Server Error
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "404 Client Error"
    )
    mock_post.return_value = mock_response

    # Act & Assert
    with pytest.raises(ModelAPIError) as exc_info:
        client.get_response("Test prompt")

    assert "Model API request failed" in str(exc_info.value)


def test_get_response_missing_response_key(mocker, client):
    # Arrange
    mock_post = mocker.patch("requests.post")
    mock_response = MagicMock()
    # Return JSON that doesn't have the expected 'response' key
    mock_response.json.return_value = {"error": "Invalid format"}
    mock_post.return_value = mock_response

    # Act & Assert
    with pytest.raises(ModelAPIError) as exc_info:
        client.get_response("Test prompt")

    assert "does not contain 'response' field" in str(exc_info.value)


def test_get_response_invalid_json(mocker, client):
    # Arrange
    mock_post = mocker.patch("requests.post")
    mock_response = MagicMock()
    # Simulate Ollama returning malformed JSON
    mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
    mock_post.return_value = mock_response

    # Act & Assert
    with pytest.raises(ModelAPIError) as exc_info:
        client.get_response("Test prompt")

    assert "returned invalid JSON" in str(exc_info.value)
