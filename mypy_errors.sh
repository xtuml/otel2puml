#!/bin/bash

mypy --strict --explicit-package-bases --namespace-packages . > mypy_errors.txt
