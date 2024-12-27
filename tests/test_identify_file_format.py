import unittest

import os
from core.data_transformer import identify_file_format

class TestIdentifyFileFormat(unittest.TestCase):



    def test_csv_valid(self):
        content = "Name,Age,Location\nJohn,30,New York\nJane,25,San Francisco\n"
        self.assertEqual(identify_file_format(".csv",content.splitlines()), "Detected format: CSV")

    def test_sylk_valid(self):
        content = "ID;P\nC;X1;Y1\nC;X2;Y2\n"
        self.assertEqual(identify_file_format(".slk",content.splitlines()), "Detected format: SYLK")

    def test_markdown_valid(self):
        content = "| Name  | Age |\n|-------|-----|\n| John  | 30  |\n| Jane  | 25  |\n"
        self.assertEqual(identify_file_format(".md",content.splitlines()), "Detected format: Markdown")

    def test_dif_valid(self):
        content = "TABLE\nHEADER\nDATA\n"
        self.assertEqual(identify_file_format(".dif",content.splitlines()), "Detected format: DIF")

    def test_ser_valid(self):
        content = "A1:Hello\nB2:World\nC3:123\nD4:Test Value\n"
        self.assertEqual(identify_file_format(".ser",content.splitlines()), "Detected format: SER")

    def test_invalid_file(self):
        content = "I am not a spreadhseet\n"
        self.assertIn("Unknown: Format not recognized", identify_file_format(".md",content.splitlines()))

if __name__ == "__main__":
    unittest.main()
