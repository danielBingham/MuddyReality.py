from interpreter.command import Command

class Say(Command):
    'Say something to the room.'

    def execute(self, player, arguments):
        for occupant in player.character.room.occupants: 
            if occupant == player.character:
                player.write('You say "%s"' % (arguments))
            else:
                occupant.player.write('%s says "%s"' % (player.character.name.title(), arguments))

