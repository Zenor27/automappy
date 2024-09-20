from typing import Protocol

from automappy.types.type_pair import TypePair


class ObjectMapper(Protocol):
    def is_compatible(self, tp: TypePair) -> bool: ...

    def map[F, T](self, tp: TypePair[F, T], from_: F) -> T: ...
