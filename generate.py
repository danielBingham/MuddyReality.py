#!/usr/bin/python3

###############################################################################
# Generate a World for the Game
#
# Generates a world of the given size.
###############################################################################
import argparse, math, random, glob

from PIL import Image
import numpy as np
from matplotlib.colors import LightSource, LinearSegmentedColormap

from generator.world import World
from generator.biome import Biome

from generator.generators.heights import generateHeights
from generator.generators.biomes import generateBiomes
from generator.generators.rooms import generateRooms

def loadBiomes():
    biomes = {}

    print("Loading biomes...")
    biome_list = glob.glob('data/biomes/**/*.json', recursive=True)
    for file_path in biome_list:
        print("Loading biome " + file_path + "...")
        biome = Biome()
        biome.load(file_path)

        if not biome.name in biomes:
            biomes[biome.name] = biome
        else:
            print("Error! Duplicate Biome(%s)" % biome.name)

    return biomes

def generate(world, heightsOnly, biomesOnly, roomsOnly, regenerate):
    '''
    Generate the world.
    ''' 
    
    biomes = loadBiomes()

    if not biomesOnly and not roomsOnly and (not world.terrain or regenerate): 
        world.terrain = generateHeights(world)

    if not heightsOnly and not roomsOnly and world.terrain and (not world.biomes or regenerate):
        world.biomes = generateBiomes(biomes, world)

    if not biomesOnly and not heightsOnly and world.terrain and world.biomes and (not world.rooms or regenerate):
        world.rooms = generateRooms(biomes, world)

    world.save() 


random.seed()

parser = argparse.ArgumentParser(
                    prog='generate',
                    description='Generate a world for Muddy Reality.')

parser.add_argument('name', help='A name for the world that heights are being generated for.  This will be used as the output directory under `data/worlds/`.')

parser.add_argument('--width', default=10, help='Width of the world in kilometers. World will be square.')
parser.add_argument('--heights-only', dest='heightsOnly', action='store_true', help='Only generate the height map.  Will generate the worlds.json file if it does not exist.')
parser.add_argument('--biomes-only', dest='biomesOnly', action='store_true', help='Only generate the biomes. world.json matching `name` must have heights already generated.')
parser.add_argument('--rooms-only', dest='roomsOnly', action='store_true', help='Only generate the rooms. world.json matching `name` must have heights and biomes already generated.')
parser.add_argument('--regenerate', action='store_true', help='Regenerate the world, overriding any previously generated world.') 

arguments = parser.parse_args()

world = World(arguments.name,  math.floor(int(arguments.width) * 1000 / 100))
if not arguments.regenerate:
    if not world.load():
        world.save()
else:
    world.save()

generate(world, arguments.heightsOnly, arguments.biomesOnly, arguments.roomsOnly, arguments.regenerate)
        
