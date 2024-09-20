from typing import get_origin

from automappy.exceptions import ValueTypeError
from automappy.mappers.registry import MapperRegistry
from automappy.types.type_pair import TypePair


class Mapper[F, T]:
    def __init__(self, from_: type[F], to: type[T]):
        self._tp = TypePair(from_, to)

    @classmethod
    def create_mapper[F_, T_](cls, from_: type[F_], to: type[T_]) -> "Mapper[F_, T_]":
        return Mapper(from_, to)

    def map(self, value: F) -> T:
        self._assert_is_type(value)

        mapper = MapperRegistry.find_mapper(self._tp)
        return mapper.map(self._tp, value)

    def _assert_is_type(self, value: F) -> None:
        expected_type = get_origin(self._tp.from_) or self._tp.from_

        if type(value) is not expected_type:
            raise ValueTypeError(value, self._tp.from_)
