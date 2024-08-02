"""Module for Platform definitions"""

from importlib_resources import files
from pydantic import BaseModel, ConfigDict, Field

from aind_data_schema_models.utils import create_literal_class, read_csv


class PlatformModel(BaseModel):
    """Base model config"""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., title="Platform name")
    abbreviation: str = Field(..., title="Platform abbreviation")


Platform = create_literal_class(
    objects=read_csv(str(files("aind_data_schema_models.models").joinpath("platforms.csv"))),
    class_name="Platform",
    base_model=PlatformModel,
    discriminator="name",
    class_module=__name__,
)

Platform.abbreviation_map = {p().abbreviation: p() for p in Platform.ALL}
Platform.from_abbreviation = lambda x: Platform.abbreviation_map.get(x)
