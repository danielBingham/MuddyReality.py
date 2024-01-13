from unittest.mock import Mock, call

from game.library.library import Library
from game.store.store import Store
from game.player import Player
from game.store.models.character import PlayerCharacter, Character
from game.store.models.room import Room

from game.commands.information import Status 

character_json = {
    "attributes": {
        "constitution": 10,
        "maxConstitution": 10,
        "maxStamina": 10,
        "maxStrength": 10,
        "stamina": 10,
        "strength": 10
    },
    "body": {
        "worn": {},
        "wounds": {}
    },
    "bodyType": "bipedal",
    "description": "",
    "details": "",
    "inventory": [ ],
    "name": "character",
    "position": "standing",
    "reserves": {
        "calories": 2400,
        "maxCalories": 2400,
        "maxSleep": 16,
        "maxThirst": 4000,
        "sleep": 16,
        "thirst": 4000 
    },
    "room": 1,
    "sex": "male",
    "speed": "walking"
}

def test_Status():
    """
    Test the Status command with a character with full reserves.
    """

    store = Store('test', '')
    library = Library(store)

    status = Status(library, store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.fromJson(character_json)

    room = Room()
    player.character.room = room
    room.occupants.append(player.character)

    status.execute(player, 'Hello')

    player.write.assert_has_calls([
                                call("You are Character."),
                                call("You are standing and walking."),
                                call("You are sated, hydrated, and awake.\nYou are breathing calmly and rested.")
    ])


def test_Status_mid_reserves():
    """
    Test the Status command with a character with half used reserves.
    """

    store = Store('test', '')
    library = Library(store)

    status = Status(library, store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.fromJson(character_json)

    player.character.reserves.calories -= player.character.reserves.max_calories * 0.5
    player.character.reserves.thirst -= player.character.reserves.max_thirst * 0.5
    player.character.reserves.sleep -= player.character.reserves.max_sleep * 0.75
    player.character.reserves.wind -= player.character.reserves.max_wind * 0.5
    player.character.reserves.energy -= player.character.reserves.max_energy * 0.5

    room = Room()
    player.character.room = room
    room.occupants.append(player.character)

    status.execute(player, 'Hello')

    player.write.assert_has_calls([
                                call("You are Character."),
                                call("You are standing and walking."),
                                call("You are hungry, thirsty, and yawning.\nYou are huffing and tired.")
    ])


def test_Status_low_reserves():
    """
    Test the Status command with a character with three quarters used reserves.
    """

    store = Store('test', '')
    library = Library(store)

    status = Status(library, store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.fromJson(character_json)

    player.character.reserves.calories -= player.character.reserves.max_calories * 0.75
    player.character.reserves.thirst -= player.character.reserves.max_thirst * 0.75
    player.character.reserves.sleep -= player.character.reserves.max_sleep 
    player.character.reserves.wind -= player.character.reserves.max_wind * 0.75
    player.character.reserves.energy -= player.character.reserves.max_energy * 0.75

    room = Room()
    player.character.room = room
    room.occupants.append(player.character)

    status.execute(player, 'Hello')

    player.write.assert_has_calls([
                                call("You are Character."),
                                call("You are standing and walking."),
                                call("You are ravenous, dehydrated, and drowsy.\nYou are winded and fatigued.")
    ])


