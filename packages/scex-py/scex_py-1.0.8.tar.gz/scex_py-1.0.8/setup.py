# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scex_py']

package_data = \
{'': ['*'], 'scex_py': ['input_xml/*', 'input_xml/balloon_payment/*']}

install_requires = \
['requests>=2.28.1,<2.29.0', 'xmltodict>=0.12.0,<0.13.0']

setup_kwargs = {
    'name': 'scex-py',
    'version': '1.0.8',
    'description': '',
    'long_description': '# scex_py\n\nPython wrapper for SCEX - Loan calculation package\n\n## Pre-commit\n\nRun the below command to install the pre-commit hooks:\n\n```bash\n$ poetry run pre-commit install\n```\n\nTo execute the hooks without making any commit:\n\n```bash\n$ poetry run pre-commit run --all-files\n```\n\n## Usage\n\n```\n>>> from scex_py.scex_client import ScexClient\n\n>>> client = ScexClient("host", "api_key")\n\n>>> client.process_equal_payment_loan({\n        "LoanDate": "2020-02-02",           # Year-month-date\n        "PmtDate": "2020-02-02",            # Year-month-date\n        "IntStartDate": "2020-02-02",       # Year-month-date\n        "Proceeds": 20000,\n        "Term": 5,\n        "IntRate": 10,\n        "TotalDown": 2000\n    })\n```\n',
    'author': 'Jatin Goel',
    'author_email': 'jatin.goel@thesummitgrp.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Lenders-Cooperative/scex_py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10.2,<4.0.0',
}


setup(**setup_kwargs)
