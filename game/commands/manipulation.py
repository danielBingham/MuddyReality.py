from interpreter.command import Command


class Open(Command):
    'Open a door or an object'
    
    def execute(self, player, arguments):
        room = player.character.room
        for direction in room.exits:
            if arguments == direction or arguments == room.exits[direction].name:
                room.exits[direction].open(player)
                return

        player.write("That doesn't appear to be something you can open.")

class Close(Command):
    'Close a door or an object'
    
    def execute(self, player, arguments):
        room = player.character.room
        for direction in room.exits:
            if arguments == direction or arguments == room.exits[direction].name:
                room.exits[direction].close(player)
                return

        player.write("That doesn't appear to be something you can close.")

