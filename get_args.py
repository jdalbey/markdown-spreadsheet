import argparse
import sys

# Handle command line argument parsing

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

def get_args():
    """ Get the command line arguments """
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

    return args
