# core/file_writer.py
# TBD import markdown
#  tbl = "|a|b|c|\n|---|---|---:|\n|1|2|3|"
#  html = markdown.markdown(tbl, extensions=['tables'])
# PDF Refs
# https://pdforge.com/blog/how-to-generate-pdf-from-html-using-reportlab-in-python
#https://medium.com/@pymupdf/how-to-convert-html-tables-to-pdf-5aead22683c8
# https://realpython.com/creating-modifying-pdf/#creating-pdf-files-with-python-and-reportlab
# https://pymupdf.readthedocs.io/en/latest/recipes-stories.html#how-to-output-an-html-table
class FileWriter:
    def write(self, worksheet, output_path: str, format: str):
        row_max = worksheet['rows']
        col_max = worksheet['columns']
        spreadsheet = worksheet['sheet']
        text_file = open(output_path, "w")
        # Logic to write data as HTML or PDF
        if format == "PDF":
            # TODO: write PDF
            pass
        else: # write HTML
            text_file.write("<HTML><TABLE>")
            for row in range(1, row_max + 1):
                text_file.write ("<TR>")
                for col in range(1, col_max + 1):
                    value = spreadsheet.get_formatted_cell_value(0, row, col)
                    text_file.write(f"<td>{value}</td>")
                text_file.write ("</TR>\n")
            text_file.write ("</TABLE></HTML>")
        text_file.close()
