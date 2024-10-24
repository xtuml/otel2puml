## E2E tel2puml Walkthrough

This section provides a complete walkthrough of using `tel2puml` to convert OpenTelemetry (OTel) data into PlantUML activity diagrams. Example data is used to demonstrate the process from input OpenTelemetry data to the final generated diagrams.

### Step 1: Set Up The Environment

Before running the commands in this walkthrough, ensure that the tool is installed. It can be installed using the provided Docker image or manually. Refer to the [Installation](https://github.com/xtuml/otel2puml/blob/main/README.md#installation) section for more details.

### Step 2: Take A Look At Example Input Data

For this walkthrough, example JSON files are provided within [docs/example_otel_data](/docs/e2e_walkthrough/example_otel_data). They are:

- [Example File 1](/docs/e2e_walkthrough/example_otel_data/example_file1.json)
- [Example File 2](/docs/e2e_walkthrough/example_otel_data/example_file2.json)
- [Example File 3](/docs/e2e_walkthrough/example_otel_data/example_file3.json)

A [config](/docs/e2e_walkthrough/example_config.yaml) file has already been setup to be used with the example files.

### Step 3: Generate PlantUML Diagram Using otel2puml Command

For manual installation, run the following command to generate a puml diagram:

```bash
cd otel2puml

python -m tel2puml -o puml_output otel2puml -c docs/e2e_walkthrough/example_config.yaml
```

For use with Docker, the following volumes must be mounted:

1. Output folder
2. Example files folder
3. Config file

Please refer to the [Using Docker Image](https://github.com/xtuml/otel2puml/blob/main/README.md#using-docker-image) as a guide.

### Step 4: View PUML output

For manual installation, if run successfully, a `Users_Service.puml` file can now be found in the newly created directory `/puml_output`. The svg output should resemble the example below. For use with docker, the output will be found in the output directory specified.

**NB. Due to the how the application works, the layout of the PUML may differ, however the structure and flow should remain consistent.**

![](/docs/images/example_Users_Service.svg)

### Step 5: Exploring other commands

For these commands, manual installation is assumed. For docker installation, please refer to the [Docker guide](https://github.com/xtuml/otel2puml/blob/main/README.md#using-docker-image)

#### otel2pv
To generate and save job JSON files, run the following command:

```bash
python -m tel2puml -o pv_event_json otel2pv -c docs/e2e_walkthrough/example_config.yaml -se
```

A directory located at `pv_event_json/Users_Service` will have been created with 3 JSON files. These should match the files located [here](/docs/e2e_walkthrough/example_pv_event_sequence_files/)

#### pv2puml
To generate the PUML from the newly created job JSON files, run the following command:

```bash
python -m tel2puml -o puml_output pv2puml -fp pv_event_json/Users_Service -jn "Users_Service_pv2puml"
```

Alternatively, the example files can be used:

```bash
python -m tel2puml -o puml_output pv2puml -fp docs/e2e_walkthrough/example_pv_event_sequence_files -jn "Users_Service_pv2puml"
```

The output should be the same as Step 4.
