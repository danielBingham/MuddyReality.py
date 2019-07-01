from model.account import Account
from model.character import Character

from commands.say import Say

class Library:
    'A library of game content.'

    def __init__(self):
        self.players = []
        self.accounts = {}
        self.characters = {}
        self.rooms = {}
        self.mobs = {}
        self.objects = {}
        self.commands = {}

        self.loadCommands()

    def loadCommands(self):
        self.commands['say'] = Say(self)

    def getCommand(self, command_name):
        if command_name in self.commands:
            return self.commands[command_name]
        else:
            return None


    def createAccount(self, name):
        account = Account()
        account.name = name
        self.accounts[account.name] = account
        return account

    def getAccountByName(self, name):
        if name in self.accounts:
            return self.account[name]
        else:
            return None

    def load(self):
        pass

    def save(self):
        pass
