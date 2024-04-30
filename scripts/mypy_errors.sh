#!/bin/bash

cd $(git rev-parse --show-toplevel)

mypy --config-file .mypy.test.ini --strict --explicit-package-bases --namespace-packages . > mypy_errors.txt

# run checks immediately after updating mypy file
flake8 .
pylint --recursive=y .
pytest
