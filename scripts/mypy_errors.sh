#!/bin/bash

cd $(git rev-parse --show-toplevel)

mypy --config-file .mypy.ini --strict --explicit-package-bases --namespace-packages .

# run checks immediately after updating mypy file
flake8 .
pylint --recursive=y .
pytest
