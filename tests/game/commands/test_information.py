from unittest.mock import Mock, call

from game.library.library import Library
from game.store.store import Store
from game.player import Player
from game.store.models.character import PlayerCharacter 
from game.store.models.room import Room
from game.store.models.world import World

from game.commands.information import Status, Look

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
        "thirst": 4000 ,
        "energy": 10000,
        "maxEnergy": 10000,
        "wind": 30,
        "maxWind": 30
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

    status.execute(player, '')

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

    status.execute(player, '')

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

    status.execute(player, '')

    player.write.assert_has_calls([
                                call("You are Character."),
                                call("You are standing and walking."),
                                call("You are ravenous, dehydrated, and drowsy.\nYou are winded and fatigued.")
    ])


room_json = {
    "id": 1,
    "title": "A Test Room",
    "description": "A test room.  Used for testing.",
    "color": [ 255,255,255 ],
    "water": 0,
    "waterType": "no-water",
    "waterVelocity": 0,
    "exits": {
        "east": {
            "direction": "east",
            "room_to": 2,
            "is_door": False,
            "is_open": True
        }
    },
    "items": [ ]
}

room_east_json = {
    "id": 2,
    "title": "A Test Room East",
    "description": "A test room to the east.  Used for testing.",
    "color": [ 255,255,255 ],
    "water": 0,
    "waterType": "no-water",
    "waterVelocity": 0,
    "exits": {
        "west": {
            "direction": "west",
            "room_to": 1,
            "is_door": False,
            "is_open": True
        }
    },
    "items": [ ]
}

def test_Look():
    """
    Test the player looking with no arguments.
    """

    store = Store('test', '')
    store.world = World()
    store.world.time.hour = 12
    store.world.time.night = False 

    library = Library(store)

    look = Look(library, store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.fromJson(character_json)

    room = Room()
    room.fromJson(room_json)

    room_east = Room()
    room_east.fromJson(room_east_json)
    
    room.exits['east'].room_to = room_east
    room_east.exits['west'].room_to = room

    player.character.room = room
    room.occupants.append(player.character)

    look.execute(player, '')

    player.write.assert_called_once_with("""\033[38;2;255;255;255mA Test Room\033[0m
A test room.  Used for testing.
---
---
Exits: \033[38;2;255;255;255meast \033[0m
""", wrap=False)


def test_Look_in_direction():
    """
    Test the player looking in a direction.
    """

    store = Store('test', '')
    store.world = World()
    store.world.time.hour = 12
    store.world.time.night = False 

    library = Library(store)

    look = Look(library, store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.fromJson(character_json)

    room = Room()
    room.fromJson(room_json)

    room_east = Room()
    room_east.fromJson(room_east_json)
    
    room.exits['east'].room_to = room_east
    room_east.exits['west'].room_to = room

    player.character.room = room
    room.occupants.append(player.character)

    look.execute(player, 'east')

    player.write.assert_called_once_with("""\033[38;2;255;255;255mA Test Room East\033[0m
A test room to the east.  Used for testing.
---
---
Exits: \033[38;2;255;255;255mwest \033[0m
""", wrap=False)


def test_Look_in_while_sleeping():
    """
    Test the player attempting to look while asleep.
    """

    store = Store('test', '')
    library = Library(store)

    look = Look(library, store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.fromJson(character_json)
    player.character.position = player.character.POSITION_SLEEPING

    room = Room()
    room.fromJson(room_json)

    room_east = Room()
    room_east.fromJson(room_east_json)
    
    room.exits['east'].room_to = room_east
    room_east.exits['west'].room_to = room

    player.character.room = room
    room.occupants.append(player.character)

    look.execute(player, '')

    player.write.assert_called_once_with("You can't see in your sleep.")


def test_Look_in_non_direction():
    """
    Test the player attempting to look in a direction with no exit.
    """

    store = Store('test', '')
    library = Library(store)

    look = Look(library, store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.fromJson(character_json)

    room = Room()
    room.fromJson(room_json)

    room_east = Room()
    room_east.fromJson(room_east_json)
    
    room.exits['east'].room_to = room_east
    room_east.exits['west'].room_to = room

    player.character.room = room
    room.occupants.append(player.character)

    look.execute(player, 'north')

    player.write.assert_called_once_with("Nothing there.")
