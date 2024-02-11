class StateInterpreter:
    """
    Handles interpreting in a state context, where the player's actions are
    limited by the state they are in and they can only move from the state they
    are in to certain other states.

    Executes the player's current state and then updates the state to the new
    one returned after the execution.
    """

    def __init__(self, states, library, store):
        """
        Initialize the StateInterpreter. 

        Parameters
        ----------
        states: dictionary[state]
            A dictionary containing all the possible states, keyed by their
            state name.
        library: Library
            The game library.
        store:  Store
            The game store.
        """

        self.library = library
        self.store = store
        self.states = states 

    def introduce(self, player):
        """
        Introduce the current state assigned to `player`.

        Parameters
        ----------
        player: Player
            The player to introduce to their current state.

        Returns
        -------
        void
        """

        state = self.states[player.current_account_state]
        state.introduce(player)

    def interpret(self, time, player, input):
        """
        Execute the state assigned to `player` with `input`.

        Parameters
        ----------
        player: Player
            The player who we're going to execute the state for.
        input:  string
            Input given by `player` to execute with.

        Returns
        -------
        void
        """

        state = self.states[player.current_account_state]
        player.setAccountState(state.execute(time, player, input))

