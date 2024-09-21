from typing import Any

from automappy.types.type_pair import TypePair


class ValueTypeError(TypeError):
    def __init__(self, value: Any, expected_type: type):
        self.value = value
        self.expected_type = expected_type
        super().__init__(f"Value '{value}' is not of type '{expected_type}'")


class ObjectMapperNotFoundError(ValueError):
    def __init__(self, tp: TypePair):
        self.tp = tp
        super().__init__(f"Object mapper not found for type pair '{tp}'")


class MissingFieldsError(ValueError):
    def __init__(self, tp: TypePair, missing_fields: list[str]):
        self.tp = tp
        self.missing_fields = missing_fields
        super().__init__(
            f"Cannot map type pair '{tp}'. Missing fields: {missing_fields}"
        )
