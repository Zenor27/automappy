from typing import NamedTuple


class TypePair[F, T](NamedTuple):
    from_: type[F]
    to: type[T]

    def __repr__(self) -> str:
        return f"{self.from_} -> {self.to}"

    def __str__(self) -> str:
        return self.__repr__()
