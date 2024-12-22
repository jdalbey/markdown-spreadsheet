from spreadsheet.spreadsheet import evaluate_spreadsheet
from markdown_table import read_file, parse_markdown_table, convert_dict_to_markdown, stringify_dict
import argparse
import sys
#
# Evaluate a Markdown-style spreadsheet
# Copyright (c) 2024 John Dalbey
#
def main():

    # Set up the argument parser
    parser = argparse.ArgumentParser(description='Process a file or read from stdin.')
    parser.add_argument('filename', nargs='?', type=str, help='The filename to read from')

    # Parse the arguments
    args = parser.parse_args()

    # Determine the source to read from (file or stdin)
    if args.filename:
        try:
            lines = read_file(args.filename)
        except FileNotFoundError:
            print(f"Error: The file '{args.filename}' does not exist.", file=sys.stderr)
            sys.exit(1)
    else:
        # Read from stdin
        print("Reading from stdin. Press Ctrl-D (or Ctrl-Z on Windows) to end input.")
        lines = sys.stdin.read()

    # Convert the markdown table into a dictionary
    header_rows, mydict = parse_markdown_table(lines)
    # Evaluate the spreadsheet
    result = evaluate_spreadsheet(mydict)
    # convert the result back to a markdown table
    formatted_lines = convert_dict_to_markdown(header_rows, stringify_dict(result))
    print("\n".join(formatted_lines))

if __name__ == '__main__':
    main()

