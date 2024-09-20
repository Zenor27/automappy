from collections.abc import Collection
from typing import cast
from automappy.mappers.object_mapper import ObjectMapper
from automappy.types.type_pair import TypePair


class CollectionMapper(ObjectMapper):
    def is_compatible(self, tp: TypePair) -> bool:
        return self._is_collection(tp.from_) and self._is_collection(tp.to)

    def map[F, T](self, tp: TypePair[F, T], from_: F) -> T:
        from automappy.mappers.registry import MapperRegistry

        assert self._is_collection(type(from_)), "from_ must be a collection"

        from_content_type = self._get_collection_content_type(tp.from_)
        to_content_type = self._get_collection_content_type(tp.to)

        content_tp = TypePair(from_content_type, to_content_type)
        content_mapper = MapperRegistry.find_mapper(content_tp)

        return tp.to.__call__(
            [content_mapper.map(content_tp, value) for value in cast(Collection, from_)]
        )

    def _is_collection(self, type_: type) -> bool:
        return hasattr(type_, "__iter__") and not self._is_mapping(type_)

    def _is_mapping(self, type_: type) -> bool:
        return (
            hasattr(type_, "items")
            and hasattr(type_, "keys")
            and hasattr(type_, "values")
        )

    def _get_collection_content_type(self, type_: type) -> type:
        return type_.__args__[0]
