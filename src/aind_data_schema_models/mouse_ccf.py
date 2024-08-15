"""Module for CCF Area definitions"""

from importlib_resources import files
from pydantic import ConfigDict, Field

from aind_data_schema_models.pid_names import BaseName
from aind_data_schema_models.utils import create_literal_class, read_csv


class CCFStructureModel(BaseName):
    """Base model config"""

    model_config = ConfigDict(frozen=True)

    atlas: str = Field(default='CCFv3')
    acronym: str = Field(title="Structure acronym")
    name: str = Field(title="Structure name")
    id: int = Field(title="Atlas ID")


CCFStructure = create_literal_class(
    objects=read_csv(str(files("aind_data_schema_models.models").joinpath("mouse_ccf_structures.csv"))),
    class_name="CCFStructure",
    base_model=CCFStructureModel,
    discriminator="id",
    class_module=__name__,
)
