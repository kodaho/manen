import pytest

from manen.helpers import extract_integer, version


@pytest.mark.parametrize(
    "expected_str,expected_int", [("1", 1), ("0", 0), ("1234", 1234), ("01234", 1234),]
)
def test_extract_simple_integer(expected_str, expected_int):
    assert extract_integer(expected_str) == expected_int


@pytest.mark.parametrize(
    "expected_str,expected_int",
    [
        ("1 thing", 1),
        ("0 thing", 0),
        ("10 things and more", 10),
        ("10 things and more...?!#", 10),
        ("There are 1234new things", 1234),
    ],
)
def test_extract_integer_inside_text(expected_str, expected_int):
    assert extract_integer(expected_str) == expected_int


@pytest.mark.parametrize("float_str,value", [("10,123.23", 10123), ("10.1", 10)])
def test_extract_integer_from_float(float_str, value):
    assert extract_integer(float_str) == value


@pytest.mark.parametrize("ambiguous_str,value", [("1 thing and 2 others", 1)])
def test_extract_ambiguous_case(ambiguous_str, value):
    assert extract_integer(ambiguous_str) == value


@pytest.mark.parametrize(
    "version_str,version_tuple",
    [("1.2.3.4", (1, 2, 3, 4)), ("80.0.0.123", (80, 0, 0, 123)),],
)
def test_create_version(version_str, version_tuple):
    assert version(version_str) == version_tuple


@pytest.mark.parametrize(
    "invalid_version", ["version", "1,2,3", "1.2", "1.2.3.4.5"],
)
def test_invalid_version(invalid_version):
    with pytest.raises(ValueError):
        version(invalid_version)


# Add test for sorting of version
