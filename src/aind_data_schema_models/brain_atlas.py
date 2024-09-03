"""Module for brain atlas definitions"""

from importlib_resources import files
from pydantic import Field, BaseModel

from aind_data_schema_models.utils import create_literal_class, read_csv


class BrainStructureModel(BaseModel):
    """Abstract model for brain atlas structures

    Use this class to create a specific atlas of structures by defining a CSV with
    columns corresponding to the acronym, name, and id.

    Define the atlas using the shared_fields feature in create_literal_class,
    see CCF example.
    """

    atlas: str = Field(..., title="Atlas name")
    acronym: str = Field(..., title="Structure acronym")
    name: str = Field(..., title="Structure name")
    id: int = Field(..., title="Structure ID")


CCFStructure = create_literal_class(
    objects=read_csv(str(files("aind_data_schema_models.models").joinpath("mouse_ccf_structures.csv"))),
    class_name="CCFStructure",
    base_model=BrainStructureModel,
    shared_fields={"atlas": "CCFv3"},
    discriminator="id",
    class_module=__name__,
)
