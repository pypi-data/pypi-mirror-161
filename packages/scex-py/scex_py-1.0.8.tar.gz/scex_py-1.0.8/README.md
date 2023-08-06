# scex_py

Python wrapper for SCEX - Loan calculation package

## Pre-commit

Run the below command to install the pre-commit hooks:

```bash
$ poetry run pre-commit install
```

To execute the hooks without making any commit:

```bash
$ poetry run pre-commit run --all-files
```

## Usage

```
>>> from scex_py.scex_client import ScexClient

>>> client = ScexClient("host", "api_key")

>>> client.process_equal_payment_loan({
        "LoanDate": "2020-02-02",           # Year-month-date
        "PmtDate": "2020-02-02",            # Year-month-date
        "IntStartDate": "2020-02-02",       # Year-month-date
        "Proceeds": 20000,
        "Term": 5,
        "IntRate": 10,
        "TotalDown": 2000
    })
```
