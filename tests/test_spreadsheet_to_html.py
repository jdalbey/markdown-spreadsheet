import unittest
import app_controller
from core.data_transformer import spreadsheet_to_html

class TestSpreadsheetToHtml(unittest.TestCase):

    def test_spreadsheet_to_html(self):
        ct = app_controller.AppController()
        content = "| Peaches | Pears | Total |\n|-------|-----|\n| 2  | 3  | =A1+B1\n"
        # send to recalculate
        worksheet = ct.evaluate(content.splitlines())
        # get results from model and write to HTML file using a table for the grid.
        actualhtml = spreadsheet_to_html(worksheet)
        self.assertEqual("<HTML><TABLE>\n<TR>\n<td>2",actualhtml[:24])


if __name__ == "__main__":
    unittest.main()
