from collections.abc import Mapping
from typing import cast
from automappy.mappers.object_mapper import ObjectMapper
from automappy.types.type_pair import TypePair


class MappingMapper(ObjectMapper):
    def is_compatible(self, tp: TypePair) -> bool:
        return self._is_mapping(tp.from_) and self._is_mapping(tp.to)

    def map[F, T](self, tp: TypePair[F, T], from_: F) -> T:
        from automappy.mappers.registry import MapperRegistry

        assert self._is_mapping(type(from_)), "from_ must be a mapping"

        from_key_type = self._get_mapping_key_type(tp.from_)
        to_key_type = self._get_mapping_key_type(tp.to)
        key_tp = TypePair(from_key_type, to_key_type)
        key_mapper = MapperRegistry.find_mapper(key_tp)

        from_value_type = self._get_mapping_value_type(tp.from_)
        to_value_type = self._get_mapping_value_type(tp.to)
        value_tp = TypePair(from_value_type, to_value_type)
        value_mapper = MapperRegistry.find_mapper(value_tp)

        return tp.to.__call__(
            {
                key_mapper.map(key_tp, key): value_mapper.map(value_tp, value)
                for key, value in cast(Mapping, from_).items()
            }
        )

    def _get_mapping_key_type(self, type_: type) -> type:
        return type_.__args__[0]

    def _get_mapping_value_type(self, type_: type) -> type:
        return type_.__args__[1]

    def _is_mapping(self, type_: type) -> bool:
        return (
            hasattr(type_, "items")
            and hasattr(type_, "keys")
            and hasattr(type_, "values")
        )
