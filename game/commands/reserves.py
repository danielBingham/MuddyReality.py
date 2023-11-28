from models.character import Character
from interpreter.command import Command
import services.equipment as equipment
import services.environment as environment

class Eat(Command):
    'Get a food item from the inventory.'

    def describe(self):
        return "eat - consume an item as food"

    def help(self):
        return """
eat [item]

Attempt to eat an item described by [item] as food.
        """

    def execute(self, player, arguments):
        if not arguments:
            player.write("Eat what?")
            return

        item = equipment.findItemInInventory(player.character, arguments)
        if item and "Food" in item.traits:
            player.character.inventory.remove(item)
            player.character.reserves.calories += item.traits["Food"].calories
            player.write("You eat " + item.description + ".")
            environment.writeToRoom(player.character, player.character.name + ' eats ' + item.description+ '.')
        else:
            player.write("There doesn't seem to be a " + arguments + " to eat.")

class Sleep(Command):
    'Go to sleep.'

    def describe(self):
        return "sleep - go to sleep"

    def help(self):
        return """
sleep

Will put your character to sleep.  You will awaken once refreshed.
        """

    def execute(self, player, arguments):
        if player.character.reserves.sleep <= 4:
            player.character.position = Character.POSITION_SLEEPING
            player.write('You go to sleep.')
        else:
            player.write("You don't feel tired enough to sleep right now.")
