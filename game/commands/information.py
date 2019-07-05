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

