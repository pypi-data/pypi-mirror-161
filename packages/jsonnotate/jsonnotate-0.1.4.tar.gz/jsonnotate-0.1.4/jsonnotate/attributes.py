from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from .serialisation import Serialisation


@(lambda cls: cls())
class MISSING:
    __slots__ = ()

    def __bool__(self):
        return False

    def __repr__(self) -> str:
        return "<MISSING>"


@dataclass
class JSON:
    name: str
    omit_empty: bool = False
    nullable: bool = False
    serialisation: Optional[Serialisation] = None
    nonempty_predicate: Optional[Callable[[Any], bool]] = None
    omitted_value: Any = MISSING

    def _nonempty(self, value: Any):
        nep = self.nonempty_predicate
        if nep is None:
            return value is not None
        return nep(value)

    def serialise(self, value: Any) -> Any:
        if value is None:
            if self.nullable:
                return None
            raise TypeError("Got 'None' but field is not nullable")
        return value if self.serialisation is None else self.serialisation.serialise(value)

    def deserialise(self, value: Any) -> Any:
        return value if self.serialisation is None else self.serialisation.deserialise(None, value)

    @staticmethod
    def default(key: str, value: Any) -> Dict[str, Any]:
        return {key: value}

    def prepare(self, value: Any) -> Dict[str, Any]:
        if not self.omit_empty or self._nonempty(value):
            return {self.name: self.serialise(value)}
        return {}

    def extract(self, input_: Any, k) -> Any:
        try:
            value = input_[self.name]
        except LookupError:
            if self.omit_empty:
                return self.omitted_value
            raise
        else:
            if value is None and not self.nullable:
                raise TypeError("Got 'None' but field is not nullable")
            return self.deserialise(value)
