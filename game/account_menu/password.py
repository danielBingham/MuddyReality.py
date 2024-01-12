from game.interpreters.state.state import State

import game.account_menu.menu 


class GetNewAccountPassword(State):
    "Get a new password for an account."

    NAME="get-new-account-password"

    def introduce(self, player):
        "See State::introduce()"

        player.setPrompt("Enter New Password: ")

    def execute(self, player, input):
        "See State::execute()"

        if player.account:
            player.account_state_data['password'] = input
            return "confirm-new-account-password" 
        else:
            raise RuntimeError('Players setting new passwords must have accounts!')


class ConfirmNewAccountPassword(State):
    "Confirm the player's newly set account password."

    NAME="confirm-new-account-password"

    def introduce(self, player):
        "See State::introduce()"

        player.setPrompt("Confirm Password: ")

    def execute(self, player, input):
        "See State::execute()"

        if player.account and input == player.account_state_data['password']:
            player.account.setPassword(input)
            self.store.saveAccount(player.account)
            del player.account_state_data['password']
            return "account-menu" 
        elif player.account:
            player.write("Passwords didn't match.  Please try again.")
            return "get-new-account-password" 
        else:
            raise RuntimeError('Players setting new passwords must have accounts!')

