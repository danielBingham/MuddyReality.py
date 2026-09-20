import pytest

from game.library.validation.errors import FieldTypeError
from game.library.validation.errors import InvalidValueError
from game.library.validation.errors import MissingFieldError
from game.library.validation.errors import UnexpectedFieldError
from game.library.validation.errors import ValidationError
from game.library.validation.validator import Validator
from game.library.validation.validator import resolveType
from game.library.validation.validator import validateModel


class Widget:
    """
    A stand in model for exercising the validator.

    The validator only asks a model for its `SCHEMA` and its name, so the
    tests here don't need a real model and shouldn't depend on one.
    """

    SCHEMA = {
        "name": Validator().isType(str).isRequired(),
        "count": Validator().isType(int),
    }


###############################################################################
# Building a validator
###############################################################################

def test_builder_methods_return_the_validator_so_they_chain():
    validator = Validator()

    assert validator.isType(int) is validator
    assert validator.isRequired() is validator
    assert validator.isOneOf([1, 2]) is validator
    assert validator.check(lambda value, path: None) is validator


def test_a_new_validator_is_optional_and_checks_nothing():
    validator = Validator()

    assert validator.is_required is False
    assert validator.checks == []
    assert validator.validate('anything at all') is True


def test_isRequired_sets_the_flag_rather_than_adding_a_check():
    validator = Validator().isRequired()

    assert validator.is_required is True
    assert validator.checks == []


def test_each_builder_method_adds_one_check():
    validator = Validator().isType(int).isOneOf([1, 2]).isRequired()

    assert len(validator.checks) == 2


###############################################################################
# Running the checks
###############################################################################

def test_checks_run_in_the_order_they_were_added():
    ran = []

    validator = (Validator()
                 .check(lambda value, path: ran.append('first'))
                 .check(lambda value, path: ran.append('second')))
    validator.validate(1)

    assert ran == ['first', 'second']


def test_validate_stops_at_the_first_check_that_fails():
    ran = []

    def fails(value, path):
        raise ValidationError(path, 'no good.')

    validator = Validator().check(fails).check(lambda value, path: ran.append('second'))

    with pytest.raises(ValidationError):
        validator.validate(1)

    assert ran == []


def test_a_custom_check_can_be_added_without_a_builder_method():
    def isEven(value, path):
        if value % 2 != 0:
            raise InvalidValueError(path, 'must be even, found %r.' % value)

    validator = Validator().isType(int).check(isEven)

    assert validator.validate(4) is True
    with pytest.raises(InvalidValueError):
        validator.validate(5)


def test_validate_reports_the_path_it_was_given():
    with pytest.raises(FieldTypeError) as error:
        Validator().isType(int).validate('two', 'Somewhere.field')

    assert error.value.path == 'Somewhere.field'


###############################################################################
# isOneOf
###############################################################################

def test_isOneOf_accepts_an_allowed_value():
    assert Validator().isOneOf(['red', 'green']).validate('red') is True


def test_isOneOf_raises_for_a_value_outside_the_allowed_set():
    with pytest.raises(InvalidValueError) as error:
        Validator().isOneOf(['red', 'green']).validate('blue', 'Paint.colour')

    assert error.value.path == 'Paint.colour'
    assert "'red', 'green'" in error.value.message


###############################################################################
# resolveType
###############################################################################

def test_resolveType_returns_a_type_unchanged():
    assert resolveType(int) is int
    assert resolveType(list[str]) == list[str]


def test_resolveType_calls_a_function_to_get_the_type():
    assert resolveType(lambda: list[Widget]) == list[Widget]


###############################################################################
# Walking a model's schema
###############################################################################

def test_validateModel_returns_true_for_valid_data():
    assert validateModel(Widget, {"name": "a widget", "count": 2}) is True


def test_validateModel_raises_when_a_required_field_is_missing():
    with pytest.raises(MissingFieldError) as error:
        validateModel(Widget, {"count": 2})

    assert error.value.path == 'Widget.name'


def test_validateModel_allows_an_optional_field_to_be_absent():
    assert validateModel(Widget, {"name": "a widget"}) is True


def test_validateModel_checks_an_optional_field_that_is_present():
    with pytest.raises(FieldTypeError) as error:
        validateModel(Widget, {"name": "a widget", "count": "two"})

    assert error.value.path == 'Widget.count'


def test_validateModel_raises_for_an_unexpected_field():
    with pytest.raises(UnexpectedFieldError) as error:
        validateModel(Widget, {"name": "a widget", "colour": "red"})

    assert error.value.path == 'Widget.colour'


def test_validateModel_raises_when_the_data_is_not_an_object():
    with pytest.raises(FieldTypeError) as error:
        validateModel(Widget, ["a widget"])

    assert error.value.path == 'Widget'
    assert 'expected Widget data' in error.value.message


def test_validateModel_roots_the_path_at_the_model_name():
    with pytest.raises(FieldTypeError) as error:
        validateModel(Widget, {"name": 7})

    assert error.value.path == 'Widget.name'


def test_validateModel_takes_a_path_for_data_inside_something_larger():
    with pytest.raises(FieldTypeError) as error:
        validateModel(Widget, {"name": 7}, 'Crate.contents[0]')

    assert error.value.path == 'Crate.contents[0].name'
