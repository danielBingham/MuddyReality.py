from game.interpreters.command.command import Command

class North(Command):
    'Go north'

    def describe(self):
        return "north - travel to the north"

    def help(self):
        return """
north

Go to the room to the north, if possible.
        """
    
    def execute(self, player, arguments):
        self.library.movement.move('north', player, arguments)
            
class East(Command):
    'Go east'

    def describe(self):
        return "east - travel to the east"

    def help(self):
        return """
east

Go to the room to the east, if possible.
        """
    
    def execute(self, player, arguments):
        self.library.movement.move('east', player, arguments)

class South(Command):
    'Go south'

    def describe(self):
        return "south - travel to the south"

    def help(self):
        return """
south

Go to the room to the south, if possible.
        """
    
    def execute(self, player, arguments):
        self.library.movement.move('south', player, arguments)

class West(Command):
    'Go west'

    def describe(self):
        return "west - travel to the west"

    def help(self):
        return """
west

Go to the room to the west, if possible.
        """
    
    def execute(self, player, arguments):
        self.library.movement.move('west', player, arguments)

class Up(Command):
    'Go up'

    def describe(self):
        return "up - travel up"

    def help(self):
        return """
up

Go to the room above, if possible.
        """
    
    def execute(self, player, arguments):
        self.library.movement.move('up', player, arguments)

class Down(Command):
    'Go down'

    def describe(self):
        return "down - travel down"

    def help(self):
        return """
down

Go to the room below, if possible.
        """
    
    def execute(self, player, arguments):
        self.library.movement.move('down', player, arguments)

