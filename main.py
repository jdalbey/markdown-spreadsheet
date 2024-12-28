import sys
import threading
from app_gui import AppGUI
from app_controller import AppController
from get_args import get_args

# This is the main module for the Spreadsheet Viewer application

# Parse the arguments and start the application in the desired mode: Interactive, Batch, or Watcher
def main():
    args = get_args()

    # Application logic based on arguments
    if args.output_file:
        print(f"Batch mode: Transforming '{args.input_file}' into '{args.output_file}'.")
        controller = AppController()
        # Read input file
        content = controller.read_file_content(args.input_file)
        # send to recalculate
        worksheet = controller.evaluate(content)
        # get results from model and write to HTML file using a table for the grid.
        controller.writer.write(worksheet,args.output_file,"HTML")

    elif args.watcher:
        print(f"Watcher mode: Monitoring '{args.input_file}'.")
        gui = AppGUI(is_watcher=True)
        # Create a new thread for the watch_and_update method
        watcher_thread = threading.Thread(target=gui.watch_and_update, args=(args.input_file,))
        watcher_thread.daemon = True  # Ensure the thread exits when the main program exits
        watcher_thread.start()
        gui.run()

    elif args.input_file:
        print("Running in interactive mode with input file ",args.input_file)
        gui = AppGUI(is_watcher=False)
        gui.open_file_in_editor(args.input_file)
        gui.recalculate()
        gui.run()
    else:
        print("Running in interactive mode.")
        gui = AppGUI(is_watcher=False)
        gui.run()

# Entry point for the application
if __name__ == "__main__":
    main()

# batch mode example
#python script.py -i input.md -o output.html
# watcher mode example
#python script.py -i input.md -w
# error example
#python script.py -o output.pdf
#Error: -o/--output-file requires -i/--input-file.

# Ref: https://wiki.documentfoundation.org/Documentation/SDKGuide/Importing_XML