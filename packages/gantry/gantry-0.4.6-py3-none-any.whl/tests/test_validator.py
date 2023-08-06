import pytest

from gantry.exceptions import GantryLoggingDataTypeError
from gantry.validators import validate_logged_field_datatype


def test_validator_list_not_primitive():
    # does not accept arbitrary malformed
    with pytest.raises(GantryLoggingDataTypeError):
        validate_logged_field_datatype(
            {"some-invalid-input": ["invalid", {"invalid": True}], "some-input": True}
        )


def test_validator_list_3d():
    # Does not accept 3 dim array
    with pytest.raises(GantryLoggingDataTypeError):
        validate_logged_field_datatype([[[1]], [[2]], [[3]]])


def test_validator_list_2d():
    # Does not raise for 2 dim array
    validate_logged_field_datatype([[1], [2], [3]])


def test_validator_list_1d():
    # Does not raise for 1 dim array
    validate_logged_field_datatype([1])


def test_validator_nested_dict_3():
    # Does not raise for 3 nested dicts
    validate_logged_field_datatype({"a": {"b": {"c": "d"}}})


def test_validator_nested_dict_2():
    # Does not raise for 2 nested dict
    validate_logged_field_datatype({"a": {"b": "c"}})


def test_validator_nested_list():
    # Does not raise for valid list inside dict
    validate_logged_field_datatype({"a": {"b": ["c"]}})


def test_validator_primitives():
    # Does not raise for primitives
    try:
        validate_logged_field_datatype("str")
        validate_logged_field_datatype(1)
        validate_logged_field_datatype(1.1)
        validate_logged_field_datatype(True)
        validate_logged_field_datatype(None)
    except GantryLoggingDataTypeError:
        pytest.fail("Raised GantryLoggingDataTypeError for a primitive")
