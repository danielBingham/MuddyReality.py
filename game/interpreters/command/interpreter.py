import game.commands.communication as communication 
import game.commands.information as information 
import game.commands.movement as movement
import game.commands.manipulation as manipulation
import game.commands.crafting as crafting
import game.commands.reserves as reserves
import game.commands.system as system

class CommandInterpreter:
    'A simple command interpreter that parses the players input.'

    def __init__(self, library, store):
        self.store = store 
        self.library = library

        self.commands = {}

        self.commands['close'] = manipulation.Close(self, self.library, self.store)
        self.commands['craft'] = crafting.Craft(self, self.library, self.store)

        self.commands['down'] = movement.Down(self, self.library, self.store)
        self.commands['drink'] = reserves.Drink(self, self.library, self.store)
        self.commands['drop'] = manipulation.Drop(self, self.library, self.store)

        self.commands['east'] = movement.East(self, self.library, self.store)
        self.commands['eat'] = reserves.Eat(self, self.library, self.store)
        self.commands['equipment'] = information.Equipment(self, self.library, self.store)
        self.commands['examine'] = information.Examine(self, self.library, self.store)

        self.commands['get'] = manipulation.Get(self, self.library, self.store)

        self.commands['harvest'] = crafting.Harvest(self, self.library, self.store)
        self.commands['help'] = system.Help(self, self.library, self.store)

        self.commands['inventory'] = information.Inventory(self, self.library, self.store)

        self.commands['look'] = information.Look(self, self.library, self.store)

        self.commands['north'] = movement.North(self, self.library, self.store)

        self.commands['open'] = manipulation.Open(self, self.library, self.store)

        self.commands['quit'] = system.Quit(self, self.library, self.store)

        self.commands['south'] = movement.South(self, self.library, self.store)
        self.commands['say'] = communication.Say(self, self.library, self.store)
        self.commands['sleep'] = reserves.Sleep(self, self.library, self.store)
        self.commands['status'] = information.Status(self, self.library, self.store)

        self.commands['west'] = movement.West(self, self.library, self.store)
        self.commands['wield'] = manipulation.Wield(self, self.library, self.store)
        self.commands['wake'] = reserves.Wake(self, self.library, self.store)

        self.commands['up'] = movement.Up(self, self.library, self.store)

    def findCommand(self, input):
        for command in self.commands:
            if command.startswith(input):
                return self.commands[command]
        return None

    def interpret(self, player, input):
        if not input:
            return

        tokens = input.split(' ', 1)

        if not tokens: 
            return

        command = tokens[0].lower()
        if len(tokens) > 1:
            arguments = tokens[1]
        else:
            arguments = ''

        command_object = self.findCommand(command)
        if command_object:
            command_object.execute(player, arguments)
        else:
            player.write("I don't think you can do that...")

#
