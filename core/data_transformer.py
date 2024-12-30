import ironcalc as ic
import re, csv

def spreadsheet_to_html(worksheet):
    """ Convert a spreadsheet into an HTML table.
     @param dictionary containing the spreadsheet
     @return string containing HTML
     """
    row_max = worksheet['rows']
    col_max = worksheet['columns']
    spreadsheet = worksheet['sheet']

    output = "<HTML><TABLE>\n"
    for row in range(1, row_max + 1):
        output += "<TR>\n"
        for col in range(1, col_max + 1):
            value = spreadsheet.get_formatted_cell_value(0, row, col)
            output += f"<td>{value}</td>"
        output += "</TR>\n"
    output += "</TABLE></HTML>\n"
    return output

class DataTransformer:
    """ Parse methods for each different file type """

    def __init__(self):
        # A worksheet contains a spreadsheet and its dimensions
        self.row_max = 0
        self.col_max = 0
        # Create an instance of the Model class
        self.spreadsheet = ic.create("model", "en", "UTC")

    def get_worksheet(self):
        sheet_dict = {'sheet':self.spreadsheet, 'rows':self.row_max, 'columns':self.col_max}
        return sheet_dict

    def get_model(self):
        return self.spreadsheet

    @staticmethod
    def identify_file_format(file_extension, source_lines):
        """ Identify the file format from file content clues
        @param file_extension: A string with the 3-character file extension
        @param source_lines: the plain text content of the file
        @return: A tuple: flag, line_num where flag is true if the file content is recognized and False if not
                 if False, line_num has the offending line number.
        """

        def is_csv(lines):
            for i, line in enumerate(lines):
                if len(line) == 0:
                    continue
                if ',' not in line and ';' not in line and '\t' not in line:
                    return False, i + 1
            return True, None

        def is_sylk(lines):
            if not lines[0].startswith('ID'):
                return False, 1
            return True, None

        def is_markdown_table(lines):
            stripped_lines = [line.strip() for line in lines if line.strip()]
            if len(stripped_lines) < 2:
                return False, 1
            if '|' not in stripped_lines[0]:
                return False, 1
            if not all(c in '-:| ' for c in stripped_lines[1]):
                return False, 2
            return True, None

        def is_dif(lines):
            if not (lines[0].strip().upper() == 'TABLE' or lines[0].strip().upper() == 'HEADER'):
                return False, 1
            return True, None

        def is_ser(lines):
            position_pattern = r'^[A-Z]+[1-9][0-9]*$'  # Regex for valid position (e.g., A1, B3, DD25)
            for i, line in enumerate(lines):
                # ignore blank lines
                line = line.strip()
                if len(line) == 0:
                    continue
                parts = line.split(':', 1)
                if len(parts) != 2 or not re.match(position_pattern, parts[0]):
                    return False, i + 1
            return True, None

        try:

            # Mapping of file extensions to check functions
            format_checkers = {
                '.csv': ('CSV', is_csv),
                '.slk': ('SYLK', is_sylk),
                '.md': ('Markdown', is_markdown_table),
                '.dif': ('DIF', is_dif),
                '.ser': ('SER', is_ser)
            }

            # Prioritize based on file extension
            file_extension = file_extension.lower()  # make lower case
            if file_extension in format_checkers:
                format_name, checker = format_checkers[file_extension]
                is_valid, line_num = checker(source_lines)
                if is_valid:
                    return f"Detected format: {format_name}"
                else:
                    print(f"identify_file_format(): {format_name} check failed at line {line_num}")

            # Fall back to checking all formats
            for format_name, checker in format_checkers.values():
                is_valid, line_num = checker(source_lines)
                if is_valid:
                    return f"Detected format: {format_name}"

            return "Unknown: Format not recognized"

        except Exception as e:
            return f"Error reading file: {e}"

    def update_max_dimensions(self, row_idx, col_idx):
        """Update the maximum row and column numbers encountered."""
        self.row_max = max(self.row_max, row_idx)
        self.col_max = max(self.col_max, col_idx)

    def process_ser(self,lines):
        """Process SER format."""
        for line in lines:
            line = line.strip()
            if len(line) == 0:
                continue
            if ':' not in line:
                raise ValueError(f"Invalid line format (missing ':'): {line}")
            position, value = line.split(':', 1)
            col_idx = ord(position[0].upper()) - 64  # Convert column letter to index (A=1, B=2, ...)
            row_idx = int(position[1:])
            self.spreadsheet.set_user_input(0, row_idx, col_idx, value.strip())
            self.update_max_dimensions(row_idx, col_idx)

    def process_csv(self,lines):
        """Process CSV format."""
        reader = csv.reader(lines)
        for row_idx, row in enumerate(reader, start=1):
            if len(row) == 0:
                continue
            for col_idx, value in enumerate(row, start=1):
                self.spreadsheet.set_user_input(0, row_idx, col_idx, value.strip())
                self.update_max_dimensions(row_idx, col_idx)

    def process_sylk(self,lines):
        """Process SYLK format."""
        for line in lines:
            if line.startswith("C;X"):
                parts = line.split(";")
                x = y = value = None
                for part in parts:
                    if part.startswith("X"):
                        x = int(part[1:])
                    elif part.startswith("Y"):
                        y = int(part[1:])
                    elif part.startswith("K"):
                        value = part[1:].strip("\"")
                if x and y and value is not None:
                    self.spreadsheet.set_user_input(0, y, x, value)
                    self.update_max_dimensions(y,x)

    def process_markdown(self,lines):
        """Process Markdown format."""
        stripped_lines = [line.strip() for line in lines if line.strip()]
        header_line = stripped_lines[0]
        separator_line = stripped_lines[1]
        data_lines = stripped_lines[2:]

        # TODO Figure out how to handle the markdown table headers
        #headers = [h.strip() for h in header_line.split('|') if h.strip()]
        for row_idx, row in enumerate(data_lines, start=1):
            values = [v.strip() for v in row.strip('|').split('|')]
            for col_idx, value in enumerate(values, start=1):
                self.spreadsheet.set_user_input(0, row_idx, col_idx, value.strip())
                self.update_max_dimensions(row_idx, col_idx)

    def process_dif(self, lines):
        """Process DIF format."""
        is_data_section = False
        current_row = 0
        current_col = 0

        for i, line in enumerate(lines):
            line = line.strip()

            # Start processing data after "DATA" directive
            if line.upper() == "DATA":
                is_data_section = True
                continue

            if not is_data_section:
                continue

            # Skip dummy numeric value after "DATA" directive
            if line == "0,0" and i + 1 < len(lines) and lines[i + 1].strip() == '""':
                continue

            # Row marker (BOT)
            if line == "-1,0" and i + 1 < len(lines) and lines[i + 1].strip().upper() == "BOT":
                current_row += 1
                current_col = 0
                continue

            # End of data (EOD)
            if line == "-1,0" and i + 1 < len(lines) and lines[i + 1].strip().upper() == "EOD":
                break

            # Handle string data (1,0 directive)
            if line.startswith("1,0") and i + 1 < len(lines):
                current_col += 1
                value = lines[i + 1].strip().strip('"')
                self.spreadsheet.set_user_input(0, current_row, current_col, value)
                self.update_max_dimensions(current_row, current_col)
                continue

            # Handle numeric data (0,value directive)
            if line.startswith("0,"):
                parts = line.split(",")
                if len(parts) >= 2:
                    value = parts[1]
                    current_col += 1
                    self.spreadsheet.set_user_input(0, current_row, current_col, value)
                    self.update_max_dimensions(current_row, current_col)

    def parse_source(self, file_extension, source_lines: list) -> bool:
        """ Parse the source lines into the spreadsheet model
        @param source_lines list of lines to be put in the spreadsheet
        @return True if parsing was successful, False otherwise"""

        # Try to identify_file_format
        format_result = self.identify_file_format(file_extension, source_lines)

        if format_result.startswith("Detected format:"):
            detected_format = format_result.split(":")[1].strip()
        else:
            #print("Unsupported format or failed validation. Exiting.")
            return False

        # reset table
        self.row_max = 0
        self.col_max = 0
        self.spreadsheet = ic.create("model", "en", "UTC")

        # Dispatch to appropriate parser
        try:
            if detected_format == "SER":
                 self.process_ser(source_lines)
            elif detected_format == "CSV":
                 self.process_csv(source_lines)
            elif detected_format == "SYLK":
                 self.process_sylk(source_lines)
            elif detected_format == "Markdown":
                 self.process_markdown(source_lines)
            elif detected_format == "DIF":
                 self.process_dif(source_lines)
            else:
                print(f"Unsupported format: {detected_format}")
                raise Exception

        except Exception as e:
            print(f"Unable to parse editor lines: {e}")
            return False

        return True

    # def parse_serialized_sheet(self, serialized_sheet: str):
    #     """ Logic to parse the serialized sheet """
    #     def get_column_number(column_name):
    #         """ Function to parse the column name and extract the column number"""
    #         # The column name is like A, B, C, ..., which corresponds to 1, 2, 3, ...
    #         column_letter = column_name[0]  # Extract the first character (column letter)
    #         column_number = ord(column_letter.upper()) - ord('A') + 1  # Convert letter to number
    #         return column_number
    #
    #     col_max = 1
    #     row_max = 1
    #     for line in serialized_sheet:
    #         # Strip any leading/trailing whitespace from the line
    #         line = line.strip()
    #         # Split the line into cell position and value by the colon
    #         if ':' in line:
    #             cell_position, value = line.split(":", 1)  # Split at the first colon
    #
    #             # Extract the column name (e.g., 'A' from 'A1')
    #             column_name = cell_position[0]  # e.g., 'A', 'B', 'C'
    #
    #             # Get the row number (e.g., '1' from 'A1', '2' from 'B2')
    #             row_index = int(cell_position[1:])  # Convert the rest to integer
    #             if row_index > row_max:
    #                 row_max = row_index
    #             # Get the column number (e.g., A -> 1, B -> 2)
    #             column_number = get_column_number(column_name)
    #             if column_number > col_max:
    #                 col_max = column_number
    #             # Call the set_user_input function with the appropriate arguments
    #             self.model.set_user_input(0, row_index, column_number, value.strip())
    #
    #     return row_max, col_max
    #
    # def parse_markdown_sheet(self, markdown_sheet: str):
    #     """ Logic to parse the markdown sheet """
    #     """ Parse a table in markdown format """
    #     # Save the first two rows
    #     header_rows = markdown_sheet[:2]
    #     data_rows = markdown_sheet[2:]
    #     col_max = 1
    #     # Process each data row
    #     for row_index, line in enumerate(data_rows, start=1):
    #         # Strip leading/trailing spaces and split by '|'
    #         cells = [cell.strip() for cell in line.strip('|').split('|')]
    #         if len(cells) > col_max:
    #             col_max = len(cells)
    #
    #         # Assign cell values to model
    #         for col_index, cell in enumerate(cells, start=1):
    #             # Update the model
    #             #print (0, row_index, col_index, cell.strip())
    #             self.model.set_user_input(0, row_index, col_index, cell.strip())
    #
    #     #return header_rows
    #     print ("markdown sheet read", len(data_rows), col_max)
    #     return len(data_rows), col_max
