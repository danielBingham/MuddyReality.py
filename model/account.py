import json
import os

from model.model import Model 
from model.character import Character


class Account(Model):
    'Represents the account of a player, organizing their characters.'

    def __init__(self, library):
        super(Account, self).__init__(library)

        self.name  = '' 
        self.password = ''

        self.characters = {} 

    def toJson(self):
        json = {}
        json['name'] = '' 
        json['password'] = self.password

        json['characters'] = []
        for name in self.characters:
            json['characters'].append(name)

        return json

    def fromJson(self, data):
        self.name = data['name']
        self.id = self.name
        self.password = data['password']

        for name in data['characters']:
            self.characters[name] = self.library.getCharacterByName(name)
            self.characters[name].account = self

        return self

    @staticmethod
    def getBasePath():
        return 'data/accounts/'

    def getFilePath(self):
        return self.getBasePath() + self.name + '.json'



