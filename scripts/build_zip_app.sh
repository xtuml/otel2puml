#!/bin/sh

# Fail if any part of this script fails
set -e

# install zipapps
pip install zipapps

# make dist directory
mkdir -p dist

# get current directory
DIR=$(pwd)

# make temp build directory
mkdir -p /tmp/otel2puml_build

# copy files to build directory
cp -r tel2puml /tmp/otel2puml_build/tel2puml
cp -r requirements.txt /tmp/otel2puml_build/requirements.txt


# get janus
git clone https://github.com/xtuml/janus.git /tmp/otel2puml_build/janus
cd /tmp/otel2puml_build/janus
git fetch --all --tags
git checkout tags/v1.0.0 -b latest
cp -r test_event_generator /tmp/otel2puml_build/test_event_generator
cp requirements.txt /tmp/otel2puml_build/janus_requirements.txt



# change directory to build directory 
cd /tmp/otel2puml_build
# create zipapp
python -m zipapps -c -a tel2puml,test_event_generator \
    -m tel2puml.__main__:main -o $DIR/dist/tel2puml.pyz -d -r requirements.txt -r janus_requirements.txt

# return to original directory
cd $DIR