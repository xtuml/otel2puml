#!/bin/bash

mypy --strict --explicit-package-bases --namespace-packages . > mypy_errors.txt

# run checks immediately after updating mypy file
flake8 .
pylint --recursive=y .
pytest
