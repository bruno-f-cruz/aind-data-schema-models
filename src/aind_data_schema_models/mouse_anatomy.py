"""Module for Mouse Anatomy"""

from typing_extensions import Annotated
from importlib_resources import files
from pydantic import BaseModel, ConfigDict, Field

from aind_data_schema_models.registries import Registry, RegistryModel
from aind_data_schema_models.utils import create_literal_class, read_csv, subset_from_column


class MouseAnatomyModel(BaseModel):
    """Base model config"""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., title="Structure name")
    registry: Annotated[RegistryModel, Field(default=Registry.from_abbreviation('EMAPA'))]
    registry_identifier: str = Field(title="Structure EMAPA ID")


mouse_objects = read_csv(str(files("aind_data_schema_models.models").joinpath("mouse_dev_anat_ontology.csv")))

MouseAnatomicalStructure = create_literal_class(
    objects=mouse_objects,
    class_name="MouseAnatomyType",
    base_model=MouseAnatomyModel,
    discriminator="registry_identifier",
    class_module=__name__,
)

MouseAnatomicalStructure.EMG_MUSCLES = subset_from_column(MouseAnatomicalStructure, mouse_objects, "EMG_MUSCLES")
