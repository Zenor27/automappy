from dataclasses import dataclass
from typing import NamedTuple
import pytest
from automappy.exceptions import (
    MissingFieldsError,
    ObjectMapperNotFoundError,
    ValueTypeError,
)
from automappy.mapper import Mapper


def test_incorrect_map_type() -> None:
    m = Mapper.create_mapper(int, str)

    with pytest.raises(ValueTypeError):
        m.map("foo")  # type: ignore[reportArgumentType]


def test_simple() -> None:
    m = Mapper.create_mapper(int, str)

    assert m.map(42) == "42"
    assert m.map(0) == "0"
    assert m.map(-42) == "-42"

    m = Mapper.create_mapper(str, int)
    assert m.map("42") == 42
    assert m.map("0") == 0
    assert m.map("-42") == -42

    m = Mapper.create_mapper(float, str)
    assert m.map(42.0) == "42.0"
    assert m.map(0.0) == "0.0"
    assert m.map(-42.0) == "-42.0"

    m = Mapper.create_mapper(str, float)
    assert m.map("42.0") == 42.0
    assert m.map("0.0") == 0.0
    assert m.map("-42.0") == -42.0


def test_object_mapper_not_found() -> None:
    m = Mapper.create_mapper(int, NamedTuple)

    with pytest.raises(ObjectMapperNotFoundError):
        m.map(42)


def test_list_to_set() -> None:
    m = Mapper.create_mapper(list[int], set[int])

    assert m.map([1, 2, 3]) == {1, 2, 3}
    assert m.map([]) == set()
    assert m.map([42]) == {42}
    assert m.map([1, 2, 3, 1, 2, 3]) == {1, 2, 3}


def test_list_content() -> None:
    m = Mapper.create_mapper(list[int], list[str])

    assert m.map([1, 2, 3]) == ["1", "2", "3"]
    assert m.map([]) == []
    assert m.map([42]) == ["42"]


def test_list_content_mapper_not_found() -> None:
    m = Mapper.create_mapper(list[int], list[NamedTuple])

    with pytest.raises(ObjectMapperNotFoundError):
        m.map([1, 2, 3])


def test_dict_mapper() -> None:
    m = Mapper.create_mapper(dict[int, str], dict[str, int])

    assert m.map({1: "1", 2: "2", 3: "3"}) == {"1": 1, "2": 2, "3": 3}
    assert m.map({}) == {}
    assert m.map({42: "42"}) == {"42": 42}


def test_dict_list_mapper() -> None:
    m = Mapper.create_mapper(dict[int, list[int]], dict[str, set[int]])

    assert m.map({1: [1, 2, 2, 3], 2: [4, 5, 6], 3: [7, 8, 9]}) == {
        "1": {1, 2, 3},
        "2": {4, 5, 6},
        "3": {7, 8, 9},
    }
    assert m.map({}) == {}
    assert m.map({42: [42]}) == {"42": {42}}


def test_dataclass_mapper() -> None:
    @dataclass
    class Source:
        a: int
        b: str

    @dataclass
    class Destination:
        a: str
        b: int

    m = Mapper.create_mapper(Source, Destination)

    assert m.map(Source(42, "42")) == Destination("42", 42)


def test_dataclass_deep_mapper() -> None:
    @dataclass
    class Source:
        a: int
        b: str

    @dataclass
    class Destination:
        a: str
        b: int

    @dataclass
    class SourceDeep:
        a: Source

    @dataclass
    class DestinationDeep:
        a: Destination

    m = Mapper.create_mapper(SourceDeep, DestinationDeep)

    assert m.map(SourceDeep(Source(42, "42"))) == DestinationDeep(Destination("42", 42))


def test_dataclass_missing_fields() -> None:
    @dataclass
    class Source:
        a: int

    @dataclass
    class Destination:
        a: int
        b: int

    m = Mapper.create_mapper(Source, Destination)
    with pytest.raises(MissingFieldsError):
        m.map(Source(42))


def test_dataclass_default_fields() -> None:
    @dataclass
    class Source:
        a: int

    @dataclass
    class Destination:
        a: int
        b: int = 42

    m = Mapper.create_mapper(Source, Destination)

    assert m.map(Source(42)) == Destination(42)


def test_dataclass_with_method() -> None:
    @dataclass
    class Source:
        a: int

        def foo(self) -> int:
            return self.a

    @dataclass
    class Destination:
        a: int

        def bar(self) -> int:
            return self.a

    m = Mapper.create_mapper(Source, Destination)

    assert m.map(Source(42)) == Destination(42)


def test_dataclass_property() -> None:
    @dataclass
    class Source:
        a: int

        @property
        def foo(self) -> int:
            return self.a

    @dataclass
    class Destination:
        a: int
        foo: int

    m = Mapper.create_mapper(Source, Destination)

    assert m.map(Source(42)) == Destination(42, 42)


def test_class_mapper() -> None:
    class Source:
        def __init__(self, a: int, b: str) -> None:
            self.a = a
            self.b = b

    class Destination:
        def __init__(self, a: str, b: int) -> None:
            self.a = a
            self.b = b

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, Destination):
                return False

            return self.a == other.a and self.b == other.b

    m = Mapper.create_mapper(Source, Destination)

    assert m.map(Source(42, "42")) == Destination("42", 42)


def test_class_deep() -> None:
    class Source:
        def __init__(self, a: int, b: str) -> None:
            self.a = a
            self.b = b

    class Destination:
        def __init__(self, a: str, b: int) -> None:
            self.a = a
            self.b = b

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, Destination):
                return False

            return self.a == other.a and self.b == other.b

    class SourceDeep:
        def __init__(self, a: Source) -> None:
            self.a = a

    class DestinationDeep:
        def __init__(self, a: Destination) -> None:
            self.a = a

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, DestinationDeep):
                return False

            return self.a == other.a

    m = Mapper.create_mapper(SourceDeep, DestinationDeep)

    assert m.map(SourceDeep(Source(42, "42"))) == DestinationDeep(Destination("42", 42))
