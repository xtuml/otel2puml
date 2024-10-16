"""Main function to call test harness

This module is the main entry point for the tel2puml package. It provides a
command line interface to
1) convert a folder of job json files to a PlantUML sequence diagram file.
2) convert a list of job json files to PlantUML sequence diagram file.
3) convert folder of job json files to a PlantUML sequence diagram file by
first grouping PV Events by job ID

Example:
```bash
    $ python -m tel2puml -fp /path/to/folder -o /path/to/output.puml
    $ python -m tel2puml file1.json file2.json -o /path/to/output.puml
    $ python -m tel2puml -fp /path/to/folder -o /path/to/output.puml \
        -sn "My Sequence Diagram"
    $ python -m tel2puml -fp /path/to/folder -o /path/to/output.puml \
        -group-by-job
```
"""

import os
import argparse
import yaml
import warnings
from typing import Any, Literal

from tel2puml.otel_to_puml import otel_to_puml
from tel2puml.tel2puml_types import (
    OtelToPVArgs,
    PvToPumlArgs,
    OtelPVOptions,
    PVPumlOptions,
    PVEventMappingConfig
)
from tel2puml.otel_to_pv.config import IngestDataConfig


parser = argparse.ArgumentParser(prog="otel2puml")
# global arguments
subparsers = parser.add_subparsers(dest="command", help="sub-command help")
parser.add_argument(
    "-o",
    "--output-dir",
    metavar="folder",
    help="Output folder path",
    default=".",
    dest="output_file_directory",
)

# mapping config, shared between otel2pv and pv2puml
mapping_config_parent_parser = argparse.ArgumentParser(add_help=False)

mapping_config_parent_parser.add_argument(
    "-mc",
    "--mapping-config",
    metavar="mapping-config",
    help="Path to mapping configuration file",
    dest="mapping_config_file",
    required=False,
)

# otel subparsers and shared arguments
otel_parent_parser = argparse.ArgumentParser(add_help=False)

otel_parent_parser.add_argument(
    "-c",
    "--config",
    metavar="config",
    help="Path to configuration file",
    dest="config_file",
    required=True,
)

otel_parent_parser.add_argument(
    "-ni",
    "--no-ingest",
    help="Flag to indicate whether to load data into the data holder",
    action="store_false",
    dest="ingest_data",
)

otel_parent_parser.add_argument(
    "-ug",
    "--unique-graphs",
    help=(
        "Flag to indicate whether to find unique graphs within the data holder"
    ),
    action="store_true",
    dest="find_unique_graphs",
)

# otel to puml and otel to pv sub parsers
otel_to_puml_parser = subparsers.add_parser(
    "otel2puml",
    help="otel to puml help",
    parents=[otel_parent_parser],
)

otel_to_pv_parser = subparsers.add_parser(
    "otel2pv",
    help="otel to pv help",
    parents=[otel_parent_parser, mapping_config_parent_parser],
)

# otel to pv args
otel_to_pv_parser.add_argument(
    "-se",
    "--save-events",
    help="Flag indicating whther to save events to the output directory",
    action="store_true",
    dest="save_events",
)

# pv to puml subparser
pv_to_puml_parser = subparsers.add_parser(
    "pv2puml", help="pv to puml help", parents=[mapping_config_parent_parser]
)
pv_input_paths = pv_to_puml_parser.add_argument_group(
    "Input paths",
    "Input path options for pv to puml. Only one option can be used at a time",
)
pv_exclusive_group = pv_input_paths.add_mutually_exclusive_group(required=True)

pv_exclusive_group.add_argument(
    "-fp",
    "--folder-path",
    metavar="dir",
    help="Path to folder containing job json files",
    dest="folder_path",
    required=False,
)

pv_exclusive_group.add_argument(
    "file_paths",
    nargs="*",
    help="Input files containing job data in json format",
    default=[],
)

pv_to_puml_parser.add_argument(
    "-jn",
    "--job-name",
    metavar="name",
    help=(
        "Name given to the puml sequence diagram and prefix for the output "
        "puml file"
    ),
    default="default_name",
    dest="job_name",
)

pv_to_puml_parser.add_argument(
    "-group-by-job",
    help="Group events by job ID",
    action="store_true",
    dest="group_by_job",
)


def generate_config(file_path: str) -> Any:
    """Parse config file.

    :param file_path: The filepath to the config file
    :type file_path: `str`
    :return: Config file represented as a dictionary
    :rtype: `dict`[`str`, `Any`]
    """
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def find_files(directory: str) -> list[str]:
    """Walk a directory path and extract files.

    :param directory: The directory path
    :type directory: `str`
    :return: List of filepaths
    :rtype: `list`[`str`]
    """
    job_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            job_files.append(os.path.join(root, file))

    if not job_files:
        raise FileNotFoundError(
            f"No files were found in directory '{directory}'"
        )

    return job_files


def generate_component_options(
    command: Literal["otel2puml", "otel2pv", "pv2puml"],
    args_dict: dict[str, Any],
) -> tuple[OtelPVOptions | None, PVPumlOptions | None]:
    """Generate puml options objects based on CLI arguments.

    :param command: The CLI command
    :type command: `Literal`["otel2puml", "otel2pv", "pv2puml"]
    :return: A tuple containing component options
    :rtype: `tuple`[:class:`OtelPVOptions` | `None`, :class:`PVPumlOptions`
    | `None`]
    """

    otel_pv_options, pv_puml_options = None, None
    mapping_config = PVEventMappingConfig()
    if command == "otel2puml" or command == "otel2pv":
        otel_to_pv_obj = OtelToPVArgs(**args_dict)
        config = IngestDataConfig(
            **generate_config(str(otel_to_pv_obj.config_file))
        )
        if otel_to_pv_obj.mapping_config_file:
            mapping_config = PVEventMappingConfig(
                **generate_config(str(otel_to_pv_obj.mapping_config_file))
            )
        otel_pv_options = OtelPVOptions(
            config=config,
            ingest_data=otel_to_pv_obj.ingest_data,
            save_events=otel_to_pv_obj.save_events,
            find_unique_graphs=otel_to_pv_obj.find_unique_graphs,
            mapping_config=mapping_config,
        )
    elif command == "pv2puml":
        pv_to_puml_obj = PvToPumlArgs(**args_dict)
        if pv_to_puml_obj.file_paths:
            file_list = [
                str(filepath) for filepath in pv_to_puml_obj.file_paths
            ]
        elif pv_to_puml_obj.folder_path:
            file_list = find_files(str(pv_to_puml_obj.folder_path))
        if pv_to_puml_obj.mapping_config_file:
            mapping_config = PVEventMappingConfig(
                **generate_config(str(pv_to_puml_obj.mapping_config_file))
            )
        pv_puml_options = PVPumlOptions(
            file_list=file_list,
            job_name=pv_to_puml_obj.job_name,
            group_by_job_id=pv_to_puml_obj.group_by_job,
            mapping_config=mapping_config,
        )

    return otel_pv_options, pv_puml_options


if __name__ == "__main__":
    warnings.filterwarnings("ignore")

    args: argparse.Namespace = parser.parse_args()
    args_dict = vars(args)
    otel_pv_options, pv_puml_options = generate_component_options(
        args.command, args_dict
    )
    otel_to_puml(
        otel_pv_options,
        pv_puml_options,
        args_dict["output_file_directory"],
        args.command,
    )
