from typing import Any
from automappy.mappers.object_mapper import ObjectMapper
from automappy.types.type_pair import TypePair


class ClassMapper(ObjectMapper):
    def is_compatible(self, tp: TypePair) -> bool:
        return self._is_class(tp.from_) and self._is_class(tp.to)

    def map[F, T](self, tp: TypePair[F, T], from_: F) -> T:
        from automappy.mappers.registry import MapperRegistry

        assert self._is_class(type(from_)), "from_ must be a class"
        assert self._is_class(tp.to), "tp.to must be a class"

        from_ctor_args = self._get_ctor_args(type(from_))
        to_ctor_args = self._get_ctor_args(tp.to)

        kw_to_value: dict[str, Any] = {}

        for arg, type_ in from_ctor_args.items():
            if arg not in to_ctor_args:
                continue

            field_tp = TypePair(type_, to_ctor_args[arg])
            from_value = getattr(from_, arg)
            to_value = MapperRegistry.find_mapper(field_tp).map(field_tp, from_value)
            kw_to_value[arg] = to_value

        return tp.to.__call__(**kw_to_value)

    def _get_ctor_args(self, cls: type) -> dict[str, type]:
        return {
            arg: type_
            for arg, type_ in cls.__init__.__annotations__.items()
            if arg != "return"
        }

    def _is_class(self, cls: type) -> bool:
        return isinstance(cls, type)
