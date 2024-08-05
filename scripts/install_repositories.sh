#!/bin/sh

# Fail if any part of this script fails
set -e

# janus - test event generator
cd /tmp/
git clone https://github.com/xtuml/janus.git
cd janus
git fetch --all --tags
git checkout tags/v1.0.0 -b latest 
pip install -r requirements.txt
pip install .
cd ..
rm -f -r janus/

# erebus - test harness
cd /tmp/
git clone https://github.com/xtuml/erebus.git
cd erebus
git fetch --all --tags
git checkout tags/v0.2.1-beta -b latest 
pip install -r requirements.txt
pip install .
cd ..
rm -f -r erebus/
