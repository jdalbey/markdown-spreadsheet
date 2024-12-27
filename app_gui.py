import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from app_controller import AppController
from core.get_displayable_string import get_displayable_string

# This is the GUI for the spreadsheet viewer
# TODO: manage state as in this example https://tech-couch.com/post/building-a-text-editor-in-python-with-tkinter

class AppGUI:
    APP_TITLE = "Spreadsheet Viewer"
    root = None

    def __init__(self,is_watcher):
        self.controller = AppController()
        self.current_file_path = None
        self.root = tk.Tk()
        self.build_gui(is_watcher)

    def run(self):
        self.root.mainloop()

    def recalculate(self):
        self.refresh_panel(self.text_editor.get(1.0, tk.END).splitlines())

    def refresh_panel(self, source_lines):
        # Consider https://github.com/bauripalash/tkhtmlview/blob/main/README.md
        # for rendering HTML in the panel
        try:
            worksheet = self.controller.evaluate(source_lines)
            evaluated_sheet = worksheet['sheet']
            row_max = worksheet['rows']
            col_max = worksheet['columns']
            print (f"Refreshing panel with {row_max} rows and {col_max} colunms.")
            for widget in self.result_panel.winfo_children():
                widget.destroy()
            # Load the cells from the sheet into the grid
            for row in range(1,row_max+1):
                for col in range(1,col_max+1):
                    #print (row,col,sheet.get_formatted_cell_value(0, row, col))
                    value = evaluated_sheet.get_formatted_cell_value(0, row, col)
                    value = get_displayable_string(value, 10)
                    # label = tk.Label(root, text=value.rjust(10), anchor='e')
                    # label = tk.Label(self.result_panel, text=value.rjust(10), bg="#e4e4e7")
                    # label.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")  # Fill the grid cell
                    label = tk.Label(self.result_panel, text=value.rjust(10),
                                     background="ivory", #bg="#e4e4e7", ,
                                     borderwidth=0, relief="solid")
                    label.grid(row=row, column=col, ipadx=5, ipady=5, sticky="nsew")
            # Configure grid weights to make cells expandable
            for i in range(1,col_max+1):
                self.result_panel.grid_columnconfigure(i, weight=1, uniform="equal")
            self.result_panel.grid_rowconfigure(row_max, weight=0, uniform="equal")  # Configure row expansion

        except Exception as e:
            print ("Error in recalculate"+e)
            messagebox.showerror("Error", f"Failed to recalculate: {e}")

    # Function for Edit menu actions
    def undo(self):
        self.text_editor.event_generate("<<Undo>>")
        return "break"

    def cut(self):
        self.text_editor.event_generate("<<Cut>>")
        return "break"

    def copy(self):
        self.text_editor.event_generate("<<Copy>>")
        return "break"

    def paste(self):
        self.text_editor.event_generate("<<Paste>>")
        return "break"

    # Functions for File menu actions
    def show_open_file_dialog(self):
        file_path = filedialog.askopenfilename()
        self.open_file_in_editor(file_path)
        self.recalculate()

    def open_file_in_editor(self,file_path):
        if file_path:
            try:
                file_content = self.controller.read_file_content(file_path)
                self.text_editor.delete(1.0, tk.END)  # Clear existing content
                for line in file_content:
                    self.text_editor.insert(tk.END, line)  # Insert each line
                self.current_file_path = file_path  # Keep track of the opened file
                folder, filename = os.path.split(file_path)
                self.root.title(f"{self.APP_TITLE} - {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")

    def save_as_file(self):
        """Save the current file as a new file."""
        # Show the SaveAs Dialog to the user
        filepath = filedialog.asksaveasfilename(
            defaultextension=self.controller.FILE_EXTENSION,
            filetypes=[("Markdown Files", "*.md"), ("Serialized Files", "*.ser"), ("All Files", "*.*")],
        )
        if not filepath:
            return
        # Write the editor contents to the file
        with open(filepath, "w") as output_file:
            text = self.text_editor.get(1.0, tk.END)
            output_file.write(text)
        folder, self.FILE_NAME = os.path.split(filepath)
        # Save the file extension
        path, dotted_extension = os.path.splitext(filepath)
        self.FILE_EXTENSION =  dotted_extension[1:]
        # Set the window title with the filename
        self.root.title(f"{self.APP_TITLE} - {self.FILE_NAME}")

    # Assemble the GUI
    def build_gui(self,is_watcher):
        """Build all the GUI components
        @param is_watcher True if the app is in watcher mode (we don't need the editor panel)
        """
        self.root.title("Spreadsheet Viewer")
        self.root.geometry("860x420")
        # Panes
        self.panes = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.panes.pack(fill=tk.BOTH, expand=1)
        if not is_watcher:
            self.text_editor = tk.Text(self.panes, wrap="word", undo=True, background="ivory")
            self.panes.add(self.text_editor)
            self.panes.paneconfig(self.text_editor, minsize=260)  # Initial width for the editor pane

        self.result_panel = tk.Text(self.panes, wrap="word", undo=True, background="ivory")
        self.panes.add(self.result_panel)
        self.panes.paneconfig(self.result_panel, minsize=600)  # Initial width for result pane
        # Menu
        self.menu = tk.Menu(self.root)
        # File menu
        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open", command=self.show_open_file_dialog, accelerator="Ctrl+O")
        self.file_menu.add_command(label="Save As", command=self.save_as_file, accelerator="Ctrl+S")
        self.root.bind("<Control-s>", lambda event: self.save_as_file())
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        # Edit menu
        edit_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        #edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        # Recalculate menu command
        self.menu.add_command(label="Recalculate", command=self.recalculate, accelerator="Ctrl+R")  # Command in the menu bar
        self.root.bind("<Control-r>", lambda event: self.recalculate())

        self.root.config(menu=self.menu)

    def get_file_mod_time(self, file_path):
        """Returns the last modified timestamp of the file."""
        return os.path.getmtime(file_path)

    # Function to watch the file for changes
    def watch_and_update(self, file_path):
        """Watch the file for changes and update the panel."""
        # Store the initial last modified timestamp of the file
        last_mod_time = self.get_file_mod_time(file_path)
        # Show the initial file contents
        file_content = self.controller.read_file_content(file_path)
        self.refresh_panel(file_content)

        while True:
            # Wait for a short period before checking for changes
            time.sleep(2)

            # Check if the file last modified time has changed
            current_mod_time = self.get_file_mod_time(file_path)
            if current_mod_time != last_mod_time:

                # Update the last modified time
                last_mod_time = current_mod_time

                file_content = self.controller.read_file_content(file_path)
                self.refresh_panel(file_content)

