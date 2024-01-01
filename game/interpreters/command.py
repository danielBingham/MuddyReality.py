class Command:
    'A base class for use by all commands. Interpreted by the CommandInterpreter'

    def __init__(self, store):
        self.store = store 
    
    def describe(self):
        pass

    def help(self):
        pass

    def execute(self, player, arguments):
        pass

# End Command

class CommandInterpreter:
    'A simple command interpreter that parses the players input.'

    def __init__(self, player, store):
        self.player = player
        self.store = store 

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

        command_object = self.store.findCommand(command)
        if command_object:
            command_object.execute(self.player, arguments)
        else:
            self.player.write("I don't think you can do that...")

# End CommandInterpreter
