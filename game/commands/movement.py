from game.interpreters.command import Command
import game.library.movement as movement 

def move(direction, player, arguments):

    if not player.character.room:
        raise RuntimeException("Player should have a room if they're trying to move!")

    room = player.character.room
    if direction in room.exits:
        if room.exits[direction].is_door and room.exits[direction].is_open == False:
            player.write("The " + room.exits[direction].name + " is closed.")
            return 

        player.write("You go " + direction + ".")
        movement.leave(player.character, player.character.room, direction=direction)
        movement.enter(player.character, room.exits[direction].room_to, direction=direction)
        player.character.reserves.calories -= 4
        player.write("\n" + player.character.room.describe(player), wrap=False)
    else:
        player.write("You can't got that way.")

class North(Command):
    'Go north'

    def describe(self):
        return "north - travel to the north"

    def help(self):
        return """
north

Go to the room to the north, if possible.
        """
    
    def execute(self, player, arguments):
        move('north', player, arguments)
            
class East(Command):
    'Go east'

    def describe(self):
        return "east - travel to the east"

    def help(self):
        return """
east

Go to the room to the east, if possible.
        """
    
    def execute(self, player, arguments):
        move('east', player, arguments)

class South(Command):
    'Go south'

    def describe(self):
        return "south - travel to the south"

    def help(self):
        return """
south

Go to the room to the south, if possible.
        """
    
    def execute(self, player, arguments):
        move('south', player, arguments)

class West(Command):
    'Go west'

    def describe(self):
        return "west - travel to the west"

    def help(self):
        return """
west

Go to the room to the west, if possible.
        """
    
    def execute(self, player, arguments):
        move('west', player, arguments)

class Up(Command):
    'Go up'

    def describe(self):
        return "up - travel up"

    def help(self):
        return """
up

Go to the room above, if possible.
        """
    
    def execute(self, player, arguments):
        move('up', player, arguments)

class Down(Command):
    'Go down'

    def describe(self):
        return "down - travel down"

    def help(self):
        return """
down

Go to the room below, if possible.
        """
    
    def execute(self, player, arguments):
        move('down', player, arguments)

