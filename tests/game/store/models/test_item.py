import pytest

from game.library.validation.errors import FieldTypeError
from game.library.validation.errors import InvalidValueError
from game.library.validation.errors import MissingFieldError
from game.library.validation.errors import UnexpectedFieldError

from game.store.models.item import Decays
from game.store.models.item import Harvestable
from game.store.models.item import HarvestProduct
from game.store.models.item import Item
from game.store.models.item import Material
from game.store.models.item import MeleeWeapon
from game.store.models.item import Wearable


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
# The Item schema
###############################################################################

def test_validate_returns_true_for_a_valid_item():
    assert Item().validate(item_json()) is True


def test_validate_raises_when_a_required_field_is_missing():
    data = item_json()
    del data['description']

    with pytest.raises(MissingFieldError) as error:
        Item().validate(data)

    assert error.value.path == 'Item.description'


def test_validate_allows_the_optional_flags_to_be_absent():
    # canPickUp, isGrowing and isEmbedded all carry defaults.
    assert Item().validate(item_json()) is True


def test_validate_raises_for_a_field_the_item_has_no_place_for():
    with pytest.raises(UnexpectedFieldError) as error:
        Item().validate(item_json(can_pick_up=True))

    assert error.value.path == 'Item.can_pick_up'


def test_validate_does_not_accept_an_integer_for_a_boolean():
    with pytest.raises(FieldTypeError) as error:
        Item().validate(item_json(canPickUp=1))

    assert error.value.path == 'Item.canPickUp'


def test_validate_accepts_a_whole_number_for_a_measurement():
    assert Item().validate(item_json(weight=2)) is True
    assert Item().validate(item_json(weight=2.5)) is True


def test_validate_accepts_seasonal_descriptions():
    assert Item().validate(item_json(seasonDescription={"summer": " It is in leaf."})) is True


def test_validate_raises_for_a_seasonal_description_that_is_not_text():
    with pytest.raises(FieldTypeError) as error:
        Item().validate(item_json(seasonDetails={"summer": 7}))

    assert error.value.path == 'Item.seasonDetails.summer'


###############################################################################
# Traits
###############################################################################

def test_validate_checks_each_trait_of_an_item():
    with pytest.raises(FieldTypeError) as error:
        Item().validate(item_json(traits={"Material": {"types": [7]}}))

    assert error.value.path == 'Material.types[0]'


def test_validate_raises_for_a_trait_that_does_not_exist():
    with pytest.raises(UnexpectedFieldError) as error:
        Item().validate(item_json(traits={"Flammable": {}}))

    assert error.value.path == 'Item.traits.Flammable'


def test_validate_accepts_an_item_with_several_traits():
    assert Item().validate(item_json(traits={
        "Material": {"types": ["wood", "oak"]},
        "Food": {"calories": 80},
    })) is True


###############################################################################
# The trait schemas
###############################################################################

def test_a_material_lists_its_types():
    assert Material().validate({"types": ["wood", "oak"]}) is True

    with pytest.raises(FieldTypeError) as error:
        Material().validate({"types": "wood"})

    assert 'expected a list of strings' in error.value.message


def test_a_melee_weapon_takes_a_damage_type_it_knows():
    assert MeleeWeapon().validate({"minDamage": 1, "maxDamage": 4, "type": "hacking"}) is True

    with pytest.raises(InvalidValueError) as error:
        MeleeWeapon().validate({"minDamage": 1, "maxDamage": 4, "type": "chopping"})

    assert error.value.path == 'MeleeWeapon.type'
    assert 'hacking' in error.value.message


def test_a_wearable_takes_a_location_it_knows():
    assert Wearable().validate({"location": "torso"}) is True

    with pytest.raises(InvalidValueError) as error:
        Wearable().validate({"location": "elbow"})

    assert error.value.path == 'Wearable.location'


def test_a_wearables_warmth_and_armor_are_optional():
    assert Wearable().validate({"location": "torso"}) is True

    with pytest.raises(FieldTypeError) as error:
        Wearable().validate({"location": "torso", "warmth": "very"})

    assert error.value.path == 'Wearable.warmth'


def test_a_decaying_item_may_name_no_decay_product():
    assert Decays().validate({"time": 100, "decayProduct": None}) is True


def test_a_decaying_item_must_say_whether_it_has_a_decay_product():
    with pytest.raises(MissingFieldError) as error:
        Decays().validate({"time": 100})

    assert error.value.path == 'Decays.decayProduct'


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
    item = Item().fromJson(item_json(traits={"Material": {"types": ["wood"]}}))

    assert item.name == 'a test item'
    assert item.weight == 1

    material = item.traits['Material']
    assert isinstance(material, Material)
    assert material.types == ['wood']


def test_fromJson_validates_nested_models_as_it_builds_them():
    # What Harvestable's own schema skipped is caught here, one level down,
    # as each product is loaded.
    with pytest.raises(FieldTypeError) as error:
        Harvestable().fromJson(harvestable_json(
            products=[{"product": "an oak stick", "amount": "several"}]))

    assert error.value.path == 'HarvestProduct.amount'


def test_toJson_output_passes_validation():
    # `PrototypeRepository.instance` builds a copy with fromJson(toJson()),
    # so anything an item writes it must also accept.
    item = Item().fromJson(item_json(traits={"Material": {"types": ["wood"]}}))

    assert Item().validate(item.toJson()) is True
