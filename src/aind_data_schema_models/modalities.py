"""Module for Modality definitions"""

from typing import Any

from importlib_resources import files
from pydantic import BeforeValidator, ConfigDict, Field

from aind_data_schema_models.pid_names import BaseName
from aind_data_schema_models.utils import create_literal_class, read_csv


# This is a hotfix to allow users to use the old ophys modality abbreviation
# It should be removed in a future release
def _coerce_ophys_to_pophys(v: Any):
    if isinstance(v, dict):
        if v.get("abbreviation") == "ophys":
            return Modality.POPHYS
    return v


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
    validators=[BeforeValidator(_coerce_ophys_to_pophys)],
)

Modality.OPHYS = Modality.POPHYS

Modality.abbreviation_map = {m().abbreviation: m() for m in Modality.ALL}
Modality.from_abbreviation = lambda x: Modality.abbreviation_map.get(x)
