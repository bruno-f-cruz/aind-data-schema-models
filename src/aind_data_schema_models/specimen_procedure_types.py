"""Script for the SpecimenProcedureType enum class."""

from importlib_resources import files

from aind_data_schema_models.utils import create_string_enum, read_csv

SpecimenProcedureType = create_string_enum(
    name="SpecimenProcedureType",
    objects=read_csv(files("aind_data_schema_models.models").joinpath("specimen_procedure_types.csv")),
)
