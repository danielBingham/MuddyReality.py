import pytest

from game.library.validation.errors import FieldTypeError
from game.library.validation.errors import InvalidValueError
from game.library.validation.errors import MissingFieldError
from game.library.validation.errors import UnexpectedFieldError

from game.store.models.character import Character
from game.store.models.character import PlayerCharacter
from game.store.models.item import Item

from game.store.models.room import DIRECTION_NAMES
from game.store.models.room import INVERT_DIRECTION
from game.store.models.room import WATER_TYPE_NAMES
from game.store.models.room import Direction
from game.store.models.room import Exit
from game.store.models.room import Room
from game.store.models.room import WaterType


###############################################################################
# Json for a minimal valid instance of each model.
###############################################################################

def exit_json(**overrides):
    data = {"direction": "north", "room_to": 2}
    data.update(overrides)
    return data


def room_json(**overrides):
    data = {
        "id": 1,
        "title": "A Rocky Beach",
        "description": "A thin strip of rocky shoreline.",
        "color": [250, 250, 180],
        "exits": {"north": exit_json()},
        "items": [],
    }
    data.update(overrides)
    return data


def item_json(**overrides):
    data = {
        "name": "a medium sized rock",
        "description": "a medium sized rock",
        "details": "A rock, about the size of two fists.",
        "keywords": "medium sized rock",
        "length": 0.2,
        "width": 0.2,
        "height": 0.2,
        "weight": 4,
        "traits": {},
    }
    data.update(overrides)
    return data


def linked_room(**overrides):
    """
    A Room with the object links Store makes once everything has loaded: the
    items it holds, and the room each of its exits leads to.

    `fromJson` leaves an id in each of those places, and `toJson` writes the id
    back out of the object, so a room only writes itself correctly once it has
    been linked up.
    """

    room = Room().fromJson(room_json(**overrides))

    room.items = [Item().fromJson(item_json())]
    for direction in room.exits:
        room.exits[direction].room_to = Room().fromJson(room_json(id=2, exits={}))

    return room


# Every model in the module, with a factory and the builder for its json.
# Exit takes the room it leads out of, so it can't just be called.
MODELS = [
    (Exit, lambda: Exit(None), exit_json),
    (Room, Room, room_json),
]

EVERY_MODEL = [
    pytest.param(model, make, build, id=model.__name__)
    for model, make, build in MODELS
]


###############################################################################
# The contract both models keep
###############################################################################

@pytest.mark.parametrize('model,make,build', EVERY_MODEL)
def test_validate_accepts_the_minimal_valid_data(model, make, build):
    assert make().validate(build()) is True


@pytest.mark.parametrize('model,make,build', EVERY_MODEL)
def test_validate_rejects_a_field_the_model_has_no_place_for(model, make, build):
    with pytest.raises(UnexpectedFieldError) as error:
        make().validate(build(notAField=1))

    assert error.value.path == '%s.notAField' % model.__name__


@pytest.mark.parametrize('model,make,build', EVERY_MODEL)
def test_validate_rejects_data_that_is_not_an_object(model, make, build):
    with pytest.raises(FieldTypeError) as error:
        make().validate(['not an object'])

    assert error.value.path == model.__name__


@pytest.mark.parametrize('model,make,build', EVERY_MODEL)
def test_fromJson_returns_the_model_so_it_can_be_chained(model, make, build):
    instance = make()

    assert instance.fromJson(build()) is instance


@pytest.mark.parametrize('model,make,build', EVERY_MODEL)
def test_fromJson_validates_before_it_loads_anything(model, make, build):
    data = build()
    required = [name for name in model.SCHEMA if model.SCHEMA[name].is_required]
    del data[required[0]]

    loaded = make()
    with pytest.raises(MissingFieldError):
        loaded.fromJson(data)

    # Nothing was written before the data was rejected.
    assert loaded.toJson() == make().toJson()


###############################################################################
# Required and optional fields
###############################################################################

EXPECTED_REQUIRED_FIELDS = {
    'Exit': ['direction', 'room_to'],
    'Room': ['color', 'description', 'exits', 'id', 'items', 'title'],
}


@pytest.mark.parametrize('model,make,build', EVERY_MODEL)
def test_the_schema_requires_the_fields_it_is_meant_to(model, make, build):
    required = sorted(name for name in model.SCHEMA if model.SCHEMA[name].is_required)

    assert required == EXPECTED_REQUIRED_FIELDS[model.__name__]


REQUIRED_FIELDS = [
    pytest.param(model, make, build, field, id='%s-%s' % (model.__name__, field))
    for model, make, build in MODELS
    for field in sorted(name for name in model.SCHEMA if model.SCHEMA[name].is_required)
]


@pytest.mark.parametrize('model,make,build,field', REQUIRED_FIELDS)
def test_a_required_field_may_not_be_absent(model, make, build, field):
    data = build()
    del data[field]

    with pytest.raises(MissingFieldError) as error:
        make().validate(data)

    assert error.value.path == '%s.%s' % (model.__name__, field)


OPTIONAL_FIELDS = [
    pytest.param(model, make, build, field, id='%s-%s' % (model.__name__, field))
    for model, make, build in MODELS
    for field in sorted(name for name in model.SCHEMA if not model.SCHEMA[name].is_required)
]


@pytest.mark.parametrize('model,make,build,field', OPTIONAL_FIELDS)
def test_an_optional_field_may_be_absent(model, make, build, field):
    data = build()
    data.pop(field, None)

    assert make().validate(data) is True


###############################################################################
# Field types
###############################################################################

WRONG_TYPES = [
    (Exit, lambda: Exit(None), exit_json, 'direction', 7),
    (Exit, lambda: Exit(None), exit_json, 'room_to', 'two'),
    (Exit, lambda: Exit(None), exit_json, 'is_door', 1),
    (Exit, lambda: Exit(None), exit_json, 'is_open', 1),
    (Exit, lambda: Exit(None), exit_json, 'name', 7),
    (Exit, lambda: Exit(None), exit_json, 'description', 7),

    (Room, Room, room_json, 'id', 'one'),
    (Room, Room, room_json, 'title', 7),
    (Room, Room, room_json, 'description', 7),
    (Room, Room, room_json, 'color', 'sandy'),
    (Room, Room, room_json, 'waterType', 7),
    (Room, Room, room_json, 'water', 'deep'),
    (Room, Room, room_json, 'waterVelocity', 'quick'),
    (Room, Room, room_json, 'exits', 'north'),
    (Room, Room, room_json, 'items', 'a medium sized rock'),
    (Room, Room, room_json, 'occupants', 'a rabbit'),
]


@pytest.mark.parametrize('model,make,build,field,wrong', [
    pytest.param(model, make, build, field, wrong, id='%s-%s' % (model.__name__, field))
    for model, make, build, field, wrong in WRONG_TYPES
])
def test_a_field_must_hold_the_type_the_schema_declares(model, make, build, field, wrong):
    with pytest.raises(FieldTypeError) as error:
        make().validate(build(**{field: wrong}))

    assert error.value.path == '%s.%s' % (model.__name__, field)


###############################################################################
# The directions and water types
###############################################################################

def test_a_direction_is_its_name():
    assert Direction.NORTH == 'north'
    assert DIRECTION_NAMES == ['north', 'east', 'south', 'west', 'up', 'down']


def test_a_water_type_is_its_name():
    assert WaterType.FRESH == 'fresh'
    assert WATER_TYPE_NAMES == ['none', 'salt', 'fresh']


@pytest.mark.parametrize('direction', DIRECTION_NAMES)
def test_every_direction_inverts_to_the_one_facing_it(direction):
    inverted = INVERT_DIRECTION[Direction(direction)]

    assert INVERT_DIRECTION[inverted] == direction


###############################################################################
# Exit
###############################################################################

@pytest.mark.parametrize('direction', DIRECTION_NAMES)
def test_an_exit_may_go_in_any_direction(direction):
    assert Exit(None).validate(exit_json(direction=direction)) is True


def test_an_exit_may_not_go_somewhere_that_is_not_a_direction():
    with pytest.raises(InvalidValueError) as error:
        Exit(None).validate(exit_json(direction="widdershins"))

    assert error.value.path == 'Exit.direction'
    assert "'north'" in error.value.message


def test_an_exit_starts_in_the_room_it_is_built_with():
    room = Room()
    exit = Exit(room)

    assert exit.room_from is room
    assert exit.room_to is None
    assert exit.exit_to is None


def test_an_exit_starts_as_an_open_way_north():
    exit = Exit(None)

    assert exit.direction == Direction.NORTH
    assert exit.is_door is False
    assert exit.is_open is True
    assert exit.name == ''
    assert exit.description == ''


def test_an_exit_loads_its_required_fields():
    exit = Exit(None).fromJson(exit_json(direction="east", room_to=2))

    assert exit.direction == 'east'
    assert exit.room_to == 2


def test_an_exit_defaults_the_fields_its_data_leaves_out():
    exit = Exit(None).fromJson(exit_json())

    assert exit.is_door is False
    assert exit.is_open is True
    assert exit.name == ''
    assert exit.description == ''


def test_an_exit_loads_the_door_it_is():
    exit = Exit(None).fromJson(exit_json(is_door=True, is_open=False))

    assert exit.is_door is True
    assert exit.is_open is False


def test_an_exit_loads_what_lies_through_it():
    exit = Exit(None).fromJson(exit_json(
        name="old growth forest",
        description="A dark, dense old-growth forest."))

    assert exit.name == 'old growth forest'
    assert exit.description == 'A dark, dense old-growth forest.'


def linked_exit(**overrides):
    """
    An Exit with the object link Store makes once every room has loaded.

    `fromJson` leaves the destination room's id in `room_to` and `toJson`
    reads the id back out of the Room, so an exit only writes itself
    correctly once it has been linked up.
    """

    exit = Exit(None).fromJson(exit_json(**overrides))
    exit.room_to = Room().fromJson(room_json(id=2, exits={}))
    return exit


def test_an_exit_writes_the_door_it_is_and_the_way_it_goes():
    written = linked_exit(direction="east").toJson()

    assert written['direction'] == 'east'
    assert written['is_door'] is False
    assert written['is_open'] is True


def test_an_exit_writes_what_lies_through_it_when_it_has_been_told():
    written = linked_exit(
        name="old growth forest",
        description="A dark, dense old-growth forest.").toJson()

    assert written['name'] == 'old growth forest'
    assert written['description'] == 'A dark, dense old-growth forest.'


def test_an_exit_leaves_out_what_lies_through_it_when_it_has_not_been_told():
    written = linked_exit().toJson()

    assert 'name' not in written
    assert 'description' not in written


def test_an_exit_writes_the_id_of_the_room_it_leads_to():
    assert linked_exit().toJson()['room_to'] == 2


def test_an_exit_with_nowhere_to_go_writes_no_destination():
    # An exit is only complete once Store has linked it to its room, so this
    # is not data an exit could be loaded from.
    written = Exit(None).toJson()

    assert 'room_to' not in written
    with pytest.raises(MissingFieldError):
        Exit(None).validate(written)


def test_an_exit_survives_a_round_trip_once_it_has_been_linked():
    once = linked_exit(
        is_door=True, is_open=False, name="a door", description="A stout door.")

    twice = Exit(None).fromJson(once.toJson())
    twice.room_to = once.room_to

    assert once.toJson() == twice.toJson()


###############################################################################
# Room
###############################################################################

def test_a_room_starts_empty_and_dry():
    room = Room()

    assert room.title == ''
    assert room.description == ''
    assert room.color == []
    assert room.water_type == WaterType.NONE
    assert room.water == 0
    assert room.water_velocity == 0
    assert room.exits == {}
    assert room.items == []
    assert room.occupants == []


def test_a_room_loads_its_required_fields():
    room = Room().fromJson(room_json())

    assert room.getId() == 1
    assert room.title == 'A Rocky Beach'
    assert room.description == 'A thin strip of rocky shoreline.'
    assert room.color == [250, 250, 180]


def test_a_room_takes_its_id_from_its_data():
    assert Room().fromJson(room_json(id=7)).getId() == 7


def test_a_room_rejects_a_colour_that_is_not_made_of_numbers():
    with pytest.raises(FieldTypeError) as error:
        Room().validate(room_json(color=[250, "blue", 180]))

    assert error.value.path == 'Room.color[1]'


###############################################################################
# A room's water
###############################################################################

def test_a_room_is_dry_when_its_data_says_nothing_about_water():
    room = Room().fromJson(room_json())

    assert room.water_type == WaterType.NONE
    assert room.water == 0
    assert room.water_velocity == 0


def test_a_room_loads_the_water_it_has():
    room = Room().fromJson(room_json(waterType="fresh", water=1.5, waterVelocity=0.5))

    assert room.water_type == 'fresh'
    assert room.water == 1.5
    assert room.water_velocity == 0.5


@pytest.mark.parametrize('water_type', WATER_TYPE_NAMES)
def test_a_room_may_hold_any_kind_of_water(water_type):
    assert Room().validate(
        room_json(waterType=water_type, water=1, waterVelocity=0)) is True


def test_a_room_may_not_hold_water_of_a_kind_that_does_not_exist():
    with pytest.raises(InvalidValueError) as error:
        Room().validate(room_json(waterType="brackish", water=1, waterVelocity=0))

    assert error.value.path == 'Room.waterType'


@pytest.mark.parametrize('field', ['water', 'waterVelocity'])
def test_a_room_that_names_a_water_type_must_describe_the_water(field):
    data = room_json(waterType="fresh", water=1, waterVelocity=0)
    del data[field]

    with pytest.raises(MissingFieldError) as error:
        Room().validate(data)

    assert error.value.path == 'Room.%s' % field


def test_a_room_writes_the_water_it_has():
    room = linked_room(waterType="fresh", water=1.5, waterVelocity=0.5)
    written = room.toJson()

    assert written['waterType'] == 'fresh'
    assert written['water'] == 1.5
    assert written['waterVelocity'] == 0.5


def test_a_dry_room_says_nothing_about_water():
    written = linked_room().toJson()

    assert 'waterType' not in written
    assert 'water' not in written
    assert 'waterVelocity' not in written


###############################################################################
# A room's exits
###############################################################################

def test_a_room_may_have_no_exits():
    room = Room().fromJson(room_json(exits={}))

    assert room.exits == {}


def test_a_room_builds_an_exit_for_each_way_out():
    room = Room().fromJson(room_json(exits={
        "north": exit_json(direction="north", room_to=2),
        "east": exit_json(direction="east", room_to=4),
    }))

    assert sorted(room.exits) == ['east', 'north']
    assert all(isinstance(way, Exit) for way in room.exits.values())
    assert room.exits['east'].room_to == 4


def test_an_exit_knows_the_room_it_leads_out_of():
    room = Room().fromJson(room_json())

    assert room.exits['north'].room_from is room


def test_a_room_may_only_key_an_exit_by_a_direction():
    with pytest.raises(InvalidValueError) as error:
        Room().validate(room_json(exits={"nrth": exit_json()}))

    assert error.value.path == 'Room.exits.nrth'
    assert "'north'" in error.value.message


def test_a_room_rejects_an_exit_that_is_not_an_object():
    with pytest.raises(FieldTypeError) as error:
        Room().validate(room_json(exits={"north": "the next room"}))

    assert error.value.path == 'Room.exits.north'
    assert 'expected Exit data' in error.value.message


def test_a_room_does_not_look_inside_an_exit():
    # An exit validates itself when `fromJson` builds it, so the room's own
    # schema only checks that each one is an object.
    assert Room().validate(room_json(exits={"north": {"direction": 7}})) is True


def test_a_room_validates_each_exit_as_it_builds_it():
    with pytest.raises(FieldTypeError) as error:
        Room().fromJson(room_json(exits={"north": exit_json(room_to="two")}))

    assert error.value.path == 'Exit.room_to'


def test_a_room_writes_each_of_its_exits():
    room = linked_room(exits={
        "north": exit_json(direction="north", room_to=2),
        "east": exit_json(direction="east", room_to=4),
    })
    written = room.toJson()

    assert sorted(written['exits']) == ['east', 'north']
    assert written['exits']['north']['direction'] == 'north'


###############################################################################
# What a room holds
###############################################################################

def test_a_room_loads_the_ids_of_the_items_it_holds():
    # Store swaps these for the Items themselves once they have all loaded.
    room = Room().fromJson(room_json(items=["a medium sized rock", "a small piece of chert"]))

    assert room.items == ['a medium sized rock', 'a small piece of chert']


def test_a_room_writes_the_name_of_each_item_it_holds():
    room = linked_room()

    assert room.toJson()['items'] == ['a medium sized rock']


def test_a_room_has_no_occupants_when_its_data_says_nothing_about_them():
    assert Room().fromJson(room_json()).occupants == []


def test_a_room_loads_the_ids_of_the_occupants_it_has():
    room = Room().fromJson(room_json(occupants=["a rabbit"]))

    assert room.occupants == ['a rabbit']


def test_a_room_writes_the_id_of_each_occupant():
    room = linked_room()
    rabbit = Character().setId('a rabbit')
    room.occupants = [rabbit]

    assert room.toJson()['occupants'] == ['a rabbit']


def test_a_room_does_not_write_the_players_standing_in_it():
    # Where a player character is gets stored on the character, so that they
    # come back to it when they log in rather than being left in the room.
    room = linked_room()
    room.occupants = [Character().setId('a rabbit'),
                      PlayerCharacter().setId('gird')]

    assert room.toJson()['occupants'] == ['a rabbit']


###############################################################################
# Round trip
###############################################################################

def test_a_room_survives_a_round_trip_once_it_has_been_linked():
    once = linked_room(waterType="fresh", water=1.5, waterVelocity=0.5)
    once.occupants = [Character().setId('a rabbit')]

    twice = Room().fromJson(once.toJson())
    twice.items = once.items
    twice.occupants = once.occupants
    for direction in twice.exits:
        twice.exits[direction].room_to = once.exits[direction].room_to

    assert once.toJson() == twice.toJson()


def test_what_a_room_writes_is_valid_room_data():
    written = linked_room(waterType="fresh", water=1.5, waterVelocity=0.5).toJson()

    assert Room().validate(written) is True
