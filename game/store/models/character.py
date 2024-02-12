from game.store.models.base import NamedModel
from game.store.models.base import JsonSerializable


class Attributes(JsonSerializable):

    def __init__(self):
        # The character's strength. Controls:
        # - How much damage the character does in combat or harvesting.
        # - How much the character can lift and carry.
        self.strength = 10
        self.max_strength = 10

        # The character's stamina. Controls:
        # - How much wind and energy the character has.
        self.stamina = 10
        self.max_stamina = 10

        # The character's constitution. Controls:
        # - How well the character resists food poisoning, disease, and cold.
        self.constitution = 10
        self.max_constitution = 10

    def toJson(self):
        data = {}

        data['strength'] = self.strength
        data['maxStrength'] = self.max_strength

        data['stamina'] = self.stamina
        data['maxStamina'] = self.max_stamina

        data['constitution'] = self.constitution
        data['maxConstitution'] = self.max_constitution

        return data

    def fromJson(self, data):
        self.strength = data['strength']
        self.max_strength = data['maxStrength']

        self.stamina = data['stamina']
        self.max_stamina = data['maxStamina']

        self.constitution = data['constitution']
        self.max_constitution = data['maxConstitution']

        return self


class Reserves(JsonSerializable):
    'Represents a characters reserves: how well fed and well rested they are.'

    def __init__(self):
        # Calories measure how many calories of food you have stored in your
        # body. Calories can go negative to indicate that you are starving.
        self.calories = 2400
        self.max_calories = 2400

        # Thirst is a measure of how much water you have stored in your body.
        # It can't go very far below zero before you suffer serious
        # consequences.
        self.thirst = 4000
        self.max_thirst = 4000

        # Sleep is a measure of how much sleep you've had.  
        self.sleep = 16 
        self.max_sleep = 16

        # Wind measures how long you can push yourself during periods of
        # extreme effort.  As an example: how long can you sprint or run before
        # you need to stop and catch your breath?  Wind is determined by stamina.
        # 1 wind allows you to run for 60 seconds.
        self.wind = 30 
        self.max_wind = 30 

        # Energy is a measure of how much you can accomplish in a single day.
        # 1 energy is the cost equivalent of walking 1 meter.  Energy is
        # determined by stamina (stamina * 10), so as stamina increases, so too
        # will energy.
        self.energy = 10000 
        self.max_energy = 10000 

    def hungerString(self, prompt=False):
        hunger = ''

        if prompt and self.calories / self.max_calories > 0.5:
            return hunger

        if self.calories / self.max_calories > 0.5:
            hunger = 'sated'

        elif self.calories / self.max_calories <= 0.5 \
                and self.calories / self.max_calories > 0.25:
            hunger = 'hungry'

        elif self.calories / self.max_calories <= 0.25 \
                and self.calories / self.max_calories > 0.1:
            hunger = 'ravenous'

        elif self.calories / self.max_calories <= 0.1 \
                and self.calories > 0:
            hunger = 'famished'

        else:
            hunger = 'starving'

        return hunger

    def thirstString(self, prompt=False):
        thirst = ''

        if prompt and self.thirst / self.max_thirst > 0.5:
            return thirst

        if self.thirst / self.max_thirst > 0.5: 
            thirst = 'hydrated'

        elif self.thirst / self.max_thirst <= 0.5 \
                and self.thirst / self.max_thirst > 0.25:
            thirst = 'thirsty'

        elif self.thirst / self.max_thirst <= 0.25 \
                and self.thirst > 0:
            thirst = 'dehydrated'

        else:
            thirst = 'parched'

        return thirst

    def sleepString(self, prompt=False):
        sleep = ''

        if prompt and self.sleep / self.max_sleep > 0.25:
            return sleep

        if self.sleep / self.max_sleep > 0.25:
            sleep = 'awake'

        elif self.sleep / self.max_sleep <= 0.25 \
                and self.sleep > 0:
            sleep = 'yawning'

        else:
            sleep = 'drowsy'

        return sleep

    def windString(self, prompt=False):
        wind = ''

        if prompt and self.wind / self.max_wind >= 1.0:
            return wind

        if self.wind / self.max_wind >= 1.0:
            wind = 'breathing calmly'
        elif self.wind / self.max_wind < 1.0 \
                and self.wind / self.max_wind > 0.5:
            wind = 'breathing heavily'
        elif self.wind / self.max_wind <= 0.5 \
                and self.wind / self.max_wind > 0.25:
            wind = 'huffing'
        elif self.wind / self.max_wind <= 0.25 \
                and self.wind / self.max_wind > 0.1:
            wind = 'winded'
        else:
            wind = 'gasping'

        return wind

    def energyString(self, prompt=False):
        energy = ''

        if prompt and self.energy / self.max_energy > 0.5:
            return energy

        if self.energy / self.max_energy > 0.5:
            energy = 'rested'
        elif self.energy / self.max_energy <= 0.5 \
                and self.energy / self.max_energy > 0.25:
            energy = 'tired'
        elif self.energy / self.max_energy <= 0.25 \
                and self.energy / self.max_energy > 0.1:
            energy = 'fatigued'
        else:
            energy = 'exhausted'

        return energy

    def toString(self):
        reservesString = ("You are %s, %s, and %s.\nYou are %s and %s." %
                          (self.hungerString(), self.thirstString(), self.sleepString(), self.windString(), self.energyString()))
        return reservesString 

    def toJson(self):
        data = {}

        data["calories"] = self.calories
        data["maxCalories"] = self.max_calories

        data["thirst"] = self.thirst
        data["maxThirst"] = self.max_thirst

        data["sleep"] = self.sleep
        data["maxSleep"] = self.max_sleep

        data["wind"] = self.wind
        data["maxWind"] = self.max_wind

        data["energy"] = self.energy
        data["maxEnergy"] = self.max_energy

        return data

    def fromJson(self, data):

        self.calories = data["calories"]
        self.max_calories = data["maxCalories"]

        self.thirst = data["thirst"]
        self.max_thirst = data["maxThirst"]

        self.sleep = data["sleep"]
        self.max_sleep = data["maxSleep"]

        self.energy = data["energy"]
        self.max_energy = data["maxEnergy"]

        self.wind = data["wind"]
        self.max_wind = data["maxWind"]

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
        self.type = self.WOUND_SCRAPED

        # The amount of blood lost per game minute due to the wound.
        self.bleed = 0

        # If the wound is infected, that causes additional consequences.
        self.infected = False

        # The amount of pain caused by the wound.
        self.pain = 0

    def toJson(self):
        data = {}
        data['type'] = self.wound
        data['bleed'] = self.bleed
        data['infected'] = self.infected
        data['pain'] = self.pain
        return data

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
        data = {}
        data['wounds'] = {}
        for body_part in self.wounds:
            data['wounds'][body_part] = self.wounds[body_part]

        data['worn'] = {}
        for body_part in self.worn:
            data['worn'][body_part] = self.worn[body_part].getId()

        return data

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

    SPEED_WALKING = 'walking'
    SPEED_RUNNING = 'running'
    SPEED_SPRINTING = 'sprinting'

    POSITION_STANDING = 'standing'
    POSITION_RESTING = 'resting'
    POSITION_SLEEPING = 'sleeping'

    POSITION_DEAD = 'dead'

    def __init__(self):
        super(Character, self).__init__()

        self.is_player_character = False

        # The short description of the character.  Displayed when the character is looked at.
        self.description = ''

        # The long description.  Displayed when the character is examined closely.
        self.details = ''

        self.sex = self.SEX_MALE

        self.position = self.POSITION_STANDING
        self.speed = self.SPEED_WALKING

        self.attributes = Attributes()
        self.reserves = Reserves()

        self.body_type = 'bipedal'
        self.body = BipedalBody()

        self.inventory = []

        self.action = None
        self.action_data = {} 
        self.action_time = 0

        self.room = None

    def toJson(self):
        data = {}

        data['name'] = self.name
        data['description'] = self.description
        data['details'] = self.details
        data['sex'] = self.sex
        data['position'] = self.position
        data['speed'] = self.speed

        data['attributes'] = self.attributes.toJson()
        data['reserves'] = self.reserves.toJson()

        data['bodyType'] = self.body_type 
        data['body'] = self.body.toJson()

        data['inventory'] = []
        for item in self.inventory:
            data['inventory'].append(item.getId())

        if self.room:
            data['room'] = self.room.getId()

        return data

    def fromJson(self, data):
        self.setId(data['name'])

        self.description = data['description']
        self.details = data['details']
        self.sex = data['sex']

        if 'position' in data:
            self.position = data['position']
        else:
            self.position = self.POSITION_STANDING

        if 'speed' in data:
            self.speed = data['speed']
        else:
            self.speed = self.SPEED_WALKING

        self.body_type = data['bodyType']
        if self.body_type == 'bipedal':
            self.body = BipedalBody()
        elif self.body_type == 'quadrapedal':
            self.body = QuadrapedalBody()

        if 'body' in data:
            self.body.fromJson(data['body'])

        self.attributes = Attributes()
        if 'attributes' in data:
            self.attributes.fromJson(data['attributes'])

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


class PlayerCharacter(Character):

    def __init__(self):
        super(PlayerCharacter, self).__init__()

        self.is_player_character = True 

        self.account = None
        self.player = None
