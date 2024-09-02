"""Module for Mouse Anatomy"""
from aind_data_schema_models.utils import one_of_instance

from aind_data_schema_models._generated.mouse_anatomy import _MouseAnatomyType as MouseAnatomicalStructure

MouseAnatomicalStructure.EMG_MUSCLES = one_of_instance(
    [
        MouseAnatomicalStructure.DELTOID,
        MouseAnatomicalStructure.PECTORALIS_MAJOR,
        MouseAnatomicalStructure.TRICEPS_BRACHII,
        MouseAnatomicalStructure.BICEPS_BRACHII,
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
