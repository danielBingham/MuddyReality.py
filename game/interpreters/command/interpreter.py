class CommandInterpreter:
    """
    A command interpreter that parses player input using a `command arguments`
    format, where each `command` has a one to one relationship with a `Command`
    object that handles parsing the `arguments` and performing any resulting
    actions.  The interpreter takes a dictionary of `Command` objects keyed by
    their associated `command` strings and uses that to interpret player input.
    """

    def __init__(self, commands, library, store):
        """
        Initialize the interpreter.

        Parameters
        ----------
        commands:   dict[command] => Command
            A dictionary of Command object keyed by their `command` string.
        library:    Library
            The game library.
        store:  Store
            The game store.
        """

        self.store = store 
        self.library = library
        self.commands = commands

    def findCommand(self, input):
        """
        Find the command matching `input`.

        Parameters
        ----------
        input:  string
            The input string we're going to match.

        Returns
        -------
        Command
            The matched `Command` object.  Or `None` if no object matched.
        """
            
        for command in self.commands:
            if command.startswith(input):
                return self.commands[command]
        return None

    def interpret(self, player, input):
        """
        Interpret a player's input, finding the matching command argument and
        then executing it with any remaining arguments.

        Parameters
        ----------
        player: Player
            The player who's input we're interpreting.
        input:  string
            The input we're interpreting.

        Returns
        -------
        void
        """

        if not input:
            return

        tokens = input.split(' ', 1)

        if not tokens: 
            return

        command = tokens[0].lower()
        if len(tokens) > 1:
            arguments = tokens[1]
        else:
            arguments = ''

        command_object = self.findCommand(command)
        if command_object:
            command_object.execute(player, arguments)
        else:
            player.write("I don't think you can do that...")

#
