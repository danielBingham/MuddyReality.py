from interpreter.command import Command
import services.movement as movement 

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
        player.write("\n" + player.character.room.describe(player), wrap=False)
    else:
        player.write("You can't got that way.")

class North(Command):
    'Go north'
    
    def execute(self, player, arguments):
        move('north', player, arguments)
            
class East(Command):
    'Go east'
    
    def execute(self, player, arguments):
        move('east', player, arguments)

class South(Command):
    'Go south'
    
    def execute(self, player, arguments):
        move('south', player, arguments)

class West(Command):
    'Go west'
    
    def execute(self, player, arguments):
        move('west', player, arguments)

class Up(Command):
    'Go up'
    
    def execute(self, player, arguments):
        move('up', player, arguments)

class Down(Command):
    'Go down'
    
    def execute(self, player, arguments):
        move('down', player, arguments)

