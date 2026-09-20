import inspect

import pytest

from game.library.validation.errors import FieldTypeError
from game.library.validation.errors import InvalidValueError
from game.library.validation.errors import MissingFieldError
from game.library.validation.errors import UnexpectedFieldError

from game.store.models.base import JsonSerializable

import game.store.models.item as item_module

from game.store.models.item import TRAITS
from game.store.models.item import Container
from game.store.models.item import Craftable
from game.store.models.item import Decays
from game.store.models.item import Food
from game.store.models.item import HarvestProduct
from game.store.models.item import Harvestable
from game.store.models.item import Item
from game.store.models.item import Material
from game.store.models.item import MeleeWeapon
from game.store.models.item import RequiredMaterial
from game.store.models.item import Tool
from game.store.models.item import Wearable


###############################################################################
# Json for a minimal valid instance of each model.
#
# Each builder returns only what the model requires, so that a test can add a
# single optional field and know that field is the only thing that changed.
###############################################################################

def decays_json(**overrides):
    data = {"time": 100, "decayProduct": "rot"}
    data.update(overrides)
    return data


def harvest_product_json(**overrides):
    data = {"product": "an oak stick", "amount": 2}
    data.update(overrides)
    return data


def harvestable_json(**overrides):
    data = {
        "products": [harvest_product_json()],
        "consumed": False,
        "calories": 100,
        "time": 10,
        "action": "pick",
        "required_tools": [],
    }
    data.update(overrides)
    return data


def food_json(**overrides):
    data = {"calories": 840}
    data.update(overrides)
    return data


def material_json(**overrides):
    data = {"types": ["wood", "oak"]}
    data.update(overrides)
    return data


def tool_json(**overrides):
    data = {"type": ["axe"]}
    data.update(overrides)
    return data


def required_material_json(**overrides):
    data = {"type": "wood", "weight": 1, "length": 1, "width": 1, "height": 1}
    data.update(overrides)
    return data


def craftable_json(**overrides):
    data = {"requiredMaterials": [required_material_json()], "requiredTools": ["axe"]}
    data.update(overrides)
    return data


def melee_weapon_json(**overrides):
    data = {"minDamage": 1, "maxDamage": 4, "type": MeleeWeapon.HACKING}
    data.update(overrides)
    return data


def wearable_json(**overrides):
    data = {"location": Wearable.TORSO}
    data.update(overrides)
    return data


def container_json(**overrides):
    data = {"volume": 10, "weightLimit": 5}
    data.update(overrides)
    return data


def item_json(**overrides):
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


# Every model in the module, with the builder for its json.
MODELS = [
    (Decays, decays_json),
    (HarvestProduct, harvest_product_json),
    (Harvestable, harvestable_json),
    (Food, food_json),
    (Material, material_json),
    (Tool, tool_json),
    (RequiredMaterial, required_material_json),
    (Craftable, craftable_json),
    (MeleeWeapon, melee_weapon_json),
    (Wearable, wearable_json),
    (Container, container_json),
    (Item, item_json),
]

EVERY_MODEL = [pytest.param(model, builder, id=model.__name__) for model, builder in MODELS]


###############################################################################
# The contract every model keeps
###############################################################################

@pytest.mark.parametrize('model,build', EVERY_MODEL)
def test_validate_accepts_the_minimal_valid_data(model, build):
    assert model().validate(build()) is True


@pytest.mark.parametrize('model,build', EVERY_MODEL)
def test_validate_rejects_a_field_the_model_has_no_place_for(model, build):
    with pytest.raises(UnexpectedFieldError) as error:
        model().validate(build(notAField=1))

    assert error.value.path == '%s.notAField' % model.__name__


@pytest.mark.parametrize('model,build', EVERY_MODEL)
def test_validate_rejects_data_that_is_not_an_object(model, build):
    with pytest.raises(FieldTypeError) as error:
        model().validate(['not an object'])

    assert error.value.path == model.__name__


@pytest.mark.parametrize('model,build', EVERY_MODEL)
def test_fromJson_returns_the_model_so_it_can_be_chained(model, build):
    instance = model()

    assert instance.fromJson(build()) is instance


@pytest.mark.parametrize('model,build', EVERY_MODEL)
def test_fromJson_validates_before_it_loads_anything(model, build):
    data = build()
    required = [name for name in model.SCHEMA if model.SCHEMA[name].is_required]
    del data[required[0]]

    loaded = model()
    with pytest.raises(MissingFieldError):
        loaded.fromJson(data)

    # Nothing was written before the data was rejected.
    assert loaded.toJson() == model().toJson()


@pytest.mark.parametrize('model,build', EVERY_MODEL)
def test_toJson_output_is_valid_data_for_the_same_model(model, build):
    # `PrototypeRepository.instance` copies a model with fromJson(toJson()),
    # so whatever a model writes it must also accept.
    written = model().fromJson(build()).toJson()

    assert model().validate(written) is True


@pytest.mark.parametrize('model,build', EVERY_MODEL)
def test_json_survives_a_round_trip(model, build):
    once = model().fromJson(build())
    twice = model().fromJson(once.toJson())

    assert once.toJson() == twice.toJson()


# Every model except these hands its prototype json straight to `toJson` and
# `fromJson`.  Decays restarts its timer and Container drops its contents, so
# both are covered on their own below.  Item has no prototype form at all:
# `PrototypeRepository.instance` copies one with fromJson(toJson()).
PROTOTYPE_PASSES_THROUGH = [
    pytest.param(model, build, id=model.__name__)
    for model, build in MODELS
    if model not in (Decays, Container, Item)
]


@pytest.mark.parametrize('model,build', PROTOTYPE_PASSES_THROUGH)
def test_prototype_json_is_the_models_json(model, build):
    loaded = model().fromJson(build())

    assert loaded.toPrototypeJson() == loaded.toJson()


@pytest.mark.parametrize('model,build', PROTOTYPE_PASSES_THROUGH)
def test_fromPrototypeJson_loads_what_fromJson_loads(model, build):
    from_prototype = model().fromPrototypeJson(build())
    from_json = model().fromJson(build())

    assert from_prototype.toJson() == from_json.toJson()


@pytest.mark.parametrize('model,build', PROTOTYPE_PASSES_THROUGH)
def test_fromPrototypeJson_validates_its_data(model, build):
    data = build()
    required = [name for name in model.SCHEMA if model.SCHEMA[name].is_required]
    del data[required[0]]

    with pytest.raises(MissingFieldError):
        model().fromPrototypeJson(data)


###############################################################################
# Required and optional fields
#
# The first test pins down which fields each schema requires, so that flipping
# one is a decision rather than an accident.  The sweep after it then checks
# that each of those is enforced.
###############################################################################

EXPECTED_REQUIRED_FIELDS = {
    'Decays': ['decayProduct', 'time'],
    'HarvestProduct': ['amount', 'product'],
    'Harvestable': ['action', 'calories', 'consumed', 'products', 'required_tools', 'time'],
    'Food': ['calories'],
    'Material': ['types'],
    'Tool': ['type'],
    'RequiredMaterial': ['height', 'length', 'type', 'weight', 'width'],
    'Craftable': ['requiredMaterials', 'requiredTools'],
    'MeleeWeapon': ['maxDamage', 'minDamage', 'type'],
    'Wearable': ['location'],
    'Container': ['volume', 'weightLimit'],
    'Item': ['description', 'details', 'height', 'keywords', 'length', 'name',
             'traits', 'weight', 'width'],
}


@pytest.mark.parametrize('model,build', EVERY_MODEL)
def test_the_schema_requires_the_fields_it_is_meant_to(model, build):
    required = sorted(name for name in model.SCHEMA if model.SCHEMA[name].is_required)

    assert required == EXPECTED_REQUIRED_FIELDS[model.__name__]


REQUIRED_FIELDS = [
    pytest.param(model, build, field, id='%s-%s' % (model.__name__, field))
    for model, build in MODELS
    for field in sorted(name for name in model.SCHEMA if model.SCHEMA[name].is_required)
]


@pytest.mark.parametrize('model,build,field', REQUIRED_FIELDS)
def test_a_required_field_may_not_be_absent(model, build, field):
    data = build()
    del data[field]

    with pytest.raises(MissingFieldError) as error:
        model().validate(data)

    assert error.value.path == '%s.%s' % (model.__name__, field)


OPTIONAL_FIELDS = [
    pytest.param(model, build, field, id='%s-%s' % (model.__name__, field))
    for model, build in MODELS
    for field in sorted(name for name in model.SCHEMA if not model.SCHEMA[name].is_required)
]


@pytest.mark.parametrize('model,build,field', OPTIONAL_FIELDS)
def test_an_optional_field_may_be_absent(model, build, field):
    data = build()
    data.pop(field, None)

    assert model().validate(data) is True


###############################################################################
# Field types
#
# One row per field of every model, holding a value of the wrong type.
###############################################################################

WRONG_TYPES = [
    (Decays, decays_json, 'time', 'a hundred'),
    (Decays, decays_json, 'timeLeft', 'a hundred'),
    (Decays, decays_json, 'decayProduct', 7),

    (HarvestProduct, harvest_product_json, 'product', 7),
    (HarvestProduct, harvest_product_json, 'amount', 'two'),

    (Harvestable, harvestable_json, 'products', 'an oak stick'),
    (Harvestable, harvestable_json, 'harvestTime', 'June'),
    (Harvestable, harvestable_json, 'preDescription', 7),
    (Harvestable, harvestable_json, 'postDescription', 7),
    (Harvestable, harvestable_json, 'consumed', 1),
    (Harvestable, harvestable_json, 'replacedWith', 7),
    (Harvestable, harvestable_json, 'calories', 'a hundred'),
    (Harvestable, harvestable_json, 'time', 'ten'),
    (Harvestable, harvestable_json, 'action', 7),
    (Harvestable, harvestable_json, 'required_tools', 'axe'),
    (Harvestable, harvestable_json, 'harvested', 1),

    (Food, food_json, 'calories', '840'),

    (Material, material_json, 'types', 'wood'),

    (Tool, tool_json, 'type', 'axe'),

    (RequiredMaterial, required_material_json, 'type', 7),
    (RequiredMaterial, required_material_json, 'weight', 'one'),
    (RequiredMaterial, required_material_json, 'length', 'one'),
    (RequiredMaterial, required_material_json, 'width', 'one'),
    (RequiredMaterial, required_material_json, 'height', 'one'),

    (Craftable, craftable_json, 'requiredMaterials', 'wood'),
    (Craftable, craftable_json, 'requiredTools', 'axe'),

    (MeleeWeapon, melee_weapon_json, 'minDamage', 'one'),
    (MeleeWeapon, melee_weapon_json, 'maxDamage', 'four'),
    (MeleeWeapon, melee_weapon_json, 'type', 7),

    (Wearable, wearable_json, 'location', 7),
    (Wearable, wearable_json, 'warmth', 'very'),
    (Wearable, wearable_json, 'armor', 'lots'),

    (Container, container_json, 'volume', 'lots'),
    (Container, container_json, 'weightLimit', 'lots'),
    (Container, container_json, 'contents', 'an oak stick'),

    (Item, item_json, 'name', 7),
    (Item, item_json, 'description', 7),
    (Item, item_json, 'seasonDescription', 'in summer'),
    (Item, item_json, 'details', 7),
    (Item, item_json, 'seasonDetails', 'in summer'),
    (Item, item_json, 'keywords', 7),
    (Item, item_json, 'length', 'one'),
    (Item, item_json, 'width', 'one'),
    (Item, item_json, 'height', 'one'),
    (Item, item_json, 'weight', 'one'),
    (Item, item_json, 'canPickUp', 1),
    (Item, item_json, 'isGrowing', 1),
    (Item, item_json, 'isEmbedded', 1),
    (Item, item_json, 'traits', 'Material'),
]


@pytest.mark.parametrize('model,build,field,wrong', [
    pytest.param(model, build, field, wrong, id='%s-%s' % (model.__name__, field))
    for model, build, field, wrong in WRONG_TYPES
])
def test_a_field_must_hold_the_type_the_schema_declares(model, build, field, wrong):
    with pytest.raises(FieldTypeError) as error:
        model().validate(build(**{field: wrong}))

    assert error.value.path == '%s.%s' % (model.__name__, field)


###############################################################################
# Decays
###############################################################################

def test_decays_loads_its_fields():
    decays = Decays().fromJson(decays_json(time=100, decayProduct="rot"))

    assert decays.time == 100
    assert decays.decay_product == 'rot'


def test_decays_may_have_no_decay_product():
    decays = Decays().fromJson(decays_json(decayProduct=None))

    assert decays.decay_product is None


def test_decays_reads_a_timer_that_is_part_way_through():
    decays = Decays().fromJson(decays_json(timeLeft=40))

    assert decays.time == 100
    assert decays.time_left == 40


def test_decays_only_writes_the_timer_when_it_differs_from_the_total():
    decays = Decays()
    decays.time = 100
    decays.time_left = 100

    assert 'timeLeft' not in decays.toJson()

    decays.time_left = 40

    assert decays.toJson()['timeLeft'] == 40


def test_decays_prototype_json_always_carries_a_full_timer():
    decays = Decays()
    decays.time = 100
    decays.time_left = 40

    # A copy made from a prototype starts its decay over.
    assert decays.toPrototypeJson()['timeLeft'] == 100


def test_decays_fromPrototypeJson_starts_the_timer_at_the_full_time():
    decays = Decays().fromPrototypeJson(decays_json())

    assert decays.time == 100
    assert decays.time_left == 100


def test_decays_fromJson_leaves_the_timer_alone_when_the_data_has_none():
    # Only `fromPrototypeJson` derives the timer from `time`; plain `fromJson`
    # keeps whatever the instance already had.
    decays = Decays().fromJson(decays_json())

    assert decays.time == 100
    assert decays.time_left == 0


###############################################################################
# HarvestProduct
###############################################################################

def test_harvest_product_loads_its_fields():
    product = HarvestProduct().fromJson(harvest_product_json())

    assert product.product == 'an oak stick'
    assert product.amount == 2


def test_harvest_product_writes_its_fields():
    product = HarvestProduct().fromJson(harvest_product_json())

    assert product.toJson() == {"product": "an oak stick", "amount": 2}


def test_harvest_product_prototype_json_is_its_json():
    product = HarvestProduct().fromJson(harvest_product_json())

    assert product.toPrototypeJson() == product.toJson()


###############################################################################
# Harvestable
###############################################################################

def test_harvestable_loads_its_required_fields():
    harvestable = Harvestable().fromJson(harvestable_json())

    assert harvestable.consumed is False
    assert harvestable.calories == 100
    assert harvestable.time == 10
    assert harvestable.action == 'pick'
    assert harvestable.required_tools == []


def test_harvestable_defaults_its_optional_fields():
    harvestable = Harvestable().fromJson(harvestable_json())

    assert harvestable.harvest_time is None
    assert harvestable.pre_description is None
    assert harvestable.post_description is None
    assert harvestable.replaced_with is None
    assert harvestable.harvested is False


def test_harvestable_loads_its_optional_fields():
    harvestable = Harvestable().fromJson(harvestable_json(
        harvestTime=["June", "July"],
        preDescription="It is in fruit.",
        postDescription="It has been picked over.",
        replacedWith="a picked bush",
        harvested=True,
    ))

    assert harvestable.harvest_time == ['June', 'July']
    assert harvestable.pre_description == 'It is in fruit.'
    assert harvestable.post_description == 'It has been picked over.'
    assert harvestable.replaced_with == 'a picked bush'
    assert harvestable.harvested is True


def test_harvestable_writes_the_optional_fields_it_has_a_value_for():
    written = Harvestable().fromJson(harvestable_json(
        harvestTime=["June"],
        preDescription="It is in fruit.",
        postDescription="It has been picked over.",
        replacedWith="a picked bush",
        harvested=True,
    )).toJson()

    assert written['harvestTime'] == ['June']
    assert written['preDescription'] == 'It is in fruit.'
    assert written['postDescription'] == 'It has been picked over.'
    assert written['replacedWith'] == 'a picked bush'
    assert written['harvested'] is True


def test_harvestable_leaves_out_the_optional_fields_it_has_no_value_for():
    written = Harvestable().fromJson(harvestable_json()).toJson()

    for field in ('harvestTime', 'preDescription', 'postDescription',
                  'replacedWith', 'harvested'):
        assert field not in written


def test_harvestable_builds_its_products():
    harvestable = Harvestable().fromJson(harvestable_json(products=[
        harvest_product_json(product="an oak stick", amount=2),
        harvest_product_json(product="an oak branch", amount=1),
    ]))

    assert [product.product for product in harvestable.products] == \
        ['an oak stick', 'an oak branch']
    assert all(isinstance(product, HarvestProduct) for product in harvestable.products)


def test_harvestable_may_yield_nothing():
    harvestable = Harvestable().fromJson(harvestable_json(products=[]))

    assert harvestable.products == []


def test_harvestable_does_not_look_inside_a_product():
    # A product validates itself when `fromJson` builds it, so the parent's
    # schema only checks that each one is an object.
    assert Harvestable().validate(harvestable_json(
        products=[harvest_product_json(amount="several")])) is True


def test_harvestable_rejects_a_product_that_is_not_an_object():
    with pytest.raises(FieldTypeError) as error:
        Harvestable().validate(harvestable_json(products=["an oak stick"]))

    assert error.value.path == 'Harvestable.products[0]'
    assert 'expected HarvestProduct data' in error.value.message


def test_harvestable_validates_each_product_as_it_builds_it():
    with pytest.raises(FieldTypeError) as error:
        Harvestable().fromJson(harvestable_json(
            products=[harvest_product_json(amount="several")]))

    assert error.value.path == 'HarvestProduct.amount'


###############################################################################
# Food
###############################################################################

def test_food_loads_its_calories():
    assert Food().fromJson(food_json()).calories == 840


def test_food_writes_its_calories():
    assert Food().fromJson(food_json()).toJson() == {"calories": 840}


def test_food_calories_must_already_be_a_number():
    # `fromJson` calls int() on the value, but validation rejects anything
    # that isn't already an integer, so the conversion never does any work.
    with pytest.raises(FieldTypeError):
        Food().fromJson(food_json(calories="840"))


###############################################################################
# Material
###############################################################################

def test_material_loads_its_types():
    assert Material().fromJson(material_json()).types == ['wood', 'oak']


def test_material_may_fulfil_no_types():
    assert Material().fromJson(material_json(types=[])).types == []


def test_material_rejects_a_type_that_is_not_text():
    with pytest.raises(FieldTypeError) as error:
        Material().validate(material_json(types=["wood", 7]))

    assert error.value.path == 'Material.types[1]'


###############################################################################
# Tool
###############################################################################

def test_tool_loads_the_types_it_fulfils():
    assert Tool().fromJson(tool_json(type=["axe", "hammer"])).type == ['axe', 'hammer']


def test_tool_rejects_a_type_that_is_not_text():
    with pytest.raises(FieldTypeError) as error:
        Tool().validate(tool_json(type=[7]))

    assert error.value.path == 'Tool.type[0]'


###############################################################################
# RequiredMaterial
###############################################################################

def test_required_material_loads_its_fields():
    required = RequiredMaterial().fromJson(
        required_material_json(type="oak", weight=2.5, length=1.5, width=0.1, height=0.1))

    assert required.type == 'oak'
    assert required.weight == 2.5
    assert required.length == 1.5
    assert required.width == 0.1
    assert required.height == 0.1


@pytest.mark.parametrize('field', ['weight', 'length', 'width', 'height'])
def test_a_required_materials_measurements_may_be_whole_numbers(field):
    # Json writes 1 and 1.0 the same way.
    assert RequiredMaterial().validate(required_material_json(**{field: 1})) is True
    assert RequiredMaterial().validate(required_material_json(**{field: 1.5})) is True


###############################################################################
# Craftable
###############################################################################

def test_craftable_loads_the_tools_it_needs():
    craftable = Craftable().fromJson(craftable_json(requiredTools=["axe", "knapper"]))

    assert craftable.required_tools == ['axe', 'knapper']


def test_craftable_builds_the_materials_it_needs():
    craftable = Craftable().fromJson(craftable_json(requiredMaterials=[
        required_material_json(type="wood"),
        required_material_json(type="cordage"),
    ]))

    assert [material.type for material in craftable.required_materials] == \
        ['wood', 'cordage']
    assert all(isinstance(material, RequiredMaterial)
               for material in craftable.required_materials)


def test_craftable_may_need_nothing():
    craftable = Craftable().fromJson(
        craftable_json(requiredMaterials=[], requiredTools=[]))

    assert craftable.required_materials == []
    assert craftable.required_tools == []


def test_craftable_rejects_a_material_that_is_not_an_object():
    with pytest.raises(FieldTypeError) as error:
        Craftable().validate(craftable_json(requiredMaterials=["wood"]))

    assert error.value.path == 'Craftable.requiredMaterials[0]'


def test_craftable_validates_each_material_as_it_builds_it():
    with pytest.raises(FieldTypeError) as error:
        Craftable().fromJson(craftable_json(
            requiredMaterials=[required_material_json(weight="one")]))

    assert error.value.path == 'RequiredMaterial.weight'


###############################################################################
# MeleeWeapon
###############################################################################

def test_melee_weapon_loads_its_fields():
    weapon = MeleeWeapon().fromJson(melee_weapon_json())

    assert weapon.min_damage == 1
    assert weapon.max_damage == 4
    assert weapon.type == MeleeWeapon.HACKING


@pytest.mark.parametrize('damage_type', MeleeWeapon.TYPES + [MeleeWeapon.NONE])
def test_melee_weapon_accepts_every_damage_type_it_knows(damage_type):
    assert MeleeWeapon().validate(melee_weapon_json(type=damage_type)) is True


def test_melee_weapon_rejects_a_damage_type_it_does_not_know():
    with pytest.raises(InvalidValueError) as error:
        MeleeWeapon().validate(melee_weapon_json(type="chopping"))

    assert error.value.path == 'MeleeWeapon.type'
    assert 'hacking' in error.value.message


def test_melee_weapon_starts_with_no_damage_type():
    assert MeleeWeapon().type == MeleeWeapon.NONE


def test_melee_weapon_writes_its_fields_under_their_json_names():
    written = MeleeWeapon().fromJson(melee_weapon_json()).toJson()

    assert written == {"minDamage": 1, "maxDamage": 4, "type": "hacking"}


###############################################################################
# Wearable
###############################################################################

def test_wearable_loads_its_fields():
    wearable = Wearable().fromJson(wearable_json(warmth=3, armor=2))

    assert wearable.location == Wearable.TORSO
    assert wearable.warmth == 3
    assert wearable.armor == 2


def test_wearable_defaults_its_warmth_and_armor():
    wearable = Wearable().fromJson(wearable_json())

    assert wearable.warmth == 0
    assert wearable.armor == 0


@pytest.mark.parametrize('location', Wearable.LOCATIONS + [Wearable.NONE])
def test_wearable_accepts_every_location_it_knows(location):
    assert Wearable().validate(wearable_json(location=location)) is True


def test_wearable_rejects_a_location_it_does_not_know():
    with pytest.raises(InvalidValueError) as error:
        Wearable().validate(wearable_json(location="elbow"))

    assert error.value.path == 'Wearable.location'


def test_wearable_starts_with_no_location():
    assert Wearable().location == Wearable.NONE


def test_wearable_always_writes_its_warmth_and_armor():
    written = Wearable().fromJson(wearable_json()).toJson()

    assert written == {"location": "torso", "warmth": 0, "armor": 0}


###############################################################################
# Container
###############################################################################

def test_container_loads_its_limits():
    container = Container().fromJson(container_json(volume=10, weightLimit=5))

    assert container.volume == 10
    assert container.weight_limit == 5


def test_container_starts_empty():
    assert Container().fromJson(container_json()).contents == []


def test_container_builds_the_items_it_holds():
    container = Container().fromJson(container_json(contents=[
        item_json(name="an oak stick"),
        item_json(name="a length of cordage"),
    ]))

    assert [held.name for held in container.contents] == \
        ['an oak stick', 'a length of cordage']
    assert all(isinstance(held, Item) for held in container.contents)


def test_container_writes_what_it_holds():
    container = Container().fromJson(container_json(contents=[item_json(name="an oak stick")]))
    written = container.toJson()

    assert [held['name'] for held in written['contents']] == ['an oak stick']


def test_container_rejects_contents_that_are_not_objects():
    with pytest.raises(FieldTypeError) as error:
        Container().validate(container_json(contents=["an oak stick"]))

    assert error.value.path == 'Container.contents[0]'


def test_container_prototype_json_leaves_out_what_it_holds():
    # A container made from a prototype starts empty rather than carrying a
    # copy of whatever the prototype happened to hold.
    container = Container().fromJson(container_json(contents=[item_json()]))

    assert 'contents' not in container.toPrototypeJson()
    assert container.toPrototypeJson() == {"volume": 10, "weightLimit": 5}


def test_container_fromPrototypeJson_reads_the_limits_and_stays_empty():
    container = Container().fromPrototypeJson({"volume": 10, "weightLimit": 5})

    assert container.volume == 10
    assert container.weight_limit == 5
    assert container.contents == []


###############################################################################
# Item
###############################################################################

def test_item_loads_its_required_fields():
    item = Item().fromJson(item_json())

    assert item.name == 'a test item'
    assert item.description == 'a test item'
    assert item.details == 'An item used for testing.'
    assert item.keywords == 'test item'
    assert item.length == 1
    assert item.width == 1
    assert item.height == 1
    assert item.weight == 1


def test_item_takes_its_id_from_its_name():
    item = Item().fromJson(item_json(name="an oak stick"))

    assert item.getId() == 'an oak stick'


def test_item_defaults_its_flags():
    item = Item().fromJson(item_json())

    assert item.can_pick_up is True
    assert item.is_growing is False
    assert item.is_embedded is False


def test_item_loads_its_flags():
    item = Item().fromJson(item_json(canPickUp=False, isGrowing=True, isEmbedded=True))

    assert item.can_pick_up is False
    assert item.is_growing is True
    assert item.is_embedded is True


def test_item_always_writes_its_flags():
    written = Item().fromJson(item_json()).toJson()

    assert written['canPickUp'] is True
    assert written['isGrowing'] is False
    assert written['isEmbedded'] is False


def test_item_defaults_its_seasonal_descriptions_to_nothing():
    item = Item().fromJson(item_json())

    assert item.season_description is None
    assert item.season_details is None


def test_item_loads_its_seasonal_descriptions():
    item = Item().fromJson(item_json(
        seasonDescription={"summer": " It is in leaf."},
        seasonDetails={"winter": " Its branches are bare."},
    ))

    assert item.season_description == {"summer": " It is in leaf."}
    assert item.season_details == {"winter": " Its branches are bare."}


def test_item_writes_the_seasonal_descriptions_it_has():
    written = Item().fromJson(item_json(
        seasonDescription={"summer": " It is in leaf."},
        seasonDetails={"winter": " Its branches are bare."},
    )).toJson()

    assert written['seasonDescription'] == {"summer": " It is in leaf."}
    assert written['seasonDetails'] == {"winter": " Its branches are bare."}


def test_item_leaves_out_the_seasonal_descriptions_it_has_none_of():
    written = Item().fromJson(item_json()).toJson()

    assert 'seasonDescription' not in written
    assert 'seasonDetails' not in written


def test_item_rejects_a_seasonal_description_that_is_not_text():
    with pytest.raises(FieldTypeError) as error:
        Item().validate(item_json(seasonDetails={"summer": 7}))

    assert error.value.path == 'Item.seasonDetails.summer'


def test_item_validate_does_not_touch_the_item():
    item = Item()
    item.validate(item_json())

    assert item.name == ''
    assert item.traits == {}


###############################################################################
# An item's traits
###############################################################################

def test_item_may_have_no_traits():
    assert Item().fromJson(item_json()).traits == {}


def test_item_builds_each_of_its_traits():
    item = Item().fromJson(item_json(traits={
        "Material": material_json(),
        "Food": food_json(),
    }))

    assert sorted(item.traits) == ['Food', 'Material']
    assert isinstance(item.traits['Material'], Material)
    assert isinstance(item.traits['Food'], Food)
    assert item.traits['Material'].types == ['wood', 'oak']
    assert item.traits['Food'].calories == 840


@pytest.mark.parametrize('trait,build', [
    pytest.param(name, build, id=name)
    for name, build in [
        ('Container', container_json),
        ('Craftable', craftable_json),
        ('Decays', decays_json),
        ('Food', food_json),
        ('Harvestable', harvestable_json),
        ('Material', material_json),
        ('MeleeWeapon', melee_weapon_json),
        ('Tool', tool_json),
        ('Wearable', wearable_json),
    ]
])
def test_every_trait_can_be_composed_on_to_an_item(trait, build):
    item = Item().fromJson(item_json(traits={trait: build()}))

    assert isinstance(item.traits[trait], TRAITS[trait])


def test_item_validates_the_json_of_each_trait():
    with pytest.raises(FieldTypeError) as error:
        Item().validate(item_json(traits={"Material": material_json(types=[7])}))

    assert error.value.path == 'Material.types[0]'


def test_item_rejects_a_trait_that_does_not_exist():
    with pytest.raises(UnexpectedFieldError) as error:
        Item().validate(item_json(traits={"Flammable": {}}))

    assert error.value.path == 'Item.traits.Flammable'


def test_item_rejects_a_trait_that_names_something_other_than_a_trait():
    # `fromJson` looks a trait up in the module's globals, so validation has
    # to be the thing that keeps a name like this out.
    with pytest.raises(UnexpectedFieldError) as error:
        Item().validate(item_json(traits={"Item": item_json()}))

    assert error.value.path == 'Item.traits.Item'


def test_item_rejects_trait_json_that_is_not_an_object():
    with pytest.raises(FieldTypeError) as error:
        Item().validate(item_json(traits={"Material": ["wood"]}))

    assert error.value.path == 'Item.traits.Material'


def test_item_writes_the_json_of_each_trait():
    item = Item().fromJson(item_json(traits={"Material": material_json()}))

    assert item.toJson()['traits'] == {"Material": {"types": ["wood", "oak"]}}


def test_an_item_with_traits_survives_a_round_trip():
    once = Item().fromJson(item_json(traits={
        "Material": material_json(),
        "Harvestable": harvestable_json(),
        "MeleeWeapon": melee_weapon_json(),
    }))
    twice = Item().fromJson(once.toJson())

    assert once.toJson() == twice.toJson()


###############################################################################
# The trait registry
###############################################################################

# Models that are loaded as part of another model rather than composed on to
# an Item, and so do not belong in `TRAITS`.
NOT_TRAITS = ['HarvestProduct', 'RequiredMaterial', 'Item']


def test_every_model_in_the_module_is_either_a_trait_or_known_not_to_be():
    models = [name for name, model in inspect.getmembers(item_module, inspect.isclass)
              if issubclass(model, JsonSerializable)
              and model is not JsonSerializable
              and model.__module__ == item_module.__name__]

    assert sorted(models) == sorted(list(TRAITS) + NOT_TRAITS)


def test_each_registered_trait_is_the_class_of_that_name():
    for name in TRAITS:
        assert TRAITS[name] is getattr(item_module, name)


def test_each_registered_trait_declares_a_schema():
    for name in TRAITS:
        assert isinstance(TRAITS[name].SCHEMA, dict)
        assert TRAITS[name].SCHEMA != {}
