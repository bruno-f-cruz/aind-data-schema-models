# generated by aind-data-schema-models:
#   filename:  src\aind_data_schema_models\models\modalities.csv
#   timestamp: 2024-08-23 11:33:19.471824


from typing import Annotated, Literal, Union

from pydantic import Field

from aind_data_schema_models.generators import _ModalityModel


class Behavior(_ModalityModel):

    name: Literal["Behavior"] = "Behavior"
    abbreviation: Literal["behavior"] = "behavior"


class BehaviorVideos(_ModalityModel):

    name: Literal["Behavior videos"] = "Behavior videos"
    abbreviation: Literal["behavior-videos"] = "behavior-videos"


class Confocal(_ModalityModel):

    name: Literal["Confocal microscopy"] = "Confocal microscopy"
    abbreviation: Literal["confocal"] = "confocal"


class Emg(_ModalityModel):

    name: Literal["Electromyography"] = "Electromyography"
    abbreviation: Literal["EMG"] = "EMG"


class Ecephys(_ModalityModel):

    name: Literal["Extracellular electrophysiology"] = "Extracellular electrophysiology"
    abbreviation: Literal["ecephys"] = "ecephys"


class Fib(_ModalityModel):

    name: Literal["Fiber photometry"] = "Fiber photometry"
    abbreviation: Literal["fib"] = "fib"


class Fmost(_ModalityModel):

    name: Literal["Fluorescence micro-optical sectioning tomography"] = (
        "Fluorescence micro-optical sectioning tomography"
    )
    abbreviation: Literal["fMOST"] = "fMOST"


class Icephys(_ModalityModel):

    name: Literal["Intracellular electrophysiology"] = "Intracellular electrophysiology"
    abbreviation: Literal["icephys"] = "icephys"


class Isi(_ModalityModel):

    name: Literal["Intrinsic signal imaging"] = "Intrinsic signal imaging"
    abbreviation: Literal["ISI"] = "ISI"


class Mri(_ModalityModel):

    name: Literal["Magnetic resonance imaging"] = "Magnetic resonance imaging"
    abbreviation: Literal["MRI"] = "MRI"


class Merfish(_ModalityModel):

    name: Literal["Multiplexed error-robust fluorescence in situ hybridization"] = (
        "Multiplexed error-robust fluorescence in situ hybridization"
    )
    abbreviation: Literal["merfish"] = "merfish"


class Pophys(_ModalityModel):

    name: Literal["Planar optical physiology"] = "Planar optical physiology"
    abbreviation: Literal["pophys"] = "pophys"


class Slap(_ModalityModel):

    name: Literal["Scanned line projection imaging"] = "Scanned line projection imaging"
    abbreviation: Literal["slap"] = "slap"


class Spim(_ModalityModel):

    name: Literal["Selective plane illumination microscopy"] = (
        "Selective plane illumination microscopy"
    )
    abbreviation: Literal["SPIM"] = "SPIM"


class _Modality:

    BEHAVIOR = Behavior()
    BEHAVIOR_VIDEOS = BehaviorVideos()
    CONFOCAL = Confocal()
    EMG = Emg()
    ECEPHYS = Ecephys()
    FIB = Fib()
    FMOST = Fmost()
    ICEPHYS = Icephys()
    ISI = Isi()
    MRI = Mri()
    MERFISH = Merfish()
    POPHYS = Pophys()
    SLAP = Slap()
    SPIM = Spim()

    ALL = tuple(_ModalityModel.__subclasses__())
    ONE_OF = Annotated[Union[ALL], Field(discriminator="name")]

    abbreviation_map = {m().abbreviation: m() for m in ALL}

    @classmethod
    def from_abbreviation(cls, abbreviation: str):
        return cls.abbreviation_map[abbreviation]
