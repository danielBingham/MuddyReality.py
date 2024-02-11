from textwrap import TextWrapper

from game.store.models.base import JsonSerializable
from game.store.models.base import Model


class Exit(JsonSerializable):
    "An exit from one room to another."

    def __init__(self, room):
        self.room_from = room

        self.is_door = False
        self.is_open = True 

        self.direction = ''
        self.room_to = None
        self.exit_to = None

    def toJson(self):
        json = {}
        json['is_door'] = self.is_door
        json['is_open'] = self.is_open
        json['direction'] = self.direction
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

    # A static text wrapper we use to wrap descriptive text.
    wrapper = TextWrapper(width=80, replace_whitespace=False, initial_indent='', break_on_hyphens=False)

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

    def __init__(self):
        super(Room, self).__init__()

        self.title = ''
        self.description = ''
        self.color = [] 

        self.water_type = self.WATER_NONE
        self.water = 0
        self.water_velocity = 0

        self.exits = {}

        self.occupants = []
        self.items = []

    def getColorString(self):
        return "\033[38;2;" + str(self.color[0]) + ";" + str(self.color[1]) + ";" + str(self.color[2]) + "m"

    def getColorReset(self):
        return "\033[0m"

    def describe(self, time, player):
        output = ""

        if self.color:
            output += self.getColorString()
        output += self.wrapper.fill(str(self.title)) 
        if self.color:
            output += self.getColorReset() 

        output += "\n"

        output += self.wrapper.fill(str(self.description)) + "\n"
        output += "---\n"
        for occupant in self.occupants:
            if occupant != player.character:
                output += occupant.name.title() + " is here.\n"

        for item in self.items:
            if item.groundAction():
                output += "%s is %s here.\n" % (item.describe(time), item.groundAction())
            else:
                output += "%s is here.\n" % (item.describe(time))

        output += "---\n"
        output += "Exits: "
        for direction in Room.DIRECTIONS:
            if direction not in self.exits:
                continue

            output += self.exits[direction].room_to.getColorString()
            if self.exits[direction].is_door:
                if self.exits[direction].is_open:
                    output += "(" + direction + ") "
                else:
                    output += "[" + direction + "] "
            else:
                output += direction + " "
            output += self.getColorReset()

        output += "\n"
        return output

    def toJson(self):
        json = {}
        json['id'] = self.getId()
        json['title'] = self.title
        json['description'] = self.description
        json['color'] = self.color

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
            if occupant.is_player_character:
                continue
            json['occupants'].append(occupant.getId())

        return json

    def fromJson(self, data):
        self.setId(data['id'])
        self.title = data['title']
        self.description = data['description']
        self.color = data['color']

        self.water_type = data['waterType']
        self.water = data['water']
        self.water_velocity = data['waterVelocity']

        for direction in data['exits']:
            self.exits[direction] = Exit(self)
            self.exits[direction].fromJson(data['exits'][direction])

        # Store will convert the list of ids into object references in
        # Store::load
        self.items = data['items']

        if 'occupants' in data:
            self.occupants = data['occupants']

        return self
