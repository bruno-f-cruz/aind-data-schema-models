from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Generic, List, Optional, Self, Type, TypeVar, Union

import black
import isort
from pydantic import BaseModel

from . import helpers
from .helpers import TemplateHelper

TModel = TypeVar("TModel", bound=BaseModel)
TMapTo = TypeVar("TMapTo", bound=Union[Any])
AllowedSources = Union[os.PathLike[str], str]
ParsedSource = Dict[str, str]


@dataclass
class ForwardClassReference:
    """A record to store a forward reference to a class."""

    module_name: str
    class_name: str


@dataclass
class ParsedSourceKeyHandler:
    """Represents an object that can handle/transform a parsed field reference"""

    field: str
    function_handle: Optional[Callable[..., str]] = None


class MappableReferenceField(Generic[TMapTo]):
    """Represents a reference that can be mapped to a class"""

    def __init__(
        self,
        typeof: Type[TMapTo] | ForwardClassReference,  # Allow for types to be passed as string references
        pattern: str,
        field_name: str,
        parsed_source_keys_handlers: Optional[Union[List[str], List[ParsedSourceKeyHandler]]] = None,
    ) -> None:
        self._typeof = typeof
        self._pattern = pattern
        self._parsed_source_keys_handlers = self._normalize_parsed_source_keys(parsed_source_keys_handlers)
        self._field_name = field_name

    @staticmethod
    def _normalize_parsed_source_keys(
        handlers: Optional[Union[List[str], List[ParsedSourceKeyHandler]]]
    ) -> List[ParsedSourceKeyHandler]:
        """Ensures that all handlers are converted to a uniform type


        Args:
            handler (Optional[Union[List[str], List[ParsedSourceKeyHandler]]]): The optional array with all handlers to be used. If left None, an empty list will be returned.
        Raises:
            ValueError: An ValueError exception will be thrown if the input type is not valid.

        Returns:
            List[ParsedSourceKeyHandler]: Returns a list where all entries are ParsedSourceKeyHandler types.
        """
        _normalized: List[ParsedSourceKeyHandler] = []
        if handlers is None:
            return _normalized
        for handle in handlers:
            if isinstance(handle, str):
                _normalized.append(ParsedSourceKeyHandler(handle))
                break
            elif isinstance(handle, ParsedSourceKeyHandler):
                _normalized.append(handle)
            else:
                raise ValueError(f"Invalid type: {type(handle)}")
        return _normalized

    @property
    def field_name(self) -> str:
        return self._field_name

    @property
    def parsed_source_keys(self) -> List[str]:
        return [value.field for value in self._parsed_source_keys_handlers]

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
        for value in self._parsed_source_keys_handlers:
            _args.append(
                value.function_handle(parsed_source[key]) if value.function_handle is not None else parsed_source[key]
            )
        return self._pattern.format(*_args)

    def has_mappable_field(self, obj: Any) -> bool:
        return hasattr(obj, self.field_name)


@dataclass
class _WrappedModelGenerator:
    model_generator: ModelGenerator
    target_path: Optional[os.PathLike[str]] = None


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


@dataclass
class LiteralModelBlueprint:
    class_name: str
    sanitized_class_name: str = field(init=False)
    code_builder: str = ""

    def __post_init__(self):
        self.sanitized_class_name = helpers.sanitize_class_name(self.class_name)


class ModelGenerator:

    _BUILDER = TemplateHelper()
    _DEFAULT_LITERAL_CLASS_NAME_HINTS = ["abbreviation", "name"]

    def __init__(
        self,
        class_name: str,
        seed_model_type: Type[TModel],
        data_source_identifier: AllowedSources,
        parser: Callable[..., List[ParsedSource]],
        discriminator: str = "name",
        literal_class_name_hints: Optional[list[str]] = None,
        preamble: Optional[str] = None,
        additional_imports: Optional[list[Type]] = None,
        render_abbreviation_map: bool = True,
        mappable_references: Optional[List[MappableReferenceField]] = None,
        default_module_name: str = "aind_data_schema_models.generators",
        **kwargs,
    ) -> None:

        self._enum_like_class_name = class_name
        self._seed_model_type = seed_model_type
        self._data_source_identifier = data_source_identifier
        self._discriminator = discriminator
        self._render_abbreviation_map = render_abbreviation_map
        self._parser = parser
        self._literal_class_name_hints = literal_class_name_hints or self._DEFAULT_LITERAL_CLASS_NAME_HINTS
        self._additional_imports = additional_imports
        self._additional_preamble = preamble
        self._mappable_references = mappable_references
        self._default_module_name = default_module_name

        self._parsed_source: List[ParsedSource] = self.parse()
        self._literal_model_blueprints: List[LiteralModelBlueprint]

        self._validate()

    @staticmethod
    def solve_import(
        builder: TemplateHelper, typeof: Type | ForwardClassReference, default_module_name: Optional[str] = None
    ) -> str:
        """Attempts tp solve a type import to be generated

        Args:
            builder (TemplateHelper): Builder class that generates the literal code
            typeof (Type | ForwardClassReference): Type or reference to a type to be imported
            default_module_name (Optional[str], optional): The default module name to be used if the module name returns as __main__. Defaults to None but will raise a ValueError if __main__ is returned and no default is provided.

        Raises:
            ValueError

        Returns:
            str: A string with a literal string representing code to import the type
        """
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
            if default_module_name is None:
                raise ValueError("Module name is '__main__' but not default value was provided to override")
            module_name = default_module_name

        return builder.import_statement(module_name=module_name, class_name=class_name)

    def generate(self, validate_code: bool = True) -> str:
        """Generates and optionally validates code from the ModelGenerator

        Args:
            validate_code (bool, optional): Optionally validate code. Defaults to True.

        Raises:
            error: If the code fails the validation check

        Returns:
            str: Literal code with a fully generated file
        """
        string_builder = "\n"

        for sub in self._parsed_source:
            class_blueprint = self.generate_literal_model(
                builder=self._BUILDER,
                parsed_source=sub,
                seed_model_type=self._seed_model_type,
                mappable_references=self._mappable_references,
                class_name_hints=self._literal_class_name_hints,
            )
            string_builder += class_blueprint.code_builder + "\n"
            self._literal_model_blueprints.append(class_blueprint)

        string_builder += self.generate_enum_like_class(
            builder=self._BUILDER,
            class_name=self._enum_like_class_name,
            discriminator=self._discriminator,
            seed_model_type=self._seed_model_type,
            literal_model_blueprints=self._literal_model_blueprints,
            render_abbreviation_map=self._render_abbreviation_map,
        )

        generated_code = "".join(
            [
                self._BUILDER.file_header(helpers.normalize_model_source_provenance(self._data_source_identifier)),
                self._BUILDER.import_statements(),
                self._generate_mappable_references(),
                self.solve_import(self._BUILDER, self._seed_model_type, default_module_name=self._default_module_name),
                "".join(
                    [
                        self.solve_import(self._BUILDER, import_module, default_module_name=self._default_module_name)
                        for import_module in self._additional_imports
                    ]
                    if self._additional_imports
                    else []
                ),
                self._additional_preamble if self._additional_preamble else "",
                string_builder,
            ]
        )

        generated_code = helpers.unindent(generated_code)
        generated_code = helpers.replace_tabs_with_spaces(generated_code)

        if validate_code:
            is_valid, error = helpers.is_valid_code(generated_code)
            if not is_valid:
                raise error if error else ValueError("Generated code is not valid")

        # TODO This could benefit from reading the pyproject.toml file
        generated_code = black.format_str(generated_code, mode=black.FileMode())
        generated_code = isort.code(generated_code)

        return generated_code

    def _generate_mappable_references(self) -> str:
        string_builder = ""
        if self._mappable_references is not None:
            refs = set([mappable.typeof for mappable in self._mappable_references])
            for ref in refs:
                string_builder += self.solve_import(self._BUILDER, ref, default_module_name=self._default_module_name)
        return string_builder

    def write(self, output_path: Union[os.PathLike, str], validate_code: bool = True):
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self.generate(validate_code=validate_code))

    @staticmethod
    def _validate_class_name(class_name: str) -> None:
        if not helpers.is_pascal_case(class_name):
            raise ValueError("model_name must be in PascalCase")

    def _validate(self):
        if not issubclass(self._seed_model_type, BaseModel):
            raise ValueError("model_type must be a subclass of pydantic.BaseModel")

        self._validate_class_name(self._enum_like_class_name)

        if self._mappable_references is not None:
            fields_name = [mappable.field_name for mappable in self._mappable_references]
            if len(fields_name) != len(set(fields_name)):
                raise ValueError(
                    f"field_name must be unique across all MappableReferenceField objects. Entries: {fields_name}"
                )

    def parse(self) -> List[ParsedSource]:
        return self._parser()

    @classmethod
    def generate_literal_model(  # noqa: C901
        cls,
        builder: TemplateHelper,
        parsed_source: ParsedSource,
        seed_model_type: Type[TModel],
        mappable_references: Optional[List[MappableReferenceField]] = None,
        class_name: Optional[str] = None,
        class_name_hints: Optional[List[str]] = None,
        require_all_fields_mapped: bool = False,
    ) -> LiteralModelBlueprint:
        """Generates code for a model (LiteralModelBlueprint) with literal fields from a ParsedSource object.

        Args:
            builder (TemplateHelper): An interface that generates literal code
            parsed_source (ParsedSource): A source of data that a has already been parsed to a Dict[str, str]
            seed_model_type (Type[TModel]): The seed model that all literal classes will inherit from.
            mappable_references (Optional[List[MappableReferenceField]], optional): Optional mappable references to be used during generation.
            class_name (Optional[str], optional): The name to give to the literal class. If None is provided it will attempt to find it using the class_name_hints.
            require_all_fields_mapped (bool, optional): If True, a ValueError will be raised if a field of the seed model is not found in the source data or in the MappableReferenceField object.

        Raises:
            ValueError

        Returns:
            LiteralModelBlueprint: A blueprint with information with the generated literal class
        """

        if class_name_hints is None:
            _class_name_hints = []
        else:
            _class_name_hints = class_name_hints.copy()

        _hint: Optional[str] = None
        # Solve for the class name
        while class_name is None and len(_class_name_hints) > 0:
            _hint = _class_name_hints.pop(0)
            class_name = parsed_source.get(_hint, None)
        if class_name is None:
            _hint = None
            raise ValueError("No class name provided and hint was found in the source data")
        class_blueprint = LiteralModelBlueprint(class_name)

        # Get all fields that exist in the seed pydantic model
        parent_model_fields = {
            field_name: field_info.annotation.__name__
            for field_name, field_info in seed_model_type.model_fields.items()
            if field_info.annotation is not None  # This should be safe as all types should be annotated by pydantic
        }

        # If require_all_fields_mapped is True, we will raise an error if
        # a field in the parent model is not found in the source data
        # or in on the the MappableReferenceField objects
        if require_all_fields_mapped:
            for field_name in parent_model_fields.keys():
                if mappable_references is not None:
                    mappable_fields = [mappable.parsed_source_keys for mappable in mappable_references]
                    if field_name not in mappable_fields:
                        raise ValueError(f"Field {field_name} not found in mappable fields")
                if field_name not in parsed_source.keys():
                    raise ValueError(f"Field {field_name} not found in source data")

                # Check if the seed class has the mappable field
                _mappable_references = mappable_references if mappable_references is not None else []
                for mappable in _mappable_references:
                    if not mappable.has_mappable_field(seed_model_type):
                        raise ValueError(f"Mappable field {mappable.field_name} not found in seed model")

        # Generate the class header
        class_blueprint.code_builder += builder.class_header(
            class_name=class_blueprint.sanitized_class_name, parent_name=seed_model_type.__name__
        )

        # Populate the value-based fields
        for field_name in parent_model_fields.keys():
            _generated = False

            # 1) Mappable fields take priority over keys in csv
            _this_mappable = cls._try_get_mappable_reference_field(field_name, mappable_references)
            if _this_mappable is not None and not _generated:
                param = _this_mappable(parsed_source)
                param = helpers.unindent(param)
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
                class_blueprint.code_builder += builder.literal_field(name=field_name, value=param)

        return class_blueprint

    @staticmethod
    def _try_get_mappable_reference_field(
        field_name: str, mappable_references: Optional[List[MappableReferenceField]]
    ) -> Optional[MappableReferenceField]:
        if mappable_references is None:
            return None
        for mappable in mappable_references:
            if mappable.field_name == field_name:
                return mappable
        return None

    @staticmethod
    def generate_enum_like_class(
        builder: TemplateHelper,
        class_name: str,
        discriminator: str,
        seed_model_type: type[TModel] | str,
        literal_model_blueprints: List[LiteralModelBlueprint],
        render_abbreviation_map: bool = True,
    ) -> str:
        """Generates code for a enum-like class that includes instances of literal class models.

        Args:
            builder (TemplateHelper): A class that generates literal code
            class_name (str): The name of the class to be generated. It is assumed that it has been previously validated.
            discriminator (str): The field used as discriminator on the union of all literal model types
            seed_model_type (type[TModel] | str): The seed model type, or name, that is common to all literal models.
            literal_model_blueprints (List[LiteralModelBlueprint]): The blueprints for all generated literal models that will be used as values of the enum-like syntax of the generated class.
            render_abbreviation_map (bool, optional): Optionally renders the abbreviation map method as part of the class. Defaults to True.

        Returns:
            str: A string with the generated code for the enum-like class.
        """
        seed_model_name = seed_model_type if isinstance(seed_model_type, str) else seed_model_type.__name__
        string_builder = ""
        string_builder += builder.class_header(class_name=class_name)

        for class_blueprint in literal_model_blueprints:
            string_builder += builder.model_enum_entry(
                key=helpers.create_enum_key_from_class_name(class_blueprint.class_name),
                value=class_blueprint.sanitized_class_name,
            )

        string_builder += builder.type_all_from_subclasses(parent_name=seed_model_name)
        string_builder += builder.type_one_of(parent_name=seed_model_name, discriminator=discriminator)
        if render_abbreviation_map:
            string_builder += builder.abbreviation_map()

        return string_builder
