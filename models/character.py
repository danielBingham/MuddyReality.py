import json

from base import Model
from base import JsonSerializable

class Abilities(JsonSerializable):
    'Represents a character\'s abilities and attributes.'

    def __init__(self):
        self.dexterity = 0
        self.strength = 0
        self.constitution = 0
        self.intelligence = 0
        self.wisdom = 0
        self.perception = 0
        self.willpower = 0
        self.charisma = 0

    def toJson(self):
        return self.__dict__

    def fromJson(self, data):
        self.__dict__ = data
        return self

class Reserves(JsonSerializable):
    'Represents a characters reserves: their health, magic, and energy.'

    def __init__(self):
        self.health = 0
        self.mana = 0
        self.vigor = 0

    def toJson(self):
        return self.__dict__

    def fromJson(self, data):
        self.__dict__ = data
        return self


class Character(Model):
    'Represents a single character in the game.'

    EQUIPMENT_LOCATIONS = [
        'left-hand',
        'right-hand',
        'forearms',
        'torso',
        'legs',
        'feet',
        'head',
        'back',
        'waist',
        'neck'
    ]


    def __init__(self, library):
        super(Character, self).__init__(library)
        
        self.account = None

        self.name = '' 
        self.title = ''
        
        self.experience = 0

        self.abilities = Abilities()
        self.reserves = Reserves()

        self.equipment = {}
        self.inventory = []


    def toJson(self):
        json = {}

        json['name'] = self.name
        json['title'] = self.title

        json['experience'] = self.experience
        
        json['abilities'] = self.abilities.toJson()
        json['reserves'] = self.reserves.toJson()

        
        return json

    def fromJson(self, data):
        self.name = data['name']
        self.id = self.name

        self.title = data['title']

        self.experience = data['experience']

        self.abilities = Abilities()
        self.abilities.fromJson(data['abilities'])

        self.reserves = Reserves()
        self.reserves.fromJson(data['reserves'])

        return self

    @staticmethod
    def getBasePath():
        return 'data/characters/'
