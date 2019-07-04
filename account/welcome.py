from interpreter.state import State

from creation import CreateNewAccount
from menu import AccountMenu

class WelcomeScreen(State):

    WELCOME_SCREEN = """
Welcome to Python Mud!

If this is your first time, you'll need to create an account by typing "new".
    """

    def introduction(self):
        self.player.write(self.WELCOME_SCREEN)
        self.player.setPrompt("\n\nAccount Name: ")

    def execute(self, input):
        if input == "new":
            return CreateNewAccount(self.player, self.library)
        else:
            account = self.library.getAccountByName(input)
            if account:
                self.player.account = account
                return GetAccountPassword(self.player, self.library)
            else:
                self.player.write("That account doesn't exist.")
        return self

# EndGetAccountName

class GetAccountPassword(State):

    def introduction(self):
        self.player.setPrompt("Password: ")

    def execute(self, input):
        if self.player.account.password == input:
            return AccountMenu(self.player, self.library)
        else:
            player.write("Incorrect password.\n\n")

# End GetAccountPassword
