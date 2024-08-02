"""Module for Harp Device Types"""

from importlib_resources import files
from pydantic import BaseModel, ConfigDict, Field

from aind_data_schema_models.utils import create_literal_class, read_csv


class HarpDeviceTypeModel(BaseModel):
    """Base model config"""

    model_config = ConfigDict(frozen=True)
    name: str = Field(..., title="Harp device type name")
    whoami: int = Field(..., title="Harp whoami value")


HarpDeviceType = create_literal_class(
    objects=read_csv(str(files("aind_data_schema_models.models").joinpath("harp_types.csv"))),
    class_name="HarpDeviceType",
    base_model=HarpDeviceTypeModel,
    discriminator="name",
    class_module=__name__,
)
