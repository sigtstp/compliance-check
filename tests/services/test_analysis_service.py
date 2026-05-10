import pytest
from unittest.mock import MagicMock
from services.analysis_service import AnalysisService


@pytest.fixture
def mock_client():
    """Fixture providing a mocked AnalysisClient."""
    return MagicMock()


@pytest.fixture
def service(mock_client):
    """Fixture providing an AnalysisService instance with injected mock client."""
    return AnalysisService(mock_client)


def test_analyze_requirements_formats_prompt_correctly(service, mock_client):
    # Arrange
    mock_client.get_response.return_value = '{"is_compliant": true}'
    test_requirement = "The system shall encrypt data at rest."

    # Act
    result = service.analyze_requirements(test_requirement)

    # Assert
    assert result == '{"is_compliant": true}'
    mock_client.get_response.assert_called_once()

    # Verify the prompt string formatting
    called_prompt = mock_client.get_response.call_args[0][0]
    assert test_requirement in called_prompt
    assert "JSON object" in called_prompt
    assert "owasp_risks" in called_prompt


def test_analyze_user_story_returns_placeholder(service, capsys):
    # Arrange
    story_id = "12345"

    # Act
    result = service.analyze_user_story(story_id)

    # Assert
    assert "12345" in result
    assert "Compliance report" in result

    # Verify print side-effect
    captured = capsys.readouterr()
    assert "Analyzing user story with ID: 12345" in captured.out
