from textwrap import TextWrapper

from models.base import JsonSerializable
from models.base import Model

###
# Represents an exit from a room leading into another room.
#
# Exits may be doors that require opening.  Some doors are secret doors.
###
class Exit(JsonSerializable):

    def __init__(self, room, library):
        self.library = library
        self.room_from = room

        self.is_door = False
        self.name = '' 
        self.is_open = True 

        self.direction = ''
        self.description = ''
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

    def describe(self, player):
        return self.description

    def connect(self):
        self.room_to = self.library.rooms.getById(self.room_to)
        if Room.INVERT_DIRECTION[self.direction] in self.room_to.exits:
            self.exit_to = self.room_to.exits[Room.INVERT_DIRECTION[self.direction]]
        return self

    def toJson(self):
        json = {}
        json['is_door'] = self.is_door
        json['name'] = self.name
        json['is_open'] = self.is_open
        json['direction'] = self.direction
        json['description'] = self.description
        json['room_to'] = self.room_to.getId()
        return json

    def fromJson(self, data):
        self.direction = data['direction']
        self.description = data['description']
        self.room_to = data['room_to']

        self.name = data['name']
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
    def __init__(self, library):
        super(Room, self).__init__(library)

        self.title = ''
        self.description = ''

        self.exits = {}

        self.occupants = []
        self.objects = []


    ###
    # Connect this rooms exits after they've been loaded.
    #
    # TECHDEBT: This method is techdebt.    Exit connections are loaded as ID numbers and converted
    # to object links on load.  However, when rooms are first loaded, we have no guaranetee that the
    # room the exit connects to has also been loaded.  It might not be in the library yet.  So we
    # have to load all of the rooms initially with out converting any of the IDS to object links and
    # then walk the room list to convert all the ids to object links.
    ###
    def connect(self):
        for direction in self.exits:
            self.exits[direction].connect()

    ###
    # Describe the room to a player.
    ###
    def describe(self, player):
        output = self.wrapper.fill(str(self.title)) + "\n"
        output += self.wrapper.fill(str(self.description)) + "\n"
        for occupant in self.occupants:
            if occupant != player.character:
                output += occupant.name.title() + " is here.\n"
        for object in self.objects:
            output += object.name.title() + " is laying here.\n"
        output += "Exits: "
        for exit in self.exits:
            if self.exits[exit].is_door:
                if self.exits[exit].is_open:
                    output += "(" + exit + ") "
                else:
                    output += "[" + exit + "] "
            else:
                output += exit + " "
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

        json['exits'] = {}
        for direction in self.exits:
            json['exits'][direction] = self.exits[direction].toJson()

        json['objects'] = []
        for object in self.objects:
            json['objects'].append(object.getId())

        return json
    ###
    # Convert a json serialization back to a room object.
    ###
    def fromJson(self, data):
        self.setId(data['id'])
        self.title = data['title']
        self.description = data['description']

        for direction in data['exits']:
            self.exits[direction] = Exit(self, self.library)
            self.exits[direction].fromJson(data['exits'][direction])

        for id in data['objects']:
            self.objects.append(self.library.objects.instance(id))

        return self

    ###
    # A static method to get the path in the data library where we store saved room files.
    ###
    @staticmethod
    def getBasePath():
        return 'data/rooms/'

### End room
