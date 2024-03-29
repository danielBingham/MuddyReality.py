from game.interpreters.command.command import Command


class Status(Command):
    'Get information about your character.'

    def describe(self):
        return "Status - get information about your character"

    def help(self):
        return """
report

Get detailed information about your character.
        """

    def execute(self, player, arguments):
        character = player.character
        player.write("You are %s." % (character.name.title()))
        player.write("You are %s and %s." % (character.position, character.speed))
        player.write(character.reserves.toString())


class Look(Command):
    'Get information about the current room.'

    DIRECTIONS = [
        'north',
        'east',
        'south',
        'west',
        'up',
        'down'
    ]

    def describe(self):
        return "look - look around your environment"

    def help(self):
        return """
look [op:direction]

Look around.  If [direction] is excluded, then you will look at your current room.  If [direction] is included, you will look in that direction.
        """

    def execute(self, player, arguments):
        if player.character.position == player.character.POSITION_SLEEPING:
            player.write("You can't see in your sleep.")
            return

        if arguments and arguments in self.DIRECTIONS:
            if arguments in player.character.room.exits:
                exit = player.character.room.exits[arguments]
                player.write(self.library.room.describe(exit.room_to, player), wrap=False)
            else:
                player.write("Nothing there.")
        else:
            player.write(self.library.room.describe(player.character.room, player), wrap=False)


class Examine(Command):
    'Get detailed information about a room, or object.'

    def describe(self):
        return "examine - get detailed information about a room or object"

    def help(self):
        return """
examine [op:object]

Get detailed information about a room or object.  If [object] is excluded, the room will be described.  Otherwise [object] will be examined.
        """

    def execute(self, player, arguments):
        if player.character.position == player.character.POSITION_SLEEPING:
            player.write("You can't examine anything in your sleep.")
            return

        if not arguments:
            proxy = Look(self.store)
            return proxy.execute(player, arguments)

        if arguments in Look.DIRECTIONS:
            proxy = Look(self.store)
            return proxy.execute(player, arguments)

        item = self.library.item.findItemByKeywords(player.character.inventory, arguments)
        if item:
            player.write(self.library.item.detail(item))
            return

        for occupant in player.character.room.occupants:
            if occupant.name.startswith(arguments):
                player.write(occupant.detail())
                return

        item = self.library.item.findItemByKeywords(player.character.room.items, arguments)
        if item:
            player.write(self.library.item.detail(item))
            return

        player.write("There doesn't seem to be a " + arguments + " to examine.")


class Inventory(Command):
    "List the items in a character's inventory."

    def describe(self):
        return "inventory - list your current inventory"

    def help(self):
        return """
inventory

List the current contents of your inventory.
        """

    def execute(self, player, arguments):
        if player.character.position == player.character.POSITION_SLEEPING:
            player.write("You can't check your inventory in your sleep.")
            return

        player.write("You are carrying:\n")
        if player.character.inventory:
            for item in player.character.inventory:
                player.write(self.library.item.describe(item))
        else:
            player.write("Nothing.")


class Equipment(Command):
    'List the items the character currently has equipped.'

    def describe(self):
        return "equipment - list current equipment"

    def help(self):
        return """
equipment

List the equipment you are currently wearing, carrying, and wielding.
        """

    def execute(self, player, arguments):
        if player.character.position == player.character.POSITION_SLEEPING:
            player.write("You can't check your equipment in your sleep.")
            return

        equipment = player.character.body.worn
        player.write("You are wearing: ")
        if (equipment):
            for location in equipment:
                player.write("%s on your %s" % (self.library.item.describe(equipment[location]), location))
        else:
            player.write("Nothing.")

class Time(Command):
    'Get information about the time.'

    def describe(self):
        return "Time - get information about the date and time"

    def help(self):
        return """
time

Get information about the date and time.
        """

    def execute(self, player, arguments):
        time = self.store.world.time

        ## Time of day based on hour.
        if time.hour <= 6:
            player.write("It is night.")
        elif time.hour == 7:
            player.write("It is dawn.")
        elif time.hour > 7 and time.hour < 12:
            player.write("It is morning.")
        elif time.hour == 12:
            player.write("It is noon.")
        elif time.hour > 12 and time.hour < 19:
            player.write("It is afternoon.")
        elif time.hour == 19:
            player.write("It is dusk.")
        elif time.hour >= 20:
            player.write("It is night.")

        ## Seasons based on months
        player.write("It is %s." % (time.SEASON_NAME[time.month]))
         

