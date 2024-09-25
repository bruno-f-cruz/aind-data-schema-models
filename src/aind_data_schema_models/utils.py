""" General utilities for constructing models from CSV files """

import csv
import re
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Type, Union

from pydantic import BaseModel, ConfigDict, Field, create_model
from typing_extensions import Annotated


def create_literal_model(
    obj: dict,
    base_model: Type[BaseModel],
    field_handlers: Optional[dict] = None,
    class_module: Optional[str] = None,
    shared_fields: Optional[dict] = None,
) -> Type[BaseModel]:
    """
    Make a dynamic pydantic literal model
    Parameters
    ----------
    obj : dict
    base_model : Type[BaseModel]
    field_handlers : Optional[dict]
      Default is  None.
    class_module : Optional[str]
      Default is None.

    Returns
    -------
    Type[BaseModel]

    """

    field_handlers = field_handlers or {}

    fields = {}
    for k, v in obj.items():
        if k in field_handlers:
            field_handlers[k](v, fields, k)
        elif k in base_model.__annotations__.keys():
            field_type = base_model.__annotations__[k]
            if v is not None:
                v = field_type(v)
            fields[k] = (Literal[v], Field(v))

    if shared_fields is not None:
        for k, v in shared_fields.items():
            fields[k] = (Literal[v], Field(v))

    class_str = obj.get("abbreviation") or obj.get("name")

    class_name = create_model_class_name(class_str)
    m = create_model(class_name, model_config=ConfigDict(frozen=True), __base__=base_model, **fields)

    if class_module:
        m.__module__ = class_module

    return m


def create_model_class_name(class_name: str) -> str:
    """
    Maps an input string to a valid class name by removing punctuation and
    white spaces.
    Parameters
    ----------
    class_name : str
      For example, "Behavior Videos"

    Returns
    -------
    str
      For example, "BEHAVIOR_VIDEOS"

    """

    # remove punctuation
    punctuation = re.compile(r'[.,!?;:\'"-()]')
    class_name = punctuation.sub("", class_name)

    # replace whitespace from upper case
    pattern = re.compile(r"[\W_]+")
    return pattern.sub("_", class_name.upper())


def create_literal_class(
    objects: List[dict],
    class_name: str,
    class_module: Optional[str] = None,
    base_model: Type[BaseModel] = BaseModel,
    discriminator: str = "name",
    field_handlers: Optional[dict] = None,
    shared_fields: Optional[dict] = None,
):
    """
    Make a dynamic pydantic literal class
    Parameters
    ----------
    objects : List[dict]
    class_name : str
    class_module : Optional[str]
      Default is None.
    base_model : Type[BaseModel]
      Default is BaseModel
    discriminator : str
      Default is 'name'
    field_handlers : Optional[dict]
      Default is None.

    Returns
    -------

    """

    cls = type(class_name, (object,), {})

    # add a "ALL" class variable
    all_models = tuple(
        create_literal_model(
            obj=obj,
            base_model=base_model,
            field_handlers=field_handlers,
            class_module=class_module,
            shared_fields=shared_fields,
        )
        for obj in objects
    )

    setattr(cls, "ALL", tuple(all_models))

    # Older versions of flake8 raise errors about 'ALL' being undefined
    setattr(cls, "ONE_OF", Annotated[Union[getattr(cls, "ALL")], Field(discriminator=discriminator)])  # noqa: F821

    # add the model instances as class variables
    for m in all_models:
        setattr(cls, m.__name__, m())

    return cls


def read_csv(file_path: Union[str, Path]) -> List[dict]:
    """
    Read a csv file and return the contents as a list of dictionaries. If a field is empty, it will be set to None.

    Parameters
    ----------
    file_path : Union[str, Path]

    Returns
    -------
    List[dict]

    """
    with open(file_path, "r") as f:
        reader = csv.DictReader(f)
        contents = list(reader)

    for item in contents:
        for k, v in item.items():
            if v == "":
                item[k] = None

    return contents


def one_of_instance(instances: List[Type[BaseModel]], discriminator="name") -> Annotated[Union[Any], Field]:
    """
    Make an annotated union of class instances
    Parameters
    ----------
    instances : List[Type[BaseModel]]
      A list of class instances.
    discriminator : str
      Each model in instances should have a common field name where each item
      is unique to the model. This will allow pydantic to know which class
      should be deserialized. Default is 'name'.

    Returns
    -------
    Annotated[Union[Any], Field]
      An annotated field that can be used to define a type where a choice from a
      possible set of classes can be selected.

    """
    return Annotated[Union[tuple(type(i) for i in instances)], Field(discriminator=discriminator)]


def create_string_enum(name: str, objects: List[Dict[str, Any]], value_key: str = "name") -> Type[Enum]:
    """
    Create a string enum from a list of objects.
    Parameters
    ----------
    name : str
    objects : List[Dict[str, Any]]
    value_key : str
      Default is 'name'.

    Returns
    -------
    Type[Enum]
      An str Enum class dynamically generated by parsing a csv file.

    """
    return Enum(
        type=str, value=name, names={create_model_class_name(obj[value_key]): obj[value_key] for obj in objects}
    )
