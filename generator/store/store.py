import glob 

from generator.store.biome import Biome
from generator.store.world import World

class Store:


    def __init__(self):
        self.world = None
        self.biomes = {}

    def initializeWorld(self, name, width, room_width):
        """
        Attempt to load the world from a file.  If we fail to load it, save our
        newly initialized world.
        """

        self.world = World(name, width, room_width)

        if not self.world.load():
            self.world.save()


    def loadBiomes(self):
        """
        Load the biomes that we'll use to generate the world.
        """

        self.biomes = {}

        print("Loading biomes...")
        biome_list = glob.glob('data/biomes/**/*.json', recursive=True)
        for file_path in biome_list:
            print("Loading biome " + file_path + "...")
            biome = Biome()
            if not biome.load(file_path):
                print("Error! Failed to load %s..." % file_path)
            else:
                if biome.name not in self.biomes:
                    self.biomes[biome.name] = biome
                else:
                    print("Error! Duplicate Biome(%s)" % biome.name)
