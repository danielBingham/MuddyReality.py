##
# Handles interpreting in a state context, where the player's actions are limited by the state they
# are in and they can only move from the state they are in to certain other states.
#
# Executes the player's current state and then update's the state to the new one returned after the
# execution.
##
class StateInterpreter:
    'An interpreter to handle game modes involving a progression of states, where the available commands are defined by the state the player is in.'

    def interpret(self, player, input):
        player.account_state = player.account_state.execute(input)

## End StateInterpreter
