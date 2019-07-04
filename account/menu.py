from interpreter.state import State
from interpreter.command import CommandInterpreter

class AccountMenu(State):

    ACCOUNT_MENU = """
Account Menu

list - list characters available to play
play - play a character

create - create a new character
    """

    def introduction(self):
        self.player.setPrompt("\n\n> ")
        self.player.write(self.ACCOUNT_MENU)

    def execute(self, input):
        tokens  = input.split(' ', 1)
        if tokens[0] == "play":
            self.player.write("Into the world we go!")
            self.player.interpreter = CommandInterpreter(self.player, self.library)
        elif tokens[0] == "create":
            pass
        else:
            self.player.write("That's not a menu option.")

# End AccountMenu

