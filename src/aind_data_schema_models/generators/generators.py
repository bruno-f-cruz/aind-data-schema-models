from __future__ import annotations

import ast
import datetime
import os
import re
from pathlib import Path
from typing import Callable, Dict, List, NamedTuple, Optional, Self, Tuple, Type, TypeVar, Union

import black
import isort
from pydantic import BaseModel

from aind_data_schema_models.utils import create_model_class_name as create_enum_key_from_class_name

TModel = TypeVar("TModel", bound=BaseModel)
AllowedSources = Union[os.PathLike[str], str]
ParsedSource = List[Dict[str, str]]


class _WrappedModelGenerator(NamedTuple):
    model_generator: ModelGenerator
    target_path: Optional[os.PathLike[str]]


class GeneratorContext:
    _self = None

    def __new__(cls) -> Self:
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __init__(self) -> None:
        self._generators: List[_WrappedModelGenerator] = []

    @property
    def generators(self) -> List[ModelGenerator]:
        return [g.model_generator for g in self._generators]

    def add_generator(self, generator: ModelGenerator, file_name: Optional[os.PathLike[str]] = None):
        self._generators.append(_WrappedModelGenerator(model_generator=generator, target_path=file_name))

    def remove_generator(self, generator: ModelGenerator):
        self._generators = [g for g in self._generators if g.model_generator != generator]

    def generate_all(self, validate_code: bool = True) -> List[str]:
        return [generator.model_generator.generate(validate_code=validate_code) for generator in self._generators]

    def write_all(self, output_folder: os.PathLike = Path("."), validate_code: bool = True, create_dir: bool = True):
        if create_dir:
            os.makedirs(output_folder, exist_ok=True)

        for generator in self._generators:
            target_path = (
                generator.target_path
                if generator.target_path
                else generator.model_generator._enum_like_class_name.lower() + ".py"
            )
            generator.model_generator.write(Path(output_folder) / str(target_path), validate_code=validate_code)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._generators = []
        self._self = None


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
        \tALL = tuple({parent_name}.__subclasses__())
        \tONE_OF = Annotated[Union[ALL], Field(discriminator="{discriminator}")]
        """

        model_abbreviation_map = """
        \tabbreviation_map = {m().abbreviation: m() for m in ALL}

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
        data_source_identifier: AllowedSources,
        parser: Callable[..., ParsedSource],
        discriminator: str = "name",
        literal_class_name_hints: Optional[list[str]] = ["abbreviation", "name"],
        additional_preamble: Optional[str] = None,
        additional_imports: Optional[list[Type]] = None,
        render_abbreviation_map: bool = True,
        **kwargs,
    ) -> None:

        self._enum_like_class_name = enum_like_class_name
        self._parent_model_type = parent_model_type
        self._data_source_identifier = data_source_identifier
        self._discriminator = discriminator
        self._render_abbreviation_map = render_abbreviation_map
        self._parser = parser
        self._literal_class_name_hints = literal_class_name_hints if literal_class_name_hints is not None else []
        self._additional_imports = additional_imports
        self._additional_preamble = additional_preamble

        self._parsed_source: ParsedSource = self.parse()
        self._hint: Optional[str] = None
        self._created_literal_classes: dict[str, str] = {}

        self._validate()

    def generate(self, validate_code: bool = True) -> str:
        string_builder = "\n"

        for sub in self._parsed_source:
            _class_name, _sub_string = self._generate_literal_model(sub)
            string_builder += _sub_string + "\n"
            self._created_literal_classes.update(_class_name)

        string_builder += self._generate_enum_like_class(render_abbreviation_map=self._render_abbreviation_map)

        generated_code = "".join(
            [
                self._Templates.generated_header.format(
                    filename_source=self._normalize_model_source_provenance(self._data_source_identifier),
                    datetime=datetime.datetime.now(),
                ),
                self._Templates.import_statements.format(),
                self._Templates.generic_import_statement.format(
                    module_name=self._normalized_module_name(self._parent_model_type.__module__),
                    class_name=self._parent_model_type.__name__,
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
                string_builder,
            ]
        )

        generated_code = self._unindent(generated_code)
        generated_code = self._replace_tabs_with_spaces(generated_code)

        if validate_code:
            is_valid, error = self._is_valid_code(generated_code)
            if not is_valid:
                raise error if error else ValueError("Generated code is not valid")

        # TODO This could benefit from reading the pyproject.toml file
        generated_code = black.format_str(generated_code, mode=black.FileMode())
        generated_code = isort.code(generated_code)

        return generated_code

    def write(self, output_path: Union[os.PathLike, str], validate_code: bool = True):
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self.generate(validate_code=validate_code))

    def _validate(self):
        if not issubclass(self._parent_model_type, BaseModel):
            raise ValueError("model_type must be a subclass of pydantic.BaseModel")
        if not self.is_pascal_case(self._enum_like_class_name):
            raise ValueError("model_name must be in PascalCase")

    def parse(self) -> ParsedSource:
        return self._parser()

    def _generate_literal_model(
        self, sub: dict[str, str], class_name: Optional[str] = None
    ) -> Tuple[dict[str, str], str]:
        _class_name_hints = self._literal_class_name_hints.copy()

        while class_name is None and len(_class_name_hints) > 0:
            self._hint = _class_name_hints.pop(0)
            class_name = sub.get(self._hint, None)
        if class_name is None:
            self._hint = None
            raise ValueError("No class name provided and hint was found in the source data")

        sanitized_class_name = self.to_pascal_case(class_name)

        # Since we are sticking with csv, I will assume only primitive types and this should suffice
        parent_model_fields = {
            field_name: field_info.annotation.__name__
            for field_name, field_info in self._parent_model_type.model_fields.items()
            if field_info.annotation is not None  # This should be safe as all types should be annotated by pydantic
        }
        for field_name in parent_model_fields.keys():
            if field_name not in sub.keys():
                raise ValueError(f"Field {field_name} not found in source data")

        string_builder = ""
        string_builder += self._Templates.sub_class_header.format(
            class_name=sanitized_class_name, parent_name=self._parent_model_type.__name__
        )

        for field_name in parent_model_fields.keys():
            param = sub[field_name]
            if parent_model_fields[field_name] == "str":
                param = f'"{param}"'
            string_builder += self._Templates.field.format(field_name=field_name, param=param)
        return ({class_name: sanitized_class_name}, string_builder)

    def _generate_enum_like_class(self, render_abbreviation_map: bool = True) -> str:
        string_builder = ""
        string_builder += self._Templates.class_header.format(model_name=self._enum_like_class_name)

        for class_name, sanitized_class_name in self._created_literal_classes.items():
            string_builder += self._Templates.model_enum_entry.format(
                key=create_enum_key_from_class_name(class_name), instance=sanitized_class_name
            )

        string_builder += self._Templates.model_one_of.format(
            parent_name=self._parent_model_type.__name__, discriminator=self._discriminator
        )
        if render_abbreviation_map:
            string_builder += self._Templates.model_abbreviation_map
        return string_builder

    @classmethod
    def _normalize_model_source_provenance(cls, model_source: AllowedSources) -> str:
        try:
            return str(model_source)
        except TypeError as e:
            raise TypeError("model_source must be a string or os.PathLike[str]") from e

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

    @staticmethod
    def _normalized_module_name(module_name: str) -> str:
        return "aind_data_schema_models.generators" if module_name == "__main__" else module_name
