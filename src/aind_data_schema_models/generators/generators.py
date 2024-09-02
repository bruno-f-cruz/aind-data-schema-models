from __future__ import annotations

import ast
import datetime
import os
import re
from pathlib import Path
from typing import Any, Callable, Dict, Generic, List, NamedTuple, Optional, Self, Tuple, Type, TypeVar, Union

import black
import isort
from pydantic import BaseModel

from aind_data_schema_models.utils import create_model_class_name as create_enum_key_from_class_name

TModel = TypeVar("TModel", bound=BaseModel)
TMapTo = TypeVar("TMapTo", bound=Any)
AllowedSources = Union[os.PathLike[str], str]
ParsedSource = Dict[str, str]
ParsedSourceCollection = List[ParsedSource]

_S = List[str]
_ST = List[Tuple[str, Optional[Callable[..., str]]]]
_SST = Union[_S, _ST]


class ForwardClassReference(NamedTuple):
    module_name: str
    class_name: str


class MappableReferenceField(Generic[TMapTo]):

    def __init__(
        self,
        typeof: Type[TMapTo] | ForwardClassReference,  # Allow for types to be passed as string references
        pattern: str,
        field_name: str,
        parsed_source_keys_handlers: Optional[_SST] = None,
    ) -> None:
        self._typeof = typeof
        self._pattern = pattern
        self._parsed_source_keys_handlers = self._normalize_parsed_source_keys(parsed_source_keys_handlers)
        self._field_name = field_name

    @staticmethod
    def _normalize_parsed_source_keys(value: Optional[_SST]) -> _ST:
        _normalized: _ST = []
        if value is None:
            return _normalized
        for item in value:
            if isinstance(item, str):
                _normalized.append((item, None))
                break
            elif isinstance(item, tuple):
                if len(item) != 2:
                    raise ValueError(f"Tuple must have 2 elements: {item}")
                if not isinstance(item[0], str):
                    raise ValueError(f"First element must be a string: {item}")
                if not callable(item[1]):
                    raise ValueError(f"Second element must be callable: {item}")
                else:
                    _normalized.append(item)
            else:
                raise ValueError(f"Invalid type: {type(item)}")
        return _normalized

    @property
    def field_name(self) -> str:
        return self._field_name

    @property
    def parsed_source_keys(self) -> List[str]:
        return [key for key, _ in self._parsed_source_keys_handlers]

    @property
    def typeof(self) -> Union[Type[TMapTo], ForwardClassReference]:
        return self._typeof

    @property
    def pattern(self) -> str:
        return self._pattern

    def __call__(self, parsed_source: ParsedSource) -> str:
        for key in self.parsed_source_keys:
            if key not in parsed_source:
                raise KeyError(f"Key not found in source data: {key}")
        _args: List[str] = []
        for key, handler in self._parsed_source_keys_handlers:
            _args.append(handler(parsed_source[key]) if handler is not None else parsed_source[key])
        return self._pattern.format(*_args)

    def has_mappable_field(self, obj: Any) -> bool:
        return hasattr(obj, self.field_name)


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
        from pydantic import Field, RootModel
        from typing import Union, Annotated, Literal
        """

        generic_import_statement = """
        from {module_name} import {class_name}\n"""

        sub_class_header = """
        class {class_name}({parent_name}):

        """

        class_header = """
        class {model_name}:

        """

        field = """\t{field_name}: Literal[{param}] = {param}
        """

        class_tail = """
        \tALL = tuple({parent_name}.__subclasses__())
        """

        model_one_of = """
        \tclass ONE_OF(RootModel):
        \t\troot: Annotated[Union[tuple({parent_name}.__subclasses__())], Field(discriminator="{discriminator}")]
        """

        model_abbreviation_map = """
        \tabbreviation_map = {m().abbreviation: m() for m in ALL}

        \t@classmethod
        \tdef from_abbreviation(cls, abbreviation: str):
        \t    return cls.abbreviation_map.get(abbreviation, None)
        """

        model_enum_entry = """\t{key} = {instance}()
        """

        generated_header = """
        # generated by aind-data-schema-models:
        #   filename:  {filename_source}
        #   timestamp: {datetime}

        """

    _SPECIAL_CHARACTERS = r"!@#$%^&*()+=<>?,./;:'\"[]{}|\\`~"
    _TRANSLATION_TABLE = str.maketrans("", "", _SPECIAL_CHARACTERS)

    def __init__(
        self,
        enum_like_class_name: str,
        parent_model_type: Type[TModel],
        data_source_identifier: AllowedSources,
        parser: Callable[..., ParsedSourceCollection],
        discriminator: str = "name",
        literal_class_name_hints: Optional[list[str]] = ["abbreviation", "name"],
        additional_preamble: Optional[str] = None,
        additional_imports: Optional[list[Type]] = None,
        render_abbreviation_map: bool = True,
        mappable_references: Optional[List[MappableReferenceField]] = None,
        **kwargs,
    ) -> None:

        self._enum_like_class_name = enum_like_class_name
        self._parent_model_type = parent_model_type
        self._data_source_identifier = data_source_identifier
        self._discriminator = discriminator
        self._render_abbreviation_map = render_abbreviation_map
        self._parser = parser
        self._literal_class_name_hints = literal_class_name_hints.copy() if literal_class_name_hints is not None else []
        self._additional_imports = additional_imports
        self._additional_preamble = additional_preamble
        self._mappable_references = mappable_references

        self._parsed_source: ParsedSourceCollection = self.parse()
        self._hint: Optional[str] = None
        self._created_literal_classes: dict[str, str] = {}

        self._validate()

    @classmethod
    def _solve_import(cls, typeof: Type | ForwardClassReference) -> str:

        module_name: str
        class_name: str

        if isinstance(typeof, ForwardClassReference):
            module_name = typeof.module_name
            class_name = typeof.class_name
        elif isinstance(typeof, type):
            module_name = typeof.__module__
            class_name = typeof.__name__
        else:
            raise ValueError("typeof must be a type or ModuleReference")

        if module_name == "builtins":
            return ""
        if module_name == "__main__":
            module_name = "aind_data_schema_models.generators"

        return cls._Templates.generic_import_statement.format(module_name=module_name, class_name=class_name)

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
                self._generate_mappable_references(),
                self._solve_import(self._parent_model_type),
                "".join(
                    [self._solve_import(import_module) for import_module in self._additional_imports]
                    if self._additional_imports
                    else []
                ),
                self._additional_preamble if self._additional_preamble else "",
                string_builder,
            ]
        )

        generated_code = self.unindent(generated_code)
        generated_code = self._replace_tabs_with_spaces(generated_code)

        if validate_code:
            is_valid, error = self._is_valid_code(generated_code)
            if not is_valid:
                raise error if error else ValueError("Generated code is not valid")

        # TODO This could benefit from reading the pyproject.toml file
        generated_code = black.format_str(generated_code, mode=black.FileMode())
        generated_code = isort.code(generated_code)

        return generated_code

    def _generate_mappable_references(self) -> str:
        string_builder = ""
        if self._mappable_references is not None:
            _refs = set([mappable.typeof for mappable in self._mappable_references])
            for r in _refs:
                string_builder += self._solve_import(r)
        return string_builder

    def write(self, output_path: Union[os.PathLike, str], validate_code: bool = True):
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self.generate(validate_code=validate_code))

    def _validate(self):
        if not issubclass(self._parent_model_type, BaseModel):
            raise ValueError("model_type must be a subclass of pydantic.BaseModel")
        if not self.is_pascal_case(self._enum_like_class_name):
            raise ValueError("model_name must be in PascalCase")

        if self._mappable_references is not None:
            fields_name = [mappable.field_name for mappable in self._mappable_references]
            if len(fields_name) != len(set(fields_name)):
                raise ValueError(
                    f"field_name must be unique across all MappableReferenceField objects. Entries: {fields_name}"
                )

    def parse(self) -> ParsedSourceCollection:
        return self._parser()

    def _generate_literal_model(  # noqa: C901
        self, parsed_source: ParsedSource, class_name: Optional[str] = None, require_all_fields_mapped: bool = False
    ) -> Tuple[dict[str, str], str]:
        _class_name_hints = self._literal_class_name_hints.copy()

        # Solve for the class name
        while class_name is None and len(_class_name_hints) > 0:
            self._hint = _class_name_hints.pop(0)
            class_name = parsed_source.get(self._hint, None)
        if class_name is None:
            self._hint = None
            raise ValueError("No class name provided and hint was found in the source data")
        sanitized_class_name = self._sanitize_class_name(class_name)

        # Get all fields that exist in the parent pydantic model
        parent_model_fields = {
            field_name: field_info.annotation.__name__
            for field_name, field_info in self._parent_model_type.model_fields.items()
            if field_info.annotation is not None  # This should be safe as all types should be annotated by pydantic
        }

        # If require_all_fields_mapped is True, we will raise an error if
        # a field in the parent model is not found in the source data
        # or in on the the MappableReferenceField objects
        if require_all_fields_mapped:
            for field_name in parent_model_fields.keys():
                if field_name in parsed_source.keys():
                    break
                if self._mappable_references is not None:
                    mappable_fields = [mappable.parsed_source_keys for mappable in self._mappable_references]
                    if field_name not in mappable_fields:
                        raise ValueError(f"Field {field_name} not found in source data")

                # Check if the parent class has the mappable field
                _mappable_references = self._mappable_references if self._mappable_references is not None else []
                for mappable in _mappable_references:
                    if not mappable.has_mappable_field(self._parent_model_type):
                        raise ValueError(f"Field {mappable.field_name} not found in parent")

        # Generate the class header
        string_builder = ""
        string_builder += self._Templates.sub_class_header.format(
            class_name=sanitized_class_name, parent_name=self._parent_model_type.__name__
        )

        # Populate the value-based fields
        for field_name in parent_model_fields.keys():
            _generated = False

            # 1) Mappable fields take priority over keys in csv
            _this_mappable = self._try_get_mappable_reference_field(field_name)
            if _this_mappable is not None and not _generated:
                param = _this_mappable(parsed_source)
                param = self.unindent(param)
                _generated = True

            # 2) if 1) fails, we try to get the value from the source data
            if field_name in parsed_source.keys() and not _generated:
                param = parsed_source[field_name]
                if parent_model_fields[field_name] == "str":
                    param = f'"{param}"'
                _generated = True

            # 3) throw if strict and 1) and 2) fail
            if not _generated and require_all_fields_mapped:
                raise ValueError(f"Field {field_name} could not be generated")

            if _generated:
                string_builder += self._Templates.field.format(field_name=field_name, param=param)

        return ({class_name: sanitized_class_name}, string_builder)

    def _try_get_mappable_reference_field(self, field: str) -> Optional[MappableReferenceField]:
        if self._mappable_references is None:
            return None
        for mappable in self._mappable_references:
            if mappable.field_name == field:
                return mappable
        return None

    def _generate_enum_like_class(self, render_abbreviation_map: bool = True) -> str:
        string_builder = ""
        string_builder += self._Templates.class_header.format(model_name=self._enum_like_class_name)

        for class_name, sanitized_class_name in self._created_literal_classes.items():
            string_builder += self._Templates.model_enum_entry.format(
                key=self._create_enum_key_from_class_name(class_name), instance=sanitized_class_name
            )

        string_builder += self._Templates.class_tail.format(parent_name=self._parent_model_type.__name__)
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
        suffix = value[0] if value[0] == "_" else ""  # Honor the first underscore
        return suffix + "".join([word.capitalize() for word in re.split(r"[_\- ]", value)])

    @classmethod
    def _sanitize_class_name(cls, class_name: str) -> str:
        # If the class name starts with a digit, we prefix it with an underscore
        class_name = class_name.translate(cls._TRANSLATION_TABLE)
        if class_name[0].isdigit():
            class_name = "_" + class_name

        return cls.to_pascal_case(class_name)

    @staticmethod
    def _create_enum_key_from_class_name(value: str) -> str:
        suffix = "_" if (value[0] == "_" or value[0].isdigit()) else ""
        return suffix + create_enum_key_from_class_name(value)

    @staticmethod
    def _is_valid_code(literal_code: str) -> Tuple[bool, Optional[SyntaxError]]:
        try:
            ast.parse(literal_code)
            return (True, None)
        except SyntaxError as e:
            return (False, e)

    @staticmethod
    def unindent(text: str) -> str:
        first_line = text.split("\n")[0]
        while first_line.strip() == "":
            text = text[1:]
            first_line = text.split("\n")[0]
        indent = len(first_line) - len(first_line.lstrip())
        return "\n".join([line[indent:] for line in text.split("\n")])

    @staticmethod
    def indent_line(text: str, level: int = 0) -> str:
        if level == 0:
            return text
        if level < 0:
            raise ValueError("Level must be greater than 0")
        return "\t" * level + text

    @classmethod
    def indent_block(cls, text: str, level: int = 0) -> str:
        return "".join([cls.indent_line(line, level) for line in text.split("\n")])

    @staticmethod
    def count_indent_level(text: str) -> int:
        return len(text) - len(text.lstrip("\t"))

    @staticmethod
    def _replace_tabs_with_spaces(text: str) -> str:
        return text.replace("\t", 4 * " ")
