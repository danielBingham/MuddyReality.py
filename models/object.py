from models.base import JsonSerializable
from models.base import Model

class Combat(JsonSerializable):
    'Represents the characteristics of an object that can be used in combat.'

    def __init__(self):
        self.hit = 0
        self.dodge = 0
        self.parry = 0

        self.armor = 0

    def toJson(self):
        return self.__dict__

    def fromJson(self, data):
       self.__dict__ = data
       return self

class Wearable(JsonSerializable):
    'Represents the characteristics of an object that can be worn.'

    EQUIPMENT_LOCATIONS = [
        'wielded',
        'held',
        'hands',
        'forearms',
        'torso',
        'legs',
        'feet',
        'head',
        'back',
        'waist',
        'neck'
    ]

    def __init__(self):
        self.locations = []
        
        self.warmth = 0
        self.armor = 0

    def toJson(self):
        return self.__dict__

    def fromJson(self, data):
       self.__dict__ = data
       return self

class Container(JsonSerializable):
    'Represents the characteristics of objects that are containers.'

    def __init__(self):
        self.contents = []

        self.volume = 0

    def toJson(self):
        return self.__dict__

    def fromJson(self, data):
       self.__dict__ = data
       return self


class Object(Model):

    def __init__(self, library):
        super(Object, self).__init__(library)

        self.name = ''
        self.description = ''
        self.details = ''
        self.keywords = [] 

        self.weight = 0

        self.uses = {} 

    def detail(self):
        return self.details

    def toJson(self):
        json = {}
        json['id'] = self.getId()
        json['name'] = self.name
        json['description'] = self.description
        json['details'] = self.details
        json['keywords'] = self.keywords

        json['uses'] = {}
        for use in self.uses:
            json['uses'][use] = self.uses[use].toJson()

        return json

    def fromJson(self, data):
        self.setId(data['id'])
        self.name = data['name']
        self.description = data['description']
        self.details = data['details']
        self.keywords = data['keywords']
        
        for use in data['uses']:
            classRef = globals()[use.title()]
            instance = classRef()
            instance.fromJson(data['uses'][use])
            self.uses[use] = instance

        return self

    @staticmethod
    def getBasePath():
        return 'data/objects/'


