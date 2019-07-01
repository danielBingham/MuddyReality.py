from account_states.state import State
from account_states.account_menu import AccountMenu

class GetNewAccountPassword(State):

    def introduction(self):
        self.player.setPrompt("\n\nEnter New Password: ")

    def execute(self, input):
        if self.player.account:
            self.player.account.password = input
            return AccountMenu(self.player, self.library)
        else:
            raise RuntimeError('Players setting new passwords must have accounts!')

