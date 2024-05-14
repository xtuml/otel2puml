#!/bin/sh

# Fail if any part of this script fails
set -e

# test event generator
cd /tmp/
git clone git@github.com:SmartDCSITlimited/test-event-generator.git
cd test-event-generator
git fetch --all --tags
git checkout tags/v1.0.1 -b latest 
pip install -r requirements.txt
pip install .
cd ..
rm -f -r test-event-generator/

# test harness
cd /tmp/
git clone git@github.com:SmartDCSITlimited/test-harness.git
cd test-harness
git fetch --all --tags
git checkout tags/v1.1.3 -b latest 
pip install -r requirements.txt
pip install .
cd ..
rm -f -r test-harness/
