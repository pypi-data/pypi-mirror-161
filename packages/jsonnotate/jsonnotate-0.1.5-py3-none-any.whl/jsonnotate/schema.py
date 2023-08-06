from dataclasses import MISSING as DC_MISSING
from dataclasses import Field, InitVar, is_dataclass

try:
    from types import NoneType
except ImportError:
    NoneType = type(None)
from typing import Any, Callable, ClassVar, List, Optional, Tuple, Type, TypeVar, Union, get_args

from typing_extensions import Annotated, get_origin

from .attributes import JSON, MISSING
from .protocol import JsonSchema

A = TypeVar("A")


class MissingJSONDefinitionError(LookupError):
    pass


def is_missing(value: Any) -> bool:
    return value is DC_MISSING


def has_default(value: Field) -> bool:
    return not is_missing(value.default) or not is_missing(value.default_factory)


def get_json_attribute(typ: Any) -> Optional[JSON]:
    if get_origin(typ) is Annotated:
        for param in get_args(typ)[1:]:
            if isinstance(param, JSON):
                return param
    return None


def is_nullable(typ: Any) -> bool:
    origin = get_origin(typ)
    if origin is Union:
        return NoneType in get_args(typ)
    if origin is Annotated:
        return is_nullable(get_args(typ)[0])
    return False


def create_builder(json: List[Tuple[Field, JSON]]) -> Callable[[Any], A]:
    def from_json(cls: Type[A], input_: Any) -> A:
        args = {f.name: v for f, v in ((f, j.extract(input_, None)) for f, j in json) if v is not MISSING}
        return cls(**args)

    return from_json


def create_writer(json: List[Tuple[Field, JSON]]) -> Callable[[Any], Any]:
    def to_json(inst: Any) -> Any:
        r = {}
        for f, j in json:
            r.update(j.prepare(getattr(inst, f.name)))
        return r

    return to_json


def validate(cls: type, *, generate_default_defn: bool = False) -> None:
    if not is_dataclass(cls):
        raise TypeError("Class must be a dataclass")

    cls_builders = []

    for field in cls.__dataclass_fields__.values():
        json = validate_field(field, generate_default_defn=generate_default_defn)
        if json is not None:
            cls_builders.append((field, json))

    return cls_builders


def validate_field(field: Field, generate_default_defn: bool = False) -> Optional[JSON]:
    typ = field.type
    origin = get_origin(typ)
    json = get_json_attribute(typ)

    if origin is ClassVar:
        if json is not None:
            raise TypeError("JSON attributes found on class variable.")
        return
    if not field.init:
        return
    if origin is InitVar:
        # init-only, if this has no defaults we can't create from json
        if not has_default(field):
            raise TypeError(
                f"Init-only field {field.name} has no default, cannot generate from_json() method. if this is optional, please set a default."
            )
        # TODO: support initvars from json
        return
    if json is None:
        if generate_default_defn:
            json = JSON(field.name, nullable=is_nullable(typ))
        else:
            if not has_default(field):
                raise TypeError(
                    f"Field {field.name} has no default, cannot generate from_json() method. if this is optional, please set a default."
                )
            return
    if json.nullable and not is_nullable(typ):
        raise TypeError(f"Field {field.name} is nullable but type is not Optional[...]")
    if json.omit_empty and not has_default(field):
        raise TypeError(f"Field {field.name} is omit_empty but has no default")

    return json


def json_schema(
    cls: Optional[type] = None, generate_default_defn: bool = False, from_json: bool = True, to_json: bool = True
):
    def decorator(cls: type) -> type:
        builders = validate(cls, generate_default_defn=generate_default_defn)
        if from_json and (not hasattr(cls, "from_json") or _is_protocol(cls, "from_json")):
            cls.from_json = classmethod(create_builder(builders))
        if to_json and (not hasattr(cls, "to_json") or _is_protocol(cls, "to_json")):
            cls.to_json = create_writer(builders)
        return cls

    if cls is None:
        return decorator
    return decorator(cls)


def _is_protocol(cls, mname: str) -> bool:
    attr = getattr(cls, mname, None)
    if attr is None:
        return True
    # classmethod
    if hasattr(attr, "__func__"):
        # bound method
        return attr.__func__ is getattr(JsonSchema, mname).__func__
    # method
    if attr is getattr(JsonSchema, mname):
        return True
    return False
