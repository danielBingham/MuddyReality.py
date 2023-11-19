from models.base import JsonSerializable
from models.base import Model

class Material(JsonSerializable):
    'A material that can be used for crafting.'

    def __init__(self):
        # An array of types this material fulfils 
        self.types = [] 

    def toPrototypeJson(self):
        return self.toJson()

    def fromPrototypeJson(self, data):
        return self.fromJson(data)

    def toJson(self):
        return self.__dict__

    def fromJson(self, data):
        self.__dict__ = data
        return self

class Tool(JsonSerializable):
    'A tool that can be used for crafting.'

    def __init__(self):
        # The an array of types this tool fulfills. 
        self.types = [] 

    def toPrototypeJson(self):
        return self.toJson()

    def fromPrototypeJson(self, data):
        return self.fromJson(data)

    def toJson(self):
        return self.__dict__

    def fromJson(self, data):
        self.__dict__ = data
        return self

class RequiredMaterial(JsonSerializable):
    'A material requirement for crafting'

    def __init__(self):
        # The types of material required.  All of the types listed must be
        # included by the material.  For example, if the requiredMartial types
        # are 'oak' and 'wood'.  Then a material must have both 'oak' and
        # 'wood' types to fulfill this requirement.
        self.type = None 

        # The amount of the material required in weight (kilograms). 
        self.weight = 0 

        # The required length of material in meters.
        self.length = 0 

        # The required width of material in meters.
        self.width = 0

        # The required height of material in meters.
        self.height = 0

    def toPrototypeJson(self):
        return self.toJson()

    def fromPrototypeJson(self, data):
        return self.fromJson(data)

    def toJson(self):
        return self.__dict__

    def fromJson(self, data):
        self.__dict__ = data
        return self


class Craftable(JsonSerializable):
    'An object that may be crafted.'

    def __init__(self):

        # The materials that are required to craft this object.
        self.requiredMaterials = []

        # The types of tools that are required to craft this object.
        self.requiredTools = []

    def toPrototypeJson(self):
        return self.toJson()

    def fromPrototypeJson(self, data):
        return self.fromJson(data)

    def toJson(self):
        json = {}

        materials = []
        for material in self.requiredMaterials:
            materials.append(material.toJson())
        json['requiredMaterials'] = materials

        json['requiredTools'] = self.requiredTools 

    def fromJson(self, data):
        for requiredMaterialJson in data['requiredMaterials']:
            requiredMaterial = RequiredMaterial()
            requiredMaterial.fromJson(requiredMaterialJson)
            self.requiredMaterials.append(requiredMaterial)
        self.requiredTools = data['requiredTools']
        return self


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

        # The volume the container can hold in litres.
        self.volume = 0

        # The weight the container can hold in kilograms.
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
        # Also serves as the item's identifier - so must be universally unique.
        self.name = ''

        # The short description of the item.  Displayed when the item is looked at.
        self.description = ''

        # The long description of the item.  Displayed when the item is examined closely.
        self.details = ''

        # The list of keywords that may be used to reference the item in commands.
        self.keywords = [] 

        self.length = 0 # size in meters 
        self.width = 0 # size in meters 
        self.height = 0 # size in meters

        # How heavy the item is in kilograms.
        self.weight = 0

        # The traits of this item.  Various traits may be composed on to each
        # items to give it a variety of uses and features.
        self.traits = {} 

    def detail(self):
        return self.details

    def toJson(self):
        json = {}
        json['id'] = self.name
        json['name'] = self.name
        json['description'] = self.description
        json['details'] = self.details
        json['keywords'] = self.keywords
        
        json['length'] = self.length
        json['width'] = self.width
        json['height'] = self.height
        json['weight'] = self.weight


        json['traits'] = {}
        for trait in self.traits:
            json['traits'][trait] = self.traits[trait].toJson()

        return json

    def fromJson(self, data):
        self.setId(data['name'])
        self.name = data['name']
        self.description = data['description']
        self.details = data['details']
        self.keywords = data['keywords']

        self.length = data['length']
        self.width = data['width']
        self.height = data['height']
        self.width = data['weight']
        
        for trait in data['traits']:
            classRef = globals()[trait]
            instance = classRef()
            instance.fromJson(data['traits'][trait])
            self.traits[trait] = instance

        return self

    @staticmethod
    def getBasePath():
        return 'data/items/'


