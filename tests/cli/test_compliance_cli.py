import pytest
import json
from unittest.mock import MagicMock
from cli.compliance_cli import ComplianceCLI
from clients.analysis_client import ModelAPIError
from helpers.report_handler import ReportHandler


@pytest.fixture
def mock_service():
    return MagicMock()


@pytest.fixture
def cli(mock_service):
    return ComplianceCLI(mock_service)


def test_do_story_empty_arg(cli, capsys, mock_service):
    # Act
    cli.do_story("")

    # Assert
    captured = capsys.readouterr()
    assert "Error: Please provide a story ID." in captured.err
    mock_service.analyze_user_story.assert_not_called()


def test_do_story_valid_arg(mocker, cli, mock_service):
    # Arrange
    mock_service.analyze_user_story.return_value = "Mocked Report"
    mock_handler = mocker.patch.object(ReportHandler, "handle")

    # Act
    cli.do_story("123")

    # Assert
    mock_service.analyze_user_story.assert_called_once_with("123")
    mock_handler.assert_called_once_with("Mocked Report")


def test_do_story_handles_service_exception(cli, capsys, mock_service):
    # Arrange
    mock_service.analyze_user_story.side_effect = Exception("Service failed")

    # Act
    cli.do_story("123")

    # Assert
    captured = capsys.readouterr()
    assert "Error analyzing story: Service failed" in captured.err


def test_do_text_empty_arg(cli, capsys, mock_service):
    # Act
    cli.do_text("")

    # Assert
    captured = capsys.readouterr()
    assert "Error: Please provide text to analyze." in captured.err
    mock_service.analyze_requirements.assert_not_called()


def test_do_text_valid_arg(mocker, cli, mock_service):
    # Arrange
    mock_report = '{"is_compliant": true}'
    mock_service.analyze_requirements.return_value = mock_report
    mock_handler = mocker.patch.object(ReportHandler, "handle")

    # Act
    cli.do_text("Some text")

    # Assert
    mock_service.analyze_requirements.assert_called_once_with("Some text")
    mock_handler.assert_called_once_with(mock_report)


def test_do_text_handles_api_error(cli, capsys, mock_service):
    # Arrange
    mock_service.analyze_requirements.side_effect = ModelAPIError("Connection refused")

    # Act
    cli.do_text("Some text")

    # Assert
    captured = capsys.readouterr()
    assert "API Error: Connection refused" in captured.err


def test_do_exit(cli, capsys):
    # Act
    result = cli.do_exit("")

    # Assert
    assert result is True
    captured = capsys.readouterr()
    assert "Exiting Compliance Checker" in captured.out
