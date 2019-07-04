from state import State

from menu import AccountMenu

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

# End CreateNewAccount

class GetNewAccountPassword(State):

    def introduction(self):
        self.player.setPrompt("\n\nEnter New Password: ")

    def execute(self, input):
        if self.player.account:
            self.player.account.password = input
            return AccountMenu(self.player, self.library)
        else:
            raise RuntimeError('Players setting new passwords must have accounts!')

# End GetNewAccountPassword
