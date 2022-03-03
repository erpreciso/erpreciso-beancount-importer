# erpreciso-beancount-importer
transform data from various sources to beancount-readable formats

# Installation

Navigate to the package folder, containing the `pyproject.toml` file, and launch 
`pip install .`.


# Usage

Call `bean-extract` passing:

* the ledger file; in this example, `start.beancount` import all other ledgers;
* the `config.py` file, containing importers and categorizers;
* the folder containing the raw inputs to be parsed.

and write to a new file.

```
bean-extract --existing ..\..\..\prod\start.beancount ..\config\config.py ..\data\ >> ..\data\%DATE:~-4%-%DATE:~-7,2%-%DATE:~-10,2%-new-transactions.beancount
```

From Windows CMD, run the `run-importer.bat`, adjusting the relative path.

