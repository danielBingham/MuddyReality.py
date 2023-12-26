import math
import numpy as np

from generator.generators.erosion import erode
import generator.utils.util as util

def generateHeights(world):
    '''
    Generate a new heightmap and save it in 'output'.  Generates two files:
    output.png and output.json

    width: The width of the world in 100mx100m rooms.
    ''' 

    # Generate the initial height map.
    terrain = util.fbm([world.width, world.width], -2.0) 

    # Erode the height map.
    terrain = erode(terrain, world.width)
    util.save_as_png(util.hillshaded(terrain), 'data/worlds/' + world.name  + '/terrain-raw.png')

    terrain_heights = terrain.tolist() 

    world_heights = [[ math.floor((terrain_heights[x][y] * 1000 - 100)) for y in range(len(terrain_heights[x])) ] for x in range(len(terrain_heights))]

    util.save_as_png(util.hillshaded(np.array(world_heights)), 'data/worlds/' + world.name + '/terrain.png')

    return world_heights
