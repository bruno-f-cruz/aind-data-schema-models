"""Common registries"""

from typing import Union

from importlib_resources import files
from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from aind_data_schema_models.pid_names import BaseName
from aind_data_schema_models.utils import create_literal_class, read_csv


class RegistryModel(BaseName):
    """Base model config"""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., title="Registry name")
    abbreviation: str = Field(..., title="Registry abbreviation")


Registry = create_literal_class(
    objects=read_csv(str(files("aind_data_schema_models.models").joinpath("registries.csv"))),
    class_name="Registry",
    base_model=RegistryModel,
    discriminator="abbreviation",
    class_module=__name__,
)

Registry.abbreviation_map = {m().abbreviation: m() for m in Registry.ALL}
Registry.from_abbreviation = lambda x: Registry.abbreviation_map.get(x)


def map_registry(abbreviation: str, record: dict, *args):
    """replace the "registry" key of a dictionary with a RegistryModel object"""
    registry = Registry.from_abbreviation(abbreviation)
    if registry:
        record["registry"] = Annotated[Union[type(registry)], Field(default=registry, discriminator="name")]
    else:
        record["registry"] = Annotated[None, Field(None)]
