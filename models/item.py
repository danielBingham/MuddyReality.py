from models.base import JsonSerializable
from models.base import Model

class MeleeWeapon(JsonSerializable):
    'Contains the properties of a melee weapon.  Composable into an Item to give it the use as a Melee Weapon.'

    SLASHING = 'slashing'
    CRUSHING = 'crushing'
    HACKING = 'hacking'
    SMITING = 'smiting'
    STABBING = 'stabbing'
    NONE = 'none'

    TYPES = [
        'slashing',
        'crushing',
        'hacking',
        'smiting',
        'stabbing'
    ]

    def __init__(self):

        # The minimum damage the weapon does on striking.
        self.minDamage = 0

        # The maximum damage the weapon can do on striking.
        self.maxDamage = 0

        # What type of weapon this is, what kind of damage does it do?
        self.type = MeleeWeapon.NONE

    def toPrototypeJson(self):
        return self.toJson()

    def fromPrototypeJson(self, data):
        return self.fromJson(data)

    def toJson(self):
        return self.__dict__

    def fromJson(self, data):
       self.__dict__ = data
       return self

class Wearable(JsonSerializable):
    'Contains the properties of a wearable item.  Composable into an Item to make it Wearable.'
    
    HANDS = 'hands'
    FOREARMS = 'forearms'
    TORSO = 'torso'
    LEGS = 'legs'
    FEET = 'feet'
    HEAD = 'head'
    BACK = 'back'
    WAIST = 'waist'
    NECK = 'neck'
    NONE = 'none'

    LOCATIONS = [
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

        # The location this item may be worn on.
        self.location = Wearable.NONE
       
        # The warmth wearing this item grants.
        self.warmth = 0

        # The armor protection wearing this item grants.
        self.armor = 0

    def toPrototypeJson(self):
        return self.toJson()

    def fromPrototypeJson(self, data):
        return self.fromJson(data)

    def toJson(self):
        return self.__dict__

    def fromJson(self, data):
       self.__dict__ = data
       return self

class Container(JsonSerializable):
    'Provides the properties of items that are containers.  Composable into an Item to make it a Container.'

    def __init__(self):

        # An array of items currently contained with in the container.
        self.contents = []

        # The volume the container can hold.
        self.volume = 0

        # The weight the container can hold.
        self.weightLimit = 0

    def toPrototypeJson(self):
        json = {}
        json['volume'] = self.volume
        json['weightLimit'] = self.weightLimit
        return json

    def fromPrototypeJson(self, data):
        self.volume = json['volume']
        self.weightLimit = json['weightLimit']
        return self

    def toJson(self):
        json = {}
        json['volume'] = self.volume
        json['weightLimit'] = self.weightLimit
        json['contents'] = []
        for item in self.contents:
            json['contents'].append(item.toJson())

    def fromJson(self, data):
       self.__dict__ = data
       return self


class Item(Model):
    'Represents an item in a game.'

    def __init__(self, library):
        super(Item, self).__init__(library)

        # The name of the item, displayed as the short name in lists.
        self.name = ''

        # The short description of the item.  Displayed when the item is looked at.
        self.description = ''

        # The long description of the item.  Displayed when the item is examined closely.
        self.details = ''

        # The list of keywords that may be used to reference the item in commands.
        self.keywords = [] 

        # The volume the item takes up.
        self.bulk = 0

        # How heavy the item is.
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
            classRef = globals()[use]
            instance = classRef()
            instance.fromJson(data['uses'][use])
            self.uses[use] = instance

        return self

    @staticmethod
    def getBasePath():
        return 'data/items/'


