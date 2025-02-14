# OTEL2PUML
This project converts [OpenTelemetry (OTel)](https://opentelemetry.io/) data into [PlantUML activity diagrams](https://plantuml.com/activity-diagram-beta). These diagrams are subsequently ingested by [plus2json](https://github.com/xtuml/plus2json), a tool that transforms them into JSON format. The resulting JSON 'job definitions' are specifically tailored for use with the [Protocol Verifier](https://github.com/xtuml/munin) (PV), a tool that monitors and verifies the behaviour of another system, to ensure that it is behaving as expected.

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#why-use-this-tool">Why Use This Tool?</a></li>
    <li><a href="#features">Features</a></li>
    <li><a href="#how-it-works">How it Works</a></li>
    <li><a href="#quick-start">Quick Start</a>
      <ol>
        <li><a href="#using-docker-image">Using Docker Image</a></li>
        <li><a href="#using-python-executable">Using Python Executable</a></li>
      </ol>
    </li>
    <li><a href="#example-input-json-pv-event-sequence">Example Input</a></li>
    <li><a href="#example-output">Example Output</a></li>
    <li><a href="#e2e-example">E2E Example</a></li>
    <li><a href="#installation">Installation</a>
      <ol>
        <li><a href="#manual-installation">Manual Installation</a></li>
        <li><a href="#using-devcontainer">Using Devcontainer</a></li>
      </ol>
    </li>
    <li><a href="#tel2puml-cli-documentation">TEL2PUML CLI Documentation</a></li>
    <li><a href="#technical-implementation">Technical Implementtation</a></li>
    <li><a href="#documentation">Documentation</a></li>
    <li><a href="#dependencies">Dependencies</a></li>
    <li><a href="#contributing">Contributing</a></li>
  </ol>
</details>

## Why Use This Tool?

Although this tool was designed for use with the Protocol Verifier, as a standalone application it offers several benefits for developers, system architects, and DevOps professionals:

* Visualisation of Complex Systems: Convert abstract OpenTelemetry data into clear, visual PlantUML diagrams, making it easier to understand system interactions and dependencies.

* Debugging and Troubleshooting: Quickly identify bottlenecks, errors, and unexpected behaviors in your distributed systems by visualising trace data.

* Documentation: Generate up-to-date system diagrams automatically from actual runtime data, ensuring your documentation accurately reflects the current state of your system.

* Communication: Use the generated diagrams to facilitate discussions between technical and non-technical stakeholders, improving overall project understanding.

* Performance Optimisation: Visualise request flows and timing information to identify areas for performance improvements.

* Microservices Architecture Analysis: Gain insights into how your microservices interact, helping with architectural decisions and optimisations.

* Integration with Existing Tools: As it works with OpenTelemetry data, it integrates seamlessly with your existing observability stack.

* Time-Saving: Automate the process of creating system diagrams, saving valuable development time.

* Training and Onboarding: Use generated diagrams to help new team members understand system architecture and workflows quickly.

By converting OpenTelemetry data to PlantUML diagrams, this tool bridges the gap between raw observability data and easily understandable visual representations, enhancing your ability to develop, maintain, and optimise complex distributed systems.

## Features
* Convert OpenTelemetry (OTel) JSON data into detailed PlantUML activity diagrams with flexible output options and multiple subcommands for various processing needs.
* Easily customize and extend the tool to support new data formats or processing requirements through a modular design.
* Identify and extract unique causal event sequences from OTel data
* Produce clear and comprehensive PlantUML activity diagrams that accurately depict the system.

## How it Works
End to end the **otel2puml** tool ingests Open Telemetry data in JSON files and outputs activity diagrams in PlantUML format that represent the causal possibilities learnt from the data. The tool is split into two main components that can be used independently or together as **otel2puml**:

- **otel2pv** - Ingests OpenTelemetry Data (currently from JSON Files only) extracting the specific data from the OpenTelemetry [Spans](https://opentelemetry.io/docs/concepts/signals/traces/#spans) that make up [Traces](https://opentelemetry.io/docs/concepts/signals/traces/) that form call trees. These are then sequenced (see [Sequencing](/docs/user/sequencer_HOWTO.md)) and converted to Protocol Verifier (PV) Event Sequences (see [Data Types](/docs/user/DataTypes.md)). These are then output as:
    - JSON files containing PV Event Sequences
    - Ingested by **pv2puml** to create PlantUML Activity Diagrams

- **pv2puml** - Converts PV Event Sequences into PlantUML Activity Diagrams. These diagrams are then output as PlantUML files that can be viewed in a PlantUML viewer. Can take as input:
    - PV Event Sequence JSON files
    - The output PV Event sequence streams from **otel2pv**.

The diagram below shows the componentes and their specific inputs and outputs. Usage of the CLI is detailed in the [CLI Documentation](#tel2puml-cli-documentation).

![](/docs/images/user/otel2puml.svg)
## Quick Start

To quickly convert a PV event sequence JSON to a PlantUML activity diagram:

1. Install the tool (see [Installation](#installation))
2. Run the following command:

    ```sh
    python -m tel2puml pv2puml <pv event sequence json> -jn <output_diagram_name>
    ```

3. This will generate a PlantUML activity diagram in the current directory with the default name `<output_diagram_name>.puml`.
4. Open the generated PlantUML file in a PlantUML viewer to see the activity diagram.
### Example
A full example follows using the command above.
#### Example Input (JSON PV event sequence)
```json
[
    {
        "jobId": "8077a248-95e9-4687-8d96-e2ca2638cfab",
        "jobName": "simple_sequence",
        "eventType": "A",
        "eventId": "31185642-eee0-4ab4-8aac-43f94a0bb1b7",
        "timestamp": "2023-09-25T10:58:06.059959Z",
        "applicationName": "test_file_simple_sequence"
    },
    {
        "jobId": "8077a248-95e9-4687-8d96-e2ca2638cfab",
        "jobName": "simple_sequence",
        "eventType": "B",
        "eventId": "721897bf-48f4-499d-a7a3-0a8bff783b66",
        "timestamp": "2023-09-25T10:58:06.059993Z",
        "applicationName": "test_file_simple_sequence",
        "previousEventIds": [
            "31185642-eee0-4ab4-8aac-43f94a0bb1b7"
        ]
    },
    {
        "jobId": "8077a248-95e9-4687-8d96-e2ca2638cfab",
        "jobName": "simple_sequence",
        "eventType": "C",
        "eventId": "91943012-02d4-478c-bcfa-e12c5d6dc880",
        "timestamp": "2023-09-25T10:58:06.060022Z",
        "applicationName": "test_file_simple_sequence",
        "previousEventIds": [
            "721897bf-48f4-499d-a7a3-0a8bff783b66"
        ]
    }
]
```
See [Data Types](docs/user/DataTypes.md) for more information on the Protocol Verifier Event structure.
#### Example Output
The following command will generate a PlantUML activity diagram from the above JSON file (using the -jn flag to specify the output diagram name):
```sh
python -m tel2puml pv2puml example_above.json -jn "Example Sequence"
```


![](docs/images/example_sequence_for_readme.svg)

## E2E Example

A full end to end example and walkthrough can be found [here](/docs/user/e2e_walkthrough.md). Example files are provided.

## Using Docker Image

You can run otel2puml using the provided [Docker image](https://github.com/orgs/xtuml/packages?repo_name=otel2puml). This is especially useful if you want to run the tool in an isolated environment without manually managing dependencies. Here’s how to do it:

Example Command:
```bash
docker run \
 -v /path/to/job_json_files:/job_json_files \
 -v /path/to/config.yaml:/config.yaml \
 -v /path/to/puml_output:/puml_output \
 ghcr.io/xtuml/otel2puml:<version> \
 -o /puml_output otel2puml -c /config.yaml
```

Explanation:

* `-v /path/to/job_json_files:/job_json_files`: Mounts a local folder containing your OTel data in JSON format to the Docker container's /job_json_files directory. Note `/job_json_files` should then be added to the `dirpath` field in the `config.yaml` file.
* `-v /path/to/config.yaml:/config.yaml`: Mounts the configuration file for `otel2puml` to the Docker container's /config.yaml.
* `-v /path/to/puml_output:/puml_output`: Mounts a local folder where the output PlantUML diagrams will be saved.

    **NOTE**: If this folder does not exist, docker will likely create it with root permissions and an error will occur when saving output files. Ensure the folder exists before running the command.
* `ghcr.io/xtuml/otel2puml`:latest: Specifies the Docker image to run.
* `-o /puml_output`: Tells `otel2puml` where to save the generated PlantUML files inside the container (linked to the local `puml_output` folder).
* `otel2puml -c /config.yaml`: Runs the `otel2puml` command using the provided configuration file.

Replace `/path/to/` with the actual paths on your local machine.

## Using Python Executable
On each new [release](https://github.com/xtuml/otel2puml/releases) of otel2puml, a python executable, `tel2puml.pyz` will be built and distributed with the release.
This is downloadable and can be run from the terminal (assuming python and pip are installed). Below is an example of usage:

```bash
python tel2puml.pyz otel2puml -o /path/to/output -c /path/to/config.yaml
```

Note that: 
- an internet connection will be required to download the dependencies for the first time.
- pip must be resolvable in the terminal as `pip` for the dependencies to be installed.

## Dependencies

TEL2PUML depends on one other repository:

1. [Janus](https://github.com/xtuml/janus): 

   Janus ingests PUML activity diagram files and generates event sequences from them.

This dependency is automatically managed when using the devcontainer setup or when running the `install_repositories.sh` script during manual installation.

## Installation

There are two ways to set up this project: manual installation (both for usage and development) or using a devcontainer (development).

### Manual Installation

The project can be installed manually in a few different ways. Make sure you have the following prerequisites for all installation methods:
* `git`
* Python version > 3.11.0 and < 3.13
* `bash`
* `pip` (Python package manager)

(OPTIONAL) If you want to use the following functions:
* `tel2puml.events.save_vis_logic_gate_tree`
* `tel2puml.utils.get_graphviz_plot`
you will also need:
* Java runtime environment (can be installed via `apt install default-jre` if using debian but will vary depending on your OS)
* [Graphviz](https://graphviz.org/download/) installed

#### With Anaconda (Recommended)

Before proceeding with the manual installation, ensure you have the following prerequisites:

* [Anaconda](https://conda.io/projects/conda/en/latest/index.html) installed and managing the Python installation

To install the project manually:

1. Clone the repository
```bash
git clone https://github.com/xtuml/otel2puml.git
```
2. Set up a Python virtual environment (recommended)
3. Navigate to the project root directory
4. Run the following commands:

```bash
conda install -c conda-forge cvxopt
conda install -c conda-forge pygraphviz
./scripts/install_repositories.sh
python3.11 -m pip install -r requirements.txt
```

#### Without Anaconda

If you don't have Anaconda installed, you can still install the project manually on both linux distributions and MacOS.

##### Linux
Before proceeding, ensure you have the following prerequisites that are required (since there is no build wheel for cvxopt1.3.2 for linux):

* lapack and blas libraries installed (can be installed via `apt install liblapack-dev libblas-dev` if using debian but will vary depending on your OS)
* suiteparse library installed (can be installed via `apt install libsuitesparse-dev` if using debian but will vary depending on your OS)
* glpk library installed (can be installed via `apt install libglpk-dev` if using debian but will vary depending on your OS)

To install the project manually:

1. Clone the repository
2. Set up a Python virtual environment (recommended)
3. Navigate to the project root directory
4. Run the following commands:

```bash
./scripts/install_repositories.sh
export CPPFLAGS="-I/usr/include/suitesparse"
export CVXOPT_BUILD_GLPK=1
python3.11 -m pip install -r requirements.txt
```

##### MacOS

To install the project manually on MacOS:

1. Clone the repository
2. Set up a Python virtual environment (recommended)
3. Navigate to the project root directory
4. Run the following commands:

```bash
./scripts/install_repositories.sh
python3.11 -m pip install -r requirements.txt
```

### Using Devcontainer

Alternatively, you can use the provided devcontainer, which manages all dependencies automatically. To use the devcontainer:

* Ensure you have Docker installed on your system
* Install the Dev Containers extension for Visual Studio Code
* Open the project folder in VS Code
* When prompted, click "Reopen in Container" or use the command palette (F1) and select "Remote-Containers: Reopen in Container"

The devcontainer will automatically set up the environment with all necessary dependencies.

It is recommended to only use this for development purposes as files/directories on the users system will not be reachable from the container without specifically mounting volumes.

## tel2puml CLI Documentation

`tel2puml` is a command-line tool designed to convert [OpenTelemetry](https://opentelemetry.io/)  into [PlantUML](https://plantuml.com/) sequence diagrams.

### Usage

The `tel2puml` CLI provides several subcommands to handle different data processing scenarios:

- `otel2puml`: Convert OpenTelemetry data directly into PlantUML sequence diagrams.
- `otel2pv`: Convert OpenTelemetry data into an intermediate PV format.
- `pv2puml`: Convert PV data into PlantUML sequence diagrams.

### General Syntax

```bash
python -m tel2puml [-o output_directory] [subcommand] [options]
```

** Global Options**
- `-o`, `--output-dir`: Output directory path (default is the current directory). Nested folder creation is not supported.

### Subcommands and Options

#### `otel2puml`

Converts OpenTelemetry data directly into a PlantUML sequence diagram.

**Usage:**

```bash
python -m tel2puml -o OUTPUT_DIR otel2puml -c CONFIG_FILE [options]
```

**Options:**

- `-c`, `--config`: **(Required)** Path to the configuration YAML file. [Usage](docs/user/Config.md)
- `-ni`, `--no-ingest`: Do not load data into the data holder.
- `-ug`, `--unique-graphs`: Find unique graphs within the data holder.
- `-d`, `--debug`: Enable debug mode to view full error stack trace.
- `-im`, `--input-puml-models`: Path to an input puml model. Can be used multiple times for each model the user wishes to input. [Usage](/docs/user/PUML_models.md)
- `-om`, `--output-puml-models`: Flag to indicate whether to output the puml models. If this flag is not set, the puml models will not be output. [Usage](/docs/user/PUML_models.md)

**Example:**

```bash
python -m tel2puml -o /output/path/ otel2puml -c /path/to/config.yaml
```

#### `otel2pv`

Converts OpenTelemetry data into an intermediate PV format.

**Usage:**

```bash
python -m tel2puml otel2pv -c CONFIG_FILE [options]
```

**Options:**

- `-c`, `--config`: **(Required)** Path to the configuration YAML file. [Usage](docs/user/Config.md)
- `-ni`, `--no-ingest`: Do not load data into the data holder.
- `-ug`, `--unique-graphs`: Find unique graphs within the data holder.
- `-se`, `--save-events`: Save PVEvents in intermediate format.
- `-mc`, `--mapping-config`: Path to the mapping configuration file. [Usage](docs/user/mapping_config.md)
- `-d`, `--debug`: Enable debug mode to view full error stack trace.

**Example:**

```bash
python -m tel2puml -o /output/path/ otel2pv -c /path/to/config.yaml -se
```

#### `pv2puml`

Converts PV Event data (see [Data Types](/docs/user/DataTypes.md) for more information on the Protocol Verifier data) into PlantUML sequence diagrams.

**Usage:**

```bash
python -m tel2puml pv2puml [options] [FILE_PATHS...]
```

**Options:**

- `-fp`, `--folder-path`: Path to a folder containing job JSON files (PV Event JSONs in array's). Cannot be used with `FILE_PATHS`.
- `FILE_PATHS`: One or more files containing job JSON (PV Event JSON arrays) array data. Cannot be used with `-fp`.
- `-jn`, `--job-name`: Name for the PlantUML sequence diagram and output file prefix (default is `"default_name"`).
- `-group-by-job`: Group events by job ID. Can only be used if there are single events in each input file otherwise an error will be raised.
- `-mc`, `--mapping-config`: Path to the mapping configuration file. [Usage](docs/user/mapping_config.md)
- `-d`, `--debug`: Enable debug mode to view full error stack trace.
- `-im`, `--input-puml-models`: Path to an input puml model. Can be used multiple times for each model the user wishes to input. [Usage](/docs/user/PUML_models.md)
- `-om`, `--output-puml-models`: Flag to indicate whether to output the puml models. If this flag is not set, the puml models will not be output. [Usage](/docs/user/PUML_models.md)

**Notes:**

- You must provide either `-fp` or `FILE_PATHS`, but not both.
- The `-group-by-job` option is used when you have single events in files and you need to group them by `job_id` (into event sequences).

**Examples:**

- Convert a folder of job files into a PlantUML sequence diagram:

  ```bash
  python -m tel2puml -o /path/to/output/ pv2puml -fp /path/to/folder
  ```

- Convert specific job json files into a PlantUML sequence diagram:

  ```bash
  python -m tel2puml -o /path/to/output/ pv2puml file1.json file2.json
  ```

- Convert a folder of job JSON files with a custom job name:

  ```bash
  python -m tel2puml -o /path/to/output/ pv2puml -fp /path/to/folder -jn "MySequenceDiagram"
  ```

- Convert a folder of job JSON files and group events by job ID:

  ```bash
  python -m tel2puml -o /path/to/output/ pv2puml -fp /path/to/folder -group-by-job
  ```

## Help and Usage Information

For detailed help on each subcommand, use the `-h` or `--help` option:

```bash
python -m tel2puml [subcommand] -h
```

**Example:**

```bash
python -m tel2puml pv2puml -h
```

## Technical Implementation

To gain a better technical understanding of the project it's recommended to read the [technical implementation overview](docs/Technical_implementation_overview.md).

## Documentation

Documentation for tel2puml can be found in the [docs](docs) folder. This contains [design notes](docs/development/design), [end to end test information](docs/development/end-to-end-tests) and the [technical implementation overview](docs/Technical_implementation_overview.md).

## Contributing

We welcome contributions to improve tel2puml! Here's how you can contribute:

1. Fork the repository
2. Create a new branch (git checkout -b feature/amazing-feature)
3. Make your changes
4. Commit your changes (git commit -m 'Add some amazing feature')
5. Push to the branch (git push origin feature/amazing-feature)
6. Open a Pull Request
