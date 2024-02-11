from game.interpreters.command.command import Command

class Quit(Command):
    'Leave the game.'

    def describe(self):
        return "quit - leave the game and return to the account menu"

    def help(self):
        return """
quit

Your character will leave the game and you will return to the account menu where you can quit or play another character.
        """

    def execute(self, time, player, arguments):
        self.store.saveCharacter(player.character)

        player.write('You leave the game.')
        self.library.room.writeToRoom(player.character, player.character.name + ' leaves the game.')

        player.character.player = None
        player.character = None

        player.status = player.STATUS_ACCOUNT
        player.setAccountState("account-menu")


class Help(Command):
    'List help contents.'

    def __init__(self, commands, library, store):
        super(Help, self).__init__(library, store)
        self.commands = commands

    def describe(self):
        return "help - get help about how to play the game"

    def help(self):
        return """
help [op:topic]

Get help about a topic.  `[topic]` is optional.  If it is left off, help will list all available commands in the game with a short description of them.
        """

    def execute(self, time, player, arguments):
        if not arguments:
            for command in self.commands:
                description = self.commands[command].describe()
                if description:
                    player.write(description)
            return
        else:
            for command in self.commands:
                if command.startswith(arguments):
                    help_text = self.commands[command].help()
                    if help_text:
                        player.write(help_text)
                        return

        player.write("There doesn't seem to be any help on that.")
