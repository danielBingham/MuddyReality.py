import json

from game.library.models.base import NamedModel
from game.library.models.base import JsonSerializable

class Abilities(JsonSerializable):
    'Represents a character\'s abilities and attributes.'

    def __init__(self):
        self.dexterity = 8 
        self.strength = 8 
        self.constitution = 8 
        self.intelligence = 8 
        self.wisdom = 8 
        self.perception = 8 
        self.willpower = 8 
        self.charisma = 8 


    def toString(self):
        return ("Str: %-2d Dex: %-2d Con: %-2d Int: %-2d Wis: %-2d Wil: %-2d Per: %-2d Cha: %-2d" %
                (self.strength, self.dexterity, self.constitution, self.intelligence, self.wisdom,
                self.willpower, self.perception, self.charisma))


    def toJson(self):
        return self.__dict__

    def fromJson(self, data):
        self.__dict__ = data
        return self

class Reserves(JsonSerializable):
    'Represents a characters reserves: how well fed and well rested they are.'

    def __init__(self):
        self.calories = 2400
        self.sleep = 16 

    def hungerString(self, prompt=False):
        hunger = ''

        if prompt and self.calories > 1200:
            return hunger

        if self.calories > 1200:
            hunger = 'not hungry'
        elif self.calories > 800:
            hunger = 'hungry'
        elif self.calories > 400:
            hunger = 'very hungry'
        elif self.calories > 0:
            hunger = 'extremely hungry'
        elif self.calories <= 0:
            hunger = 'starving'
        return hunger

    def sleepString(self, prompt=False):
        tired = ''
        if prompt and self.sleep > 8:
            return tired

        if self.sleep > 8:
            tired = 'not sleepy'
        elif self.sleep > 4:
            tired = 'a little sleepy'
        elif self.sleep > 0:
            tired = 'sleepy'
        else:
            tired = 'exhausted'
        return tired

    def toString(self):
        return ("You are %s and %s." %
            (self.hungerString(), self.sleepString()))

    def toJson(self):
        return self.__dict__

    def fromJson(self, data):
        self.__dict__ = data
        return self


class Character(NamedModel):
    'Represents a single character in the game.'

    POSITION_SPRINTING = 'sprinting'
    POSITION_RUNNING = 'running'
    POSITION_WALKING = 'walking'
    POSITION_STANDING = 'standing'
    POSITION_SITTING = 'sitting'
    POSITION_LAYING_DOWN = 'laying down'
    POSITION_SLEEPING = 'sleeping'

    def __init__(self):
        super(Character, self).__init__()
        
        self.account = None
        self.player = None

        self.title = ''
       
        self.level = 1
        self.experience = 0

        self.position = self.POSITION_STANDING

        self.abilities = Abilities()
        self.reserves = Reserves()

        self.equipment = {}
        self.inventory = []

        self.room = None

    def describe(self):
        return ("%s %s\n" % (self.name, self.title))

    def detail(self):
        details = ("%s %s\n" % (self.name, self.title))
        for item in equipment:
            details += ("%s on %s\n" % (item, self.equipment[item].name))
        return details

    def toJson(self):
        json = {}

        json['name'] = self.name
        json['title'] = self.title

        json['experience'] = self.experience
        json['position'] = self.position
        
        json['abilities'] = self.abilities.toJson()
        json['reserves'] = self.reserves.toJson()

        if self.room:
            json['room'] = self.room.getId()

        
        return json

    def fromJson(self, data):
        self.setId(data['name'])

        self.title = data['title']

        self.experience = data['experience']
        self.position = data['position']

        self.abilities = Abilities()
        self.abilities.fromJson(data['abilities'])

        self.reserves = Reserves()
        self.reserves.fromJson(data['reserves'])

        # lazy migrations
        if 'room' in data:
            self.room = data['room']

        return self
