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
