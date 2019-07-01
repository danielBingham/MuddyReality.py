from state import State
from account_menu import AccountMenu

class GetAccountPassword(State):

    def introduction(self):
        self.player.setPrompt("Password: ")

    def execute(self, input):
        if self.player.account.password == input:
            return AccountMenu(self.player, self.library)
        else:
            player.write("Incorrect password.\n\n")

# End GetAccountPassword
