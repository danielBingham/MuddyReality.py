from game.interpreters.command.command import Command

class Say(Command):
    'Say something to the room.'
    
    def describe(self):
        return "say - say something to everyone in the vicinity"

    def help(self):
        return """
say [text]

Your character will say `[text]` outloud so that everyone in the vicinity (your current room) can hear it.
        """

    def execute(self, player, arguments):
        if player.character.position == player.character.POSITION_SLEEPING:
            player.write("You can't speak in your sleep.")
            return

        for occupant in player.character.room.occupants: 
            if occupant == player.character:
                player.write('You say "%s"' % (arguments))
            else:
                occupant.player.write('%s says "%s"' % (player.character.name.title(), arguments))

