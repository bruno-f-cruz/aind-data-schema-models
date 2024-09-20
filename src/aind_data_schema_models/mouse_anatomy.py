"""Module for Mouse Anatomy"""

from typing_extensions import Annotated
from importlib_resources import files
from pydantic import BaseModel, ConfigDict, Field

from aind_data_schema_models.registries import Registry, RegistryModel
from aind_data_schema_models.utils import create_literal_class, read_csv, one_of_instance


class MouseAnatomyModel(BaseModel):
    """Base model config"""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., title="Structure name")
    registry: Annotated[RegistryModel, Field(default=Registry.from_abbreviation("EMAPA"))]
    registry_identifier: str = Field(..., title="Structure EMAPA ID")


mouse_objects = read_csv(str(files("aind_data_schema_models.models").joinpath("mouse_dev_anat_ontology.csv")))

MouseAnatomicalStructure = create_literal_class(
    objects=mouse_objects,
    class_name="MouseAnatomyType",
    base_model=MouseAnatomyModel,
    discriminator="registry_identifier",
    class_module=__name__,
)

MouseAnatomicalStructure.EMG_MUSCLES = one_of_instance(
    [
        MouseAnatomicalStructure.DELTOID,
        MouseAnatomicalStructure.PECTORALIS_MAJOR,
        MouseAnatomicalStructure.TRICEPS_BRACHII,
        MouseAnatomicalStructure.LATERAL_HEAD_OF_TRICEPS_BRACHII,
        MouseAnatomicalStructure.LONG_HEAD_OF_TRICEPS_BRACHII,
        MouseAnatomicalStructure.MEDIAL_HEAD_OF_TRICEPS_BRACHII,
        MouseAnatomicalStructure.BICEPS_BRACHII,
        MouseAnatomicalStructure.LONG_HEAD_OF_BICEPS_BRACHII,
        MouseAnatomicalStructure.SHORT_HEAD_OF_BICEPS_BRACHII,
        MouseAnatomicalStructure.TENDON_OF_BICEPS_BRACHII,
        MouseAnatomicalStructure.PARS_SCAPULARIS_OF_DELTOID,
        MouseAnatomicalStructure.EXTENSOR_CARPI_RADIALIS_LONGUS,
        MouseAnatomicalStructure.EXTENSOR_DIGITORUM_COMMUNIS,
        MouseAnatomicalStructure.EXTENSOR_DIGITORUM_LATERALIS,
        MouseAnatomicalStructure.EXTENSOR_CARPI_ULNARIS,
        MouseAnatomicalStructure.FLEXOR_CARPI_RADIALIS,
        MouseAnatomicalStructure.FLEXOR_CARPI_ULNARIS,
        MouseAnatomicalStructure.FLEXOR_DIGITORUM_PROFUNDUS,
    ]
)

MouseAnatomicalStructure.BODY_PARTS = one_of_instance(
    [
        MouseAnatomicalStructure.FORELIMB,
        MouseAnatomicalStructure.HEAD,
        MouseAnatomicalStructure.HINDLIMB,
        MouseAnatomicalStructure.NECK,
        MouseAnatomicalStructure.TAIL,
        MouseAnatomicalStructure.TRUNK,
    ]
)
