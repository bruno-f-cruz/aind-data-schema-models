"""Module for Organization definitions, including manufacturers, institutions, and vendors"""

from importlib_resources import files
from pydantic import BaseModel, ConfigDict

from aind_data_schema_models.registries import RegistryModel, map_registry
from aind_data_schema_models.utils import create_literal_class, one_of_instance, read_csv


class OrganizationModel(BaseModel):
    """Base model config"""

    model_config = ConfigDict(frozen=True)

    name: str
    abbreviation: str = None
    registry: RegistryModel = None
    registry_identifier: str = None


Organization = create_literal_class(
    objects=read_csv(str(files("aind_data_schema_models.models").joinpath("organizations.csv"))),
    class_name="Organization",
    base_model=OrganizationModel,
    discriminator="name",
    field_handlers={"registry_abbreviation": map_registry},
    class_module=__name__,
)

Organization.abbreviation_map = {m().abbreviation: m() for m in Organization.ALL}
Organization.name_map = {m().name: m() for m in Organization.ALL}
Organization.from_abbreviation = lambda x: Organization.abbreviation_map.get(x)
Organization.from_name = lambda x: Organization.name_map.get(x)


Organization.DETECTOR_MANUFACTURERS = one_of_instance(
    [
        Organization.AILIPU,
        Organization.ALLIED,
        Organization.BASLER,
        Organization.DODOTRONIC,
        Organization.EDMUND_OPTICS,
        Organization.HAMAMATSU,
        Organization.SPINNAKER,
        Organization.FLIR,
        Organization.THE_IMAGING_SOURCE,
        Organization.THORLABS,
        Organization.VIEWORKS,
        Organization.OTHER,
    ]
)

Organization.FILTER_MANUFACTURERS = one_of_instance(
    [
        Organization.CHROMA,
        Organization.EDMUND_OPTICS,
        Organization.MIDOPT,
        Organization.SEMROCK,
        Organization.THORLABS,
        Organization.OTHER,
    ]
)

Organization.LENS_MANUFACTURERS = one_of_instance(
    [
        Organization.COMPUTAR,
        Organization.EDMUND_OPTICS,
        Organization.FUJINON,
        Organization.HAMAMATSU,
        Organization.INFINITY_PHOTO_OPTICAL,
        Organization.LEICA,
        Organization.MITUTUYO,
        Organization.NAVITAR,
        Organization.NIKON,
        Organization.OLYMPUS,
        Organization.SCHNEIDER_KREUZNACH,
        Organization.THORLABS,
        Organization.CARL_ZEISS,
        Organization.OTHER,
    ]
)

Organization.DAQ_DEVICE_MANUFACTURERS = one_of_instance(
    [
        Organization.AIND,
        Organization.CHAMPALIMAUD,
        Organization.NATIONAL_INSTRUMENTS,
        Organization.IMEC,
        Organization.OEPS,
        Organization.SECOND_ORDER_EFFECTS,
        Organization.OTHER,
    ]
)

Organization.LASER_MANUFACTURERS = one_of_instance(
    [
        Organization.COHERENT_SCIENTIFIC,
        Organization.HAMAMATSU,
        Organization.OXXIUS,
        Organization.QUANTIFI,
        Organization.VORTRAN,
        Organization.OTHER,
    ]
)

Organization.LED_MANUFACTURERS = one_of_instance(
    [Organization.AMS_OSRAM, Organization.DORIC, Organization.PRIZMATIX, Organization.THORLABS, Organization.OTHER]
)

Organization.MANIPULATOR_MANUFACTURERS = one_of_instance([Organization.NEW_SCALE_TECHNOLOGIES, Organization.OTHER])

Organization.MONITOR_MANUFACTURERS = one_of_instance([Organization.ASUS, Organization.LG, Organization.OTHER])

Organization.SPEAKER_MANUFACTURERS = one_of_instance([Organization.TYMPHANY, Organization.ISL, Organization.OTHER])

Organization.FUNDERS = one_of_instance(
    [
        Organization.AI,
        Organization.CZI,
        Organization.MBF,
        Organization.MJFF,
        Organization.NCCIH,
        Organization.NIMH,
        Organization.NINDS,
        Organization.SIMONS_FOUNDATION,
        Organization.TWCF,
    ]
)

Organization.RESEARCH_INSTITUTIONS = one_of_instance(
    [
        Organization.AIBS,
        Organization.AIND,
        Organization.COLUMBIA,
        Organization.HUST,
        Organization.JANELIA,
        Organization.NYU,
        Organization.OTHER,
    ]
)

Organization.SUBJECT_SOURCES = one_of_instance(
    [
        Organization.AI,
        Organization.COLUMBIA,
        Organization.HUST,
        Organization.JANELIA,
        Organization.JAX,
        Organization.NYU,
        Organization.OTHER,
    ]
)
