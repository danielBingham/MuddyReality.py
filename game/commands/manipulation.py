from interpreter.command import Command


class Open(Command):
    'Open a door or an item'
    
    def execute(self, player, arguments):
        room = player.character.room
        for direction in room.exits:
            if arguments == direction or arguments == room.exits[direction].name:
                room.exits[direction].open(player)
                return

        player.write("That doesn't appear to be something you can open.")

class Close(Command):
    'Close a door or an item'
    
    def execute(self, player, arguments):
        room = player.character.room
        for direction in room.exits:
            if arguments == direction or arguments == room.exits[direction].name:
                room.exits[direction].close(player)
                return

        player.write("That doesn't appear to be something you can close.")

class Get(Command):
    'Get an item from the environment.'

    def execute(self, player, arguments):
        if not arguments:
            player.write("Get what?")
            return

        items = player.character.room.items
        for item in items:
            if arguments in item.keywords:
                items.remove(item)
                player.character.inventory.append(item)
                player.write("You pick up " + item.name + ".")
                return

        player.write("There doesn't seem to be a " + arguments + " to get.")



class Drop(Command):
    'Drop an item you are carrying.'

    def execute(self, player, arguments):
        if not arguments:
            player.write("Drop what?")
            return

        for item in player.character.inventory:
            if arguments in item.keywords:
                player.character.inventory.remove(item)
                player.character.room.items.append(item)
                player.write("You drop " + item.name + ".")
                return

        player.write("You don't seem to be carrying a " + arguments + ".")

class Wield(Command):
    'Wield a weapon.'

    def execute(self, player, arguments):
        if not arguments:
            player.write("Wield what?")
            return

        inventory = player.character.inventory
        for item in inventory:
            if arguments in item.keywords:
                if "MeleeWeapon" in item.uses:
                    player.write("You wield " + item.name + ".")
                    inventory.remove(item)
                    player.character.equipment['wield'] = item

                    for occupant in player.character.room.occupants:
                        if occupant.player:
                            occupant.player.write(player.character.name + ' wields ' + item.name + '.')
                else:
                    player.write("You can't wield " + item.name + ".")
                return

        player.write("You don't seem to have a " + arguments + ".")



