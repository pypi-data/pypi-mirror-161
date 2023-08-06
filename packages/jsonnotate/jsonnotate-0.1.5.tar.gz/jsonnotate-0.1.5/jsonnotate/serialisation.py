import datetime
from dataclasses import Field
from typing import Any, Protocol

from . import rfc3339 as _rfc3339


class Serialisation(Protocol):
    def serialise(self, value: Any) -> Any:
        ...

    def deserialise(self, into: Field, value: Any) -> Any:
        ...

    def as_list(self) -> "ListOf":
        return ListOf(self)

    def as_map(self) -> "MapOf":
        return MapOf(self)


class ListOf(Serialisation):
    def __init__(self, serialisation: Serialisation) -> None:
        self.serialisation = serialisation

    def serialise(self, value: Any) -> Any:
        ser = self.serialisation.serialise
        return [ser(i) for i in value]

    def deserialise(self, into: Field, value: Any) -> Any:
        des = self.serialisation.deserialise
        return [des(into, i) for i in value]


class MapOf(Serialisation):
    def __init__(self, serialisation: Serialisation) -> None:
        self.serialisation = serialisation

    def serialise(self, value: Any) -> Any:
        ser = self.serialisation.serialise
        return {k: ser(v) for k, v in value.items()}

    def deserialise(self, into: Field, value: Any) -> Any:
        des = self.serialisation.deserialise
        return {k: des(into, v) for k, v in value.items()}


class Identity(Serialisation):
    def serialise(self, value: Any) -> Any:
        return value

    def deserialise(self, into: Field, value: Any) -> Any:
        return value


class RFC3339Enc(Serialisation):
    def serialise(self, value: Any) -> Any:
        return _rfc3339.serialise(value) if value is not None else None

    def deserialise(self, into: Field, value: Any) -> Any:
        return _rfc3339.deserialise(value)


class ObjEnc(Serialisation):
    def __init__(self, cls: type) -> None:
        self._cls = cls

    def serialise(self, value: Any) -> Any:
        return value.to_json() if value is not None else None

    def deserialise(self, into: Field, value: Any) -> Any:
        return self._cls.from_json(value)


class TimestampEnc(Serialisation):
    def serialise(self, value: Any) -> Any:
        return value.timestamp() if value is not None else None

    def deserialise(self, into: Field, value: Any) -> Any:
        return datetime.datetime.fromtimestamp(value, datetime.timezone.utc)


RFC3339 = RFC3339Enc()
UNIX_TIMESTAMP = TimestampEnc()
