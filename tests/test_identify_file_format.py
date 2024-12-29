import pytest
from core.data_transformer import DataTransformer


class TestIdentifyFileFormat:
    dt = DataTransformer()

    def test_csv_valid(self):
        content = "Name,Age,Location\nJohn,30,New York\nJane,25,San Francisco\n"
        assert self.dt.identify_file_format(".csv", content.splitlines()) == "Detected format: CSV"

    def test_sylk_valid(self):
        content = "ID;P\nC;X1;Y1\nC;X2;Y2\n"
        assert self.dt.identify_file_format(".slk", content.splitlines()) == "Detected format: SYLK"

    def test_markdown_valid(self):
        content = "| Name  | Age |\n|-------|-----|\n| John  | 30  |\n| Jane  | 25  |\n"
        assert self.dt.identify_file_format(".md", content.splitlines()) == "Detected format: Markdown"

    def test_dif_valid(self):
        content = "TABLE\nHEADER\nDATA\n"
        assert self.dt.identify_file_format(".dif", content.splitlines()) == "Detected format: DIF"

    def test_ser_valid(self):
        content = "A1:Hello\nB2:World\nC3:123\nD4:Test Value\n"
        assert self.dt.identify_file_format(".ser", content.splitlines()) == "Detected format: SER"

    def test_invalid_file(self):
        content = "I am not a spreadhseet\n"
        assert "Unknown: Format not recognized" in self.dt.identify_file_format(".md", content.splitlines())
