"""Module to handle e2e operations of handling otel data and producing puml
files."""

import os
from typing import Optional, Literal

from tel2puml.tel2puml_types import OtelPumlOptions, PVPumlOptions
from tel2puml.otel_to_pv.sequence_otel_v2 import otel_to_pv
from tel2puml.pv_to_puml import pv_streams_to_puml_files
from tel2puml.otel_to_pv.config import load_config_from_yaml
from tel2puml.otel_to_pv.ingest_otel_data import ingest_data_into_dataholder


def otel_to_puml(
    otel_to_puml_options: Optional[OtelPumlOptions] = None,
    pv_to_puml_options: Optional[PVPumlOptions] = None,
    output_file_directory: str = "puml_output",
    components: Literal["all", "otel_to_puml", "pv_to_puml"] = "all",
) -> None:
    """Creates puml files from otel data. Takes optional parameters to handle
    separate parts of the process individually.

    :param otel_to_puml_options: Options for otel to puml. Defaults to `None`
    :type otel_to_puml: `Optional`[:class:`OtelPumlOptions`]
    :param pv_to_puml_options: Options for pv to puml. Defaults to `None`
    :type pv_to_puml_options: `Optional`[:class:`PVPumlOptions`]
    :param output_file_directory: Output file directory. Defaults to
    "puml_output".
    :type output_file_directory: `str`
    :param components: The parts of the process that are required. Defaults to
    "all".
    :type components: `Literal`["all", "otel_to_puml", "pv_to_puml"]
    """
    if components == "otel_to_puml" and otel_to_puml_options is None:
        raise ValueError(
            "'otel_to_puml' has been selected, 'otel_to_puml_options' is"
            " required."
        )
    elif components == "all" and otel_to_puml_options is None:
        raise ValueError(
            "'all' has been selected, 'otel_to_puml_options' is required."
        )
    elif components == "pv_to_puml" and pv_to_puml_options is None:
        raise ValueError(
            "'pv_to_puml' has been selected, 'pv_to_puml_options' is required."
        )

    if not os.path.isdir(output_file_directory):
        os.mkdir(output_file_directory)

    if components == "all":
        pv_streams = otel_to_pv(
            config=otel_to_puml_options["config"],
            ingest_data=True,
        )
        pv_streams_to_puml_files(pv_streams, output_file_directory)
    elif components == "otel_to_puml":
        # if we just want to ingest data, ingest_data = True
        # if ingest_data = False, stream from data_holder
        if otel_to_puml_options["ingest_data"]:
            ingest_data_into_dataholder(otel_to_puml_options["config"])
        else:
            pv_streams = otel_to_pv(
                config=otel_to_puml_options["config"],
                ingest_data=False,
            )
            pv_streams_to_puml_files(pv_streams, output_file_directory)
    elif components == "pv_to_puml":
        pass
    else:
        raise ValueError(
            "components should be one of 'all', 'otel_to_puml', 'pv_to_puml'"
        )


if __name__ == "__main__":
    otel_to_puml_options = {
        "config": load_config_from_yaml("tel2puml/otel_to_pv/config.yaml"),
        "ingest_data": False,
    }
    otel_to_puml(
        otel_to_puml_options=otel_to_puml_options, components="otel_to_puml"
    )
