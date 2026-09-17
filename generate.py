###############################################################################
# Generate a World for the Game
#
# Generates a world of the given size.  Invoked through `main.py`:
#
#   python3 main.py generator [name] [generator arguments]
###############################################################################
import sys, random

import generator.utils.snapshot as snapshot

from generator.store.store import Store

from generator.generators.heights import generateTerrain, generateHeights 
from generator.generators.water import WaterGenerator 
from generator.generators.biomes import generateBiomes
from generator.generators.rooms import generateRooms


class Generator:

    def __init__(self):
        self.store = Store()

        self.arguments = {}

        self.generate_all = True
        self.generate_heights = False 
        self.generate_water = False 
        self.generate_biomes = False 
        self.generate_rooms = False 
        
        self.regenerate_all = False 
        self.regenerate_heights = False 
        self.regenerate_water = False 
        self.regenerate_biomes = False 
        self.regenerate_rooms = False 


    def initialize(self, arguments):
        """
        Initialize the generator from the command line arguments.

        Parameters
        ----------
        arguments:  dict
            A dictionary of command line arguments.
        """

        self.store.initializeWorld(arguments.name, int(arguments.width), int(arguments.room_width))
        self.world = self.store.world

        self.arguments = arguments

        # Which stages should we generate?  If no specific stage is specified,
        # then we generate all of them.
        self.generate_all = not (arguments.generate_heights or arguments.generate_water 
                                 or arguments.generate_biomes or arguments.generate_rooms)

        self.generate_heights = self.generate_all or arguments.generate_heights \
            or arguments.generate_water or arguments.generate_biomes \
            or arguments.generate_rooms
        self.generate_water = self.generate_all or arguments.generate_water \
            or arguments.generate_biomes or arguments.generate_rooms
        self.generate_biomes = self.generate_all or arguments.generate_biomes \
            or arguments.generate_rooms
        self.generate_rooms = self.generate_all or arguments.generate_rooms 

        # Should we regenerate any stages? If we regenerate all, then we set
        # them all to to regenerate.
        self.regenerate_all = arguments.regenerate_all
        self.regenerate_heights = arguments.regenerate_all or arguments.regenerate_heights
        self.regenerate_water = arguments.regenerate_all or arguments.regenerate_water
        self.regenerate_biomes = arguments.regenerate_all or arguments.regenerate_biomes
        self.regenerate_rooms = arguments.regenerate_all or arguments.regenerate_rooms

        if int(arguments.width) != self.world.width or int(arguments.room_width) != self.world.room_width:
            if not self.regenerate_all:
                print("Error! You can't regenerate a single stage with different world parameters.  If you want to change the world width or room_width, please regenerate the whole world.")
                sys.exit() 
            elif self.regenerate_all:
                print("Regenerating world with new world parameters...")
                self.world.width = int(arguments.width)
                self.world.room_width = int(arguments.room_width)
                self.world.save()


    def generate(self):
        '''
        Generate the world.
        ''' 

        print("Generating world %s, width [%d, %d] totaling %d rooms of size %d meters by %d meters" 
              % (self.world.name, self.world.width, self.world.width, self.world.width * self.world.width, self.world.room_width, self.world.room_width))

        if self.generate_heights and (self.world.terrain.size == 0 or self.regenerate_heights): 
            generateTerrain(self.world)
            snapshot.terrain(self.world)

            generateHeights(self.world)

        if self.generate_water and (self.world.water.size == 0 or self.regenerate_water):
            if self.world.terrain.size == 0 or not self.world.heights:
                print("Error! Must have generated a heightmap to generate water.")
                return

            water_generator = WaterGenerator(self.world, self.arguments)
            water_generator.generate()
            snapshot.water(self.world)

        if self.generate_biomes and (not self.world.biomes or self.regenerate_biomes):
            if self.world.terrain.size == 0 or not self.world.heights:
                print("Error! Must have generated a heightmap to generate biomes.")
                return
            if self.world.water.size == 0:
                print("Error! Must have generated water to generate biomes.")
                return

            self.world.biomes = generateBiomes(self.biomes, self.world)
            snapshot.biomes(self.world, self.biomes)

        if self.generate_rooms and (not self.world.rooms or self.regenerate_rooms):
            if self.world.terrain.size == 0 or not self.world.heights:
                print("Error! Must have generated a heightmap to generate rooms.")
                return
            if self.world.water.size == 0:
                print("Error! Must have generated water to generate rooms.")
                return
            if not self.world.biomes:
                print("Error! Must have generated biomes to generate rooms.")
                return

            self.world.rooms = generateRooms(self.biomes, self.world)

        self.world.save() 


def run(arguments):
    """
    Generate a world.

    Parameters
    ----------
    arguments:  argparse.Namespace
        The parsed command line arguments for the `generator` command, as
        defined in `main.py`.
    """

    random.seed()

    generator = Generator()
    generator.initialize(arguments)
    generator.generate()
