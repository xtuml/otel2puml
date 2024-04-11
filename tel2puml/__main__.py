"""Main function to call test harness
"""
import argparse
from tel2puml.pv_to_puml import (
    pv_jobs_from_folder_to_puml_file,
    pv_jobs_from_files_to_puml_file
)

parser = argparse.ArgumentParser(
    prog="tel2puml"
)

parser.add_argument(
    '-fp', '--folder-path', metavar='dir',
    help="Path to folder containing job json files",
    default=".",
    dest="folder_path"
)

parser.add_argument(
    '-o', '--output', metavar='file',
    help="Output file path",
    default="./default.puml",
    dest="puml_file_path"
)

parser.add_argument(
    '-sn', '--sequence-name', metavar='name',
    help="Name given to the puml sequence diagram",
    default="default_name",
    dest="puml_name"
)

parser.add_argument(
    'file_paths', nargs='*', help='Input .json files containing job data',
)


if __name__ == "__main__":
    args: argparse.Namespace = parser.parse_args()
    args_dict = vars(args)
    if args_dict['file_paths']:
        pv_jobs_from_files_to_puml_file(**args_dict)
    else:
        args_dict.pop('file_paths')
        pv_jobs_from_folder_to_puml_file(**args_dict)
