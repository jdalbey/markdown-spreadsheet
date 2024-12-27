import unittest
import app_controller

class TestModelEvaluate(unittest.TestCase):

    def test_evaluate_markdown(self):
        content = "| Peaches | Pears | Total |\n|-------|-----|\n| 2  | 3  | =A1+B1\n"
        ct = app_controller.AppController()
        worksheet = ct.evaluate(content.splitlines())
        model = worksheet['sheet']
        result = model.get_formatted_cell_value(0,1,3)
        self.assertEqual("5",result)


if __name__ == "__main__":
    unittest.main()
