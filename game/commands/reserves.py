from game.store.models.character import Character
from game.interpreters.command import Command
import game.library.environment as environment
import game.library.items as ItemLibrary

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
        if player.character.position == player.character.POSITION_SLEEPING:
            player.write("You can't eat in your sleep.")
            return

        if not arguments:
            player.write("Eat what?")
            return

        item = ItemLibrary.findItemByKeywords(player.character.inventory, arguments)
        if item and "Food" in item.traits:
            player.character.inventory.remove(item)
            player.character.reserves.calories += item.traits["Food"].calories
            player.write("You eat " + item.description + ".")
            environment.writeToRoom(player.character, player.character.name + ' eats ' + item.description+ '.')
        else:
            player.write("There doesn't seem to be a " + arguments + " to eat.")

class Drink(Command):
    ''

    def describe(self):
        return 'drink - consume water'

    def help(self):
        return ""

    def execute(self, player, arguments):
        if player.character.room.water == player.character.room.WATER_FRESH:
            player.character.thirst += 500

            player.write("You drink from the fresh water.")
            environment.writeToRoom(player.character, player.character.name + " drinks from the fresh water.")
            return
        else:
            player.write("There's not drinkable water here.")
            return


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
        if player.character.position == Character.POSITION_SLEEPING:
            player.write("You are already asleep.")
            return

        if player.character.reserves.sleep <= 4:
            player.character.position = Character.POSITION_SLEEPING
            player.write('You go to sleep.')
        else:
            player.write("You don't feel tired enough to sleep right now.")

class Wake(Command):
    'Attempt to wake up.'

    def describe(self):
        return "wake - attempt to wake up"

    def help(self):
        return """
wake

You will attempt to wake up before fully refreshed.
        """

    def execute(self, player, arguments):
        if player.character.position != Character.POSITION_SLEEPING:
            player.write("You are already awake.")
            return

        if player.character.reserves.sleep <= 4:
            player.write("You are too tired to wake.")
        else:
            player.character.position = Character.POSITION_STANDING
            player.write("You wake up.")

