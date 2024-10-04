"""Module to handle e2e operations of handling otel data and producing puml
files."""

import os
from logging import getLogger
from typing import Generator, Optional, Literal, Any, Union

from tel2puml.tel2puml_types import OtelPVOptions, PVEvent, PVPumlOptions
from tel2puml.otel_to_pv.otel_to_pv import otel_to_pv
from tel2puml.pv_to_puml.pv_to_puml import (
    pv_streams_to_puml_files,
    pv_files_to_pv_streams,
)


def otel_to_puml(
    otel_to_pv_options: Optional[OtelPVOptions] = None,
    pv_to_puml_options: Optional[PVPumlOptions] = None,
    output_file_directory: str = "puml_output",
    components: Literal["otel2puml", "otel2pv", "pv2puml"] = "otel2puml",
) -> None:
    """Creates puml files from otel data. Takes optional parameters to handle
    separate parts of the process individually.

    :param otel_to_pv_options: Options for otel to pv. Defaults to `None`
    :type otel_to_pv: `Optional`[:class:`OtelPVOptions`]
    :param pv_to_puml_options: Options for pv to puml. Defaults to `None`
    :type pv_to_puml_options: `Optional`[:class:`PVPumlOptions`]
    :param output_file_directory: Output file directory. Defaults to
    "puml_output".
    :type output_file_directory: `str`
    :param components: The parts of the process that are required. Defaults to
    "otel2puml".
    :type components: `Literal`["otel2puml", "otel2pv", "pv2puml"]
    """
    # Create output directory if non-existant.
    if not os.path.isdir(output_file_directory):
        try:
            os.mkdir(output_file_directory)
        except PermissionError:
            getLogger(__name__).error(
                "Permission denied: cannot create directory."
            )
            return
        except OSError as e:
            getLogger(__name__).error(f"Error creating directory.{e}")
            return

    match components:
        case "otel2puml" | "otel2pv":
            if otel_to_pv_options is None:
                raise ValueError(
                    f"'{components}' has been selected, 'otel_to_pv_options'"
                    " is required."
                )
            pv_streams: Union[
                Generator[
                    tuple[
                        str,
                        Generator[Generator[PVEvent, Any, None], Any, None],
                    ],
                    Any,
                    None,
                ],
                Generator[
                    tuple[str, Generator[list[PVEvent], Any, None]],
                    Any,
                    None,
                ],
            ] = otel_to_pv(**otel_to_pv_options)
            if components == "otel2pv":
                return
        case "pv2puml":
            if pv_to_puml_options is None:
                raise ValueError(
                    "'pv2puml' has been selected, 'pv_to_puml_options' is"
                    " required."
                )
            pv_streams = pv_files_to_pv_streams(**pv_to_puml_options)
        case _:
            raise ValueError(
                "components should be one of 'otel2puml', 'otel2pv',"
                " 'pv2puml'"
            )
    # Convert streams to puml files
    pv_streams_to_puml_files(pv_streams, output_file_directory)
