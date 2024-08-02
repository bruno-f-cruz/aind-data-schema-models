"""Module for species definitions"""

from importlib_resources import files
from pydantic import BaseModel, ConfigDict, Field

from aind_data_schema_models.registries import RegistryModel, map_registry
from aind_data_schema_models.utils import create_literal_class, read_csv


class SpeciesModel(BaseModel):
    """base model for species, like Mus musculus"""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., title="Species name")
    registry: RegistryModel = Field(..., title="Species registry")
    registry_identifier: str = Field(..., title="Species registry identifier")


Species = create_literal_class(
    objects=read_csv(str(files("aind_data_schema_models.models").joinpath("species.csv"))),
    class_name="Species",
    base_model=SpeciesModel,
    discriminator="name",
    field_handlers={"registry_abbreviation": map_registry},
    class_module=__name__,
)
