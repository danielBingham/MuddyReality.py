from interpreter.command import Command
import services.environment as environment
import services.equipment as equipment

class Open(Command):
    'Open a door or an item'

    def describe(self):
        return "open - open a door or an item"

    def help(self):
        return """
open [direction|door|item]

Open will open a door or an item described by [direction|door|item].
        """
    
    def execute(self, player, arguments):
        room = player.character.room
        for direction in room.exits:
            if arguments == direction or arguments == room.exits[direction].name:
                room.exits[direction].open(player)
                return

        player.write("That doesn't appear to be something you can open.")

class Close(Command):
    'Close a door or an item'

    def describe(self):
        return "close - close a door or an item"

    def help(self):
        return """
close [direction|door|item]

Close will close a door or an item described by [direction|door|item].
        """
    
    def execute(self, player, arguments):
        room = player.character.room
        for direction in room.exits:
            if arguments == direction or arguments == room.exits[direction].name:
                room.exits[direction].close(player)
                return

        player.write("That doesn't appear to be something you can close.")

class Get(Command):
    'Get an item from the environment.'

    def describe(self):
        return "get - get an item from the current room and add it to your inventory"

    def help(self):
        return """
get [item]

Get an item described by [item] from the current room and add it to your inventory.
        """

    def execute(self, player, arguments):
        if not arguments:
            player.write("Get what?")
            return

        item = environment.findItemInRoom(player.character, arguments)
        if item:
            if item.can_pick_up:
                player.character.room.items.remove(item)
                player.character.inventory.append(item)
                player.write("You pick up " + item.description + ".")
                environment.writeToRoom(player.character, player.character.name + ' picks up ' + item.description+ '.')
            else:
                player.write("You can't pick up " + item.description)
        else:
            player.write("There doesn't seem to be a " + arguments + " to get.")


class Drop(Command):
    'Drop an item you are carrying.'

    def describe(self):
        return "drop - drop an item you are carrying"

    def help(self):
        return """
drop [item]

Drop an item described by [item] from your inventory and leave it in the current room.
        """

    def execute(self, player, arguments):
        if not arguments:
            player.write("Drop what?")
            return

        item = environment.findItemInInventory(player.character, arguments)
        if item: 
            player.character.inventory.remove(item)
            player.character.room.items.append(item)
            player.write("You drop " + item.description + ".")
            environment.writeToRoom(player.character, player.character.name + ' drops ' + item.description+ '.')
        else:
            player.write("You don't seem to be carrying a " + arguments + ".")

class Wield(Command):
    'Wield a weapon.'

    def describe(self):
        return "wield - wield a weapon"

    def help(self):
        return """
wield [item]

Wield an item described by [item] as a weapon.
        """

    def execute(self, player, arguments):
        if not arguments:
            player.write("Wield what?")
            return

        item = equipment.findItemInInventory(player.character, arguments)
        if item:
            if "MeleeWeapon" in item.traits:
                player.character.inventory.remove(item)
                player.character.equipment['wield'] = item
                player.write("You wield " + item.name + ".")
                environment.writeToRoom(player.character, player.character.name + ' wields ' + item.description+ '.')
            else:
                player.write("You can't wield " + item.description + ".")
        else:
            player.write("You don't seem to have a " + arguments + ".")
