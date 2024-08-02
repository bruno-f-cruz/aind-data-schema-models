"""Module for process names definitions"""

from importlib_resources import files

from aind_data_schema_models.utils import create_string_enum, read_csv

ProcessName = create_string_enum(
    name="ProcessName", objects=read_csv(str(files("aind_data_schema_models.models").joinpath("process_names.csv")))
)
