#!/usr/bin/python3

###############################################################################
# Generate a World for the Game
#
# Generates a world of the given size.
###############################################################################
import sys, argparse, random, glob, math

import generator.utils.snapshot as snapshot

from generator.world import World
from generator.biome import Biome

from generator.generators.heights import generateTerrain, generateHeights 
from generator.generators.water import generateWater
from generator.generators.biomes import generateBiomes
from generator.generators.rooms import generateRooms

def loadBiomes():
    """
    Load the biomes that we'll use to generate the world.

    :returns:   `dict(Biome)`   A dictionary of all the biomes keyed by `Biome.name`.
    """

    biomes = {}

    print("Loading biomes...")
    biome_list = glob.glob('data/biomes/**/*.json', recursive=True)
    for file_path in biome_list:
        print("Loading biome " + file_path + "...")
        biome = Biome()
        if not biome.load(file_path):
            print("Error! Failed to load %s..." % file_path)
        else:
            if not biome.name in biomes:
                biomes[biome.name] = biome
            else:
                print("Error! Duplicate Biome(%s)" % biome.name)

    return biomes

def generate(world, heights_only=False, water_only=False, biomes_only=False, rooms_only=False, regenerate=False):
    '''
    Generate the world.
    ''' 
    
    biomes = loadBiomes()

    print(world.terrain.size)
    print(world.terrain)
    if not water_only and not biomes_only and not rooms_only and (world.terrain.size == 0 or regenerate): 
        generateTerrain(world)
        snapshot.terrain(world)

        generateHeights(world)

    if not heights_only and not biomes_only and not rooms_only and (world.water.size == 0 or regenerate):
        if world.terrain.size == 0 or not world.heights:
            print("Error! Must have generated a heightmap to generate water.")
            return

        generateWater(world)
        snapshot.water(world)

    if not heights_only and not water_only and not rooms_only and (not world.biomes or regenerate):
        if world.terrain.size == 0 or not world.heights:
            print("Error! Must have generated a heightmap to generate biomes.")
            return
        if world.water.size == 0:
            print("Error! Must have generated water to generate biomes.")
            return

        world.biomes = generateBiomes(biomes, world)
        snapshot.biomes(world, biomes)

    if not heights_only and not water_only and not biomes_only and (not world.rooms or regenerate):
        if world.terrain.size == 0 or not world.heights:
            print("Error! Must have generated a heightmap to generate rooms.")
            return
        if world.water.size == 0:
            print("Error! Must have generated water to generate rooms.")
            return
        if not world.biomes:
            print("Error! Must have generated biomes to generate rooms.")
            return

        world.rooms = generateRooms(biomes, world)

    world.save() 


random.seed()

parser = argparse.ArgumentParser(
                    prog='generate',
                    description='Generate a world for Muddy Reality.')

parser.add_argument('name', help='A name for the world that heights are being generated for.  This will be used as the output directory under `data/worlds/`.')

# World shape parameters.
parser.add_argument('--width', default=100, help='Width of the world in rooms.  World will be square with width^2 total rooms..')
parser.add_argument('--room-width', dest='room_width', default=100, help='Width of an individual room in meters.  World will be (room-width*width)^2 total area.')

parser.add_argument('--initial-water', default=30, dest='initial_water', help='The initial water that will be dumped on the world and allowed to flow to the low areas in depth (meters) per world point.')

# Parameters for controlling which parts of the generating we're doing.
parser.add_argument('--heights-only', dest='heights_only', action='store_true', help='Only generate the height map.  Will generate the worlds.json file if it does not exist.')
parser.add_argument('--water-only', dest='water_only', action='store_true', help='Only generate the worlds water.')
parser.add_argument('--biomes-only', dest='biomes_only', action='store_true', help='Only generate the biomes. world.json matching `name` must have heights already generated.')
parser.add_argument('--rooms-only', dest='rooms_only', action='store_true', help='Only generate the rooms. world.json matching `name` must have heights and biomes already generated.')

parser.add_argument('--regenerate', action='store_true', help='Regenerate the world, overriding any previously generated world.') 

arguments = parser.parse_args()
print(arguments)

world = World(arguments.name,  int(arguments.width), int(arguments.room_width))

world.initial_water = int(arguments.initial_water)

if not world.load():
    world.save()

if int(arguments.width) != world.width or int(arguments.room_width) != world.room_width:
    if not arguments.regenerate or arguments.heights_only \
            or arguments.water_only or arguments.biomes_only or arguments.rooms_only:
        print("Error! You can't regenerate a single stage with different world parameters.  If you want to change the world width or room_width, please regenerate the whole world.")
        sys.exit() 
    elif arguments.regenerate:
        print("Regenerating world with new world parameters...")
        world.width = int(arguments.width)
        world.room_width = int(arguments.room_width)
        world.save()


print("Generating world %s, width [%d, %d] totaling %d rooms of size %d meters by %d meters" % (world.name, world.width, world.width, world.width * world.width, world.room_width, world.room_width))
generate(world, arguments.heights_only, arguments.water_only, arguments.biomes_only, arguments.rooms_only, arguments.regenerate)
        
