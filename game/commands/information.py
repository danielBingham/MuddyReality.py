from interpreter.command import Command

class Report(Command):
    'Get information about your character.'
    
    def execute(self, player, arguments):
        character = player.character
        player.write("You are %s %s." % (character.name.title(), character.title))
        player.write("Your stats are:")
        player.write(character.abilities.toString())
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

    def execute(self, player, arguments):
        if arguments and arguments in self.DIRECTIONS:
            if arguments in player.character.room.exits:
                player.write(player.character.room.exits[arguments].describe(player))
            else:
                player.write("Nothing there.")
        else:
            player.write(player.character.room.describe(player), wrap=False)

class Examine(Command):
    'Get detailed information about a room, or object.'

    def execute(self, player, arguments):
        if not arguments:
            proxy = Look(self.library)
            proxy.execute(player, arguments)
        elif arguments:
            if arguments in Look.DIRECTIONS:
                proxy = Look(self.library)
                proxy.execute(player, arguments)
            elif player.character.room.isOccupant(arguments):
                occupant = player.character.room.getOccupant(arguments)
                player.write(occupant.detail()) 
            elif player.character.room.isObject(arguments):
                object = player.character.room.getObject(arguments)
                player.write(object.detail())

class Inventory(Command):
    'List the items in a character\'s inventory.'

    def execute(self, player, arguments):
        player.write("You are carrying:\n")
        if player.character.inventory:
            for object in player.character.inventory:
                player.write(object.name)
        else:
            player.write("Nothing.")

class Equipment(Command):
    'List the items the character currently has equipped.'

    def execute(self, player, arguments):
        equipment = player.character.equipment
        player.write("You are wearing: ")
        if ( equipment ):
            for location in equipment:
                player.write("%s on your %s" % (equipment[location].name, location))
        else:
            player.write("Nothing.")

