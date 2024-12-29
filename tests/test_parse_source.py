
import ironcalc
from core.data_transformer import DataTransformer

class TestParseSource():

    def test_parse_source_markdown(self):
        content = "| Name  | Age |\n|-------|-----|\n| John  | 30  |\n| Jane  | 25  |\n"
        dt = DataTransformer()
        dt.parse_source(".md", content.splitlines())
        model = dt.get_model()
        result = model.get_formatted_cell_value(0,1,1)
        assert "John" == result

    def test_parse_source_ser(self):
        content = "A1:Hello\nB2:World\nC3:123\nD4:Test Value\n"
        dt = DataTransformer()
        dt.parse_source(".ser", content.splitlines())
        model = dt.get_model()
        result = model.get_formatted_cell_value(0,1,1)
        assert "Hello" == result
