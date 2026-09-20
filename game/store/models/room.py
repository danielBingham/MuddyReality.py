from __future__ import annotations

from typing import TYPE_CHECKING

from enum import StrEnum

from game.store.models.base import JsonSerializable
from game.store.models.base import Model
from game.library.validation.errors import InvalidValueError
from game.library.validation.errors import MissingFieldError
from game.library.validation.validator import Validator
from game.library.validation.validator import validateModel

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


# The enum values as they are written in json, for the schemas below.  The
# members themselves would be written into an error message by their repr,
# which reads as `<Direction.NORTH: 'north'>` rather than `'north'`.
DIRECTION_NAMES = [direction.value for direction in Direction]
WATER_TYPE_NAMES = [water_type.value for water_type in WaterType]


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

    # A name for what lies through this exit, used to refer to it in commands.
    # Eg. 'old growth forest'. Optional.
    name: str

    # A description of what lies through this exit. Optional.
    description: str

    SCHEMA = {
        "direction": Validator().isType(str).isOneOf(DIRECTION_NAMES).isRequired(),

        # The `id` of the room this exit leads to.  Store swaps it for the Room
        # itself once every room has been loaded.
        "room_to": Validator().isType(int).isRequired(),

        "is_door": Validator().isType(bool),
        "is_open": Validator().isType(bool),

        "name": Validator().isType(str),
        "description": Validator().isType(str),
    }

    def __init__(self, room):
        self.room_from = room
        self.room_to = None
        self.exit_to = None

        self.is_door = False
        self.is_open = True

        self.direction = Direction.NORTH

        self.name = ''
        self.description = ''

    def validate(self, data):
        """
        Validate that `data` is valid Exit json.

        Parameters
        ----------
        data:   dict
            The json data to validate.

        Returns
        -------
        True
            If `data` is valid.

        Raises
        ------
        ValidationError
            If `data` does not match `SCHEMA`.
        """

        return validateModel(type(self), data)

    def toJson(self):
        json = {}
        json['is_door'] = self.is_door
        json['is_open'] = self.is_open
        json['direction'] = self.direction

        if self.name:
            json['name'] = self.name
        if self.description:
            json['description'] = self.description

        # An exit that has not been given a destination yet has nothing to
        # write here.  Store links `room_to` to the Room once every room has
        # been loaded, so until then this is the room's `id`.
        if self.room_to:
            json['room_to'] = self.room_to.getId()

        return json

    def fromJson(self, data):

        self.validate(data)

        self.direction = data['direction']
        self.room_to = data['room_to']

        if 'is_door' in data:
            self.is_door = data['is_door']
        if 'is_open' in data:
            self.is_open = data['is_open']

        if 'name' in data:
            self.name = data['name']
        if 'description' in data:
            self.description = data['description']

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

    SCHEMA = {
        "id": Validator().isType(int).isRequired(),
        "title": Validator().isType(str).isRequired(),
        "description": Validator().isType(str).isRequired(),
        "color": Validator().isType(list[int]).isRequired(),

        # A room either says nothing about water or says all three of these.
        # `validate` holds them together, since a schema can only speak about
        # one field at a time.
        "waterType": Validator().isType(str).isOneOf(WATER_TYPE_NAMES),
        "water": Validator().isType(float),
        "waterVelocity": Validator().isType(float),

        # Each exit validates itself as `fromJson` builds it, so the room only
        # checks that each one is the object an Exit loads from.  `validate`
        # checks the keys, which a schema has no way to speak about.
        "exits": Validator().isType(dict[str, Exit]).isRequired(),

        # The `name` of each Item, and the `id` of each non player Character.
        # Store swaps both for the objects themselves once everything has been
        # loaded.
        "items": Validator().isType(list[str]).isRequired(),
        "occupants": Validator().isType(list[str]),
    }

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

    def validate(self, data):
        """
        Validate that `data` is valid Room json.

        Parameters
        ----------
        data:   dict
            The json data to validate.

        Returns
        -------
        True
            If `data` is valid.

        Raises
        ------
        ValidationError
            If `data` does not match `SCHEMA`, if an exit is keyed by
            something that isn't a direction, or if the room describes its
            water without saying how much of it there is.
        """

        validateModel(type(self), data)

        for direction in data['exits']:
            if direction not in DIRECTION_NAMES:
                raise InvalidValueError(
                    'Room.exits.%s' % direction,
                    'expected one of %s, since an exit is keyed by the direction it goes.'
                    % ', '.join(repr(name) for name in DIRECTION_NAMES))

        # `fromJson` reads all three together, so a room that names a water
        # type without the rest would fail to load rather than fail to
        # validate.
        if 'waterType' in data:
            for field in ('water', 'waterVelocity'):
                if field not in data:
                    raise MissingFieldError(
                        'Room.%s' % field,
                        'a room that says what water it has must also say how '
                        'deep it is and how fast it moves.')

        return True

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

        self.validate(data)

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
