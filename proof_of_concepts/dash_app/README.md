# Dash App POC
This is a proof of concept for a Dash app that uses the [Dash](https://dash.plotly.com/) library to create a web application that displays a simple graph.

## Installation
Install the required dependencies for otel2puml using instructions from the root [README.md](../../README.md).

The following dependencies are required for this proof of concept:
- java installed and in your PATH variable of your shell (https://www.java.com/en/download/)
- graphviz installed (https://graphviz.gitlab.io/download/)
- plantuml jar file (https://plantuml.com/download)

Then run the following command to install the required python packages:
```bash
pip install -r requirements_app.txt
```

## Usage

To run the Dash app, run the following command in the terminal from the root of the repository:
```bash
python proof_of_concepts/dash_app/app.py <path_to_folder_of_jobs> <path_to_plantuml_jar>
```

* You will need to point to a folder that contains folders holding linked sequences of PV events in separate json files.
* You will also need to point to the plantuml jar file.

The app will run on `http://localhost:8050/` and will have the following layout:

![Dash App Layout](app.png)