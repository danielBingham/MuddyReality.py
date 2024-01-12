from game.store.models.base import JsonSerializable
from game.store.models.base import NamedModel

class HarvestProduct(JsonSerializable):
    'A product from an item that can be harvested.'

    def __init__(self):
        self.product = None
        self.amount = 0

    def toPrototypeJson(self):
        return self.toJson()
    
    def fromPrototypeJson(self, data):
        return self.fromJson(data)

    def toJson(self):
        return self.__dict__

    def fromJson(self, data):
        self.__dict__ = data
        return self

class Harvestable(JsonSerializable):
    'An item that can be harvested.'

    def __init__(self):

        self.products = []

        self.pre_description = None 
        self.post_description = None

        self.consumed = False
        self.replaced_with = None

        self.calories = 0
        self.time = 0

        self.action = 'harvest'
        self.required_tools = []

        self.harvested = False

    def toPrototypeJson(self):
        return self.toJson()
    
    def fromPrototypeJson(self, data):
        return self.fromJson(data)

    def toJson(self):
        json = {}

        json['products'] = []
        for product in self.products:
            json['products'].append(product.toJson())

        if self.pre_description:
            json['preDescription'] = self.pre_description
        if self.post_description:
            json['postDescription'] = self.post_description

        json['consumed'] = self.consumed

        if self.replaced_with:
            json['replacedWith'] = self.replaced_with
        
        json['calories'] = self.calories
        json['time'] = self.time

        json['action'] = self.action
        json['required_tools'] = self.required_tools

        return json

    def fromJson(self, data):
        if 'preDescription'in data:
            self.pre_description = data['preDescription']
        if 'postDescription' in data:
            self.post_description = data['postDescription']

        self.consumed = data['consumed']
        
        if 'replaceWith' in data:
            self.replace_with = data['replaceWith']

        self.calories = data['calories']
        self.time = data['time']
        
        self.action = data['action']
        self.required_tools = data['required_tools']

        for product_json in data['products']:
            product = HarvestProduct()
            product.fromJson(product_json)
            self.products.append(product)

        return self

class Food(JsonSerializable):
    'A food that can be eaten for calories.'

    def __init__(self):
        self.calories = 0

    def toPrototypeJson(self):
        return self.toJson()
    
    def fromPrototypeJson(self, data):
        return self.fromJson(data)

    def toJson(self):
        return self.__dict__

    def fromJson(self, data):
        self.__dict__ = data
        return self

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
        self.volume = data['volume']
        self.weightLimit = data['weightLimit']
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


class Item(NamedModel):
    'Represents an item in a game.'

    def __init__(self):
        super(Item, self).__init__()

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

        # Can you pick up this item and carry it around?
        self.can_pick_up = True
        self.is_growing = False
        self.is_embedded = False

        # The traits of this item.  Various traits may be composed on to each
        # items to give it a variety of uses and features.
        self.traits = {} 

    def detail(self):
        output = self.details
        if "Harvestable" in self.traits:
            if self.traits["Harvestable"].harvested:
                output += " " + self.traits["Harvestable"].post_description
            else:
                output += " " + self.traits["Harvestable"].pre_description
        return output 

    def groundAction(self):
        if self.can_pick_up:
            return "laying"
        if self.is_growing:
            return "growing"
        if self.is_embedded:
            return "embedded"
        return None 


    def toJson(self):
        json = {}
        
        json['name'] = self.name
        json['description'] = self.description
        json['details'] = self.details
        json['keywords'] = self.keywords
        
        json['length'] = self.length
        json['width'] = self.width
        json['height'] = self.height
        json['weight'] = self.weight
        
        json['canPickUp'] = self.can_pick_up
        json['isGrowing'] = self.is_growing
        json['isEmbedded'] = self.is_embedded

        json['traits'] = {}
        for trait in self.traits:
            json['traits'][trait] = self.traits[trait].toJson()

        return json

    def fromJson(self, data):
        self.setId(data['name'])
        
        self.description = data['description']
        self.details = data['details']
        self.keywords = data['keywords']

        self.length = data['length']
        self.width = data['width']
        self.height = data['height']
        self.weight = data['weight']

        if "canPickUp" in data:
            self.can_pick_up = data['canPickUp']

        if "isGrowing" in data:
            self.is_growing = data['isGrowing']

        if "isEmbedded" in data:
            self.is_embedded = data['isEmbedded']
        
        for trait in data['traits']:
            classRef = globals()[trait]
            instance = classRef()
            instance.fromJson(data['traits'][trait])
            self.traits[trait] = instance

        return self
