from typing import NamedTuple
import pytest
from automappy.exceptions import ObjectMapperNotFoundError, ValueTypeError
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
