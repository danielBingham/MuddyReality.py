from interpreter.state import State

from account.creation import CreateNewAccount
from account.menu import AccountMenu

class WelcomeScreen(State):

    WELCOME_SCREEN = """
Welcome to Python Mud!

If this is your first time, you'll need to create an account by typing "new".
    """

    def introduction(self):
        self.player.write(self.WELCOME_SCREEN)
        self.player.setPrompt("Account Name: ")

    def execute(self, input):
        if input == "new":
            return CreateNewAccount(self.player, self.library)
        else:
            account = self.library.accounts.getById(input.lower())
            if account:
                self.player.account = account
                return GetAccountPassword(self.player, self.library)
            else:
                self.player.write("That account doesn't exist.")
        return self

# EndGetAccountName

class GetAccountPassword(State):

    def introduction(self):
        self.player.write("Please enter the password for the account '" + self.player.account.name + "'.")
        self.player.setPrompt("Password: ")

    def execute(self, input):
        if self.player.account.isPassword(input):
            return AccountMenu(self.player, self.library)
        else:
            self.player.write("Incorrect password.")
        
        return self

# End GetAccountPassword
