import csv
import os
import ast
from typing import Type, TypeVar, Union, Tuple
import re
from pydantic import BaseModel, ConfigDict, Field
from pathlib import Path
import datetime
from aind_data_schema_models.pid_names import BaseName
from aind_data_schema_models.registries import Registry, RegistryModel
from aind_data_schema_models.utils import create_model_class_name as create_enum_key_from_class_name
import black
import isort


class _HarpDeviceTypeModel(BaseModel):
    """Base model config"""

    model_config = ConfigDict(frozen=True)
    name: str = Field(..., title="Harp device type name")
    whoami: int = Field(..., title="Harp whoami value")


class _ModalityModel(BaseName):
    """Base model config"""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., title="Modality name")
    abbreviation: str = Field(..., title="Modality abbreviation")


class _MouseAnatomyModel(BaseModel):
    """Base model config"""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., title="Structure name")
    registry: RegistryModel = Field(..., title="Structure registry")
    registry_identifier: str = Field(title="Structure EMAPA ID")


class _OrganizationModel(BaseModel):
    """Base model config"""

    model_config = ConfigDict(frozen=True)

    name: str
    abbreviation: str = None
    registry: RegistryModel = None
    registry_identifier: str = None


class _SpeciesModel(BaseModel):
    """base model for species, like Mus musculus"""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., title="Species name")
    registry: RegistryModel = Field(..., title="Species registry")
    registry_identifier: str = Field(..., title="Species registry identifier")


class _PlatformModel(BaseModel):
    """Base model config"""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., title="Platform name")
    abbreviation: str = Field(..., title="Platform abbreviation")


TModel = TypeVar("TModel", bound=BaseModel)
from typing import Optional


class ModelGenerator:

    class _Templates:

        import_statements = """
        from pydantic import Field
        from typing import Union, Annotated, Literal
        """

        generic_import_statement = """from {module_name} import {class_name}\n"""

        sub_class_header = """
        class {class_name}({parent_name}):

        """

        class_header = """
        class {model_name}:

        """

        field = """\t{field_name}: Literal[{param}] = {param}
        """

        model_one_of = """
        \t_ALL = tuple({parent_name}.__subclasses__())
        \tONE_OF = Annotated[Union[_ALL], Field(discriminator="{discriminator}")]
        """

        model_abbreviation_map = """
        \tabbreviation_map = {m().abbreviation: m() for m in _ALL}

        \t@classmethod
        \tdef from_abbreviation(cls, abbreviation: str):
        \t    return cls.abbreviation_map[abbreviation]
        """

        model_enum_entry = """\t{key} = {instance}()
        """

        generated_header = """
        # generated by aind-data-schema-models:
        #   filename:  {filename_source}
        #   timestamp: {datetime}

        """

    def __init__(
        self,
        enum_like_class_name: str,
        parent_model_type: Type[TModel],
        source_data_path: Union[os.PathLike, str],
        discriminator: str = "name",
        literal_class_name_hints: Optional[list[str]] = ["abbreviation", "name"],
        additional_preamble: Optional[str] = None,
        additional_imports: Optional[list[Type]] = None,
        **kwargs,
    ) -> None:

        self.enum_like_class_name = enum_like_class_name
        self.parent_model_type = parent_model_type
        self.source_data_path = Path(source_data_path)
        self.discriminator = discriminator
        self._parsed_source = self._parse_source(fieldnames=kwargs.pop("fieldnames", None))
        self._literal_class_name_hints = literal_class_name_hints if literal_class_name_hints is not None else []
        self._hint: Optional[str] = None
        self._created_literal_classes: dict[str, str] = {}
        self._additional_imports = additional_imports
        self._additional_preamble = additional_preamble
        self._validate()

    def _validate(self):
        if not issubclass(self.parent_model_type, BaseModel):
            raise ValueError("model_type must be a subclass of pydantic.BaseModel")
        if not self.is_pascal_case(self.enum_like_class_name):
            raise ValueError("model_name must be in PascalCase")

    @staticmethod
    def is_pascal_case(value: str) -> bool:
        if value.isidentifier():
            return value[1].isupper() if value[0] == "_" else value[0].isupper()
        else:
            return False

    @staticmethod
    def to_pascal_case(value: str) -> str:
        """Converts a string to PascalCase by splitting the word on "_", "-", and " " and capitalizing each sub-word"""
        return "".join([word.capitalize() for word in re.split(r"[_\- ]", value)])

    def _parse_source(self, fieldnames: Optional[list[str]]) -> list[dict[str, str]]:
        with open(self.source_data_path, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f, fieldnames=fieldnames))

    def _generate_literal_model(
        self, sub: dict[str, str], class_name: Optional[str] = None
    ) -> Tuple[dict[str, str], str]:
        _class_name_hints = self._literal_class_name_hints.copy()

        while class_name is None and len(_class_name_hints) > 0:
            self._hint = _class_name_hints.pop(0)
            class_name = sub.get(self._hint, None)
        if class_name is None:
            raise ValueError("No class name provided and hint was found in the source data")

        sanitized_class_name = self.to_pascal_case(class_name)

        # Since we are sticking with csv, I will assume only primitive types and this should suffice
        parent_model_fields = {
            field_name: field_info.annotation.__name__
            for field_name, field_info in self.parent_model_type.model_fields.items()
        }
        for field_name in parent_model_fields.keys():
            if field_name not in sub.keys():
                raise ValueError(f"Field {field_name} not found in source data")

        string_builder = ""
        string_builder += self._Templates.sub_class_header.format(
            class_name=sanitized_class_name, parent_name=self.parent_model_type.__name__
        )

        for field_name in parent_model_fields.keys():
            param = sub[field_name]
            if parent_model_fields[field_name] == "str":
                param = f'"{param}"'
            string_builder += self._Templates.field.format(field_name=field_name, param=param)
        return ({class_name: sanitized_class_name}, string_builder)

    def _generate_enum_like_class(self, render_abbreviation_map: bool = True) -> str:
        string_builder = ""
        string_builder += self._Templates.class_header.format(model_name=self.enum_like_class_name)

        for class_name, sanitized_class_name in self._created_literal_classes.items():
            string_builder += self._Templates.model_enum_entry.format(
                key=create_enum_key_from_class_name(class_name), instance=sanitized_class_name
            )

        string_builder += self._Templates.model_one_of.format(
            parent_name=self.parent_model_type.__name__, discriminator=self.discriminator
        )
        if render_abbreviation_map:
            string_builder += self._Templates.model_abbreviation_map
        return string_builder

    def generate(self, validate_code: bool = True) -> str:
        string_builder = "\n"

        for sub in self._parsed_source:
            _class_name, _sub_string = self._generate_literal_model(sub)
            string_builder += _sub_string + "\n"
            self._created_literal_classes.update(_class_name)

        string_builder += self._generate_enum_like_class()

        if validate_code:
            is_valid, error = self._is_valid_code(string_builder)
            if not is_valid:
                raise error if error else ValueError("Generated code is not valid")

        return string_builder

    def write(self, output_path: Union[os.PathLike, str], validate_code: bool = True):
        with open(output_path, "w", encoding="utf-8") as f:
            generated_code = "".join(
                [
                    self._Templates.generated_header.format(
                        filename_source=self.source_data_path.relative_to(Path(".").resolve()),
                        datetime=datetime.datetime.now(),
                    ),
                    self._Templates.import_statements.format(),
                    self._Templates.generic_import_statement.format(
                        module_name=self.parent_model_type.__module__, class_name=self.parent_model_type.__name__
                    ),
                    "".join(
                        [
                            self._Templates.generic_import_statement.format(
                                module_name=import_module.__module__, class_name=import_module.__name__
                            )
                            for import_module in self._additional_imports
                        ]
                        if self._additional_imports
                        else []
                    ),
                    self._additional_preamble if self._additional_preamble else "",
                    self.generate(validate_code=validate_code),
                ]
            )

            generated_code = self._unindent(generated_code)
            generated_code = self._replace_tabs_with_spaces(generated_code)
            generated_code = black.format_str(generated_code, mode=black.FileMode())
            generated_code = isort.code(generated_code)

            f.write(generated_code)

    @staticmethod
    def _is_valid_code(literal_code: str) -> Tuple[bool, Optional[SyntaxError]]:
        try:
            ast.parse(literal_code)
            return (True, None)
        except SyntaxError as e:
            return (False, e)

    @staticmethod
    def _unindent(text: str) -> str:
        first_line = text.split("\n")[0]
        while first_line.strip() == "":
            text = text[1:]
            first_line = text.split("\n")[0]
        indent = len(first_line) - len(first_line.lstrip())
        return "\n".join([line[indent:] for line in text.split("\n")])

    @staticmethod
    def _replace_tabs_with_spaces(text: str) -> str:
        return text.replace("\t", 4 * " ")
