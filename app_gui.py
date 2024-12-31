import os
import string
import sys
import time

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction, QTextEdit, QSplitter, \
    QTableWidget, QTableWidgetItem, QWidget, QFileDialog, QAbstractItemView, QMessageBox, QShortcut, QHBoxLayout
from app_controller import AppController

class AppGUI:

    def __init__(self,is_watcher):

        # Create the application
        self.qtapp = QApplication([])

        # Create the main window
        self.window = MainWindow(is_watcher)

    def run(self):
        # Run the application event loop
        self.qtapp.exec_()

    def start_with_file(self,file_path):
        # Start the application with a given file
        self.window.open_file_in_editor(file_path)

    def start_with_watcher(self, file_path):
        self.window.watch_and_update(file_path)

class MainWindow(QMainWindow):  # Subclass QMainWindow
    APP_TITLE = "Spreadsheet Viewer"
    def __init__(self,is_watcher):
        super().__init__()  # Initialize the QMainWindow class
        self.controller = AppController()
        self.current_file_path = None
        self.unsaved_changes = False  # Track unsaved changes
        self.build_gui(is_watcher)

    def clear_grid(self):
        self.grid.setRowCount(0)
        self.grid.setColumnCount(1)

    def recalculate(self):
        self.update_grid(self.text_editor.toPlainText().splitlines())

    def update_grid(self, source_lines):
        try:
            # Clear previous grid
            self.clear_grid()
            # Evaluate the source lines
            worksheet = self.controller.evaluate(source_lines)
            evaluated_sheet = worksheet['sheet']
            row_max = worksheet['rows']
            col_max = worksheet['columns']
            # Set dimensions of updated grid
            self.grid.setRowCount(row_max)
            self.grid.setColumnCount(col_max)
            # Create header labels A-Z
            # TODO handle more than 26 columns
            label_list = list(string.ascii_uppercase)[:col_max]
            # FIXME in watcher mode this causes QObject::connect: Cannot queue arguments of type 'Qt::Orientation'
            self.grid.setHorizontalHeaderLabels(label_list)
            # Load the cells from the sheet into the grid
            for row in range(1, row_max + 1):
                for col in range(1, col_max + 1):
                    value = evaluated_sheet.get_formatted_cell_value(0, row, col)
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignRight)
                    #item.setFont(font)  # Optional: Set font for each table cell individually
                    self.grid.setItem(row - 1, col - 1, item)  # 0-based

        except Exception as e:
            print(f"Error in update grid: {e}")
            QMessageBox.critical(self,"Error",f"Failed to update grid: {e}")

    def build_gui(self,is_watcher):
        self.setWindowTitle(self.APP_TITLE)

        # Create the menu bar
        menu_bar = self.menuBar()  # Use the menuBar method from QMainWindow

        # File menu
        file_menu = QMenu("File", menu_bar)
        new_action = QAction("&New", self)
        open_action = QAction("&Open", self)
        save_action = QAction("&Save", self)
        quit_action = QAction("&Exit", self)
        new_action.setShortcut("Ctrl+N")
        open_action.setShortcut("Ctrl+O")
        save_action.setShortcut("Ctrl+S")
        quit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(quit_action)

        # Edit menu
        edit_menu = QMenu("Edit", menu_bar)
        undo_action = QAction("Undo", self)
        cut_action = QAction("Cut", self)
        copy_action = QAction("Copy", self)
        paste_action = QAction("Paste", self)
        verify_action = QAction("&Verify", self)
        # Display the key combination for shortcuts for each menu item
        cut_action.setShortcut("Ctrl+X")
        undo_action.setShortcut("Ctrl+Z")
        copy_action.setShortcut("Ctrl+C")
        paste_action.setShortcut("Ctrl+V")
        verify_action.setShortcut("Ctrl+Y")

        # Add actions to the Edit menu
        edit_menu.addAction(undo_action)
        edit_menu.addAction(cut_action)
        edit_menu.addAction(copy_action)
        edit_menu.addAction(paste_action)
        edit_menu.addAction(verify_action)

        # Add menus to the menu bar
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(edit_menu)

        # Panel 1: Text Editor (Used when we aren't in watcher mode)
        if not is_watcher:
            self.text_editor = QTextEdit(self)
            # Set monospaced font for the editor
            editor_font = QFont("DejaVu Sans Mono", 12)
            editor_font.setStyleHint(QFont.Monospace)
            self.text_editor.setFont(editor_font)
            self.text_editor.setStyleSheet("QTextEdit"
                                    "{"
                                    "background : ivory;"
                                    "}")
            #self.text_editor.setPlaceholderText("Enter your text here...")

            # Connect the actions to their respective methods in QTextEdit
            undo_action.triggered.connect(self.text_editor.undo)
            cut_action.triggered.connect(self.text_editor.cut)
            copy_action.triggered.connect(self.text_editor.copy)
            paste_action.triggered.connect(self.text_editor.paste)
            verify_action.triggered.connect(self.verify_editor)
            self.shortcut_verify_editor = QShortcut(QKeySequence('Ctrl+Y'), self)
            self.shortcut_verify_editor.activated.connect(self.verify_editor)
            self.text_editor.textChanged.connect(self.on_text_changed)

        # Panel 2: Grid (like an HTML table)
        self.grid = QTableWidget(1,1)  # row, col dimensions
        self.grid.setHorizontalHeaderLabels(["A"]) # Set column header
        # If you want to apply different font sizes or styles to the table headers,
        # you can set the font for the header separately using table.horizontalHeader().setFont().

        # Make the grid read-only
        self.grid.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # Set monospaced font for the grid
        grid_font = QFont("DejaVu Sans Mono", 12)
        grid_font.setStyleHint(QFont.Monospace)
        self.grid.setFont(grid_font)
        self.grid.setStyleSheet("QTableWidget"
                                "{"
                                "background : aliceblue;"
                                "}")
        # Connect File Open and Save actions
        new_action.triggered.connect(self.new_file)
        open_action.triggered.connect(self.show_open_file_dialog)
        save_action.triggered.connect(self.save_file)
        quit_action.triggered.connect(self.quit)

        # Place everything in a layout
        main_layout = QHBoxLayout()
        if not is_watcher:
            # Create a splitter layout to hold both panels side by side
            self.splitter = QSplitter(Qt.Horizontal)  # Horizontal splitter
            self.splitter.addWidget(self.text_editor)  # Add the text editor to the splitter
            self.splitter.addWidget(self.grid)  # Add the table to the splitter
            #splitter.setSizes([500,900])  # must issue after adding widgets
            # Set ratio of sizes of panels
            self.splitter.setStretchFactor(0,2)  #index=0,stretch=2
            self.splitter.setStretchFactor(1,3)
            # set the splitter in the layout
            main_layout.addWidget(self.splitter)
        else:
            # We only need the grid panel (don't use a splitter)
            main_layout.addWidget(self.grid)

        self.resize(900, 400)  # Adjust window size
        # Create a central widget and set the layout
        central_widget = QWidget()  # Create a QWidget for the central widget
        central_widget.setLayout(main_layout)  # Set the layout for the central widget

        self.setCentralWidget(central_widget)  # Set the central widget of the main window

        self.show()

    def on_text_changed(self):
        """Recalculate the spreadsheet when the text changes"""
        if not self.unsaved_changes:
            # Indicate we now have unsaved changes
            self.unsaved_changes = True
            self.update_window_title()
        self.recalculate()

    def verify_editor(self):
        content_lines = self.text_editor.toPlainText().splitlines()
        filetype = self.controller.verify_editor_content(content_lines)
        if filetype == "":
            QMessageBox.information(self, "Verify Spreadsheet","Not Verified.  Editor content is not a recognized spreadsheet format.")
        else:
            QMessageBox.information(self, "Verify Spreadsheet",f"Verified! Editor content identified as {filetype}.")

    # Manage state
    # The current window title is to reflect the current state of the text editor with an asterisk
    # if we have unsaved changes. We also want to ensure we are warned with a confirmation dialog
    # if there are unsaved changes that would be lost if we
    #   1. create a new file
    #   2. open a file
    #   3. close the application.
    def update_window_title(self):
        """Update the window title to reflect the unsaved changes."""
        filename = os.path.basename(self.current_file_path) if self.current_file_path else "Untitled"
        title = f"{self.APP_TITLE} - {filename}"
        if self.unsaved_changes:
            title += " *"  # Add asterisk for unsaved changes
        self.setWindowTitle(title)

    def confirm_unsaved_changes(self):
        """Show a confirmation dialog if there are unsaved changes."""
        if self.unsaved_changes:
            response = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to discard them?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            return response == QMessageBox.Yes
        return True

    def new_file(self):
        if not self.confirm_unsaved_changes():
            return
        self.clear_grid()
        self.text_editor.clear()
        self.current_file_path = None
        self.unsaved_changes = False
        self.update_window_title()

    def show_open_file_dialog(self):
        """Handle opening a file, checking for unsaved changes."""
        if not self.confirm_unsaved_changes():
            return
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Markdown Files (*.md);;Text Files (*.txt)", options=options)
        if file_path:
            self.open_file_in_editor(file_path)

    def open_file_in_editor(self,file_path):
        if file_path:
            try:
                file_content = self.controller.read_file_content(file_path)
                # Set the contents of the file to the text editor
                # Causes grid recalculate
                self.text_editor.setPlainText(file_content)
                self.current_file_path = file_path  # Keep track of the opened file
                self.unsaved_changes = False
                # TODO: Use self.update_window_title()?
                filename = os.path.basename(file_path)
                # Append filename to the window title
                new_title = f"{self.APP_TITLE} - {filename}"
                self.setWindowTitle(new_title)
            except Exception as e:
                QMessageBox.critical(self,"Error", f"Failed to open file: {e}")

    def save_file(self):
        """Save the file, checking if it's already saved or not."""
        if not self.current_file_path:
            self.show_save_file_dialog()
        else:
            self.write_file(self.current_file_path)

    def show_save_file_dialog(self):
        """Show a save file dialog."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*)", options=options)
        if file_path:
            self.write_file(file_path)

    def write_file(self, file_path):
        """Write content to the specified file."""
        try:
            with open(file_path, 'w') as file:
                file.write(self.text_editor.toPlainText())
                self.current_file_path = file_path
                self.unsaved_changes = False
                # TODO Use self.update_window_title()?
                folder, self.FILE_NAME = os.path.split(file_path)
                # Save the file extension
                path, dotted_extension = os.path.splitext(file_path)
                self.FILE_EXTENSION = dotted_extension[1:]
                # Set the window title with the filename
                self.setWindowTitle(f"{self.APP_TITLE} - {self.FILE_NAME}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {e}")

    def closeEvent(self, event):
        """Handle closing the application, checking for unsaved changes."""
        if self.confirm_unsaved_changes():
            event.accept()
        else:
            event.ignore()

    def quit(self):
        if self.confirm_unsaved_changes():
            sys.exit()

    # Function to watch the file for changes
    def watch_and_update(self, file_path):
        """Watch the file for changes and update the panel."""
        # Store the initial last modified timestamp of the file
        last_mod_time = os.path.getmtime(file_path)
        # Show the initial file contents
        file_content = self.controller.read_file_content(file_path)
        self.update_grid(file_content.splitlines())
        # Set the window title with this filename
        new_title = f"{self.APP_TITLE} - {os.path.basename(file_path)}"
        self.setWindowTitle(new_title)

        while True:
            # Wait for a short period before checking for changes
            time.sleep(2)

            # Check if the file last modified time has changed
            current_mod_time = os.path.getmtime(file_path)
            if current_mod_time != last_mod_time:

                # Update the last modified time
                last_mod_time = current_mod_time
                # Refresh the grid
                file_content = self.controller.read_file_content(file_path)
                self.update_grid(file_content.splitlines())
