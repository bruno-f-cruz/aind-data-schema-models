"""Module for CCF Area definitions"""

from typing_extensions import Annotated
from importlib_resources import files
from pydantic import ConfigDict, Field

from aind_data_schema_models.pid_names import BaseName
from aind_data_schema_models.registries import RegistryModel, Registry
from aind_data_schema_models.utils import create_literal_class, read_csv


class CCFStructureModel(BaseName):
    """Base model config"""

    model_config = ConfigDict(frozen=True)

    acronym: str = Field(title="Acronym")
    name: str = Field(..., title="Structure name")
    registry: Annotated[RegistryModel, Field(default=Registry.from_abbreviation('CCF'))]
    registry_identifier: int = Field(title="Atlas ID")


CCFStructure = create_literal_class(
    objects=read_csv(str(files("aind_data_schema_models.models").joinpath("mouse_ccf_structures.csv"))),
    class_name="CCFStructure",
    base_model=CCFStructureModel,
    discriminator="id",
    class_module=__name__,
)
