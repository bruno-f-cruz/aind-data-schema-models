# generated by aind-data-schema-models:
#   filename:  src\aind_data_schema_models\models\platforms.csv
#   timestamp: 2024-08-23 11:31:10.864160


from typing import Annotated, Literal, Union

from pydantic import Field

from aind_data_schema_models.generators import _PlatformModel


class Behavior(_PlatformModel):

    name: Literal["Behavior platform"] = "Behavior platform"
    abbreviation: Literal["behavior"] = "behavior"


class Confocal(_PlatformModel):

    name: Literal["Confocal microscopy platform"] = "Confocal microscopy platform"
    abbreviation: Literal["confocal"] = "confocal"


class Ecephys(_PlatformModel):

    name: Literal["Electrophysiology platform"] = "Electrophysiology platform"
    abbreviation: Literal["ecephys"] = "ecephys"


class Exaspim(_PlatformModel):

    name: Literal["ExaSPIM platform"] = "ExaSPIM platform"
    abbreviation: Literal["exaSPIM"] = "exaSPIM"


class Fip(_PlatformModel):

    name: Literal["Frame-projected independent-fiber photometry platform"] = (
        "Frame-projected independent-fiber photometry platform"
    )
    abbreviation: Literal["FIP"] = "FIP"


class Hcr(_PlatformModel):

    name: Literal["Hybridization chain reaction platform"] = (
        "Hybridization chain reaction platform"
    )
    abbreviation: Literal["HCR"] = "HCR"


class Hsfp(_PlatformModel):

    name: Literal["Hyperspectral fiber photometry platform"] = (
        "Hyperspectral fiber photometry platform"
    )
    abbreviation: Literal["HSFP"] = "HSFP"


class Isi(_PlatformModel):

    name: Literal["Intrinsic signal imaging platform"] = (
        "Intrinsic signal imaging platform"
    )
    abbreviation: Literal["ISI"] = "ISI"


class Merfish(_PlatformModel):

    name: Literal["MERFISH platform"] = "MERFISH platform"
    abbreviation: Literal["MERFISH"] = "MERFISH"


class Mri(_PlatformModel):

    name: Literal["Magnetic resonance imaging platform"] = (
        "Magnetic resonance imaging platform"
    )
    abbreviation: Literal["MRI"] = "MRI"


class Mesospim(_PlatformModel):

    name: Literal["MesoSPIM platform"] = "MesoSPIM platform"
    abbreviation: Literal["mesoSPIM"] = "mesoSPIM"


class MotorObservatory(_PlatformModel):

    name: Literal["Motor observatory platform"] = "Motor observatory platform"
    abbreviation: Literal["motor-observatory"] = "motor-observatory"


class MultiplaneOphys(_PlatformModel):

    name: Literal["Multiplane optical physiology platform"] = (
        "Multiplane optical physiology platform"
    )
    abbreviation: Literal["multiplane-ophys"] = "multiplane-ophys"


class Slap2(_PlatformModel):

    name: Literal["SLAP2 platform"] = "SLAP2 platform"
    abbreviation: Literal["SLAP2"] = "SLAP2"


class SinglePlaneOphys(_PlatformModel):

    name: Literal["Single-plane optical physiology platform"] = (
        "Single-plane optical physiology platform"
    )
    abbreviation: Literal["single-plane-ophys"] = "single-plane-ophys"


class Smartspim(_PlatformModel):

    name: Literal["SmartSPIM platform"] = "SmartSPIM platform"
    abbreviation: Literal["SmartSPIM"] = "SmartSPIM"


class _Platform:

    BEHAVIOR = Behavior()
    CONFOCAL = Confocal()
    ECEPHYS = Ecephys()
    EXASPIM = Exaspim()
    FIP = Fip()
    HCR = Hcr()
    HSFP = Hsfp()
    ISI = Isi()
    MERFISH = Merfish()
    MRI = Mri()
    MESOSPIM = Mesospim()
    MOTOR_OBSERVATORY = MotorObservatory()
    MULTIPLANE_OPHYS = MultiplaneOphys()
    SLAP2 = Slap2()
    SINGLE_PLANE_OPHYS = SinglePlaneOphys()
    SMARTSPIM = Smartspim()

    _ALL = tuple(_PlatformModel.__subclasses__())
    ONE_OF = Annotated[Union[_ALL], Field(discriminator="name")]

    abbreviation_map = {m().abbreviation: m() for m in _ALL}

    @classmethod
    def from_abbreviation(cls, abbreviation: str):
        return cls.abbreviation_map[abbreviation]
