
import tempfile
import app_controller


class TestController:

    def create_temp_file(self, content, extension):
        """Helper method to create a temporary file with specific content and extension."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=extension, mode='w', encoding='utf-8')
        temp_file.write(content)
        temp_file.close()
        return temp_file.name

    def test_controller(self):
        ct = app_controller.AppController()
        content = "| Peaches | Pears | Total |\n|-------|-----|\n| 2  | 3  | =A1+B1\n"
        tempfilename = self.create_temp_file(content, "md")

        # Read input file
        content = ct.read_file_content(tempfilename)

        # Send to recalculate
        worksheet = ct.evaluate(content.splitlines())

        # Get results from model and write to HTML file using a table for the grid
        outfilename = self.create_temp_file("<HTML>", "html")
        ct.writer.write(worksheet, outfilename, "HTML")

        # Read the result back in so we can test it
        actualhtml = ct.read_file_content(outfilename)
        assert actualhtml[:22] == "<HTML><TABLE><TR><td>2"
