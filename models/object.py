from models.base import JsonSerializable
from models.base import Model

class MeleeWeapon(JsonSerializable):
    'Contains the properties of a melee weapon.  Composable into an Object to give it the use as a Melee Weapon.''

    SLASHING = 'slashing'
    CRUSHING = 'crushing'
    HACKING = 'hacking'
    SMITING = 'smiting'
    STABBING = 'stabbing'
    NONE = 'none'

    WEAPON_TYPES = [
        MeleeWeapon.SLASHING,
        MeleeWeapon.CRUSHING,
        MeleeWeapon.HACKING,
        MeleeWeapon.SMITING, 
        MeleeWeapon.STABBING
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
    'Contains the properties of a wearable object.  Composable into an Object to make it Wearable.'
    
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
        Wearable.HANDS,
        Wearable.FOREARMS,
        Wearable.TORSO,
        Wearable.LEGS, 
        Wearable.FEET,
        Wearable.HEAD,
        Wearable.BACK,
        Wearable.WAIST,
        Wearable.NECK 
    ]

    def __init__(self):

        # The location this object may be worn on.
        self.location = Wearable.NONE
       
        # The warmth wearing this object grants.
        self.warmth = 0

        # The armor protection wearing this object grants.
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
    'Provides the properties of objects that are containers.  Composable into an Object to make it a Container.'

    def __init__(self):

        # An array of objects currently contained with in the container.
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


class Object(Model):

    def __init__(self, library):
        super(Object, self).__init__(library)

        # The name of the object, displayed as the short name in lists.
        self.name = ''

        # The short description of the object.  Displayed when the object is looked at.
        self.description = ''

        # The long description of the object.  Displayed when the object is examined closely.
        self.details = ''

        # The list of keywords that may be used to reference the object in commands.
        self.keywords = [] 

        # The volume the object takes up.
        self.bulk = 0

        # How heavy the object is.
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


