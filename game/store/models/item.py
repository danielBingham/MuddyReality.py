from __future__ import annotations

from typing import TYPE_CHECKING

from game.store.models.base import JsonSerializable
from game.store.models.base import Model, NamedModel
from game.store.models.validation import UnexpectedFieldError
from game.store.models.validation import Validator
from game.store.models.validation import validateModel

if TYPE_CHECKING:
    from game.store.models.character import Character


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

    SCHEMA = {
        "time": Validator().isType(int).isRequired(),
        "timeLeft": Validator().isType(int),
        "decayProduct": Validator().isType(str | None).isRequired(),
    }

    def __init__(self):
        self.time = 0
        self.time_left = self.time
        self.decay_product = None

    def validate(self, data):
        """
        Validate that `data` is valid Decays json.

        Parameters
        ----------
        data:   dict
            The json data to validate.

        Returns
        -------
        True
            If `data` is valid.

        Raises
        ------
        ValidationError
            If `data` does not match `SCHEMA`.
        """

        return validateModel(type(self), data)

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

        self.validate(data)

        self.time = data["time"]

        if "timeLeft" in data:
            self.time_left = data["timeLeft"]

        self.decay_product = data["decayProduct"]
        return self


class HarvestProduct(JsonSerializable):
    'A product from an item that can be harvested.'

    # The `name` attribute of the Item this harvest yields.  `None` until it
    # is loaded from data. Required.
    product: str | None

    # The number of copies of `product` a single harvest yields. Required.
    amount: int

    SCHEMA = {
        "product": Validator().isType(str).isRequired(),
        "amount": Validator().isType(int).isRequired(),
    }

    def __init__(self):
        self.product = None
        self.amount = 0

    def validate(self, data):
        """
        Validate that `data` is valid HarvestProduct json.

        Parameters
        ----------
        data:   dict
            The json data to validate.

        Returns
        -------
        True
            If `data` is valid.

        Raises
        ------
        ValidationError
            If `data` does not match `SCHEMA`.
        """

        return validateModel(type(self), data)

    def toPrototypeJson(self):
        return self.toJson()

    def fromPrototypeJson(self, data):
        return self.fromJson(data)

    def toJson(self):
        json = {}

        json["product"] = self.product
        json["amount"] = self.amount

        return json

    def fromJson(self, data):

        self.validate(data)

        self.product = data["product"]
        self.amount = data["amount"]
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

    SCHEMA = {
        "products": Validator().isType(list[HarvestProduct]).isRequired(),
        "harvestTime": Validator().isType(list[str]),
        "preDescription": Validator().isType(str),
        "postDescription": Validator().isType(str),
        "consumed": Validator().isType(bool).isRequired(),
        "replacedWith": Validator().isType(str),
        "calories": Validator().isType(int).isRequired(),
        "time": Validator().isType(int).isRequired(),
        "action": Validator().isType(str).isRequired(),
        "required_tools": Validator().isType(list[str]).isRequired(),
        "harvested": Validator().isType(bool),
    }

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

    def validate(self, data):
        """
        Validate that `data` is valid Harvestable json.

        Parameters
        ----------
        data:   dict
            The json data to validate.

        Returns
        -------
        True
            If `data` is valid.

        Raises
        ------
        ValidationError
            If `data` does not match `SCHEMA`.
        """

        return validateModel(type(self), data)

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

        self.validate(data)

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

    SCHEMA = {
        "calories": Validator().isType(int).isRequired(),
    }

    def __init__(self):
        self.calories = 0

    def validate(self, data):
        """
        Validate that `data` is valid Food json.

        Parameters
        ----------
        data:   dict
            The json data to validate.

        Returns
        -------
        True
            If `data` is valid.

        Raises
        ------
        ValidationError
            If `data` does not match `SCHEMA`.
        """

        return validateModel(type(self), data)

    def toPrototypeJson(self):
        return self.toJson()

    def fromPrototypeJson(self, data):
        return self.fromJson(data)

    def toJson(self):
        data = {}
        data["calories"] = self.calories
        return data

    def fromJson(self, data):

        self.validate(data)

        self.calories = int(data["calories"])
        return self


class Material(JsonSerializable):
    'A material that can be used for crafting.'

    # An array of material type names this Material fulfills. Eg. wood, oak,
    # stone, etc. Required.
    types: list[str]

    SCHEMA = {
        "types": Validator().isType(list[str]).isRequired(),
    }

    def __init__(self):
        self.types = []

    def validate(self, data):
        """
        Validate that `data` is valid Material json.

        Parameters
        ----------
        data:   dict
            The json data to validate.

        Returns
        -------
        True
            If `data` is valid.

        Raises
        ------
        ValidationError
            If `data` does not match `SCHEMA`.
        """

        return validateModel(type(self), data)

    def toPrototypeJson(self):
        return self.toJson()

    def fromPrototypeJson(self, data):
        return self.fromJson(data)

    def toJson(self):
        data = {}
        data['types'] = self.types
        return data

    def fromJson(self, data):

        self.validate(data)

        self.types = data['types']
        return self


class Tool(JsonSerializable):
    'A tool that can be used for crafting.'

    # The list of tool types that this tool fulfills. Required.
    type: list[str]

    SCHEMA = {
        "type": Validator().isType(list[str]).isRequired(),
    }

    def __init__(self):
        self.type = []

    def validate(self, data):
        """
        Validate that `data` is valid Tool json.

        Parameters
        ----------
        data:   dict
            The json data to validate.

        Returns
        -------
        True
            If `data` is valid.

        Raises
        ------
        ValidationError
            If `data` does not match `SCHEMA`.
        """

        return validateModel(type(self), data)

    def toPrototypeJson(self):
        return self.toJson()

    def fromPrototypeJson(self, data):
        return self.fromJson(data)

    def toJson(self):
        data = {}
        data['type'] = self.type
        return data

    def fromJson(self, data):

        self.validate(data)

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
    weight: float

    # The required length of material (meters). Required.
    length: float

    # The required width of material (meters). Required.
    width: float

    # The required height of material (meters). Required.
    height: float

    SCHEMA = {
        "type": Validator().isType(str).isRequired(),
        "weight": Validator().isType(float).isRequired(),
        "length": Validator().isType(float).isRequired(),
        "width": Validator().isType(float).isRequired(),
        "height": Validator().isType(float).isRequired(),
    }

    def __init__(self):
        self.type = "material"
        self.weight = 0
        self.length = 0
        self.width = 0
        self.height = 0

    def validate(self, data):
        """
        Validate that `data` is valid RequiredMaterial json.

        Parameters
        ----------
        data:   dict
            The json data to validate.

        Returns
        -------
        True
            If `data` is valid.

        Raises
        ------
        ValidationError
            If `data` does not match `SCHEMA`.
        """

        return validateModel(type(self), data)

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

        self.validate(data)

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

    SCHEMA = {
        "requiredMaterials": Validator().isType(list[RequiredMaterial]).isRequired(),
        "requiredTools": Validator().isType(list[str]).isRequired(),
    }

    def __init__(self):
        self.required_materials = []
        self.required_tools = []

    def validate(self, data):
        """
        Validate that `data` is valid Craftable json.

        Parameters
        ----------
        data:   dict
            The json data to validate.

        Returns
        -------
        True
            If `data` is valid.

        Raises
        ------
        ValidationError
            If `data` does not match `SCHEMA`.
        """

        return validateModel(type(self), data)

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

        self.validate(data)

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

    # The minimum damage this weapon does on striking.  Damage is a bare
    # number rather than a measure of anything; combat is not implemented
    # yet, so the scale is still undefined. Required.
    #
    # TODO Implement me.
    min_damage: int

    # The maximum damage this weapon can do on striking.  On the same scale
    # as `min_damage`. Required.
    #
    # TODO Implement me.
    max_damage: int

    # What type of weapon this is, and so what kind of damage it does.  One
    # of `TYPES`, or `NONE` for a weapon that has not been given a type.
    # Required.
    type: str

    SCHEMA = {
        "minDamage": Validator().isType(int).isRequired(),
        "maxDamage": Validator().isType(int).isRequired(),
        "type": Validator().isType(str).isOneOf(TYPES + [NONE]).isRequired(),
    }

    def __init__(self):
        self.min_damage = 0
        self.max_damage = 0
        self.type = MeleeWeapon.NONE

    def validate(self, data):
        """
        Validate that `data` is valid MeleeWeapon json.

        Parameters
        ----------
        data:   dict
            The json data to validate.

        Returns
        -------
        True
            If `data` is valid.

        Raises
        ------
        ValidationError
            If `data` does not match `SCHEMA`.
        """

        return validateModel(type(self), data)

    def toPrototypeJson(self):
        return self.toJson()

    def fromPrototypeJson(self, data):
        return self.fromJson(data)

    def toJson(self):
        json = {}

        json['minDamage'] = self.min_damage
        json['maxDamage'] = self.max_damage
        json['type'] = self.type

        return json

    def fromJson(self, data):

        self.validate(data)

        self.min_damage = data['minDamage']
        self.max_damage = data['maxDamage']
        self.type = data['type']
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

    # The location on the body this item may be worn.  One of `LOCATIONS`,
    # or `NONE` for an item that cannot be worn anywhere yet. Required.
    location: str

    # The warmth wearing this item grants.  A bare number rather than a
    # measure of anything; exposure is not implemented yet, so the scale is
    # still undefined. Optional, defaults to 0.
    #
    # TODO Implement me.
    warmth: int

    # The armor protection wearing this item grants.  On the same undefined
    # scale as `warmth`. Optional, defaults to 0.
    #
    # TODO Implement me.
    armor: int

    SCHEMA = {
        "location": Validator().isType(str).isOneOf(LOCATIONS + [NONE]).isRequired(),
        "warmth": Validator().isType(int),
        "armor": Validator().isType(int),
    }

    def __init__(self):
        self.location = Wearable.NONE
        self.warmth = 0
        self.armor = 0

    def validate(self, data):
        """
        Validate that `data` is valid Wearable json.

        Parameters
        ----------
        data:   dict
            The json data to validate.

        Returns
        -------
        True
            If `data` is valid.

        Raises
        ------
        ValidationError
            If `data` does not match `SCHEMA`.
        """

        return validateModel(type(self), data)

    def toPrototypeJson(self):
        return self.toJson()

    def fromPrototypeJson(self, data):
        return self.fromJson(data)

    def toJson(self):
        json = {}

        json['location'] = self.location
        json['warmth'] = self.warmth
        json['armor'] = self.armor

        return json

    def fromJson(self, data):

        self.validate(data)

        self.location = data['location']

        if 'warmth' in data:
            self.warmth = data['warmth']

        if 'armor' in data:
            self.armor = data['armor']

        return self


class Container(JsonSerializable):
    'Provides the properties of items that are containers.  Composable into an Item to make it a Container.'

    # The Items currently inside this container.  This is the container's
    # contents at a moment in time, so `toPrototypeJson` leaves it out: a
    # container created from a prototype starts empty. Optional.
    contents: list[Item]

    # The volume this container can hold (litres). Required.
    volume: float

    # The weight this container can hold (kilograms). Required.
    weight_limit: float

    SCHEMA = {
        "volume": Validator().isType(float).isRequired(),
        "weightLimit": Validator().isType(float).isRequired(),
        # `Item` is defined below this class, so the type is deferred behind a
        # function that isn't called until the data is validated.
        "contents": Validator().isType(lambda: list[Item]),
    }

    def __init__(self):
        self.contents = []
        self.volume = 0
        self.weight_limit = 0

    def validate(self, data):
        """
        Validate that `data` is valid Container json.

        Parameters
        ----------
        data:   dict
            The json data to validate.

        Returns
        -------
        True
            If `data` is valid.

        Raises
        ------
        ValidationError
            If `data` does not match `SCHEMA`.
        """

        return validateModel(type(self), data)

    def toPrototypeJson(self):
        json = {}
        json['volume'] = self.volume
        json['weightLimit'] = self.weight_limit
        return json

    def fromPrototypeJson(self, data):
        self.volume = data['volume']
        self.weight_limit = data['weightLimit']
        return self

    def toJson(self):
        json = {}
        json['volume'] = self.volume
        json['weightLimit'] = self.weight_limit
        json['contents'] = []
        for item in self.contents:
            json['contents'].append(item.toJson())
        return json

    def fromJson(self, data):

        self.validate(data)

        self.volume = data['volume']
        self.weight_limit = data['weightLimit']

        if 'contents' in data:
            for item_json in data['contents']:
                item = Item()
                item.fromJson(item_json)
                self.contents.append(item)

        return self


# The traits that may be composed on to an Item, keyed by the name they are
# written under in an Item's `traits`.  Every trait in this module belongs
# here; an item naming a trait that isn't listed fails validation.
TRAITS = {
    'Craftable': Craftable,
    'Container': Container,
    'Decays': Decays,
    'Food': Food,
    'Harvestable': Harvestable,
    'Material': Material,
    'MeleeWeapon': MeleeWeapon,
    'Tool': Tool,
    'Wearable': Wearable,
}


class Item(NamedModel):
    'Represents an item in a game.'

    # The Room this Item is lying in, if it is on the ground.  Runtime state
    # set by the game as the item moves around the world, not something the
    # item is loaded with. Optional.
    room: Model | None

    # The Character carrying, wearing or wielding this Item.  Runtime state,
    # as with `room`. Optional.
    character: Character | None

    # The Container this Item is inside.  Runtime state, as with `room`.
    # Optional.
    container: Container | None

    # The short description of the item.  Displayed when the item is looked
    # at, or listed in the room the item is lying in. Required.
    description: str

    # Addendums to `description`, keyed by season ('winter', 'spring',
    # 'summer', 'fall'), appended to it when the item is described during
    # that season. Optional.
    season_description: dict[str, str] | None

    # The long description of the item.  Displayed when the item is examined
    # closely. Required.
    details: str

    # Addendums to `details`, keyed by season as `season_description` is.
    # Optional.
    season_details: dict[str, str] | None

    # The keywords that may be used to reference the item in commands, as a
    # single space separated string. Eg. 'small greyish-brown stick'. Required.
    keywords: str

    # The length of the item, its longest dimension (meters). Required.
    length: float

    # The width of the item (meters). Required.
    width: float

    # The height of the item (meters). Required.
    height: float

    # How heavy the item is (kilograms). Required.
    weight: float

    # Can you pick up this item and carry it around? This only references
    # whether the item is rooted to the ground in someway, not whether it
    # is too heavy/large. Whether the character can actually pick it up
    # based on its size/weight will be determined by the character's own
    # attributes. Optional, defaults to `True`.
    can_pick_up: bool

    # Is this item growing from the ground? Is it a living
    # plant/fungus/creature? Optional, defaults to `False`.
    is_growing: bool

    # Is this item embedded in the ground in someway, either as a boulder
    # or on a foundation? Optional, defaults to `False`.
    is_embedded: bool

    # The traits of this item.  Various traits may be composed on to each
    # items to give it a variety of uses and features.  Keyed by the trait's
    # class name as it is written in this module. Eg. 'Material',
    # 'Harvestable'. Required.
    traits: dict[str, JsonSerializable]

    SCHEMA = {
        "name": Validator().isType(str).isRequired(),
        "description": Validator().isType(str).isRequired(),
        "seasonDescription": Validator().isType(dict[str, str]),
        "details": Validator().isType(str).isRequired(),
        "seasonDetails": Validator().isType(dict[str, str]),
        "keywords": Validator().isType(str).isRequired(),
        "length": Validator().isType(float).isRequired(),
        "width": Validator().isType(float).isRequired(),
        "height": Validator().isType(float).isRequired(),
        "weight": Validator().isType(float).isRequired(),
        "canPickUp": Validator().isType(bool),
        "isGrowing": Validator().isType(bool),
        "isEmbedded": Validator().isType(bool),
        # Each trait is checked against its own schema by `validate`, which
        # knows which model belongs to which key.
        "traits": Validator().isType(dict[str, dict]).isRequired(),
    }

    def __init__(self):
        super(Item, self).__init__()

        # Item's location in the game.
        self.room = None # If the item is lying in a room.
        self.character = None # If the item is on a character.
        self.container = None # If the item is in a container.

        self.description = ''
        self.season_description = None

        self.details = ''
        self.season_details = None

        self.keywords = ''

        self.length = 0
        self.width = 0
        self.height = 0

        self.weight = 0

        self.can_pick_up = True
        self.is_growing = False
        self.is_embedded = False

        self.traits = {}

    def validate(self, data):
        """
        Validate that `data` is valid Item json, including the json of each
        of its traits.

        Parameters
        ----------
        data:   dict
            The json data to validate.

        Returns
        -------
        True
            If `data` is valid.

        Raises
        ------
        ValidationError
            If `data`, or the data of any of its traits, does not match the
            relevant `SCHEMA`.
        """

        validateModel(type(self), data)

        for trait in data['traits']:
            if trait not in TRAITS:
                raise UnexpectedFieldError('Item.traits.%s' % trait,
                                           'there is no such trait.')

            TRAITS[trait]().validate(data['traits'][trait])

        return True

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

        self.validate(data)

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
