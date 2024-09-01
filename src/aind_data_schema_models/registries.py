"""Common registries"""

from typing import Union

from pydantic import Field
from typing_extensions import Annotated

from aind_data_schema_models._generated.registries import _Registry as Registry
from aind_data_schema_models._generated.registries import _RegistryModel as RegistryModel


def map_registry(abbreviation: str, record: dict):
    """replace the "registry" key of a dictionary with a RegistryModel object"""
    registry = Registry.from_abbreviation(abbreviation)
    if registry:
        record["registry"] = Annotated[Union[type(registry)], Field(default=registry, discriminator="name")]
    else:
        record["registry"] = Annotated[None, Field(None)]
