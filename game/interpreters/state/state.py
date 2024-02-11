class State:
    "A base class for States used with the StateInterpreter."

    def __init__(self, time, library, store):
        """
        Initialize the state.

        Parameters
        ----------
        library:    Library
            The game library.
        store:  Store
            The game store.
        """

        self.time = time
        self.library = library
        self.store = store

    def introduce(self, player):
        """
        Introduce this state to the player, giving them any introductory text
        to explain the state and setting the player's prompt.

        Parameters 
        ----------
        player: Player
            The player to whom we want to introduce this state.

        Returns
        -------
        void
        """

        pass

    def execute(self, player, input):
        """
        Execute the behavior defined for the current state with the given `input`.

        Parameters
        ----------
        player: Player
            The player who is in this state and who has provided `input`.
        input: string
            The input string provided by `player`.

        Returns
        -------
        next_state: string
            The next state for `player`.  Could just be the current state.
        """

        pass
