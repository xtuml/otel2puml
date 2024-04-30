"""
Module to update the current status of the end-to-end tests. This module runs
pytest on the end-to-end tests and parses the output to produce a markdown file
in the doucmentation folder for the end to end tests.

Usage:

python3 scripts/update_test_status.py

"""
from textwrap import dedent
import subprocess


TEMPLATE = dedent(
    """
    # Current Status
    Below we present the current status of the end-to-end tests.
    The tests are divided into the following categories:
    * [Branch counts](#branch-counts)
    * [Loops](#loops)
    * [Constraints](#constraints)
        * [One level](#one-level)
        * [Nested](#nested)
        * [Bunched](#bunched)
        * [Kill/Detach](#kill-detach)

    {full}

    ## Branch counts

    {branch}

    ## Loops

    {loops}

    ## Constraints
    ### One level

    {simple}

    ### Nested

    {nested}

    ### Bunched

    {bunched}

    ### Kill/Detach

    {kill}

    """
)
PATH = "tests/end-to-end-tests"
PARAMS = {
    "full": (0, PATH),
    "branch": (1, f"{PATH}/test_branch_counts.py"),
    "loops": (1, f"{PATH}/test_loops.py"),
    "simple": (1, f"{PATH}/constraints/test_constraints_simple.py"),
    "nested": (1, f"{PATH}/constraints/test_constraints_nested.py"),
    "bunched": (1, f"{PATH}/constraints/test_constraints_bunched.py"),
    "kill": (1, f"{PATH}/constraints/test_constraints_kill.py"),
}


def update_status() -> str:
    """Update the status of the end-to-end tests. Using the subprocess module
    to run pytest to produce markdown output and parse this into a single
    string which can be written to a current status file."""

    pytest_output = ["xfailed", "xpassed", "failed", "error", "skipped"]

    top_level = subprocess.run(
        "git rev-parse --show-toplevel".split(),
        capture_output=True
    ).stdout.decode().strip()

    results = {}
    full_test_count = 0
    full_fail_count = 0
    for name, (verbose, path) in PARAMS.items():
        results[name] = ""
        temp_path = f"{top_level}/TEMP.md"

        if verbose == 1:
            subprocess.run(
                [
                    "pytest",
                    path,
                    "--md-report",
                    f"--md-report-verbose={verbose}",
                    "--md-report-flavor",
                    "github",
                    f"--md-report-output={temp_path}",
                    "--md-report-color=never",
                ],
                capture_output=True,
                cwd=top_level,
            )

            with open(temp_path, "r") as f:
                lines = f.readlines()

            headings = [
                heading
                for raw_heading in lines[0].split("|")
                if (heading := raw_heading.strip())
            ]
            body = [
                [
                    word
                    for raw_word in line.split("|")
                    if (word := raw_word.strip())
                ]
                for line in lines[2:-1]
            ]

            path_index = headings.index("filepath")
            func_index = headings.index("function")
            indexes = {}
            for heading in headings:
                if heading in pytest_output:
                    indexes[heading] = headings.index(heading)

            result_strings = {key: "" for key in indexes.keys()}
            fail_count = 0
            for line in body:
                for key, index in indexes.items():
                    if line[index] != "0":
                        result_strings[key] += (
                            f"* `{line[path_index]}::{line[func_index]}`\n"
                        )
                        fail_count += 1

            test_count = len(body)
            percent = 100 * (test_count - fail_count) / test_count

            results[name] += (
                f"Currently the number of {name} tests stands at "
                + f"{test_count}, with {test_count - fail_count} passing "
                + f"and {fail_count} failing "
                + f"({percent:.2f}% coverage).\n\n"
            )
            for key, value in result_strings.items():
                results[name] += f"{key}:\n{value}\n"

            full_test_count += test_count
            full_fail_count += fail_count

        subprocess.run(
            [
                "pytest",
                path,
                "--md-report",
                f"--md-report-verbose={verbose}",
                "--md-report-flavor",
                "github",
                f"--md-report-output={temp_path}",
            ],
            capture_output=True,
            cwd=top_level,
        )

        with open(temp_path, "r") as f:
            results[name] += f.read()

    full_percent = 100 * (full_test_count - full_fail_count) / full_test_count
    results["full"] = (
        "Currently the number of end-to-end tests stands at "
        + f"{full_test_count}, with {full_test_count - full_fail_count} "
        + f"passing and {full_fail_count} failing "
        + f"({full_percent:.2f}% coverage).\n\n"
    ) + results["full"]

    subprocess.run(["rm", "-f", temp_path], cwd=top_level)

    return TEMPLATE.format(
        full=results["full"],
        branch=results["branch"],
        loops=results["loops"],
        simple=results["simple"],
        nested=results["nested"],
        bunched=results["bunched"],
        kill=results["kill"],
    ).replace("\\\\_", "\\_")


if __name__ == "__main__":
    with open("docs/development/Current-status.md", "w") as f:
        print(update_status(), file=f)
