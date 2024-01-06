import os
import json

class Biome:

    WATER_NONE = 'none'
    WATER_FRESH = 'fresh'
    WATER_SALT = 'salt'

    def __init__(self):

        # The name of the biome.
        self.name = ''
        self.color = ()

        self.titles = []
        self.descriptions = []  

        # An array of Item.id that represents trees that can spawn in this
        # biome.
        self.trees = []

        # The density at which trees grow in this biome.
        #
        # For values less than 1.0, trees will be spread out and the canopy
        # will have frequent breaks.
        #
        # 1.0 - Trees will grow to the maximum density allowed by their full
        # canopy.  Rooms are 100m x 100m, so a tree with a 50m canopy can spawn
        # 2 to a room. 
        #
        # Values over 1.0 mean trees grow closer together than their full
        # canopy and will spawn more densly.
        self.tree_density = 0 

        # An array of shrubs that can spawn in this biome. 
        self.shrubs = []

        # The density of the shrub layer.  See `tree_density`.
        self.shrub_density = 0 

        # An array of herbs that can spawn in this biome.  
        self.herbs = []

        # The density of the herb layer.  See `tree_density`.
        self.herb_density = 0

        # An array of debris that can spawn on the floor of this biome.
        self.debris = []

        self.debris_density = 0

        # Is there water in this biome?  How much?
        self.water = Biome.WATER_NONE

        ###  Biome Evolution ###
        # Values managing the way the biome evolves over time.
        ###

        # What biome does this biome eventually evolve into?
        self.succession = None

        # How long does it take this biome to evolve in 1 years.
        self.succession_time = 0

        # A list of disruptions that can occur.  Each list item includes the
        # chance of the disruption as a percentage, its name, the the biome that results.
        # { name: 'forest fire', chance: 10, biome: 'meadow' }
        self.disruptions = []

    
    def toJson(self):
        json = {}

        json['name'] = self.name
        json['color'] = self.color

        json['titles'] = self.titles
        json['descriptions'] = self.descriptions

        json['trees'] = self.trees
        json['treeDensity'] = self.tree_density

        json['shrubs'] = self.shrubs
        json['shrubDensity'] = self.shrub_density

        json['herbs'] = self.herbs
        json['herbDensity'] = self.herb_density

        json['debris'] = self.debris
        json['debrisDensity'] = self.debris_density

        json['water'] = self.water

        json['succession'] = self.succession
        json['successionTime'] = self.succession_time

        json['disruptions'] = self.disruptions

        return json

    def fromJson(self, data):
        self.name = data['name']
        self.color = tuple(data['color'])

        self.titles = data['titles']
        self.descriptions = data['descriptions']

        self.trees = data['trees']
        self.tree_density = data['treeDensity']
        
        self.shrubs = data['shrubs']
        self.shrub_density = data['shrubDensity']

        self.herbs = data['herbs']
        self.herb_density = data['herbDensity']

        self.debris = data['debris']
        self.debris_density = data['debrisDensity']

        self.water = data['water']

        self.succession = data['succession']
        self.succession_time = data['successionTime']

        self.disruptions = data['disruptions']

        return self 
    
    def save(self, base_path='data/biomes/'):
        if not os.path.exists(base_path):
            os.mkdir(base_path)

        file = open(base_path + self.name + '.json', 'w')
        try:
            json.dump(self.toJson(), file)    
        except Exception:
            raise
        finally:
            file.close()

        return self

    def load(self, path):
        if not os.path.exists(path):
            return False 

        file = open(path, 'r')
        try: 
            self.fromJson(json.load(file))
        except:
            return False
        finally:
            file.close()

        return True 
