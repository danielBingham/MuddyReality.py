from game.store.models.character import Character
from game.interpreters.command.command import Command

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

        item = self.library.items.findItemByKeywords(player.character.inventory, arguments)
        if item and "Food" in item.traits:
            player.character.inventory.remove(item)
            player.character.reserves.calories += item.traits["Food"].calories
            player.write("You eat " + item.description + ".")
            self.library.environment.writeToRoom(player.character, player.character.name + ' eats ' + item.description+ '.')
        else:
            player.write("There doesn't seem to be a " + arguments + " to eat.")

class Drink(Command):
    ''

    def describe(self):
        return 'drink - consume water'

    def help(self):
        return ""

    def execute(self, player, arguments):
        if player.character.position == Character.POSITION_SLEEPING:
            player.write("You can't drink while you're asleep.")
            return

        if player.character.room.water_type == player.character.room.WATER_FRESH:
            player.character.reserves.thirst += 500

            player.write("You drink from the fresh water.")
            self.library.environment.writeToRoom(player.character, player.character.name + " drinks from the fresh water.")
            return
        else:
            player.write("There's no drinkable water here.")
            return

class Rest(Command):
    'Sit down and rest.'

    def describe(self):
        return "rest - sit down and rest"

    def help(self):
        return """
rest

Your character sits down to rest.
        """
    
    def execute(self, player, arguments):
        if player.character.position == Character.POSITION_SLEEPING:
            player.write("You can't rest while you're asleep.")
            return
        
        if player.character.position == Character.POSITION_RESTING:
            player.write("You are already resting.")
            return

        player.character.position = Character.POSITION_RESTING
        player.write('You sit down to rest.')
        self.library.environment.writeToRoom(player.character, "%s sits down to rest." % player.character.name.title())

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

        if player.character.reserves.wind <= player.character.reserves.max_wind:
            player.write("You'll need to catch your breath before you can go to sleep.")
            return

        if player.character.reserves.sleep / player.character.reserves.max_sleep <= 0.25:
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

