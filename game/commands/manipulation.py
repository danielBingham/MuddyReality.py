from interpreter.command import Command
import services.environment as environment
import services.equipment as equipment

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

        item = environment.findItemInRoom(player, arguments)
        if item:
            player.character.room.items.remove(item)
            player.character.inventory.append(item)
            player.write("You pick up " + item.description + ".")
            environment.writeToRoom(player, player.character.name + ' picks up ' + item.description+ '.')
        else:
            player.write("There doesn't seem to be a " + arguments + " to get.")


class Drop(Command):
    'Drop an item you are carrying.'

    def execute(self, player, arguments):
        if not arguments:
            player.write("Drop what?")
            return

        item = environment.findItemInInventory(player, arguments)
        if item: 
            player.character.inventory.remove(item)
            player.character.room.items.append(item)
            player.write("You drop " + item.description + ".")
            environment.writeToRoom(player, player.character.name + ' drops ' + item.description+ '.')
        else:
            player.write("You don't seem to be carrying a " + arguments + ".")

class Wield(Command):
    'Wield a weapon.'

    def execute(self, player, arguments):
        if not arguments:
            player.write("Wield what?")
            return

        item = equipment.findItemInInventory(player, arguments)
        if item:
            if "MeleeWeapon" in item.traits:
                player.character.inventory.remove(item)
                player.character.equipment['wield'] = item
                player.write("You wield " + item.name + ".")
                environment.writeToRoom(player, player.character.name + ' wields ' + item.description+ '.')
            else:
                player.write("You can't wield " + item.description + ".")
        else:
            player.write("You don't seem to have a " + arguments + ".")



