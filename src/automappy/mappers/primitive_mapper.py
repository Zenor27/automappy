from automappy.mappers.object_mapper import ObjectMapper
from automappy.types.type_pair import TypePair


class PrimitiveMapper(ObjectMapper):
    def is_compatible(self, tp: TypePair) -> bool:
        return self._is_primitive(tp.from_) and self._is_primitive(tp.to)

    def map[F, T](self, tp: TypePair[F, T], from_: F) -> T:
        return tp.to.__call__(from_)

    def _is_primitive(self, type_: type) -> bool:
        return type_ in {int, float, str, bool}
