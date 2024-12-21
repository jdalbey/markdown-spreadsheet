from contextlib import ExitStack as DoesNotRaise

import lark
import pytest

from spreadsheet.spreadsheet import evaluate_spreadsheet

# The first argument "spreadsheet, result, raises_exception" is a string with variable names separated by commas.
# These names (spreadsheet, result, raises_exception) correspond to the parameters that will be passed into the test function test_get_cell.
#
# The second argument is a list of tuples. Each tuple represents one test case, containing:
#     spreadsheet: The input data for the test case (the spreadsheet dictionary).
#     result: The expected output (the dictionary of results that evaluate_spreadsheet should produce).
#     raises_exception: This defines whether an exception is expected during the test (in this case, it uses DoesNotRaise() which means no exception is expected).
@pytest.mark.parametrize(
    "spreadsheet, result, raises_exception",
    [  # identity and integer conversion
        (
            {
                "A1": "5",
            },
            {
                "A1": 5,
            },
            DoesNotRaise(),
        ),
        # String
        (
                {
                    "A1": "Hello World",
                },
                {
                    "A1": "Hello World",
                },
                DoesNotRaise(),
        ),
        # reference to another cell
        (
            {
                "A1": "5",
                "A2": "=A1",
            },
            {
                "A1": 5,
                "A2": 5,
            },
            DoesNotRaise(),
        ),
        # missing equals sign
        (
            {
                "A1": "5",
                "A2": "A1",
            },
            {"A1": 5, "A2": "A1"},
            DoesNotRaise(),
        ),
        # multiplication
        (
            {
                "A1": "5",
                "A2": "=(A1 * A1)",
            },
            {"A1": 5, "A2": 25},
            DoesNotRaise(),
        ),
        # integer division
        (
            {
                "A1": "10",
                "A2": "=(A1 / 5)",
            },
            {"A1": 10, "A2": 2},
            DoesNotRaise(),
        ),
        # integer division
        (
            {
                "A1": "2.1",
                "A2": "=(A1 / 2)",
            },
            {"A1": 2.1, "A2": 1.05},
            DoesNotRaise(),
        ),
        # addition
        (
            {
                "A1": "10",
                "A2": "=(A1 + 5)",
            },
            {"A1": 10, "A2": 15},
            DoesNotRaise(),
        ),
        # subtraction
        (
            {
                "A1": "10",
                "A2": "=(A1 - 5)",
            },
            {"A1": 10, "A2": 5},
            DoesNotRaise(),
        ),
        # nested expression
        (
            {
                "A1": "10",
                "A2": "=(A1 - (2 + 2))",
            },
            {"A1": 10, "A2": 6},
            DoesNotRaise(),
        ),
        # query with two nested terms
        (
            {
                "A1": "10",
                "A2": "=((A1 * 2) - (2 + 2))",
            },
            {"A1": 10, "A2": 16},
            DoesNotRaise(),
        ),
        # SUM function in a column
        (
                {
                    "A1": "2",
                    "A2": "3",
                    "A3": "=SUM(A1:A2)",
                },
                {"A1": 2, "A2": 3, "A3": 5},
                DoesNotRaise(),
        ),
        # SUM function in a row - NOT IMPLEMENTED
        (
                {
                    "A1": "2",
                    "B1": "3",
                    "C1": "=SUM(A1:B1)",
                },
                {"A1": 2, "B1": 3, "C1": 5},
                pytest.raises(KeyError),  # Exception expected here
        ),
        # invalid formula
        (
                {"A1": "5", "A2": "=INVALID_FORMULA"},
                {},
                pytest.raises(lark.exceptions.UnexpectedCharacters),  # Exception expected here
        ),
    ],
)
def test_get_cell(spreadsheet, result, raises_exception):
    with raises_exception:
        # process the spreadsheet and compute the values based on the rules
        computed_spreadsheet = evaluate_spreadsheet(spreadsheet)

        for cell in spreadsheet:
            #  ensures that the value of each cell in computed_spreadsheet matches the expected value from result
            assert computed_spreadsheet[cell] == result[cell]
