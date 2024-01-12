import json, os, bcrypt 

from game.store.models.base import NamedModel 
from game.store.models.character import Character


class Account(NamedModel):
    'Represents the account of a player, organizing their characters.'

    def __init__(self):
        super(Account, self).__init__()

        self.password_hash = ''

        self.characters = {} 

    def addCharacter(self, character):
        self.characters[character.name] = character
        character.account = self
        self.save('data/accounts/')
        return self

    def setPassword(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return self

    def isPassword(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash)

    def toJson(self):
        json = {}
        json['name'] = self.name 

        json['password_hash'] = self.password_hash.decode('utf-8', 'strict')

        json['characters'] = []
        for name in self.characters:
            json['characters'].append(name)

        return json

    def fromJson(self, data):
        self.setId(data['name'])

        self.password_hash = data['password_hash'].encode('utf-8')

        # Store will convert the list of names to actual object references in
        # Store::load
        self.characters = data['characters']

        return self
