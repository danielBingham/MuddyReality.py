from account_states.state import State
from account_states.create_new_account import CreateNewAccount
from account_states.get_account_password import GetAccountPassword

class GetAccountName(State):

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
