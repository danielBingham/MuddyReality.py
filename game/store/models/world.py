from game.store.models.base import NamedModel

class World(NamedModel):

    def __init__(self):
        super(World, self).__init__()

        self.name = '' 
        self.width = 0 
        self.room_width = 0  

        self.rooms = []

    def toJson(self):
        json = {}

        json['name'] = self.name
        json['width'] = self.width
        json['roomWidth'] = self.room_width

        json['rooms'] = self.rooms

        return json

    def fromJson(self, json):
        self.name = json['name']
        self.width = json['width']
        self.room_width = json['roomWidth']

        self.rooms = json['rooms']

        return self

