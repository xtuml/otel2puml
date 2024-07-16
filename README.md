# TEL2PUML
Repository for functionality of converting Telemetry streams into PUML activity diagrams.

### <b>Installation</b>
The project can be installed on the machine by choosing the project root directory as the working directory and running the following sequence of commands (it is recommended that a python virtual environment is set up so as not to pollute the main install). The following pre-requisites must be satisfied before installation can occur properly:

* anaconda (https://www.anaconda.com/) must be installed and managing the below python installation
* the python version must be 3.11.8 or lower
* a Java runtime environment must be available (can be installed via `apt install default-jre`)

The installation instructions are then as follows

* graphviz must be installed (installation instructions can be found https://graphviz.org/download/)
* `conda install -c conda-forge cvxopt`
* `conda install -c conda-forge pygraphviz`
* `./scripts/install_repositories.sh`
* `python3.11 -m pip install -r requirements.txt`

# tel2puml CLI Documentation

`tel2puml` is a command-line tool for converting job JSON files to PlantUML sequence diagrams.

## Usage

```sh
python -m tel2puml [-h] [file_paths] [-fp dir] [-o file] [-sn name] [-group-by-job]
```

## Options

- `-h`, `--help`: Show this help message and exit.

- `-fp dir`, `--folder-path dir`: 
  Path to folder containing job JSON files. 
  Default: current directory.

- `-o file`, `--output file`: 
  Output file path for the generated PlantUML file. 
  Default: `./default.puml`

- `-sn name`, `--sequence-name name`: 
  Name given to the PlantUML sequence diagram. 
  Default: `default_name`

- `file_paths`: 
  Input .json files containing job data. Multiple files can be specified.

- `-group-by-job`: 
  Group events by job ID. This option doesn't take any value.

## Examples

1. Convert a folder of job JSON files to a PlantUML sequence diagram file:

```sh
python -m tel2puml -fp /path/to/folder -o /path/to/output.puml
```

2. Convert a list of job JSON files to a PlantUML sequence diagram file:

```sh
python -m tel2puml file1.json file2.json -o /path/to/output.puml
```

3. Convert a folder of job JSON files to a PlantUML sequence diagram file with a custom name:

```sh
python -m tel2puml -fp /path/to/folder -o /path/to/output.puml -sn "My Sequence Diagram"
```

4. Convert a folder of job JSON files to PlantUML sequence diagram file, grouping PV Events by job ID:

```sh
python -m tel2puml -fp /path/to/folder -o /path/to/output.puml -sn "My Sequence Diagram" -group-by-job
```

## Behaviour

- If individual file paths are provided, the tool will convert those specific files to a single PlantUML diagram.
- If the `-group-by-job` option is used, the tool will process all files in the specified folder, grouping events by job ID and outputting a PlantUML file to the specified output filepath.
- If neither individual files nor the `-group-by-job` option are specified, the tool will convert all JSON files in the specified folder (or current directory if not specified) to a single PlantUML diagram.