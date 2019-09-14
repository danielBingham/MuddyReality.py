from interpreter.command import Command


class Open(Command):
    'Open a door or an object'
    
    def execute(self, player, arguments):
        room = player.character.room
        for direction in room.exits:
            if arguments == direction or arguments == room.exits[direction].name:
                room.exits[direction].open(player)
                return

        player.write("That doesn't appear to be something you can open.")

class Close(Command):
    'Close a door or an object'
    
    def execute(self, player, arguments):
        room = player.character.room
        for direction in room.exits:
            if arguments == direction or arguments == room.exits[direction].name:
                room.exits[direction].close(player)
                return

        player.write("That doesn't appear to be something you can close.")

class Get(Command):
    'Get an object from the environment.'

    def execute(self, player, arguments):
        if not arguments:
            player.write("Get what?")
            return


        objects = player.character.room.objects
        for object in objects:
            if arguments in object.keywords:
                objects.remove(object)
                player.character.inventory.append(object)
                player.write("You pick up " + object.name + ".")
                return

        player.write("There doesn't seem to be a " + arguments + " to get.")



class Drop(Command):
    'Drop an object you are carrying.'

    def execute(self, player, arguments):
        if not arguments:
            player.write("Drop what?")
            return

        for object in player.character.inventory:
            if arguments in object.keywords:
                player.character.inventory.remove(object)
                player.character.room.objects.append(object)
                player.write("You drop " + object.name + ".")
                return

        player.write("You don't seem to be carrying a " + arguments + ".")

class Wield(Command):
    'Wield a weapon.'

    def execute(self, player, arguments):
        if not arguments:
            player.write("Wield what?")
            return

        inventory = player.character.inventory
        for object in inventory:
            if arguments in object.keywords:
                if player.character.wield(object):
                    player.write("You wield " + object.name + ".")
                    inventory.remove(object)
                else:
                    player.write("You can't wield " + object.name + ".")
                return

        player.write("You don't seem to have a " + arguments + '.")



