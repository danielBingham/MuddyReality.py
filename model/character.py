class Character:
    'Represents a single character in the game.'

    EQUIPMENT_LOCATIONS = [
        'left-hand',
        'right-hand',
        'forearms',
        'torso',
        'legs',
        'feet',
        'head',
        'back',
        'waist',
        'neck'
    ]

    def __init__(self, name):
        self.name = name 
        self.title = ''

        self.dexterity = 0
        self.strength = 0
        self.constitution = 0
        self.intelligence = 0
        self.wisdom = 0
        self.perception = 0

        self.experience = 0

        self.health = 0
        self.mana = 0

        self.inventory = []
        self.equipment = {}

    def save(self):
        pass

    def load(self):
        pass


