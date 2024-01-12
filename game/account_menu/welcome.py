from game.interpreters.state.state import State

from game.account_menu.creation import CreateNewAccount
from game.account_menu.menu import AccountMenu


class WelcomeScreen(State):
    """
    Introduce the game to the new player and start them on the account flow.
    From here they can create a new account or login to an existing one.
    """

    NAME = "welcome-screen"
    WELCOME_SCREEN = """
Welcome to Muddy Reality!

If this is your first time, you'll need to create an account by typing "new".
    """

    def introduce(self, player):
        "See State::introduce()"

        player.write(self.WELCOME_SCREEN)
        player.setPrompt("Account Name: ")

    def execute(self, player, input):
        "See State::execute()"

        if input == "new":
            return "create-new-account" 
        else:
            account = self.store.accounts.getById(input.lower())
            if account:
                player.account = account
                return "get-account-password" 
            else:
                player.write("That account doesn't exist.")

        return self.NAME 


class GetAccountPassword(State):
    "Get the player's account password and validate it."

    NAME = "get-account-password"

    def introduce(self, player):
        player.write("Please enter the password for the account '" + player.account.name + "'.")
        player.setPrompt("Password: ")

    def execute(self, player, input):
        if player.account.isPassword(input):
            return "account-menu" 
        else:
            player.write("Incorrect password.")

        return self.NAME 

# End GetAccountPassword
