import json

from models.base import NamedModel
from models.base import JsonSerializable

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
    'Represents a characters reserves: their health, magic, and energy.'

    def __init__(self):
        self.health = 0
        self.mana = 0
        self.vigor = 0

    def toString(self):
        return ("You have %d health, %d mana, and %d vigor." %
            (self.health, self.mana, self.vigor))

    def toJson(self):
        return self.__dict__

    def fromJson(self, data):
        self.__dict__ = data
        return self


class Character(NamedModel):
    'Represents a single character in the game.'

    def __init__(self, library):
        super(Character, self).__init__(library)
        
        self.account = None
        self.player = None

        self.title = ''
       
        self.level = 1
        self.experience = 0

        self.abilities = Abilities()
        self.reserves = Reserves()

        self.equipment = {}
        self.inventory = []

        self.room = None

    def wield(self, object):
        return False

    def describe(self):
        return ("%s %s\n" % (self.name, self.title))

    def detail(self):
        details = ("%s %s\n" % (self.name, self.title))
        for item in equipment:
            details += ("%s on %s\n" % (item, self.equipment[item].name))
        return details

    def leave(self, room, direction=''):
        room.occupants.remove(self)
        self.room = None
        for occupant in room.occupants:
            if occupant.player:
                if direction:
                    occupant.player.write(self.name.title() + " leaves to the " + direction + ".")
                else:
                    occupant.player.write(self.name.title() + " leaves.")

    def enter(self, room, direction=''):
        for occupant in room.occupants:
            if occupant.player:
                if direction:
                    occupant.player.write(self.name.title() + " enters from the " + room.INVERT_DIRECTION[direction])
                else:
                    occupant.player.write(self.name.title() + " enters.")
        room.occupants.append(self)
        self.room = room

    def initialize(self):
        self.reserves.health = int(self.abilities.constitution*1.5) \
                + int(self.abilities.strength*0.5) 
        self.reserves.mana = self.abilities.intelligence \
            + int(self.abilities.wisdom * 0.75) \
            + int(self.abilities.willpower * 0.5) \
            + int(self.abilities.perception * 0.25) 
        self.reserves.vigor = int(self.abilities.constitution * 4) \
            + int(self.abilities.willpower * 3.5) \
            + int(self.abilities.strength * 2.5) 


    def toJson(self):
        json = {}

        json['name'] = self.name
        json['title'] = self.title

        json['experience'] = self.experience
        
        json['abilities'] = self.abilities.toJson()
        json['reserves'] = self.reserves.toJson()

        if self.room:
            json['room'] = self.room.getId()

        
        return json

    def fromJson(self, data):
        self.setId(data['name'])

        self.title = data['title']

        self.experience = data['experience']

        self.abilities = Abilities()
        self.abilities.fromJson(data['abilities'])

        self.reserves = Reserves()
        self.reserves.fromJson(data['reserves'])

        # lazy migrations
        if 'room' in data:
            self.room = self.library.rooms.getById(data['room'])

        return self

    @staticmethod
    def getBasePath():
        return 'data/characters/'
