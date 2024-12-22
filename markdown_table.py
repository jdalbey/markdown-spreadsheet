def read_file(file_path):
    """Reads a file and returns its lines as a list of strings."""
    with open(file_path, 'r') as file:
        content = file.readlines()
        # remove whitespace characters like `\n` at the end of each line
        content = [x.strip() for x in content]
        return content

def generate_column_labels():
    """Generates column labels A-Z, AA-AZ, BA-BZ, etc. through ZA-ZZ"""
    from itertools import product

    single_letters = [chr(i) for i in range(65, 91)]  # A-Z
    double_letters = ["".join(p) for p in product(single_letters, repeat=2)]  # AA-ZZ

    return single_letters + double_letters

def parse_markdown_table(lines):
    """ Parse a table in markdown format can convert to a dictionary """
    # Save the first two rows
    header_rows = lines[:2]
    data_rows = lines[2:]

    # Initialize the dictionary for storing parsed cells
    table_dict = {}

    # Generate column labels (A, B, C, ..., AA, AB, ...)
    column_labels = generate_column_labels()

    # Process each data row
    for row_index, line in enumerate(data_rows, start=1):
        # Strip leading/trailing spaces and split by '|'
        cells = [cell.strip() for cell in line.strip('|').split('|')]

        # Assign cell values to dictionary
        for col_index, cell in enumerate(cells):
                cell_label = f"{column_labels[col_index]}{row_index}"
                table_dict[cell_label] = cell

    return header_rows, table_dict

def convert_dict_to_markdown(header_rows, table_dict):
    """Converts a dictionary back into a markdown style table like the original input."""
    from itertools import groupby

    # Extract row numbers and column labels
    items = sorted(table_dict.items(), key=lambda x: (int(x[0][1:]), x[0][0]))

    # Group by row numbers
    grouped = groupby(items, key=lambda x: int(x[0][1:]))

    rows = []
    for _, group in grouped:
        row = []
        for cell_label, value in group:
            col_index = ord(cell_label[0]) - 65  # Convert column letter to index (A=0, B=1, ...)
            while len(row) <= col_index:
                row.append("")  # Fill empty cells
            row[col_index] = value
        rows.append(f"| {' | '.join(row)} |")

    return [line.strip() for line in header_rows] + rows

def stringify_dict(dictionary):
    for key, value in dictionary.items():
        if not isinstance(value, str):
            dictionary[key] = str(value)
    return dictionary


