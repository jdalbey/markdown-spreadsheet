from contextlib import ExitStack as DoesNotRaise

import lark
import pytest

from spreadsheet.spreadsheet import evaluate_spreadsheet

import pytest
import json

@pytest.fixture
def spreadsheet_data():
    with open('fixtures/spreadsheet.json') as f:
        return json.load(f)

expected_result = {
    "A1": "10.0",
    "A2": "10.0",
    "A3": "500.0",
    "A4": "=A1:A3",
    "A5": 500.0,
    "A6": 3.0,
    "A7": 1.0
}
def test_evaluate(spreadsheet_data):
    # Now you can use the `spreadsheet_data` fixture to run tests
    computed_spreadsheet = evaluate_spreadsheet(spreadsheet_data)
    assert computed_spreadsheet == expected_result
