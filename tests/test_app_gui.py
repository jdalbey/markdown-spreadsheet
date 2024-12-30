from unittest.mock import MagicMock

import pytest
from PyQt5.QtWidgets import QApplication, QMessageBox
from app_gui import MainWindow
from app_controller import AppController

@pytest.fixture(scope="module")
def app():
    """Fixture to create the QApplication instance."""
    return QApplication([])

@pytest.fixture
def main_window(app):
    """Fixture to create and return a MainWindow instance."""
    main_window = MainWindow(is_watcher=False)
    main_window.controller = AppController()  # Use the actual controller
    return main_window

def test_update_grid(main_window):
    """Test the update_grid method of MainWindow using the actual controller."""
    # Example source lines for the spreadsheet (with colons added after the first field)
    source_lines = [
        "A1: 5",
        "A2: 10",
        "B1: 15",
        "B2: 20"
    ]

    # Call update_grid with the actual controller
    main_window.update_grid(source_lines)

    # Verify that the grid dimensions are correctly updated
    assert main_window.grid.rowCount() == 2
    assert main_window.grid.columnCount() == 2

    # Verify the content of the grid
    assert main_window.grid.item(0, 0).text() == "5"   # A1
    assert main_window.grid.item(1, 0).text() == "10"  # A2
    assert main_window.grid.item(0, 1).text() == "15"  # B1
    assert main_window.grid.item(1, 1).text() == "20"  # B2

def test_verify_editor(main_window, monkeypatch):
    """Test the verify_editor method of MainWindow with the actual controller."""
    # Use the actual AppController
    main_window.controller = AppController()

    # Mock QMessageBox to capture the information dialog
    mock_msg_box = MagicMock()
    monkeypatch.setattr(QMessageBox, 'information', mock_msg_box)

    # Test the "Verified" case
    valid_content = "5,10\n7,12"   # create a CSV spreadsheet
    main_window.text_editor.setPlainText(valid_content)

    # Call verify_editor
    main_window.verify_editor()

    # Verify that QMessageBox displayed the "Verified!" message
    mock_msg_box.assert_called_once_with(
        main_window, "Verify Spreadsheet", "Verified! Editor content identified as CSV."
    )

    # Test the "Not Verified" case
    mock_msg_box.reset_mock()
    invalid_content = "a1"
    main_window.text_editor.setPlainText(invalid_content)

    # Call verify_editor
    main_window.verify_editor()

    # Verify that QMessageBox displayed the "Not Verified" message
    mock_msg_box.assert_called_once_with(
        main_window, "Verify Spreadsheet", "Not Verified.  Editor content is not a recognized spreadsheet format."
    )

