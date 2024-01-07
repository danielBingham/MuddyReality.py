import json

from game.store.models.base import NamedModel
from game.store.models.base import JsonSerializable

class Reserves(JsonSerializable):
    'Represents a characters reserves: how well fed and well rested they are.'

    def __init__(self):
        self.calories = 2400
        self.thirst = 4000
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
    
    def thirstString(self, prompt=False):
        thirst = ''

        if prompt and self.thirst > 3000:
            return thirst

        if self.thirst > 3000:
            thirst = 'not thirsty'
        elif self.thirst > 2000:
            thirst = 'thirsty'
        elif self.thirst > 1000:
            thirst = 'very thirsty'
        elif self.thirst > 0:
            thirst = 'extremely thirsty'
        else:
            thirst = 'parched'
        return thirst

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
        return ("You are %s, %s, and %s." %
            (self.hungerString(), self.thirstString(), self.sleepString()))

    def toJson(self):
        json = {}

        json["calories"] = self.calories
        json["thirst"] = self.thirst
        json["sleep"] = self.sleep

        return json

    def fromJson(self, data):

        self.calories = data["calories"]
        self.thirst = data["thirst"]
        self.sleep = data["sleep"]

        return self

class Wound(JsonSerializable):
    
    WOUND_SCRAPED = 'scraped'

    WOUND_CUT = 'cut'
    WOUND_DEEP_CUT = 'deeply-cut'
    WOUND_SEVERED = 'severed'

    WOUND_BRUISED = 'bruised'
    WOUND_BROKEN = 'broken'

    WOUND_PUNCTURE = 'puncture'
    WOUND_DEEP_PUNCTURE = 'deep-puncture'

    WOUND_FIRST_DEGREE_BURN = 'first-degree-burn'
    WOUND_SECOND_DEGREE_BURN = 'second-degree-burn'
    WOUND_THIRD_DEGREE_BURN = 'third-degree-burn'

    def __init__(self):
        self.type = WOUND_SCRAPED

        # The amount of blood lost per game minute due to the wound.
        self.bleed = 0

        # If the wound is infected, that causes additional consequences.
        self.infected = False

        # The amount of pain caused by the wound.
        self.pain = 0


    def toJson(self):
        json = {}
        json['type'] = self.wound
        json['bleed'] = self.bleed
        json['infected'] = self.infected
        json['pain'] = self.pain
        return json

    def fromJson(self, data):
        self.type = data['type']
        self.bleed = data['bleed']
        self.infected = data['infected']
        self.pain = data['pain']
        return self


class Body(JsonSerializable):

    def __init__(self):
        self.wounds = {}
        self.worn = {}

        self.body_parts = []

    def wear(self, body_part, item):
        if body_part in self.body_parts:
            self.worn[body_part] = item
            return True
        else:
            return False

    def wound(self, body_part, wound):
        if body_part in self.body_parts:
            self.wounds[body_part] = wound
            return True
        else:
            return False

    def toJson(self):
        json = {}
        json['wounds'] = {}
        for body_part in self.wounds:
            json['wounds'][body_part] = self.wounds[body_part]

        json['worn'] = {}
        for body_part in self.worn:
            json['worn'][body_part] = self.worn[body_part].getId()

        return json

    def fromJson(self, data):
        if 'wounds' in data:
            for body_part in data['wounds']:
                self.wounds[body_part] = data['wounds'][body_part]

        if 'worn' in data:
            for body_part in data['worn']:
                self.worn[body_part] = data['worn'][body_part]

        return self


class QuadrapedalBody(Body):

    # Body Parts 
    BODY_HEAD = 'head'
    BODY_NECK = 'neck'
    BODY_CORE = 'core'

    BODY_FRONT_LEFT_THIGH = 'front left thigh'
    BODY_FRONT_LEFT_CALF = 'front left calf'
    BODY_FRONT_LEFT_FOOT = 'front left foot'

    BODY_FRONT_RIGHT_THIGH = 'front right thigh'
    BODY_FRONT_RIGHT_CALF = 'front right calf'
    BODY_FRONT_IGHT_FOOT = 'front right foot'

    BODY_BACK_LEFT_THIGH = 'back left thigh'
    BODY_BACK_LEFT_CALF = 'back left calf'
    BODY_BACK_LEFT_FOOT = 'back left foot'

    BODY_BACK_RIGHT_THIGH = 'back right thigh'
    BODY_BACK_RIGHT_CALF = 'back right calf'
    BODY_BACK_RIGHT_FOOT = 'back right foot'

    def __init__(self):
        super(QuadrapedalBody, self).__init__()

        self.body_parts = [
            self.BODY_HEAD,
            self.BODY_NECK,
            self.BODY_CORE,
            self.BODY_FRONT_LEFT_THIGH,
            self.BODY_FRONT_LEFT_CALF,
            self.BODY_FRONT_LEFT_FOOT,
            self.BODY_FRONT_RIGHT_THIGH,
            self.BODY_FRONT_RIGHT_CALF,
            self.BODY_FRONT_IGHT_FOOT,
            self.BODY_BACK_LEFT_THIGH,
            self.BODY_BACK_LEFT_CALF,
            self.BODY_BACK_LEFT_FOOT,
            self.BODY_BACK_RIGHT_THIGH,
            self.BODY_BACK_RIGHT_CALF,
            self.BODY_BACK_RIGHT_FOOT
        ]


class BipedalBody(Body):

    # Body Parts 
    BODY_HEAD = 'head'

    BODY_NECK = 'neck'

    BODY_TORSO = 'torso'

    BODY_LEFT_UPPER_ARM = 'left-upper-arm'
    BODY_LEFT_FOREARM = 'left-forearm'
    BODY_LEFT_WRIST = 'left-wrist'
    BODY_LEFT_HAND = 'left-hand'

    BODY_RIGHT_UPPER_ARM = 'right-upper-arm'
    BODY_RIGHT_FOREARM = 'right-forearm'
    BODY_RIGHT_WRIST = 'right-wrist'
    BODY_RIGHT_HAND = 'right-hand'

    BODY_LEFT_THIGH = 'left-thigh'
    BODY_LEFT_CALF = 'left-calf'
    BODY_LEFT_FOOT = 'left-foot'

    BODY_RIGHT_THIGH = 'right-thigh'
    BODY_RIGHT_CALF = 'right-calf'
    BODY_RIGHT_FOOT = 'right-foot'

    def __init__(self):
        super(BipedalBody, self).__init__()

        self.body_parts = [
            self.BODY_HEAD,
            self.BODY_NECK,
            self.BODY_TORSO,
            self.BODY_LEFT_UPPER_ARM,
            self.BODY_LEFT_FOREARM,
            self.BODY_LEFT_WRIST,
            self.BODY_LEFT_HAND,
            self.BODY_RIGHT_UPPER_ARM,
            self.BODY_RIGHT_FOREARM,
            self.BODY_RIGHT_WRIST,
            self.BODY_RIGHT_HAND,
            self.BODY_LEFT_THIGH,
            self.BODY_LEFT_CALF,
            self.BODY_LEFT_FOOT,
            self.BODY_RIGHT_THIGH,
            self.BODY_RIGHT_CALF,
            self.BODY_RIGHT_FOOT
        ]


class Character(NamedModel):
    'Represents a single character in the game.'

    SEX_MALE = 'male'
    SEX_FEMALE = 'female'

    POSITION_SPRINTING = 'sprinting'
    POSITION_RUNNING = 'running'
    POSITION_WALKING = 'walking'
    POSITION_STANDING = 'standing'
    POSITION_SITTING = 'sitting'
    POSITION_LAYING_DOWN = 'laying down'
    POSITION_SLEEPING = 'sleeping'

    def __init__(self):
        super(Character, self).__init__()
       
        # The short description of the character.  Displayed when the character is looked at.
        self.description = ''

        # The long description.  Displayed when the character is examined closely.
        self.details = ''

        self.sex = self.SEX_MALE

        self.account = None
        self.player = None

        self.position = self.POSITION_STANDING

        self.reserves = Reserves()

        self.body_type = 'bipedal'
        self.body = BipedalBody()

        self.inventory = []

        self.action = None
        self.action_data = {} 
        self.action_time = 0

        self.room = None

    def toJson(self):
        json = {}

        json['name'] = self.name
        json['description'] = self.description
        json['details'] = self.details
        json['sex'] = self.sex
        json['position'] = self.position
        
        json['reserves'] = self.reserves.toJson()

        json['bodyType'] = self.body_type 
        json['body'] = self.body.toJson()

        json['inventory'] = []
        for item in self.inventory:
            json['inventory'].append(item.getId())

        if self.room:
            json['room'] = self.room.getId()

        return json

    def fromJson(self, data):
        self.setId(data['name'])

        self.description = data['description']
        self.details = data['details']
        self.sex = data['sex']

        if 'position' in data:
            self.position = data['position']
        else:
            self.position = self.POSITION_STANDING

        self.body_type = data['bodyType']
        if self.body_type == 'bipedal':
            self.body = BipedalBody()
        elif self.body_type == 'quadrapedal':
            self.body = QuadrapedalBody()

        if 'body' in data:
            self.body.fromJson(data['body'])

        self.reserves = Reserves()
        if 'reserves' in data:
            self.reserves.fromJson(data['reserves'])

        if 'inventory' in data:
            for item in data['inventory']:
                self.inventory.append(item)

        # lazy migrations
        if 'room' in data:
            self.room = data['room']

        return self
