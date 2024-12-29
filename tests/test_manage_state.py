import pytest
from unittest.mock import MagicMock
from PyQt5.QtWidgets import QApplication, QMessageBox
from app_gui import MainWindow

@pytest.fixture(scope="module")
def app():
    """Fixture to create the QApplication instance."""
    return QApplication([])

@pytest.fixture
def main_window(app):
    """Fixture to create and return a MainWindow instance."""
    return MainWindow(is_watcher=False)

def test_unsaved_changes_tracking(main_window):
    """Test that unsaved changes are tracked and reflected in the window title."""
    main_window.current_file_path = "test.txt"
    main_window.unsaved_changes = False
    main_window.update_window_title()

    assert main_window.windowTitle() == "Spreadsheet Viewer - test.txt"

    # Modify the editor state
    main_window.text_editor.setPlainText("Unsaved content")

    assert main_window.unsaved_changes
    assert main_window.windowTitle() == "Spreadsheet Viewer - test.txt *"


def test_confirm_unsaved_changes_yes(main_window, monkeypatch):
    """Test confirm_unsaved_changes when user clicks 'Yes'."""
    mock_msg_box = MagicMock(return_value=QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "question", mock_msg_box)

    # Modify the editor state
    main_window.text_editor.setPlainText("Unsaved content")

    assert main_window.confirm_unsaved_changes() is True
    mock_msg_box.assert_called_once_with(
        main_window,
        "Unsaved Changes",
        "You have unsaved changes. Do you want to discard them?",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )

def test_confirm_unsaved_changes_no(main_window, monkeypatch):
    """Test confirm_unsaved_changes when user clicks 'No'."""
    mock_msg_box = MagicMock(return_value=QMessageBox.No)
    monkeypatch.setattr(QMessageBox, "question", mock_msg_box)

    # Modify the editor state
    main_window.text_editor.setPlainText("Unsaved content")
    result = main_window.confirm_unsaved_changes()

    assert result is False
    mock_msg_box.assert_called_once()

def test_new_file_with_unsaved_changes(main_window, monkeypatch):
    """Test new_file with unsaved changes."""
    # Mock confirmation dialog to return "Yes"
    monkeypatch.setattr(main_window, "confirm_unsaved_changes", MagicMock(return_value=True))

    # Set up a test state
    main_window.text_editor.setPlainText("Unsaved content")

    # Call new_file
    main_window.new_file()

    # Verify that the editor was cleared and unsaved changes were reset
    assert main_window.text_editor.toPlainText() == ""
    assert not main_window.unsaved_changes
    assert main_window.windowTitle() == "Spreadsheet Viewer - Untitled"

def test_close_event_with_unsaved_changes(main_window, monkeypatch):
    """Test closeEvent with unsaved changes."""
    # Mock confirmation dialog to return "No"
    monkeypatch.setattr(main_window, "confirm_unsaved_changes", MagicMock(return_value=False))

    # Mock the close event
    mock_event = MagicMock()

    # Set up a test state
    main_window.text_editor.setPlainText("Unsaved content")

    # Call closeEvent
    main_window.closeEvent(mock_event)

    # Verify that the event was ignored
    mock_event.ignore.assert_called_once()
    mock_event.accept.assert_not_called()

    # Mock confirmation dialog to return "Yes"
    monkeypatch.setattr(main_window, "confirm_unsaved_changes", MagicMock(return_value=True))
    mock_event = MagicMock()

    # Call closeEvent again
    main_window.closeEvent(mock_event)

    # Verify that the event was accepted
    mock_event.accept.assert_called_once()
    mock_event.ignore.assert_not_called()

def test_save_file_without_current_path(main_window, monkeypatch):
    """Test save_file when no current file path is set."""
    mock_show_save_file_dialog = MagicMock()
    monkeypatch.setattr(main_window, "show_save_file_dialog", mock_show_save_file_dialog)

    # Ensure no current file path is set
    main_window.current_file_path = None

    # Call save_file
    main_window.save_file()

    # Verify that show_save_file_dialog was called
    mock_show_save_file_dialog.assert_called_once()
