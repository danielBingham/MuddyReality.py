from game.interpreters.state.state import State

from game.account_menu.creation import CreateNewAccount
from game.account_menu.menu import AccountMenu

class WelcomeScreen(State):

    WELCOME_SCREEN = """
Welcome to Muddy Reality!

If this is your first time, you'll need to create an account by typing "new".
    """

    def introduction(self):
        self.player.write(self.WELCOME_SCREEN)
        self.player.setPrompt("Account Name: ")

    def execute(self, input):
        if input == "new":
            return CreateNewAccount(self.player, self.library, self.store)
        else:
            account = self.store.accounts.getById(input.lower())
            if account:
                self.player.account = account
                return GetAccountPassword(self.player, self.library, self.store)
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
            return AccountMenu(self.player, self.library, self.store)
        else:
            self.player.write("Incorrect password.")
        
        return self

# End GetAccountPassword
