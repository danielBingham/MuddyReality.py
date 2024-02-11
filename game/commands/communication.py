from game.interpreters.command.command import Command


class Say(Command):
    'Say something to the room.'

    def describe(self):
        "See Command.describe()"

        return "say - say something to everyone in the vicinity"

    def help(self):
        "See Command.help()"

        return """
say [text]

Your character will say `[text]` outloud so that everyone in the vicinity (your current room) can hear it.
        """

    def execute(self, time, player, arguments):
        "See Command.execute()"

        if player.character.position == player.character.POSITION_SLEEPING:
            player.write("You can't speak in your sleep.")
            return

        player.write('You say "%s"' % (arguments))
        self.library.room.writeToRoom(player.character, '%s says "%s"' % (player.character.name.title(), arguments))
