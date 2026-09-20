from __future__ import annotations

from typing import TYPE_CHECKING

from enum import StrEnum

from game.store.models.base import JsonSerializable
from game.store.models.base import Model

if TYPE_CHECKING:
    from game.store.models.character import Character
    from game.store.models.item import Item

class Direction(StrEnum):
    "The directions you may travel from one room to the next."

    NORTH = "north"
    EAST = "east"
    SOUTH = "south"
    WEST = "west"
    UP = "up"
    DOWN = "down"

class WaterType(StrEnum):
    "The types of water that exist in the world."

    NONE = "none"
    SALT = "salt"
    FRESH = "fresh"


# A helper to invert a direction.
INVERT_DIRECTION = {
    Direction.NORTH: Direction.SOUTH,
    Direction.EAST: Direction.WEST,
    Direction.SOUTH: Direction.NORTH,
    Direction.WEST: Direction.EAST,
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP
}

class Exit(JsonSerializable):
    "An exit from one room to another."

    # An object link to the room this exit comes from. Not deserialized by
    # fromJson(), instead it is set by store after all rooms have been loaded.
    # This is because we won't have all the rooms (and thus the ability to set
    # the room) until then.
    room_from: Room | None

    # An object link to the room this exit goes to. Set by Store after all
    # rooms have been loaded, so this isn't deserialized by fromJson().
    room_to: Room | None

    # An object link to the other side of this exit in `room_to`. Set by store
    # after all rooms have been loaded, so this isn't deserialized by
    # `fromJson()`.
    exit_to: Exit | None

    # Is this exit a door that can be opened and closed? If yes, True.  False
    # otherwise. Optional.
    is_door: bool

    # If this exit is a door, is it currently open?  True is open, False is
    # closed. Optional.
    is_open: bool

    # The direction this exit goes. Required.
    direction: Direction

    def __init__(self, room):
        self.room_from = room
        self.room_to = None
        self.exit_to = None

        self.is_door = False
        self.is_open = True

        self.direction = Direction.NORTH

    def toJson(self):
        json = {}
        json['is_door'] = self.is_door
        json['is_open'] = self.is_open
        json['direction'] = self.direction
        if self.room_to:
            json['room_to'] = self.room_to.getId()
        return json

    def fromJson(self, data):
        self.direction = data['direction']
        self.room_to = data['room_to']

        self.is_door = data['is_door']
        self.is_open = data['is_open']
        return self

class Room(Model):
    "A location in the game world."

    # A list of possible directions leading out of this room.
    DIRECTIONS = [
        'north',
        'east',
        'south',
        'west',
        'up',
        'down'
    ]

    # A helper to invert a direction.
    INVERT_DIRECTION = {
        "north": "south",
        "east": "west",
        "south": "north",
        "west": "east",
        "up": "down",
        "down": "up"
    }

    WATER_NONE = 'none'
    WATER_SALT = 'salt'
    WATER_FRESH = 'fresh'

    # The room's title, displayed at the top of the room description. A short
    # descriptive phrase. eg. "An Ancient Forest". Required.
    title: str

    # The room's long description. A paragraph describing the area contained in
    # the room. Required.
    description: str

    # A color definition in RGB format. A list of three integers representing
    # the RGB color code. Required.
    color: list[int]

    # What type of water is present in this room (if any). Optional.
    water_type: WaterType

    # How deep the water in this room is. (meters) Optional.
    water: float

    # How fast the water in this room is moving. (meters per second) Optional.
    water_velocity: float

    # A dictionary of exits that lead out of this room and connect to other
    # rooms. Optional.
    exits: dict[Direction, Exit]

    # A list of Characters who are currently present in this room. Serialized
    # as a list of Ids and converted to object references by Store after
    # loading. Optional.
    occupants: list[Character]

    # A list of Items currently present in this room. Serialized as a list of
    # Ids and converted to object references by Store after loading. Optional.
    items: list[Item]

    def __init__(self):
        super(Room, self).__init__()

        self.title = ''
        self.description = ''
        self.color = []

        self.water_type = WaterType.NONE
        self.water = 0
        self.water_velocity = 0

        self.exits = {}

        self.occupants = []
        self.items = []

    def toJson(self):
        json = {}
        json['id'] = self.getId()
        json['title'] = self.title
        json['description'] = self.description
        json['color'] = self.color

        if self.water_type != WaterType.NONE:
            json['waterType'] = self.water_type
            json['water'] = self.water
            json['waterVelocity'] = self.water_velocity

        json['exits'] = {}
        for direction in self.exits:
            json['exits'][direction] = self.exits[direction].toJson()

        json['items'] = []
        for item in self.items:
            json['items'].append(item.getId())

        json['occupants'] = []
        for occupant in self.occupants:

            # We don't store player characters in the room serializations.
            # Instead, the room the character is in is stored in the character
            # itself.  They will be loaded into that room when they log back
            # in.
            if occupant.is_player_character:
                continue
            json['occupants'].append(occupant.getId())

        return json

    def fromJson(self, data):
        self.setId(data['id'])
        self.title = data['title']
        self.description = data['description']
        self.color = data['color']

        if 'waterType' in data:
            self.water_type = data['waterType']
            self.water = data['water']
            self.water_velocity = data['waterVelocity']

        for direction in data['exits']:
            self.exits[direction] = Exit(self)
            self.exits[direction].fromJson(data['exits'][direction])

        # Store will convert the list of ids into object references in
        # Store::load
        self.items = data['items']

        # Store will convert the list of ids into object references in
        # Store::load
        if 'occupants' in data:
            self.occupants = data['occupants']

        return self
