import math
import numpy as np

from generator.generators.erosion import erode
import generator.utils.util as util


def generateTerrain(world):
    """
    Generate terrain for `world`.  Terrain will be generated and stored in
    `world.terrain`.  Must have `world.name` and `world.width` populated.

    :param world:   `World` The world to generate terrain for.

    :returns:   `void`
    """

    print("Generating terrain for world %s..." % world.name)

    world.terrain = util.fbm([world.width, world.width], -2.0) 
    erode(world)


def generateHeights(world):
    """ 
    Generate a heightmap for `world` and store it on the world object.

    The `world` object must have `world.terrain` populated.  `world.terrain`
    will be translated to a height map with values in `meters` and stored in
    `world.heights`.

    :param world:   `World` The world to generate a heightmap for.  

    :returns:   `void`
    """ 

    print("Generating heightmap for world %s..." % world.name)
    terrain_heights = world.terrain.tolist() 
    world.heights = [[ (terrain_heights[x][y] * 2000 - 400) for y in range(len(terrain_heights[x])) ] for x in range(len(terrain_heights))]
