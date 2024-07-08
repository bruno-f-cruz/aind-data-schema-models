import importlib
from typing import Iterator
import argparse
import json
import sys
from pathlib import Path
import aind_data_schema_models
import os

pydantic_models  = {
    "modalities" : "Modality",
    "organizations": "Organization",
    "species": "Species",
    "registry": "Registry"
}

enum_models = {
     "process_names": "ProcessName"
}

for mod in {**pydantic_models, **enum_models}.keys():
        importlib.import_module(f"aind_data_schema_models.{mod}")

class SchemaWriter:
    """Class to write Pydantic schemas to JSON"""

    DEFAULT_FILE_PATH = os.getcwd()

    def __init__(self, args: list) -> None:
        """Initialize schema writer class."""
        self.args = args
        self.configs = self._parse_arguments(args)

    def _parse_arguments(self, args: list) -> argparse.Namespace:
        """Parses sys args with argparse"""

        help_message = "Output directory, defaults to current working directory"

        parser = argparse.ArgumentParser()

        parser.add_argument(
            "-o",
            "--output",
            required=False,
            default=self.DEFAULT_FILE_PATH,
            help=help_message,
        )

        parser.add_argument(
            "--attach-version",
            action="store_true",
            help="Add extra directory with schema version number",
        )
        parser.set_defaults(attach_version=False)

        optional_args = parser.parse_args(args)

        return optional_args

    @staticmethod
    def get_schemas(model_name: str, class_name: str) -> Iterator:
        """
        Returns Iterator of classes
        """
        module_object = sys.modules[f"aind_data_schema_models.{model_name}"]
        class_object = getattr(module_object, class_name)

        for schema in class_object._ALL:
            yield schema

    def write_to_json(self, models_map: dict) -> None:
        """
        Writes Pydantic models to JSON file.
        """
        output_path = self.configs.output
        for models in models_map:
            filename = models_map[models].lower()
            file_extension = "".join(Path(filename).suffixes)
            schema_filename = f"{filename}_schema.json"
            print(f"******{schema_filename}*******")
            schemas_to_write = self.get_schemas(models, models_map[models])
            for schema in schemas_to_write:
                if self.configs.attach_version:
                    schema_version = schema.model_construct().schema_version
                    model_directory_name = schema_filename.replace("_schema.json", "")
                    sub_directory = Path(output_path) / model_directory_name / schema_version
                    output_file = sub_directory / schema_filename
                else:
                    output_file = Path(output_path) / schema_filename

                if not os.path.exists(output_file.parent):
                    os.makedirs(output_file.parent)

                with open(output_file, "w") as f:
                    schema_json: dict = schema.model_json_schema()
                    schema_json_str: str = json.dumps(schema_json, indent=3)
                    f.write(schema_json_str)


if __name__ == "__main__":
    """User defined argument for output directory"""
    sys_args = sys.argv[1:]
    s = SchemaWriter(sys_args)
    s.write_to_json(pydantic_models)
