import os
import json

class World:

    def __init__(self, name, width):
        self.name = name
        self.width = width

        self.terrain = []
        self.biomes = []
        self.rooms = []

    def toJson(self):
        json = {}

        json['name'] = self.name
        json['width'] = self.width

        json['terrain'] = self.terrain
        json['biomes'] = self.biomes
        json['rooms'] = self.rooms

        return json

    def fromJson(self, json):
        self.name = json['name']
        self.width = json['width']

        self.terrain = json['terrain']
        self.biomes = json['biomes']
        self.rooms = json['rooms']

        return self

    def save(self, base_path='data/worlds/'):
        path = base_path + self.name + '/'

        if not os.path.exists(path):
            os.mkdir(path)

        file = open(path + 'world.json', 'w')
        try:
            json.dump(self.toJson(), file)    
        finally:
            file.close()

        return self

    def load(self, base_path='data/worlds/'):
        path = base_path + self.name + '/'

        if not os.path.exists(path) or not os.path.exists(path + 'world.json'):
            return False 

        file = open(path + 'world.json', 'r')
        try: 
            self.fromJson(json.load(file))
        except:
            return False
        finally:
            file.close()

        return True 



