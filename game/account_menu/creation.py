from game.interpreters.state.state import State

from game.account_menu.password import GetNewAccountPassword 

class CreateNewAccount(State):
    "Create a new account for `player`."

    NAME = "create-new-account"

    def introduce(self, player):
        "See State::introduce()"

        player.setPrompt("Enter New Account Name: ")

    def execute(self, player, input):
        "See State::execute()"

        if self.store.accounts.hasId(input):
            player.write("An account by that name already exists.  Please choose a different name.")
        else:
            player.account = self.store.accounts.create(input) 
            player.write("Welcome to Python Mud, %s!" % player.account.name)
            return "get-new-account-password" 

        return self.NAME 
