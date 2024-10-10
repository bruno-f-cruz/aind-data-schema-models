import argparse
import csv
import os
from pathlib import Path
from typing import Dict, List, Optional

from aind_pydantic_codegen.formatters import BlackFormatter, ISortFormatter
from aind_pydantic_codegen.generators import (
    ForwardClassReference,
    GeneratorContext,
    MappableReferenceField,
    ModelGenerator,
)
from aind_pydantic_codegen.validators import AstValidator

from aind_data_schema_models._generators._base import (
    _HarpDeviceTypeModel,
    _ModalityModel,
    _MouseAnatomyModel,
    _PlatformModel,
    _RegistryModel,
    _SpeciesModel,
)


def csv_parser(value: os.PathLike, fieldnames: Optional[List[str]] = None) -> List[Dict[str, str]]:
    with open(value, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f, fieldnames=fieldnames))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Generate models from CSV files.")
    parser.add_argument(
        "--root",
        type=str,
        required=False,
        default="./src/aind_data_schema_models/models",
        help="The root directory where the CSV files are located.",
    )
    parser.add_argument(
        "--target_folder",
        type=str,
        required=False,
        default="./src/aind_data_schema_models/_generated",
        help="The target directory where the generated models will be saved.",
    )
    args = parser.parse_args()

    root = Path(args.root)
    target_folder = Path(args.target_folder)

    platforms = ModelGenerator(
        class_name="_Platform",
        seed_model_type=_PlatformModel,
        discriminator="name",
        data_source_identifier="platforms.csv",
        parser=lambda: csv_parser(root / "platforms.csv"),
    )

    modalities = ModelGenerator(
        class_name="_Modality",
        seed_model_type=_ModalityModel,
        discriminator="name",
        data_source_identifier="modalities.csv",
        parser=lambda: csv_parser(root / "modalities.csv"),
    )

    harp_device_types = ModelGenerator(
        class_name="_HarpDeviceType",
        seed_model_type=_HarpDeviceTypeModel,
        discriminator="name",
        data_source_identifier="https://raw.githubusercontent.com/harp-tech/protocol/97ded281bd1d0d7537f90ebf545d74cf8ba8805e/whoami.yml",  # noqa: E501
        parser=lambda: csv_parser(root / "harp_types.csv"),
        render_abbreviation_map=False,
    )

    registry = ModelGenerator(
        class_name="_Registry",
        seed_model_type=_RegistryModel,
        discriminator="name",
        data_source_identifier="registries.csv",
        parser=lambda: csv_parser(root / "registries.csv"),
    )

    species = ModelGenerator(
        class_name="_Species",
        seed_model_type=_SpeciesModel,
        discriminator="name",
        data_source_identifier="species.csv",
        parser=lambda: csv_parser(root / "species.csv"),
        render_abbreviation_map=False,
        mappable_references=[
            MappableReferenceField(
                typeof=ForwardClassReference(
                    module_name="aind_data_schema_models._generated.registries", class_name="_Registry"
                ),
                field_name="registry",
                parsed_source_keys_handlers=["registry_abbreviation"],
                pattern="_Registry.{}",
            ),
            MappableReferenceField(
                typeof=str,
                field_name="registry_identifier",
                parsed_source_keys_handlers=["registry_identifier"],
                pattern='"{}"',
            ),
        ],
    )

    mouse_anatomy = ModelGenerator(
        class_name="_MouseAnatomyType",
        seed_model_type=_MouseAnatomyModel,
        discriminator="registry_identifier",
        data_source_identifier="mouse_dev_anat_ontology.csv",
        parser=lambda: csv_parser(root / "mouse_dev_anat_ontology.csv"),
        mappable_references=[
            MappableReferenceField(
                typeof=ForwardClassReference(
                    module_name="aind_data_schema_models._generated.registries", class_name="_Registry"
                ),
                field_name="registry",
                parsed_source_keys_handlers=["registry_identifier"],
                pattern="_Registry.EMAPA",
            ),
            MappableReferenceField(
                typeof=str,
                field_name="registry_identifier",
                parsed_source_keys_handlers=["registry_identifier"],
                pattern='"{}"',
            ),
        ],
        render_abbreviation_map=False,
    )

    with GeneratorContext(
        code_validators=[AstValidator()], code_formatters=[BlackFormatter(), ISortFormatter()]
    ) as ctx:
        ctx.add_generator(registry, "registries.py")
        ctx.add_generator(harp_device_types, "harp_types.py")
        ctx.add_generator(platforms, "platforms.py")
        ctx.add_generator(modalities, "modalities.py")
        ctx.add_generator(species, "species.py")
        ctx.add_generator(mouse_anatomy, "mouse_anatomy.py")
        ctx.write_all(target_folder)
