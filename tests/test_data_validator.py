import argparse
import json
import os

import pytest

import data_validator

from game.library.validation.errors import MissingFieldError
from game.library.validation.errors import UnexpectedFieldError

from game.store.loading import LoadError
from game.store.models.item import Item
from game.store.models.world import World
from game.store.store import Store


###############################################################################
# A data library to validate.
#
# Each builder makes the json for one valid file, with any of its fields
# replaced by `overrides`, so that a test can say what it is breaking and
# nothing else.
###############################################################################

def item_json(**overrides):
    data = {
        "name": "a rock",
        "description": "a rock",
        "details": "A rock, of the sort you might throw.",
        "keywords": "rock",
        "length": 0.1,
        "width": 0.1,
        "height": 0.1,
        "weight": 1,
        "traits": {},
    }
    data.update(overrides)
    return data


def room_json(**overrides):
    data = {
        "id": 1,
        "title": "A Test Room",
        "description": "A room used for testing.",
        "color": [250, 250, 180],
        "exits": {},
        "items": [],
    }
    data.update(overrides)
    return data


def npc_json(**overrides):
    data = {
        "name": "a rabbit",
        "description": "a small fluffy rodent with long ears",
        "details": "A small fluffy rodent with long ears.",
        "sex": "male",
        "bodyType": "quadrapedal",
    }
    data.update(overrides)
    return data


def character_json(**overrides):
    data = {
        "name": "gird",
        "description": "",
        "details": "",
        "sex": "male",
        "position": "standing",
        "speed": "walking",
        "attributes": {
            "strength": 10, "maxStrength": 10,
            "stamina": 10, "maxStamina": 10,
            "constitution": 10, "maxConstitution": 10,
        },
        "reserves": {
            "calories": 2400, "maxCalories": 2400,
            "thirst": 4000, "maxThirst": 4000,
            "sleep": 16, "maxSleep": 16,
            "wind": 30, "maxWind": 30,
            "energy": 10000, "maxEnergy": 10000,
        },
        "bodyType": "bipedal",
        "body": {"wounds": {}, "worn": {}},
        "inventory": [],
        "room": 1,
    }
    data.update(overrides)
    return data


def account_json(**overrides):
    data = {
        "name": "tester",
        "password_hash": "not-really-a-hash",
        "characters": ["gird"],
    }
    data.update(overrides)
    return data


def world_json(**overrides):
    data = {
        "name": "base",
        "width": 1,
        "roomWidth": 100,
        "rooms": [[1]],
    }
    data.update(overrides)
    return data


def biome_json(**overrides):
    data = {
        "name": "plain",
        "color": [20, 230, 0],
        "titles": ["A Plain"],
        "descriptions": {
            "initial": ["A wide open plain."],
            "flavor": ["The grass is tall."],
        },
        "trees": [],
        "treeDensity": 0,
        "shrubs": [],
        "shrubDensity": 0,
        "herbs": [],
        "herbDensity": 0,
        "debris": [],
        "debrisDensity": 0,
        "water": "none",
        "succession": None,
        "successionTime": 0,
        "disruptions": {
            "fire": {"chance": 0.01, "spread": 50, "biome": "plain"},
        },
    }
    data.update(overrides)
    return data


def write(directory, *path, data=None, text=None):
    """
    Write a data file, making the directories above it.  Takes `data` to be
    written as json, or `text` to be written as it is.
    """

    file_path = os.path.join(directory, *path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    file = open(file_path, 'w')
    try:
        file.write(text if text is not None else json.dumps(data))
    finally:
        file.close()

    return file_path


@pytest.fixture
def library(tmp_path):
    """
    A small data library that validates cleanly: one of each of the things
    the server loads, and one world of two rooms that lead to each other.
    """

    directory = str(tmp_path / 'data')

    write(directory, 'items', 'rock.json', data=item_json())
    write(directory, 'npcs', 'rabbit.json', data=npc_json())
    write(directory, 'characters', 'gird.json', data=character_json())
    write(directory, 'accounts', 'tester.json', data=account_json())
    write(directory, 'biomes', 'plain.json', data=biome_json())
    write(directory, 'worlds', 'base', 'world.json', data=world_json())
    # The rooms deliberately hold no items, so that a test breaking the item
    # sees the one problem it made rather than that one and every room that
    # went looking for it.
    write(directory, 'worlds', 'base', 'rooms', '1.json', data=room_json(
        exits={"east": {"direction": "east", "room_to": 2}}))
    write(directory, 'worlds', 'base', 'rooms', '2.json', data=room_json(
        id=2, exits={"west": {"direction": "west", "room_to": 1}}))

    return directory


def problems(directory, world=None):
    "The messages the validator reports for a data library, in file order."

    collector = data_validator.validate(directory, world)[0]
    return ['%s' % problem for problem in collector.problems]


def problemsIn(directory, *path):
    """
    The messages the validator reports for one file of a data library.

    Breaking one room can leave the rooms that lead to it broken too, so a
    test about one file says which one it means.
    """

    wanted = os.path.join(directory, *path)

    collector = data_validator.validate(directory)[0]
    return [problem.message for problem in collector.problems if problem.path == wanted]


###############################################################################
# Data that is fine
###############################################################################

def test_a_clean_library_has_no_problems(library):
    assert problems(library) == []


def test_a_clean_library_is_reported_as_a_success(library, capsys):
    status = data_validator.run(argparse.Namespace(data=library, world=None, verbose=False))

    assert status == 0
    assert 'No problems found.' in capsys.readouterr().out


def test_everything_that_was_checked_is_counted(library):
    counts = data_validator.validate(library)[1]

    assert counts == {
        'items': 1,
        'npcs': 1,
        'characters': 1,
        'accounts': 1,
        'biomes': 1,
        'worlds': 1,
        'rooms': 2,
    }


def test_the_load_is_quiet_unless_it_is_asked_not_to_be(library, capsys):
    data_validator.validate(library)

    assert capsys.readouterr().out == ''


def test_the_load_can_be_narrated(library, capsys):
    data_validator.validate(library, verbose=True)

    assert 'Loading the game store.' in capsys.readouterr().out


###############################################################################
# Data that isn't
###############################################################################

def test_a_bad_field_is_reported_against_its_file(library):
    write(library, 'items', 'rock.json', data=item_json(can_pick_up=True))

    assert problems(library) == [
        os.path.join(library, 'items', 'rock.json') + ': Item.can_pick_up: Item has no such field.'
    ]


def test_a_missing_field_is_reported(library):
    data = item_json()
    del data['weight']
    write(library, 'items', 'rock.json', data=data)

    assert 'Item.weight: Item requires this field.' in problems(library)[0]


def test_a_file_that_is_not_json_is_reported(library):
    write(library, 'items', 'rock.json', text='{ not json at all')

    reported = problems(library)

    assert len(reported) == 1
    assert 'JSONDecodeError' in reported[0]


def test_a_problem_is_reported_once_per_file_not_once_per_world(library):
    # The items are shared by every world, so they are loaded again for each
    # one.  A problem in an item is still only one problem.
    write(library, 'items', 'rock.json', data=item_json(can_pick_up=True))
    write(library, 'worlds', 'other', 'world.json', data=world_json(name='other'))
    write(library, 'worlds', 'other', 'rooms', '1.json', data=room_json())

    assert len(problems(library)) == 1


###############################################################################
# Taking a file apart
#
# A model stops at the first problem it finds, so the validator checks each
# piece of a file on its own to get the rest of them out of the same run.
###############################################################################

def test_every_bad_trait_of_an_item_is_reported(library):
    write(library, 'items', 'rock.json', data=item_json(traits={
        "MeleeWeapon": {"minDamage": 1, "maxDamage": 4, "type": "chopping"},
        "Tool": {"type": "hammer"},
    }))

    reported = problems(library)

    # Without taking the item apart, the weapon would hide the tool.
    assert len(reported) == 2
    assert any('MeleeWeapon.type' in message for message in reported)
    assert any('Tool.type' in message for message in reported)


def test_a_trait_that_does_not_exist_is_reported(library):
    write(library, 'items', 'rock.json', data=item_json(traits={"Flammable": {}}))

    assert 'Item.traits.Flammable: there is no such trait.' in problems(library)[0]


def test_the_problem_an_item_stopped_at_is_not_reported_twice(library):
    write(library, 'items', 'rock.json', data=item_json(traits={
        "Tool": {"type": "hammer"},
    }))

    assert problems(library) == [
        os.path.join(library, 'items', 'rock.json')
        + ': Tool.type: expected a list of strings, found a string (\'hammer\').'
    ]


def test_a_bad_item_field_and_a_bad_trait_are_both_reported(library):
    write(library, 'items', 'rock.json', data=item_json(
        can_pick_up=True, traits={"Tool": {"type": "hammer"}}))

    reported = problems(library)

    assert len(reported) == 2
    assert any('Item.can_pick_up' in message for message in reported)
    assert any('Tool.type' in message for message in reported)


def test_every_bad_exit_of_a_room_is_reported(library):
    write(library, 'worlds', 'base', 'rooms', '1.json', data=room_json(exits={
        "east": {"direction": "east", "room_to": 2, "is_door": "yes"},
        "west": {"direction": "west", "room_to": 2, "is_open": "no"},
    }))

    reported = problemsIn(library, 'worlds', 'base', 'rooms', '1.json')

    assert len(reported) == 2
    assert any('Room.exits.east.is_door' in message for message in reported)
    assert any('Room.exits.west.is_open' in message for message in reported)


def test_exits_that_are_wrong_in_the_same_way_are_reported_separately(library):
    # Every exit reports its problems the same way, so they are labelled with
    # the direction they go.  Without that, these two would read identically
    # and one would be taken for a repeat of the other.
    write(library, 'worlds', 'base', 'rooms', '1.json', data=room_json(exits={
        "east": {"direction": "east", "room_to": 2, "is_door": "yes"},
        "west": {"direction": "west", "room_to": 2, "is_door": "yes"},
    }))

    reported = problemsIn(library, 'worlds', 'base', 'rooms', '1.json')

    assert len(reported) == 2
    assert reported[0] != reported[1]


def test_a_bad_room_field_and_a_bad_exit_are_both_reported(library):
    write(library, 'worlds', 'base', 'rooms', '1.json', data=room_json(
        color="green",
        exits={"east": {"direction": "east", "room_to": 2, "is_door": "yes"}}))

    reported = problemsIn(library, 'worlds', 'base', 'rooms', '1.json')

    assert len(reported) == 2
    assert any('Room.color' in message for message in reported)
    assert any('Room.exits.east.is_door' in message for message in reported)


def test_a_model_that_cannot_be_taken_apart_reports_what_it_stopped_at(library):
    # A biome has no pieces that validate on their own, so the problem that
    # stopped it loading is the whole story.
    write(library, 'biomes', 'plain.json', data=biome_json(water='no-water'))

    reported = problems(library)

    assert len(reported) == 1
    assert "Biome.water: expected one of 'none', 'salt', 'fresh', found a string ('no-water')." in reported[0]


###############################################################################
# Linking
###############################################################################

def test_an_exit_that_leads_nowhere_is_reported(library):
    write(library, 'worlds', 'base', 'rooms', '1.json', data=room_json(
        exits={"east": {"direction": "east", "room_to": 99}}))

    assert problems(library) == [
        os.path.join(library, 'worlds', 'base', 'rooms', '1.json')
        + ": the 'east' exit leads to Room(99), which does not exist."
    ]


def test_an_item_a_room_does_have_is_linked_into_it(library):
    write(library, 'worlds', 'base', 'rooms', '2.json', data=room_json(
        id=2, exits={"west": {"direction": "west", "room_to": 1}}, items=["a rock"]))

    assert problems(library) == []


def test_an_item_a_room_does_not_have_is_reported(library):
    write(library, 'worlds', 'base', 'rooms', '2.json', data=room_json(
        id=2, exits={"west": {"direction": "west", "room_to": 1}},
        items=["a thing that does not exist"]))

    assert problems(library) == [
        os.path.join(library, 'worlds', 'base', 'rooms', '2.json')
        + ': there is no Item(a thing that does not exist) to put in this room.'
    ]


def test_an_npc_that_will_not_load_is_reported(library):
    data = npc_json()
    del data['bodyType']
    write(library, 'npcs', 'rabbit.json', data=data)

    assert problemsIn(library, 'npcs', 'rabbit.json') == ["KeyError: 'bodyType'"]


def test_a_character_that_will_not_load_is_reported(library):
    data = character_json()
    del data['sex']
    write(library, 'characters', 'gird.json', data=data)

    reported = problemsIn(library, 'characters', 'gird.json')

    assert reported == ["KeyError: 'sex'"]

    # The account that has this character is checked afterwards, so the load
    # carried on past it rather than stopping there.
    assert problemsIn(library, 'accounts', 'tester.json') \
        == ['this account has a Character(gird), which does not exist.']


def test_an_account_whose_character_does_not_exist_is_reported(library):
    write(library, 'accounts', 'tester.json', data=account_json(characters=['nobody']))

    assert problemsIn(library, 'accounts', 'tester.json') \
        == ['this account has a Character(nobody), which does not exist.']


def test_an_account_that_will_not_load_is_reported(library):
    data = account_json()
    del data['password_hash']
    write(library, 'accounts', 'tester.json', data=data)

    assert problemsIn(library, 'accounts', 'tester.json') == ["KeyError: 'password_hash'"]


def test_a_characters_inventory_and_equipment_are_linked_to_their_items(library):
    write(library, 'characters', 'gird.json', data=character_json(
        inventory=['a rock'],
        body={"wounds": {}, "worn": {"right hand": "a rock"}}))

    assert problems(library) == []


def test_an_npc_a_room_does_have_is_linked_into_it(library):
    write(library, 'worlds', 'base', 'rooms', '2.json', data=room_json(
        id=2, exits={"west": {"direction": "west", "room_to": 1}},
        occupants=["a rabbit"]))

    assert problems(library) == []


def test_an_npc_a_room_does_not_have_is_reported(library):
    write(library, 'worlds', 'base', 'rooms', '2.json', data=room_json(
        id=2, exits={"west": {"direction": "west", "room_to": 1}},
        occupants=["a bear"]))

    assert 'there is no NPC(a bear) to put in this room.' in problems(library)[0]


def test_linking_carries_on_past_a_room_that_would_not_load(library):
    write(library, 'worlds', 'base', 'rooms', '2.json', data=room_json(id=2, color='green'))
    write(library, 'worlds', 'base', 'rooms', '3.json', data=room_json(
        id=3, exits={"east": {"direction": "east", "room_to": 99}}))

    reported = problems(library)

    # Room 1 still leads to room 2, which never loaded, and room 3 is still
    # checked after both of them.
    assert len(reported) == 3
    assert any('Room.color' in message for message in reported)
    assert any('Room(2), which does not exist' in message for message in reported)
    assert any('Room(99), which does not exist' in message for message in reported)


def test_a_world_that_will_not_load_does_not_take_its_rooms_with_it(library):
    write(library, 'worlds', 'base', 'world.json', text='{ not json at all')

    reported = problems(library)

    # Without the world we don't know where its rooms are kept, so the world
    # is the only thing reported.
    assert len(reported) == 1
    assert 'world.json' in reported[0]


###############################################################################
# Which worlds
###############################################################################

def test_every_world_is_validated(library):
    write(library, 'worlds', 'other', 'world.json', data=world_json(name='other'))
    write(library, 'worlds', 'other', 'rooms', '1.json', data=room_json(
        exits={"east": {"direction": "east", "room_to": 99}}))

    assert data_validator.findWorlds(library) == ['base', 'other']
    assert any('Room(99)' in message for message in problems(library))


def test_a_single_world_may_be_named(library):
    write(library, 'worlds', 'other', 'world.json', data=world_json(name='other'))
    write(library, 'worlds', 'other', 'rooms', '1.json', data=room_json(
        exits={"east": {"direction": "east", "room_to": 99}}))

    assert problems(library, world='base') == []


def test_a_directory_that_is_not_a_world_is_not_one(library):
    # The generator writes `world.json` first, so a world part way through
    # being generated is skipped rather than reported as broken.
    os.makedirs(os.path.join(library, 'worlds', 'half-generated'))

    assert data_validator.findWorlds(library) == ['base']


def test_a_library_with_no_worlds_at_all(tmp_path):
    assert data_validator.findWorlds(str(tmp_path)) == []


###############################################################################
# Reporting
###############################################################################

def test_the_problems_are_reported_and_the_run_fails(library, capsys):
    write(library, 'items', 'rock.json', data=item_json(can_pick_up=True))

    status = data_validator.run(argparse.Namespace(data=library, world=None, verbose=False))
    output = capsys.readouterr().out

    assert status == 1
    assert 'Found 1 problem in 1 file:' in output
    assert 'Item.can_pick_up: Item has no such field.' in output


def test_the_problems_are_grouped_by_the_file_they_are_in(library, capsys):
    write(library, 'items', 'rock.json', data=item_json(
        can_pick_up=True, traits={"Tool": {"type": "hammer"}}))

    data_validator.run(argparse.Namespace(data=library, world=None, verbose=False))
    output = capsys.readouterr().out

    assert 'Found 2 problems in 1 file:' in output

    # The file is named once, with both of its problems under it.
    assert output.count(os.path.join(library, 'items', 'rock.json')) == 1


def test_a_problem_that_is_not_about_a_file_is_reported_too(library, capsys):
    collector = data_validator.ProblemCollector()
    collector.error(LoadError(None, 'No Character(gird) found.', fatal=False))

    data_validator.report(collector, data_validator.validate(library)[1])
    output = capsys.readouterr().out

    assert 'the world as a whole' in output
    assert 'No Character(gird) found.' in output


def test_what_was_checked_is_described_in_the_plural_where_it_should_be():
    description = data_validator.describeCounts({
        'items': 1, 'npcs': 0, 'characters': 2,
        'accounts': 0, 'biomes': 25, 'worlds': 1, 'rooms': 9,
    })

    assert description == '1 item, 0 npcs, 2 characters, 0 accounts, 25 biomes, 1 world, 9 rooms'


###############################################################################
# What the server still does
#
# The validator and the server load the data through the same `Store.load`.
# The only difference is the reporter they hand it, so it is worth saying
# what the server's one still does.
###############################################################################

def test_the_server_stops_at_the_first_problem_it_finds(library, capsys):
    write(library, 'items', 'rock.json', data=item_json(can_pick_up=True))

    with pytest.raises(UnexpectedFieldError) as error:
        Store('base', library).load()

    assert error.value.path == 'Item.can_pick_up'

    # And it narrates the load on the way, as it always has.
    assert 'Loading the game store.' in capsys.readouterr().out


def test_the_server_still_starts_on_a_room_missing_an_item(library, capsys):
    write(library, 'worlds', 'base', 'rooms', '2.json', data=room_json(
        id=2, exits={"west": {"direction": "west", "room_to": 1}},
        items=["a thing that does not exist"]))

    # The room comes up without it rather than the server refusing to start,
    # which is how the game has always treated this.
    store = Store('base', library)
    store.load()

    assert store.rooms.getById(2).items == []
    assert 'there is no Item(a thing that does not exist) to put in this room.' in capsys.readouterr().out


def test_the_server_starts_on_data_that_is_fine(library):
    store = Store('base', library)
    store.load()

    assert store.rooms.getById(1).exits['east'].room_to is store.rooms.getById(2)


###############################################################################
# The pieces on their own
###############################################################################

def test_a_problem_with_no_file_behind_it_is_left_alone():
    problem = LoadError(None, 'No Character(gird) found.')

    assert data_validator.inspect(problem) == [problem]


def test_a_problem_found_while_linking_is_left_alone(library):
    # A linking problem names no model, since it isn't about the shape of the
    # file at all.
    problem = LoadError(os.path.join(library, 'items', 'rock.json'), 'unlinked')

    assert data_validator.inspect(problem) == [problem]


def test_a_file_that_cannot_be_read_is_left_alone(library):
    problem = LoadError(os.path.join(library, 'items', 'no-such-file.json'),
                        'gone', model=Item)

    assert data_validator.inspect(problem) == [problem]


def test_a_model_with_no_pieces_is_left_alone(library):
    # A world has no pieces that validate on their own, and no schema of its
    # own yet either, so the problem that stopped it loading is all there is
    # to say about it.
    path = write(library, 'worlds', 'base', 'world.json', data=world_json())
    problem = LoadError(path, "KeyError: 'roomWidth'", model=World)

    assert data_validator.inspect(problem) == [problem]


def test_an_error_is_relabelled_to_say_which_piece_it_came_from():
    error = MissingFieldError('Exit.direction', 'Exit requires this field.')

    assert data_validator.relabel(error, 'Room.exits.east') \
        == 'Room.exits.east.direction: Exit requires this field.'


def test_an_error_about_a_whole_piece_is_relabelled_too():
    error = MissingFieldError('Exit', 'expected Exit data, found a string.')

    assert data_validator.relabel(error, 'Room.exits.east') \
        == 'Room.exits.east: expected Exit data, found a string.'


def test_a_file_that_is_not_an_object_has_no_pieces():
    assert list(data_validator.takeApart(Item, ['not', 'an', 'object'])) == []
