"""Module for CCF Area definitions"""

from typing import List
from typing_extensions import Annotated
from importlib_resources import files
from pydantic import ConfigDict, Field

from aind_data_schema_models.pid_names import BaseName
from aind_data_schema_models.utils import create_literal_class, read_csv


def map_pid(value: str, record: dict):
    """Replace the parent_structure_id with an int"""
    if not value:
        record["parent_id"] = Annotated[None, Field(None)]
    else:
        record["parent_id"] = Annotated[int, Field(int(float(value)))]


def map_structure_list(value: str, record: dict):
    """Replace the structure list with a List[int]"""
    record["structure_id_path"] = Annotated[List[int],
                                            Field(list(map(int, value.strip('/').split('/'))))]


class CCFStructureModel(BaseName):
    """Base model config"""

    model_config = ConfigDict(frozen=True)

    acronym: str = Field(title="Acronym")
    name: str = Field(..., title="Structure name")
    id: int = Field(title="Atlas ID")
    structure_id_path: List[int] = Field(title="Structure path")
    parent_id: int = Field(title="Parent ID")
    color_hex_code: str = Field(title="Color HEX")


CCFStructure = create_literal_class(
    objects=read_csv(str(files("aind_data_schema_models.models").joinpath("mouse_ccf_structures.csv"))),
    class_name="CCFStructure",
    base_model=CCFStructureModel,
    field_handlers={"parent_structure_id": map_pid,
                    "structure_id_path": map_structure_list},
    discriminator="id",
    class_module=__name__,
)

CCFStructure._id_map = {m().id: m() for m in CCFStructure.ALL}
CCFStructure._acronym_map = {m().acronym: m() for m in CCFStructure.ALL}

CCFStructure.from_id = lambda x: CCFStructure._id_map.get(x)
CCFStructure.from_acronym = lambda x: CCFStructure._acronym_map.get(x)
CCFStructure.id2acronym = lambda x: CCFStructure._id_map.get(x).acronym
CCFStructure.acronym2id = lambda x: CCFStructure._acronym_map.get(x).id
