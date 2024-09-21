from typing import Any, ClassVar, Dict, Protocol, cast
from automappy.exceptions import MissingFieldsError
from automappy.mappers.object_mapper import ObjectMapper
from automappy.types.type_pair import TypePair

import dataclasses

from dataclasses import is_dataclass


class IsDataclass(Protocol):
    __dataclass_fields__: ClassVar[Dict[str, Any]]


class DataclassMapper(ObjectMapper):
    def is_compatible(self, tp: TypePair) -> bool:
        return self._is_dataclass(tp.from_) and self._is_dataclass(tp.to)

    def map[F, T](self, tp: TypePair[F, T], from_: F) -> T:
        assert self._is_dataclass(type(from_)), "from_ must be a dataclass"
        assert self._is_dataclass(tp.to), "tp.to must be a dataclass"

        to_kw_to_value = self._map_from_fields(tp, from_)
        to_kw_to_value |= self._map_from_properties(tp, from_)

        missing_fields = [
            field
            for field in dataclasses.fields(cast(IsDataclass, tp.to))
            if field.name not in to_kw_to_value and field.default == dataclasses.MISSING
        ]
        if missing_fields:
            raise MissingFieldsError(tp, [field.name for field in missing_fields])

        return tp.to.__call__(**to_kw_to_value)

    def _map_from_fields[F, T](self, tp: TypePair[F, T], from_: F) -> dict[str, Any]:
        from automappy.mappers.registry import MapperRegistry

        from_fields = dataclasses.fields(cast(IsDataclass, from_))
        to_fields = dataclasses.fields(cast(IsDataclass, tp.to))

        to_kw_to_value: dict[str, Any] = {}

        for from_field in from_fields:
            to_field = next(
                (field for field in to_fields if field.name == from_field.name), None
            )
            if to_field is None:
                continue

            from_field_type = from_field.type
            to_field_type = to_field.type

            assert isinstance(from_field_type, type), "from_field_type must be a type"
            assert isinstance(to_field_type, type), "to_field_type must be a type"

            field_tp = TypePair(from_field_type, to_field_type)
            from_value = getattr(from_, from_field.name)
            to_value = MapperRegistry.find_mapper(field_tp).map(field_tp, from_value)
            to_kw_to_value[to_field.name] = to_value

        return to_kw_to_value

    def _map_from_properties[
        F, T
    ](self, tp: TypePair[F, T], from_: F) -> dict[str, Any]:
        from automappy.mappers.registry import MapperRegistry

        from_properties = {
            k: v for k, v in tp.from_.__dict__.items() if isinstance(v, property)
        }
        to_fields = dataclasses.fields(cast(IsDataclass, tp.to))
        to_kw_to_value: dict[str, Any] = {}
        for from_property_name, from_property in from_properties.items():
            if from_property.fget is None:
                continue

            to_field = next(
                (field for field in to_fields if field.name == from_property_name), None
            )
            if to_field is None:
                continue

            from_property_type = from_property.fget.__annotations__["return"]
            to_field_type = to_field.type
            assert isinstance(
                from_property_type, type
            ), "from_property_type must be a type"
            assert isinstance(to_field_type, type), "to_field_type must be a type"

            field_tp = TypePair(from_property_type, to_field_type)
            from_value = from_property.fget(from_)
            to_value = MapperRegistry.find_mapper(field_tp).map(field_tp, from_value)
            to_kw_to_value[to_field.name] = to_value

        return to_kw_to_value

    def _is_dataclass(self, type_: type) -> bool:
        return is_dataclass(type_)
