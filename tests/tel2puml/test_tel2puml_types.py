"""Tests for the pydantic models within tel2puml_types.py"""

import tempfile

import pytest
from pydantic import ValidationError

from tel2puml.tel2puml_types import OtelToPVArgs, PvToPumlArgs


def test_otel_to_pv_args() -> None:
    """Tests for the pydantic model OtelToPVArgs"""

    # Test 1: Valid inputs
    with tempfile.NamedTemporaryFile(suffix=".yaml") as tmp_file:
        args = OtelToPVArgs(config_file=tmp_file.name, command="otel2pv")
        assert str(args.config_file) == tmp_file.name
        assert args.ingest_data is True
        assert args.find_unique_graphs is False
        assert args.save_events is False

    # Test 2: Incorrect file extension for config file
    with tempfile.NamedTemporaryFile(suffix=".incorrect") as tmp_file:
        with pytest.raises(ValidationError):
            args = OtelToPVArgs(config_file=tmp_file.name, command="otel2pv")

    # Test 3: Check error handling with save_events=True, command=otel2puml
    with tempfile.NamedTemporaryFile(suffix=".yaml") as tmp_file:
        with pytest.raises(ValidationError):
            args = OtelToPVArgs(
                config_file=tmp_file.name,
                command="otel2puml",
                save_events=True,
            )
