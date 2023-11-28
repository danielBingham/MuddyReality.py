from interpreter.command import Command
from interpreter.state import StateInterpreter
from account.menu import AccountMenu
import services.environment as environment

class Quit(Command):
    'Leave the game.'
    
    def describe(self):
        return "quit - leave the game and return to the account menu"

    def help(self):
        return """
quit

Your character will leave the game and you will return to the account menu where you can quit or play another character.
        """

    def execute(self, player, arguments):
        player.write('You leave the game.')
        environment.writeToRoom(player.character, player.character.name + ' leaves the game.')

        player.character.player = None
        player.character = None

        player.interpreter = StateInterpreter(player, self.library, AccountMenu(player, self.library))


class Help(Command):
    'List help contents.'

    def describe(self):
        return "help - get help about how to play the game"

    def help(self):
        return """
help [op:topic]

Get help about a topic.  `[topic]` is optional.  If it is left off, help will list all available commands in the game with a short description of them.
        """

    def execute(self, player, arguments):
        if not arguments:
            for command in self.library.commands:
                description = self.library.commands[command].describe()
                if description:
                    player.write(description)
            return
        else:
            for command in self.library.commands:
                if command.startswith(arguments):
                    help_text = self.library.commands[command].help()
                    if help_text:
                        player.write(help_text)
                        return

        player.write("There doesn't seem to be any help on that.")
