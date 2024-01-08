class State:
    'A base state class as used by the StateInterpreter.'

    def __init__(self, player, library, store):
        self.library = library
        self.store = store
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
