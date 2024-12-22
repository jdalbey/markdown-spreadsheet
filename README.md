# Markdown spreadsheet
Evaluate a Markdown-style spreadsheet.

Takes as input a Markdown-style table that may include simple spreadsheet expressions and formulas.  Will evaluate the spreadsheet and print a Markdown table containing the resulting values.

## Development

Create and activate a venv:

```shell
python -m venv .venv
. .venv/bin/activate  # on Linux
env\Scripts\activate  # on Windows
```

Install the package and its runtime and test dependencies:

```shell
python -m pip install -e .[tests]
```

Run the tests:

```shell
python -m pytest
```

Run the application:
```shell
python main.py tests/table1.md
```

### Acknowledgement
This project is a fork of @capjamesg/spreadsheet.
Significant updates have been made by @jdalbey.
