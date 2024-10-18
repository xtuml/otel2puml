## Walkthrough

This section provides a complete walkthrough of using `tel2puml` to convert OpenTelemetry (OTel) data into PlantUML activity diagrams. Example data is used to demonstrate the process from input OpenTelemetry data to the final generated diagrams.

### Step 1: Set Up the Environment

Before running the commands in this walkthrough, ensure that the tool is installed. It can be installed using the provided Docker image or through manual dependency installation. Refer to the [Installation](https://github.com/xtuml/otel2puml/blob/main/README.md#installation) section for more details.

### Step 2: Prepare Input Data

For this walkthrough, example JSON files are provided within [docs/example_otel_data](/docs/example_otel_data). They are:

- [Example File 1](/docs/example_otel_data/example_file1.json)
- [Example File 2](/docs/example_otel_data/example_file2.json)
- [Example File 3](/docs/example_otel_data/example_file3.json)

A [config](docs/example_otel_data/example_config.yaml) file has already been setup to be used with the example files.

### Step 3: Generate a PlantUML Diagram using otel2puml command

If you have manually installed otel2puml, run the following command to generate a puml diagram:

```bash
python -m tel2puml -o puml_output otel2puml -c docs/e2e_walkthrough/example_config.yaml
```

### Step 4: View PUML output

If run successfully, a [Users_Service.puml](/puml_output/Users_Service.puml) file should exist within the directory `puml_output`.