import pytest

from game.library.validation.check_type import checkType
from game.library.validation.check_type import describeType
from game.library.validation.check_type import describeValue
from game.library.validation.check_type import isUnion
from game.library.validation.errors import FieldTypeError, ValidationError
from game.library.validation.validator import Validator


class Part:
    """
    A stand in model for exercising the nested model case.

    `checkType` only asks whether a type has a `SCHEMA`, so the tests here
    don't need a real model and shouldn't depend on one.
    """

    SCHEMA = {
        "label": Validator().isType(str).isRequired(),
    }


def check(value, field_type, path='field') -> ValidationError | None:
    """Run `checkType` and hand back the error it raised, if any."""

    try:
        checkType(value, field_type, path)
    except FieldTypeError as error:
        return error
    return None


###############################################################################
# Scalars
###############################################################################

def test_a_string_matches_str():
    assert check('a string', str) is None


def test_a_number_does_not_match_str():
    assert check(7, str) is not None


def test_an_integer_matches_int():
    assert check(7, int) is None


def test_a_boolean_does_not_match_int():
    # Booleans are a subclass of int in python, but json keeps them apart.
    assert check(True, int) is not None


def test_an_integer_does_not_match_bool():
    assert check(1, bool) is not None


def test_a_boolean_matches_bool():
    assert check(True, bool) is None
    assert check(False, bool) is None


def test_a_whole_number_matches_float():
    # Json writes 2 and 2.0 the same way, so either is a valid number.
    assert check(2, float) is None
    assert check(2.5, float) is None


def test_a_boolean_does_not_match_float():
    assert check(True, float) is not None


###############################################################################
# Null and unions
###############################################################################

def test_null_matches_a_nullable_type():
    assert check(None, str | None) is None


def test_a_string_matches_a_nullable_string():
    assert check('a string', str | None) is None


def test_null_does_not_match_a_type_that_is_not_nullable():
    assert check(None, str) is not None


def test_a_union_reports_itself_as_a_whole_when_nothing_matches():
    error = check(7, str | None)

    assert error is not None
    assert 'expected a string or null' in error.message


def test_isUnion_recognises_a_union():
    assert isUnion(str | None) is True
    assert isUnion(str) is False


###############################################################################
# Lists
###############################################################################

def test_a_list_of_strings_matches():
    assert check(['one', 'two'], list[str]) is None


def test_a_string_does_not_match_a_list():
    assert check('one', list[str]) is not None


def test_each_element_of_a_list_is_checked():
    error = check(['one', 7], list[str], 'Model.field')

    assert error is not None
    assert error.path == 'Model.field[1]'


def test_a_list_with_no_element_type_only_checks_that_it_is_a_list():
    assert check(['one', 7], list) is None


def test_an_empty_list_matches():
    assert check([], list[str]) is None


###############################################################################
# Objects
###############################################################################

def test_an_object_of_strings_matches():
    assert check({"summer": "warm"}, dict[str, str]) is None


def test_each_value_of_an_object_is_checked():
    error = check({"summer": 7}, dict[str, str], 'Model.field')

    assert error is not None
    assert error.path == 'Model.field.summer'


def test_a_list_does_not_match_an_object():
    assert check(['summer'], dict[str, str]) is not None


###############################################################################
# Nested models
#
# A nested model validates itself when its parent's `fromJson` builds it, so
# `checkType` confirms the shape and stops there.
###############################################################################

def test_a_nested_model_matches_any_object():
    assert check({"label": "a part"}, Part) is None


def test_a_nested_model_is_not_looked_inside():
    # `label` is wrong, but that is Part's business.
    assert check({"label": 7}, Part) is None


def test_a_nested_model_must_still_be_an_object():
    error = check('a part', Part, 'Assembly.parts[0]')

    assert error is not None
    assert error.path == 'Assembly.parts[0]'
    assert 'expected Part data' in error.message


def test_a_list_of_nested_models_checks_each_element():
    error = check([{"label": "a part"}, 'a part'], list[Part], 'Assembly.parts')

    assert error is not None
    assert error.path == 'Assembly.parts[1]'


###############################################################################
# Describing types and values
###############################################################################

@pytest.mark.parametrize('field_type,description', [
    (str, 'a string'),
    (int, 'an integer'),
    (float, 'a number'),
    (bool, 'a boolean'),
    (None, 'null'),
    (str | None, 'a string or null'),
    (list[str], 'a list of strings'),
    (dict[str, str], 'an object of strings'),
    (list[Part], 'a list of Part data'),
    (Part, 'Part data'),
])
def test_describeType(field_type, description):
    assert describeType(field_type) == description


@pytest.mark.parametrize('value,description', [
    (None, 'null'),
    (True, "a boolean (True)"),
    (7, "an integer (7)"),
    (2.5, "a number (2.5)"),
    ('a string', "a string ('a string')"),
    ([], "a list ([])"),
    ({}, "an object ({})"),
])
def test_describeValue(value, description):
    assert describeValue(value) == description


def test_describeValue_truncates_a_long_value():
    described = describeValue('a very long string ' * 10)

    assert described.endswith("...)")
    assert len(described) < 60
