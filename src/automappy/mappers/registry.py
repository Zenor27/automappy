from automappy.exceptions import ObjectMapperNotFoundError
from automappy.mappers.collection_mapper import CollectionMapper
from automappy.mappers.mapping_mapper import MappingMapper
from automappy.mappers.object_mapper import ObjectMapper
from automappy.mappers.primitive_mapper import PrimitiveMapper
from automappy.types.type_pair import TypePair


class MapperRegistry:
    _mappers: list[ObjectMapper] = [
        PrimitiveMapper(),
        CollectionMapper(),
        MappingMapper(),
    ]

    @classmethod
    def find_mapper(cls, tp: TypePair) -> ObjectMapper:
        for mapper in cls._mappers:
            if mapper.is_compatible(tp):
                return mapper

        raise ObjectMapperNotFoundError(tp)
