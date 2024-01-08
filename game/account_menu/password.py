from game.interpreters.state.state import State

import game.account_menu.menu 

class GetNewAccountPassword(State):

    def introduction(self):
        self.player.setPrompt("Enter New Password: ")

    def execute(self, input):
        if self.player.account:
            state = ConfirmNewAccountPassword(self.player, self.library, self.store, input)
            return state
        else:
            raise RuntimeError('Players setting new passwords must have accounts!')

# End GetNewAccountPassword

class ConfirmNewAccountPassword(State):

    def __init__(self, player, store, password):
        super(ConfirmNewAccountPassword, self).__init__(player, store)
        self.password = password

    def introduction(self):
        self.player.setPrompt("Confirm Password: ")

    def execute(self, input):
        if self.player.account and input == self.password:
            self.player.account.setPassword(input)
            self.player.account.save('data/accounts/')
            return account.menu.AccountMenu(self.player, self.library, self.store)
        elif self.player.account:
            self.player.write("Passwords didn't match.  Please try again.")
            return GetNewAccountPassword(self.player, self.library, self.store)
        else:
            raise RuntimeError('Players setting new passwords must have accounts!')

# End GetNewAccountPassword
