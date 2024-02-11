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


class Walk(Command):
    'Start walking'

    def describe(self):
        return "walk - set movement speed to walking"

    def help(self):
        return """
walk

Your character will now walk when moving.
        """

    def execute(self, player, arguments):
        player.character.speed = player.character.SPEED_WALKING
        player.write("You begin to walk.")
        self.library.room.writeToRoom(player.character, "%s begins to walk." % player.character.name)


class Run(Command):
    'Start running'

    def describe(self):
        return "run - set movement speed to run"

    def help(self):
        return """
run

Your character will now run when moving.  You will run through 2 rooms in a single move.
        """

    def execute(self, player, arguments):
        player.character.speed = player.character.SPEED_RUNNING
        player.write("You begin to run.")
        self.library.room.writeToRoom(player.character, "%s begins to run." % player.character.name)


class Sprint(Command):
    'Start sprinting'

    def describe(self):
        return "sprint - set movement speed to sprinting"

    def help(self):
        return """
sprint

Your character will now sprint when moving.  You will run through 4 rooms in a single move.
        """

    def execute(self, player, arguments):
        player.character.speed = player.character.SPEED_SPRINTING
        player.write("You begin to sprint.")
        self.library.room.writeToRoom(player.character, "%s begins to sprint." % player.character.name)
