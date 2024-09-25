"""Module for Modality and ExpectedFile definitions"""

from importlib_resources import files
from pydantic import ConfigDict, Field
from enum import IntEnum
from typing_extensions import Annotated

from aind_data_schema_models.pid_names import BaseName
from aind_data_schema_models.utils import create_literal_class, read_csv


class ModalityModel(BaseName):
    """Base model config"""

    model_config = ConfigDict(frozen=True)
    name: str = Field(..., title="Modality name")
    abbreviation: str = Field(..., title="Modality abbreviation")


Modality = create_literal_class(
    objects=read_csv(str(files("aind_data_schema_models.models").joinpath("modalities.csv"))),
    class_name="Modality",
    base_model=ModalityModel,
    discriminator="abbreviation",
    class_module=__name__,
)

Modality.abbreviation_map = {m().abbreviation: m() for m in Modality.ALL}
Modality.from_abbreviation = lambda x: Modality.abbreviation_map.get(x)


class FileRequirement(IntEnum):
    """Whether a file is required for a specific modality"""

    REQUIRED = 1
    OPTIONAL = 0
    EXCLUDED = -1


class ExpectedFilesModel(BaseName):
    """Model config"""

    model_config = ConfigDict(frozen=True)
    name: str = Field(..., title="Modality name")
    modality_abbreviation: str = Field(..., title="Modality abbreviation")
    subject: FileRequirement = Field(..., title="Subject file requirement")
    data_description: FileRequirement = Field(..., title="Data description file requirement")
    procedures: FileRequirement = Field(..., title="Procedures file requirement")
    session: FileRequirement = Field(..., title="Session file requirement")
    rig: FileRequirement = Field(..., title="Processing file requirement")
    processing: FileRequirement = Field(..., title="Processing file requirement")
    acquisition: FileRequirement = Field(..., title="Acquisition file requirement")
    instrument: FileRequirement = Field(..., title="Instrument file requirement")
    quality_control: FileRequirement = Field(..., title="Quality control file requirement")


def map_file_requirement(value: int, record: dict, field: str):
    """Map integers to Annotated[FileRequirement, value]

    Parameters
    ----------
    value : int
        File required value
    record : dict
        Full class dictionary
    field : str
        Field name that the FileRequirement value will be assigned to
    """
    record[field] = Annotated[
        FileRequirement,
        Field(default=FileRequirement(int(value))),
    ]


ExpectedFiles = create_literal_class(
    objects=read_csv(str(files("aind_data_schema_models.models").joinpath("modality_expected_files.csv"))),
    class_name="ExpectedFiles",
    base_model=ExpectedFilesModel,
    discriminator="modality_abbreviation",
    field_handlers={
        "subject": map_file_requirement,
        "data_description": map_file_requirement,
        "procedures": map_file_requirement,
        "session": map_file_requirement,
        "rig": map_file_requirement,
        "processing": map_file_requirement,
        "acquisition": map_file_requirement,
        "instrument": map_file_requirement,
        "quality_control": map_file_requirement,
    },
    class_module=__name__,
)
