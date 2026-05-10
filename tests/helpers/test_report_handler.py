import pytest
import os
from unittest.mock import mock_open, patch
from helpers.report_handler import ReportHandler


def test_handle_writes_to_file_and_prints(mocker, capsys):
    # Arrange
    test_json = '{"test": "data"}'

    # Mock os.makedirs to prevent creating actual directories
    mock_makedirs = mocker.patch("os.makedirs")

    # Mock built-in open() to prevent writing actual files
    m = mock_open()
    mock_file = mocker.patch("builtins.open", m)

    # Freeze time so we can predict the filename
    mock_datetime = mocker.patch("helpers.report_handler.datetime")
    mock_datetime.datetime.now.return_value.strftime.return_value = (
        "2026-01-01_12-00-00"
    )

    # Act
    ReportHandler.handle(test_json)

    # Assert Print Output
    captured = capsys.readouterr()
    assert "--- Compliance Report ---" in captured.out
    assert '"test": "data"' in captured.out
    assert "Compliance report saved to" in captured.out

    # Assert File Operations
    mock_makedirs.assert_called_once()
    mock_file.assert_called_once()

    # Verify the exact data written to the file
    handle = m()
    handle.write.assert_called_once_with(test_json)


def test_handle_invalid_json_fallback(mocker, capsys):
    # Arrange
    invalid_json = "This is not json"
    mocker.patch("os.makedirs")
    mocker.patch("builtins.open", mock_open())

    # Act
    ReportHandler.handle(invalid_json)

    # Assert
    captured = capsys.readouterr()
    # It should fallback to printing the raw string without crashing
    assert invalid_json in captured.out


def test_create_file_handles_os_errors(mocker, capsys):
    # Arrange
    mocker.patch("os.makedirs", side_effect=PermissionError("Access denied"))

    # Act
    ReportHandler.handle('{"test": "data"}')

    # Assert
    captured = capsys.readouterr()
    # The application shouldn't crash, but it should log the error to stderr
    assert "Error saving report to file: Access denied" in captured.err
