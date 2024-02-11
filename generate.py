#!/usr/bin/python3

###############################################################################
# Generate a World for the Game
#
# Generates a world of the given size.
###############################################################################
import sys, argparse, random 

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

        print("Generating world %s, width [%d, %d] totaling %d rooms of size %d meters by %d meters" \
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


def main():
    random.seed()

    parser = argparse.ArgumentParser(
                        prog='generate',
                        description='Generate a world for Muddy Reality.')

    parser.add_argument('name', help='A name for the world that heights are being generated for.  This will be used as the output directory under `data/worlds/`.')

    # World shape parameters.
    parser.add_argument('--width', default=100, help='Width of the world in rooms.  World will be square with width^2 total rooms..')
    parser.add_argument('--room-width', dest='room_width', default=100, help='Width of an individual room in meters.  World will be (room-width*width)^2 total area.')

    # Parameters for controlling which parts of the generating we're doing.
    parser.add_argument('--generate-heights', dest='generate_heights', action='store_true', help='Only generate the height map.  Will generate the worlds.json file if it does not exist.')
    parser.add_argument('--generate-water', dest='generate_water', action='store_true', help='Only generate the worlds water.')
    parser.add_argument('--generate-biomes', dest='generate_biomes', action='store_true', help='Only generate the biomes. world.json matching `name` must have heights already generated.')
    parser.add_argument('--generate-rooms', dest='generate_rooms', action='store_true', help='Only generate the rooms. world.json matching `name` must have heights and biomes already generated.')

    # Parmeters for controlling what, if anything, we should regenerate.  If
    # none of these are true, then anything previously generated will be reused
    # as is.  That stage of generation will be skipped.
    parser.add_argument('--regenerate-all', dest='regenerate_all', action='store_true', help='Regenerate the world, overriding any previously generated world.') 
    parser.add_argument('--rengerate-heights', dest='regenerate_heights', action='store_true', help="Regenerate the world's heightmap, overriding any previously generated terrain.")
    parser.add_argument('--regenerate-water', dest='regenerate_water', action='store_true', help="Regenerate the world's water, overriding any previously generated water.")
    parser.add_argument('--regenerate-biomes', dest='regenerate_biomes', action='store_true', help="Regenerate the world's biomes, overriding any previously generated biomes.")
    parser.add_argument('--regenerate-rooms', dest='regenerate_rooms', action='store_true', help="Regenerate the world's rooms, overriding any previously generated rooms.")

    # Water generation parameters
    parser.add_argument('--water-initial-amount', default=30, dest='water__initial_amount', help="The initial water that will be dumped on the world and allowed to flow to the low areas in depth (meters) per world point.")
    parser.add_argument('--water-algorithm', default='inria', dest='water__algorithm', help='Choose the algorithm that will be used to generate water.')
    parser.add_argument('--water-debug', dest="water__debug", action="store_true", help="Turn on debugging output for the water algorith.")
    parser.add_argument("--water-snapshot", dest="water__snapshot", action="store_true", help="Turn on snapshotting for the water algorithm.  This will take an image snapshot of the water at the end of each iteration and then construct an animation of them showing the full water flow for the duration of the simulation at the end.  Images will be stored in the `snaps/` directory.")
    parser.add_argument("--water-flat-terrain", dest="water__flat_terrain", action="store_true", help="Run the water simulation on a flat terrain instead of the terrain generated in the previous step.")

    arguments = parser.parse_args()

    generator = Generator()
    generator.initialize(arguments)
    generator.generate()

if __name__ == '__main__':
    main()
