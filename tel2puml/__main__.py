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

import argparse
from tel2puml.pv_to_puml import (
    pv_jobs_from_folder_to_puml_file,
    pv_jobs_from_files_to_puml_file,
    pv_events_from_folder_to_puml_file,
)

parser = argparse.ArgumentParser(prog="tel2puml")

parser.add_argument(
    "-fp",
    "--folder-path",
    metavar="dir",
    help="Path to folder containing job json files",
    default=".",
    dest="folder_path",
)

parser.add_argument(
    "-o",
    "--output",
    metavar="file",
    help="Output file path",
    default="./default.puml",
    dest="puml_file_path",
)

parser.add_argument(
    "-sn",
    "--sequence-name",
    metavar="name",
    help="Name given to the puml sequence diagram",
    default="default_name",
    dest="puml_name",
)

parser.add_argument(
    "file_paths",
    nargs="*",
    help="Input .json files containing job data",
)

parser.add_argument(
    "-group-by-job",
    help="Group events by job ID",
    action="store_true",
    dest="group_by_job",
)


if __name__ == "__main__":
    args: argparse.Namespace = parser.parse_args()
    args_dict = vars(args)
    if args_dict["file_paths"]:
        args_dict.pop("folder_path")
        args_dict.pop("group_by_job")
        pv_jobs_from_files_to_puml_file(**args_dict)
    elif args_dict["group_by_job"]:
        args_dict.pop("file_paths")
        pv_events_from_folder_to_puml_file(**args_dict)
    else:
        args_dict.pop("file_paths")
        args_dict.pop("group_by_job")
        pv_jobs_from_folder_to_puml_file(**args_dict)
