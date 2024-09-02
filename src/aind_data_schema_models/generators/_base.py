from typing import Any, get_args

from pydantic import BaseModel, ConfigDict, Field, field_validator

from aind_data_schema_models.pid_names import BaseName


class _RegistryModel(BaseName):
    """Base model config"""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., title="Registry name")
    abbreviation: str = Field(..., title="Registry abbreviation")


class _HarpDeviceTypeModel(BaseModel):
    """Base model config"""

    model_config = ConfigDict(frozen=True)
    name: str = Field(..., title="Harp device type name")
    whoami: int = Field(..., title="Harp whoami value")


class _ModalityModel(BaseName):
    """Base model config"""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., title="Modality name")
    abbreviation: str = Field(..., title="Modality abbreviation")


class _MouseAnatomyModel(BaseModel):
    """Base model config"""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., title="Structure name")
    registry: _RegistryModel = Field(..., title="Structure registry")
    registry_identifier: str = Field(title="Structure EMAPA ID")

    @field_validator("registry", mode="before")
    @classmethod
    def dict_to_model(cls, v: Any):
        # I dont think we should use classes as enums, but I think this is the lowest footprint solution I could think of ...
        if isinstance(v, dict):
            this_literal_class = get_args(cls.model_fields["registry"].annotation)[0].__class__
            return this_literal_class.model_validate(v)
        return v


class _OrganizationModel(BaseModel):
    """Base model config"""

    model_config = ConfigDict(frozen=True)

    name: str
    abbreviation: str
    registry: _RegistryModel
    registry_identifier: str

    @field_validator("registry", mode="before")
    @classmethod
    def dict_to_model(cls, v: Any):
        # I dont think we should use classes as enums, but I think this is the lowest footprint solution I could think of ...
        if isinstance(v, dict):
            this_literal_class = get_args(cls.model_fields["registry"].annotation)[0].__class__
            return this_literal_class.model_validate(v)
        return v


class _SpeciesModel(BaseModel):
    """base model for species, like Mus musculus"""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., title="Species name")
    registry: _RegistryModel = Field(..., title="Species registry")
    registry_identifier: str = Field(..., title="Species registry identifier")

    @field_validator("registry", mode="before")
    @classmethod
    def dict_to_model(cls, v: Any):
        # I dont think we should use classes as enums, but I think this is the lowest footprint solution I could think of ...
        if isinstance(v, dict):
            this_literal_class = get_args(cls.model_fields["registry"].annotation)[0].__class__
            return this_literal_class.model_validate(v)
        return v


class _PlatformModel(BaseModel):
    """Base model config"""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., title="Platform name")
    abbreviation: str = Field(..., title="Platform abbreviation")
