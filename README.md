# TEL2PUML
Repository for functionality of converting Telemetry streams into PUML activity diagrams.

### <b>Installation</b>
The project can be installed on the machine by choosing the project root directory as the working directory and running the following sequence of commands (it is recommended that a python virtual environment is set up so as not to pollute the main install). The following pre-requisites must be satisfied before installation can occur properly:

* anaconda (https://www.anaconda.com/) must be installed and managing the below python installation
* the python version must be 3.11

The installation instructions are then as follows

* graphviz must be installed (installation instructions can be found https://graphviz.org/download/)
* `conda install -c conda-forge cvxopt`
* `conda install -c conda-forge pygraphviz`
* `./scripts/install_repositories.sh`
* `python3.11 -m pip install -r requirements.txt`
