"""Module for species definitions"""

from typing import Literal, Union

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from aind_data_schema_models.pid_names import PIDName
from aind_data_schema_models.registry import NationalCenterForBiotechnologyInformation, Registry


class _Species(PIDName):
    """Base model config"""

    model_config = ConfigDict(frozen=True)


class CallithrixJacchus(_Species):
    """Callithrix Jacchus"""

    name: Literal["Callithrix jacchus"] = "Callithrix jacchus"
    registry: Annotated[
        Union[NationalCenterForBiotechnologyInformation], Field(default=Registry.NCBI, discriminator="name")
    ]
    registry_identifier: Literal["NCBI:txid9483"] = "NCBI:txid9483"


class HomoSapiens(_Species):
    """Homo Sapiens"""

    name: Literal["Homo sapiens"] = "Homo sapiens"
    registry: Annotated[
        Union[NationalCenterForBiotechnologyInformation], Field(default=Registry.NCBI, discriminator="name")
    ]
    registry_identifier: Literal["NCBI:txid9606"] = "NCBI:txid9606"


class MacacaMulatta(_Species):
    """Macaca Mulatta"""

    name: Literal["Macaca mulatta"] = "Macaca mulatta"
    registry: Annotated[
        Union[NationalCenterForBiotechnologyInformation], Field(default=Registry.NCBI, discriminator="name")
    ]
    registry_identifier: Literal["NCBI:txid9544"] = "NCBI:txid9544"


class MusMusculus(_Species):
    """Mus Musculus"""

    name: Literal["Mus musculus"] = "Mus musculus"
    registry: Annotated[
        Union[NationalCenterForBiotechnologyInformation], Field(default=Registry.NCBI, discriminator="name")
    ]
    registry_identifier: Literal["NCBI:txid10090"] = "NCBI:txid10090"


class RattusNorvegicus(_Species):
    """Rattus Norvegicus"""

    name: Literal["Rattus norvegicus"] = "Rattus norvegicus"
    registry: Annotated[
        Union[NationalCenterForBiotechnologyInformation], Field(default=Registry.NCBI, discriminator="name")
    ]
    registry_identifier: Literal["NCBI:txid10116"] = "NCBI:txid10116"


class Species:
    """Species classes"""

    CALLITHRIX_JACCHUS = CallithrixJacchus()
    HOMO_SAPIENS = HomoSapiens()
    MACACA_MULATTA = MacacaMulatta()
    MUS_MUSCULUS = MusMusculus()
    RATTUS_NOVEGICUS = RattusNorvegicus()
    _ALL = tuple(_Species.__subclasses__())
    ONE_OF = Annotated[Union[_ALL], Field(discriminator="name")]
