from game.interpreters.state.state import State

from game.account_menu.password import GetNewAccountPassword 

class CreateNewAccount(State):

    def introduction(self):
        self.player.setPrompt("Enter New Account Name: ")

    def execute(self, input):
        if self.store.accounts.hasId(input):
            self.player.write("An account by that name already exists.  Please choose a different name.")
        else:
            self.player.account = self.store.accounts.create(input) 
            self.player.write("Welcome to Python Mud, %s!" % self.player.account.name)
            return GetNewAccountPassword(self.player, self.library, self.store)

        return self

# End CreateNewAccount

