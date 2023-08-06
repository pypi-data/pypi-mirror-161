from typing import Any, Generic, Protocol, Type, TypeVar

A = TypeVar("A", covariant=True)


class JsonSchema(Generic[A], Protocol):
    @classmethod
    def from_json(cls: Type[A], value: Any) -> A:
        raise NotImplementedError()

    def to_json(self) -> Any:
        raise NotImplementedError()
