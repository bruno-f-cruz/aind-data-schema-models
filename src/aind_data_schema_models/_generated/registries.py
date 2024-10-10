# generated by aind-data-schema-models:
#     filename:  registries.csv
#     timestamp: 2024-10-10 19:32:56.078834+00:00

from typing import Annotated, Literal, Union

from pydantic import Field, RootModel

from aind_data_schema_models._generators._base import _RegistryModel


class Addgene(_RegistryModel):

    name: Literal["Addgene"] = "Addgene"
    abbreviation: Literal["ADDGENE"] = "ADDGENE"


class Emapa(_RegistryModel):

    name: Literal["Edinburgh Mouse Atlas Project"] = "Edinburgh Mouse Atlas Project"
    abbreviation: Literal["EMAPA"] = "EMAPA"


class Mgi(_RegistryModel):

    name: Literal["Mouse Genome Informatics"] = "Mouse Genome Informatics"
    abbreviation: Literal["MGI"] = "MGI"


class Ncbi(_RegistryModel):

    name: Literal["National Center for Biotechnology Information"] = "National Center for Biotechnology Information"
    abbreviation: Literal["NCBI"] = "NCBI"


class Orcid(_RegistryModel):

    name: Literal["Open Researcher and Contributor ID"] = "Open Researcher and Contributor ID"
    abbreviation: Literal["ORCID"] = "ORCID"


class Ror(_RegistryModel):

    name: Literal["Research Organization Registry"] = "Research Organization Registry"
    abbreviation: Literal["ROR"] = "ROR"


class Rrid(_RegistryModel):

    name: Literal["Research Resource Identifiers"] = "Research Resource Identifiers"
    abbreviation: Literal["RRID"] = "RRID"


class _Registry:

    ADDGENE = Addgene()
    EMAPA = Emapa()
    MGI = Mgi()
    NCBI = Ncbi()
    ORCID = Orcid()
    ROR = Ror()
    RRID = Rrid()

    ALL = tuple(_RegistryModel.__subclasses__())

    class ONE_OF(RootModel):
        root: Annotated[Union[tuple(_RegistryModel.__subclasses__())], Field(discriminator="name")]

    abbreviation_map = {m().abbreviation: m() for m in ALL}

    @classmethod
    def from_abbreviation(cls, abbreviation: str):
        return cls.abbreviation_map.get(abbreviation, None)
