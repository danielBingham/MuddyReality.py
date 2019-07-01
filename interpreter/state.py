##
# A basic state as used by the state interpreter.
##
class State:
    'A base state class as used by the StateInterpreter.'

    def __init__(self, player, library):
        self.library = library
        self.player = player
        self.introduction()

    ## 
    # Introduce this state to the player.  This can include laying out the state's options,
    # or presenting a menu, or doing any preparation for the state.
    ##
    def introduction(self):
        pass

    def execute(self, input):
        pass

## End State

##
# Handles interpreting in a state context, where the player's actions are limited by the state they
# are in and they can only move from the state they are in to certain other states.
#
# Executes the player's current state and then update's the state to the new one returned after the
# execution.
##
class StateInterpreter:
    'An interpreter to handle game modes involving a progression of states, where the available commands are defined by the state the player is in.'

    def __init__(self, player, library, initial_state):
        self.library = library 
        self.player = player
        self.state = initial_state 

    def interpret(self, input):
        self.state = self.state.execute(input)

## End StateInterpreter
