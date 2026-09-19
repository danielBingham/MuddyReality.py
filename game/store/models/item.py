from game.store.models.base import JsonSerializable
from game.store.models.base import Model,NamedModel

class Decays(JsonSerializable):
    'An item that gradually decays over time.'

    # The time it takes this item to decay.
    time: int

    # The amount of time left out of the total time before this item
    # decays.
    time_left: int

    # The `name` attribute of the Item that this Item will become when it
    # decays. Optional.
    decay_product: str | None

    def __init__(self):
        self.time = 0
        self.time_left = self.time
        self.decay_product = None

    def toPrototypeJson(self):
        json = self.toJson()
        json["timeLeft"] = self.time
        return json


    def fromPrototypeJson(self,  data):
        self.fromJson(data)
        self.time_left = self.time
        return self

    def toJson(self):
        json = {}

        json["time"] = self.time

        # Only store the time_left if it has actually changed.
        if self.time_left != self.time:
            json["timeLeft"] = self.time_left

        json["decayProduct"] = self.decay_product

        return json

    def fromJson(self, data):

        self.time = data["time"]

        if "timeleft" in data:
            self.time_left = data["timeLeft"]

        self.decay_product = data["decayProduct"]
        return self


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

    # The products received from executing this particular harvest.
    products: list[HarvestProduct]

    # The time (months) during which harvest may occur. Optional.
    harvest_time: list[str] | None

    # A description addendum for the parent item before harvest occurs. Optional.
    pre_description: str | None

    # A description addendum for the parent item after harvest occurs. Optional.
    post_description: str | None

    # Is this item consumed when it is harvested?  If so, the item will be
    # removed and optional replaced with the item identified by
    # `replaced_with`. Required.
    consumed: bool

    # When this item is harvested, it is consumed and replaced with another item.  This
    # indicates the item or items it may be replaced with. Optional.
    replaced_with: str | None

    # The number of calories expended by a character during the harvest process. Required.
    calories: int

    # The amount of time, in ticks, expended during the harvest process. Required.
    time: int

    # The name of the action used to havest this particular harvest and gain
    # its products. eg. 'pick', 'cut', etc. Required.
    action: str

    # A list of tool types required to harvest this. Required.
    required_tools: list[str]

    # Whether this harvest has already been harvested. Optional.
    harvested: bool

    def __init__(self):

        self.products = []
        self.harvest_time = None
        self.pre_description = None
        self.post_description = None
        self.consumed = False
        self.replaced_with = None

        self.calories = 0
        self.time = 0

        self.action = "harvest"
        self.required_tools = []

        self.harvested = False

    def toPrototypeJson(self):
        return self.toJson()

    def fromPrototypeJson(self, data):
        return self.fromJson(data)

    def toJson(self):
        json = {}

        json["products"] = []
        for product in self.products:
            json["products"].append(product.toJson())

        if self.harvest_time:
            json["harvestTime"] = self.harvest_time

        if self.pre_description:
            json["preDescription"] = self.pre_description
        if self.post_description:
            json["postDescription"] = self.post_description

        json["consumed"] = self.consumed

        if self.replaced_with:
            json["replacedWith"] = self.replaced_with

        json["calories"] = self.calories
        json["time"] = self.time

        json["action"] = self.action
        json["required_tools"] = self.required_tools

        if self.harvested:
            json["harvested"] = self.harvested

        return json

    def fromJson(self, data):
        if "harvestTime" in data:
            self.harvest_time = data["harvestTime"]

        if "preDescription" in data:
            self.pre_description = data["preDescription"]
        if "postDescription" in data:
            self.post_description = data["postDescription"]

        self.consumed = data["consumed"]

        if "replacedWith" in data:
            self.replaced_with = data["replacedWith"]

        self.calories = data["calories"]
        self.time = data["time"]

        self.action = data["action"]
        self.required_tools = data["required_tools"]

        if "harvested" in data:
            self.harvested = data["harvested"]

        for product_json in data["products"]:
            product = HarvestProduct()
            product.fromJson(product_json)
            self.products.append(product)

        return self


class Food(JsonSerializable):
    'A food that can be eaten for calories.'

    # The number of calories gained from eating this food. Required.
    calories: int

    def __init__(self):
        self.calories = 0

    def toPrototypeJson(self):
        return self.toJson()

    def fromPrototypeJson(self, data):
        return self.fromJson(data)

    def toJson(self):
        data = {}
        data["calories"] = self.calories
        return data

    def fromJson(self, data):
        self.calories = int(data["calories"])
        return self


class Material(JsonSerializable):
    'A material that can be used for crafting.'

    # An array of material type names this Material fulfills. Eg. wood, oak,
    # stone, etc. Required.
    types: list[str]

    def __init__(self):
        self.types = []

    def toPrototypeJson(self):
        return self.toJson()

    def fromPrototypeJson(self, data):
        return self.fromJson(data)

    def toJson(self):
        data = {}
        data['types'] = self.types
        return data

    def fromJson(self, data):
        self.types = data['types']
        return self


class Tool(JsonSerializable):
    'A tool that can be used for crafting.'

    # The list of tool types that this tool fulfills. Required.
    type: list[str]

    def __init__(self):
        self.type = []

    def toPrototypeJson(self):
        return self.toJson()

    def fromPrototypeJson(self, data):
        return self.fromJson(data)

    def toJson(self):
        data = {}
        data['type'] = self.type
        return data

    def fromJson(self, data):
        self.type = data['type']
        return self


class RequiredMaterial(JsonSerializable):
    'A material requirement for crafting'

    # The types of material required.  All of the types listed must be
    # included by the material.  For example, if the requiredMartial types
    # are 'oak' and 'wood'.  Then a material must have both 'oak' and
    # 'wood' types to fulfill this requirement. Required.
    type: str

    # The amount of the material required in weight (kilograms). Required.
    weight: int

    # The required length of material (meters). Required.
    length: int

    # The required width of material (meters). Required.
    width: int

    # The required height of material (meters). Required.
    height: int

    def __init__(self):
        self.type = "material"
        self.weight = 0
        self.length = 0
        self.width = 0
        self.height = 0

    def toPrototypeJson(self):
        return self.toJson()

    def fromPrototypeJson(self, data):
        return self.fromJson(data)

    def toJson(self):
        data = {}
        data['type'] = self.type
        data['weight'] = self.weight
        data['length'] = self.length
        data['width'] = self.width
        data['height'] = self.height
        return data

    def fromJson(self, data):
        self.type = data['type']
        self.weight = data['weight']
        self.length = data['length']
        self.width = data['width']
        self.height = data['height']
        return self


class Craftable(JsonSerializable):
    'An object that may be crafted.'

    # A list of material types requried to craft this object. Required.
    required_materials: list[RequiredMaterial]

    # The types of tools that are required to craft this object. Required.
    required_tools: list[str]

    def __init__(self):
        self.required_materials = []
        self.required_tools = []

    def toPrototypeJson(self):
        return self.toJson()

    def fromPrototypeJson(self, data):
        return self.fromJson(data)

    def toJson(self):
        data = {}

        materials = []
        for material in self.required_materials:
            materials.append(material.toJson())
        data['requiredMaterials'] = materials

        data['requiredTools'] = self.required_tools
        return data

    def fromJson(self, data):
        for required_material_json in data['requiredMaterials']:
            required_material = RequiredMaterial()
            required_material.fromJson(required_material_json)
            self.required_materials.append(required_material)
        self.required_tools = data['requiredTools']
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
        return json

    def fromJson(self, data):
        self.__dict__ = data
        return self


class Item(NamedModel):
    'Represents an item in a game.'

    def __init__(self):
        super(Item, self).__init__()

        # Item's location in the game.
        self.room = None # If the item is lying in a room.
        self.character = None # If the item is on a character.
        self.container = None # If the item is in a container.

        # The short description of the item.  Displayed when the item is looked at.
        self.description = ''
        self.season_description = None

        # The long description of the item.  Displayed when the item is examined closely.
        self.details = ''
        self.season_details = None

        # The list of keywords that may be used to reference the item in commands.
        self.keywords = ''

        self.length = 0 # size in meters
        self.width = 0 # size in meters
        self.height = 0 # size in meters

        # How heavy the item is in kilograms.
        self.weight = 0

        # Can you pick up this item and carry it around? This only references
        # whether the item is rooted to the ground in someway, not whether it
        # is too heavy/large. Whether the character can actually pick it up
        # based on its size/weight will be determined by the character's own
        # attributes.
        self.can_pick_up = True

        # Is this item growing from the ground? Is it a living
        # plant/fungus/creature?
        self.is_growing = False

        # Is this item embedded in the ground in someway, either as a boulder
        # or on a foundation?
        self.is_embedded = False

        # The traits of this item.  Various traits may be composed on to each
        # items to give it a variety of uses and features.
        self.traits = {}

    def toJson(self):
        json = {}

        json['name'] = self.name
        json['description'] = self.description
        if self.season_description:
            json['seasonDescription'] = self.season_description

        json['details'] = self.details
        if self.season_details:
            json['seasonDetails'] = self.season_details

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
        if 'seasonDescription' in data:
            self.season_description = data['seasonDescription']

        self.details = data['details']
        if 'seasonDetails' in data:
            self.season_details = data['seasonDetails']

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
