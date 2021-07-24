class AdminCommand:
    'A base class for use by all admin commands. Interpreted by the AdminCommandInterpreter'

    def __init__(self, library):
        self.library = library 

    def help(self):
        pass

    def execute(self, player, arguments):
        pass

# End Command

class AdminCommandInterpreter:
    'A simple admin command interpreter that parses the players input.'

    def __init__(self, player, library):
        self.player = player
        self.library = library 

    def interpret(self, input):
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

        command_object = self.library.findCommand(command)
        if command_object:
            command_object.execute(self.player, arguments)
        else:
            self.player.write("I don't think you can do that...")

# End CommandInterpreter
