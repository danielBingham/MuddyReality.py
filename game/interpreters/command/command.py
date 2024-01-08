class Command:
    'A base class for use by all commands. Interpreted by the CommandInterpreter'

    def __init__(self, interpreter, library, store):
        self.interpreter = interpreter
        self.library = library
        self.store = store 
    
    def describe(self):
        pass

    def help(self):
        pass

    def execute(self, player, arguments):
        pass
