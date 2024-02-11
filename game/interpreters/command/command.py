class Command:
    """
    A base class for commands used by the CommandInterpreter. 
    """

    def __init__(self, time, library, store):
        """
        Initialize the command.

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

    def describe(self):
        """
        Provide a one line description of this command.

        Eg.
        `help - get help on the game's commands`

        Returns
        -------
        string
            The one line description.
        """

        pass

    def help(self):
        """
        Provide a detailed description of this command, its arguments, and how
        it functions in the game.

        Returns
        -------
        string
            Help entry for this command.
        """

        pass

    def execute(self, player, arguments):
        """
        Execute this command for `player` and `arguments`.

        Parameters
        ----------
        player: Player
            The player who is executing this command.
        arguments:  string
            The arguments to execute this command with.

        Returns
        void
        """

        pass
