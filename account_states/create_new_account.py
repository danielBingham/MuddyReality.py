from state import State
from get_new_account_password import GetNewAccountPassword

class CreateNewAccount(State):

    def introduction(self):
        self.player.setPrompt("\n\nEnter New Account Name: ")

    def execute(self, input):
        account = self.library.getAccountByName(input)
        if account:
            self.player.write("An account by that name already exists.  Please choose a different name.")
        else:
            self.player.account = self.library.createAccount(input) 
            self.player.write("Welcome to Python Mud, %s!\n" % self.player.account.name)
            return GetNewAccountPassword(self.player, self.library)

        return self
