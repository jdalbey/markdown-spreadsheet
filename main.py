import argparse
import sys
import threading
from app_gui import AppGUI
from app_controller import AppController

# This is the main module for the Spreadsheet Viewer application

def validate_arguments(args):
    # If output file (-o) is provided, ensure input file (-i) is also provided
    if args.output_file and not args.input_file:
        print("Error: -o/--output-file requires -i/--input-file.", file=sys.stderr)
        sys.exit(1)
    
    # Validate output file extension if provided
    if args.output_file:
        if not args.output_file.endswith(('.html', '.pdf')):
            print("Error: Output file must have a .html or .pdf extension.", file=sys.stderr)
            sys.exit(1)
    
    # If watcher mode (-w) is specified, ensure input file (-i) is also provided
    if args.watcher and not args.input_file:
        print("Error: -w/--watcher requires -i/--input-file.", file=sys.stderr)
        sys.exit(1)

# Parse the arguments and start the application in the desired mode: Interactive, Batch, or Watcher
def main():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="A versatile file processing application.")
    
    # Define arguments
    parser.add_argument('-i', '--input_file', type=str, help="(Optional) The file to be opened by the application. If not specified, a new file is opened.")
    parser.add_argument('-o', '--output-file', type=str, help="(Optional) The output file to be generated. Runs in batch mode when specified.")
    parser.add_argument('-w', '--watcher', action='store_true', help="(Optional) Start in watcher mode to monitor the specified input file.")

    # Parse arguments
    args = parser.parse_args()

    # Validate arguments
    validate_arguments(args)

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