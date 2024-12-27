import unittest
import app_controller
import tempfile

class TestController(unittest.TestCase):

    def create_temp_file(self, content, extension):
        """Helper method to create a temporary file with specific content and extension."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=extension, mode='w', encoding='utf-8')
        temp_file.write(content)
        temp_file.close()
        return temp_file.name

    def test_controller(self):
        ct = app_controller.AppController()
        content = "| Peaches | Pears | Total |\n|-------|-----|\n| 2  | 3  | =A1+B1\n"
        tempfilename = self.create_temp_file(content,"md")
        # Read input file
        content = ct.read_file_content(tempfilename)
        # send to recalculate
        worksheet = ct.evaluate(content)
        # get results from model and write to HTML file using a table for the grid.
        outfilename = self.create_temp_file("<HTML>", "html")
        ct.writer.write(worksheet,outfilename,"HTML")
        # Read the result back in so we can test it
        actualhtml = ct.read_file_content(outfilename)[0]
        self.assertEqual("<HTML><TABLE><TR><td>2",actualhtml[:22])

if __name__ == "__main__":
    unittest.main()
