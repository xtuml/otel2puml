#!/bin/sh

# Fail if any part of this script fails
set -e

# get test event generator
git clone https://github.com/xtuml/janus.git
cd janus
git fetch --all --tags
git checkout tags/v1.0.0 -b latest
cd ..
cp -r janus/test_event_generator ./test_event_generator


# install zipapps
pip install zipapps

# create zipapp
python -m zipapps -c -u AUTO -a tel2puml -a test_event_generator \
    -o tel2puml_arm.pyz -r requirements.txt -r janus/requirements.txt