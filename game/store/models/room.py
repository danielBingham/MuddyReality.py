from textwrap import TextWrapper

from game.store.models.base import JsonSerializable
from game.store.models.base import Model

###
# Represents an exit from a room leading into another room.
#
# Exits may be doors that require opening.  Some doors are secret doors.
###
class Exit(JsonSerializable):

    def __init__(self, room):
        self.room_from = room

        self.is_door = False
        self.is_open = True 

        self.direction = ''
        self.room_to = None
        self.exit_to = None

    def open(self, player):
        if not self.is_door and player:
            player.write("There's no door to open that way.")
            return

        if self.is_open and player:
            player.write("It's already open.")
            return

        self.is_open = True
        if player:
            player.write("You open " + self.name + ".")
        for occupant in self.room_from.occupants:
            if player and occupant.player != player:
                occupant.player.write(player.character.name.title() + " opens the " + self.name + ".")
            elif not player:
                occupant.player.write("The " + self.name + " is opened from the other side.")

        if self.exit_to and self.exit_to.is_open == False:
            self.exit_to.open(None)


    def close(self, player):
        if not self.is_door and player:
            player.write("There's no door to close that way.")
            return

        if not self.is_open and player:
            player.write("It's already closed.")
            return

        self.is_open = False 
        if player:
            player.write("You close " + self.name + ".")
        for occupant in self.room_from.occupants:
            if player and occupant.player != player:
                occupant.player.write(player.character.name.title() + " closes the " + self.name + ".")
            elif not player:
                occupant.player.write("The " + self.name + " is closed from the other side.")

        if self.exit_to and self.exit_to.is_open == True:
            self.exit_to.close(None)

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

### End Exit

###
# Represents a location in the game world. 
###
class Room(Model):

    # A static text wrapper we use to wrap descriptive text.
    wrapper = TextWrapper(width=80, replace_whitespace=False, initial_indent='', break_on_hyphens=False)

    ###
    # A list of possible directions leading out of this room.
    ###
    DIRECTIONS = [
        'north',
        'east',
        'south',
        'west',
        'up',
        'down'
    ]

    ###
    # A handy helper map for inverting directions.
    ###
    INVERT_DIRECTION = {
        "north": "south",
        "east": "west",
        "south": "north",
        "west": "east",
        "up": "down",
        "down": "up"
    }


    ###
    # Initialize the room.  
    ###
    def __init__(self ):
        super(Room, self).__init__()

        self.title = ''
        self.description = ''
        self.color = [] 

        self.exits = {}

        self.occupants = []
        self.items = []


    def isOccupant(self, argument):
        for occupant in self.occupants:
            if occupant.name.startswith(argument):  
                return True
        return False


    def getColorString(self):
        return "\033[38;2;" + str(self.color[0]) + ";" + str(self.color[1]) + ";" + str(self.color[2]) + "m"

    def getColorReset(self):
        return "\033[0m"

    ###
    # Describe the room to a player.
    ###
    def describe(self, player):
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
                output += "%s is %s here.\n" % ((item.description[0].title() + item.description[1:]), item.groundAction())
            else:
                output += "%s is here.\n" % (item.description[0].title() + item.description[1:])

        output += "---\n"
        output += "Exits: "
        for direction in Room.DIRECTIONS:
            if not direction in self.exits:
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

    ###
    # Convert the room to simple json for serialization and saving.
    ###
    def toJson(self):
        json = {}
        json['id'] = self.getId()
        json['title'] = self.title
        json['description'] = self.description
        json['color'] = self.color

        json['exits'] = {}
        for direction in self.exits:
            json['exits'][direction] = self.exits[direction].toJson()

        json['items'] = []
        for item in self.items:
            json['items'].append(item.getId())

        return json

    ###
    # Convert a json serialization back to a room object.
    ###
    def fromJson(self, data):
        self.setId(data['id'])
        self.title = data['title']
        self.description = data['description']
        self.color = data['color']

        for direction in data['exits']:
            self.exits[direction] = Exit(self)
            self.exits[direction].fromJson(data['exits'][direction])

        # Store will convert the list of ids into object references in
        # Store::load
        self.items = data['items']

        return self

### End room