import pytest

from game.store.models.item import Decays
from game.store.models.item import Harvestable
from game.store.models.item import HarvestProduct
from game.store.models.item import Item
from game.store.models.item import Material
from game.store.models.item import MeleeWeapon
from game.store.models.item import Wearable

from game.library.validation.errors import FieldTypeError
from game.library.validation.errors import InvalidValueError
from game.library.validation.errors import MissingFieldError
from game.library.validation.errors import UnexpectedFieldError
from game.library.validation.errors import ValidationError
from game.library.validation.validator import Validator


def item_json(**overrides):
    """
    Build the json for a minimal valid Item, with any of its fields replaced
    by `overrides`.
    """

    data = {
        "name": "a test item",
        "description": "a test item",
        "details": "An item used for testing.",
        "keywords": "test item",
        "length": 1,
        "width": 1,
        "height": 1,
        "weight": 1,
        "traits": {},
    }
    data.update(overrides)
    return data


def harvestable_json(**overrides):
    """
    Build the json for a minimal valid Harvestable, with any of its fields
    replaced by `overrides`.
    """

    data = {
        "products": [{"product": "an oak stick", "amount": 2}],
        "consumed": False,
        "calories": 10,
        "time": 10,
        "action": "pick",
        "required_tools": [],
    }
    data.update(overrides)
    return data


###############################################################################
# The Validator builder
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
# Walking a model's schema
###############################################################################

def test_validate_returns_true_for_valid_data():
    assert Material().validate({"types": ["wood", "oak"]}) is True


def test_validate_raises_when_a_required_field_is_missing():
    with pytest.raises(MissingFieldError) as error:
        Material().validate({})

    assert error.value.path == 'Material.types'


def test_validate_allows_an_optional_field_to_be_absent():
    assert Wearable().validate({"location": "torso"}) is True


def test_validate_checks_the_type_of_an_optional_field_that_is_present():
    with pytest.raises(FieldTypeError) as error:
        Wearable().validate({"location": "torso", "warmth": "very"})

    assert error.value.path == 'Wearable.warmth'


def test_validate_raises_for_an_unexpected_field():
    with pytest.raises(UnexpectedFieldError) as error:
        Material().validate({"types": ["wood"], "colour": "brown"})

    assert error.value.path == 'Material.colour'


###############################################################################
# isType
###############################################################################

def test_validate_raises_for_the_wrong_type():
    with pytest.raises(FieldTypeError) as error:
        Material().validate({"types": "wood"})

    assert error.value.path == 'Material.types'
    assert 'expected a list of strings' in error.value.message


def test_validate_checks_the_type_of_each_element_of_a_list():
    with pytest.raises(FieldTypeError) as error:
        Material().validate({"types": ["wood", 7]})

    assert error.value.path == 'Material.types[1]'


def test_validate_does_not_accept_a_boolean_for_an_integer():
    # Booleans are a subclass of int in python, but json keeps them apart.
    with pytest.raises(FieldTypeError):
        Wearable().validate({"location": "torso", "warmth": True})


def test_validate_does_not_accept_an_integer_for_a_boolean():
    with pytest.raises(FieldTypeError) as error:
        Item().validate(item_json(canPickUp=1))

    assert error.value.path == 'Item.canPickUp'


def test_validate_accepts_a_boolean_for_a_boolean():
    assert Item().validate(item_json(canPickUp=False)) is True


def test_validate_accepts_a_whole_number_for_a_float():
    # Json writes 2 and 2.0 the same way.
    assert Item().validate(item_json(weight=2)) is True
    assert Item().validate(item_json(weight=2.5)) is True


def test_validate_accepts_null_for_a_nullable_field():
    assert Decays().validate({"time": 100, "decayProduct": None}) is True


def test_validate_raises_for_null_in_a_field_that_is_not_nullable():
    with pytest.raises(FieldTypeError):
        Material().validate({"types": None})


def test_isType_resolves_a_type_deferred_behind_a_function():
    validator = Validator().isType(lambda: list[Item])

    assert validator.validate([item_json()], 'contents') is True

    with pytest.raises(FieldTypeError) as error:
        validator.validate(['not an item'], 'contents')

    assert error.value.path == 'contents[0]'


###############################################################################
# isOneOf
###############################################################################

def test_validate_accepts_an_allowed_value():
    assert MeleeWeapon().validate({"minDamage": 1, "maxDamage": 4, "type": "hacking"}) is True


def test_validate_raises_for_a_value_outside_the_allowed_set():
    with pytest.raises(InvalidValueError) as error:
        MeleeWeapon().validate({"minDamage": 1, "maxDamage": 4, "type": "chopping"})

    assert error.value.path == 'MeleeWeapon.type'
    assert 'hacking' in error.value.message


###############################################################################
# Nested models
#
# A nested model validates itself when its parent's `fromJson` builds it, so
# the parent checks only that the value is the object a model loads from.
###############################################################################

def test_validate_accepts_a_nested_model_as_an_object():
    assert Harvestable().validate(harvestable_json()) is True


def test_validate_does_not_look_inside_a_nested_model():
    # `amount` is wrong, but that is HarvestProduct's business, not
    # Harvestable's.
    assert Harvestable().validate(harvestable_json(
        products=[{"product": "an oak stick", "amount": "several"}])) is True


def test_validate_raises_when_a_nested_model_is_not_an_object():
    with pytest.raises(FieldTypeError) as error:
        Harvestable().validate(harvestable_json(products=["an oak stick"]))

    assert error.value.path == 'Harvestable.products[0]'
    assert 'expected HarvestProduct data' in error.value.message


def test_a_nested_model_validates_itself():
    with pytest.raises(FieldTypeError) as error:
        HarvestProduct().validate({"product": "an oak stick", "amount": "several"})

    assert error.value.path == 'HarvestProduct.amount'


def test_fromJson_validates_nested_models_as_it_builds_them():
    # What the parent skipped is caught here, one level down, when
    # Harvestable.fromJson loads each product.
    with pytest.raises(FieldTypeError) as error:
        Harvestable().fromJson(harvestable_json(
            products=[{"product": "an oak stick", "amount": "several"}]))

    assert error.value.path == 'HarvestProduct.amount'


###############################################################################
# Traits
###############################################################################

def test_validate_descends_into_the_traits_of_an_item():
    with pytest.raises(FieldTypeError) as error:
        Item().validate(item_json(traits={"Material": {"types": [7]}}))

    assert error.value.path == 'Material.types[0]'


def test_validate_raises_for_a_trait_that_does_not_exist():
    with pytest.raises(UnexpectedFieldError) as error:
        Item().validate(item_json(traits={"Flammable": {}}))

    assert error.value.path == 'Item.traits.Flammable'


###############################################################################
# fromJson
###############################################################################

def test_fromJson_validates_before_loading():
    data = item_json()
    del data['name']

    item = Item()
    with pytest.raises(MissingFieldError):
        item.fromJson(data)

    # The item is left untouched by the failed load.
    assert item.name == ''
    assert item.description == ''


def test_fromJson_loads_valid_data():
    item = Item().fromJson(item_json())

    assert item.name == 'a test item'
    assert item.weight == 1
