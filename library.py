import json
import glob

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
        account = Account(self)
        account.name = name
        self.accounts[account.name] = account
        return account

    def getAccountByName(self, name):
        if name in self.accounts:
            return self.accounts[name]
        else:
            return None

    def createCharacter(self, name):
        character = Character(self)
        character.name = name
        self.characters[name] = character
        return character

    def getCharacterByName(self, name):
        if name in self.characters:
            return self.characters[name]
        else:
            return None

    def load(self):
        print("Loading the game library.")

        print("Loading characters...")
        character_list = glob(Character.getBasePath() + '*.json')
        for file_path in character_list:
            character = Character(self)
            character.load(file_path)
            self.characters[character.name] = character

        print("Loading accounts...")
        account_list = glob(Account.getBasePath() + '*.json') 
        for file_path in account_list:
            account = Account(self)
            account.load(file_path)
            self.accounts[account.name] = account
