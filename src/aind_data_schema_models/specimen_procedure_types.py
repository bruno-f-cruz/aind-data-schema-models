"""Script for the SpecimenProcedureType enum class."""

from enum import Enum


class SpecimenProcedureType(str, Enum):
    """Names for general specimen procedures"""

    DELIPIDATION = "Delipidation"
    CLEARING = "Clearing"
    EMBEDDING = "Embedding"
    EXPANSION = "Expansion"
    FIXATION = "Fixation"
    FIXATION_PERMEABILIZATION = "Fixation and permeabilization"
    GELATION = "Gelation"
    HYBRIDIZATION_AMPLIFICATION = "Hybridication and amplification"
    HCR = "Hybridization Chain Reaction"
    IMMUNOLABELING = "Immunolabeling"
    MOUNTING = "Mounting"
    REFRACTIVE_INDEX_MATCHING = "Refractive index matching"
    SECTIONING = "Sectioning"
    SOAK = "Soak"
    STORAGE = "Storage"
    STRIPPING = "Stripping"
    TAMOXIFEN_INDUCTION = "Tamoxifen induction"
    OTHER = "Other - see notes"
