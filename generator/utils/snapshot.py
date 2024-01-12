###############################################################################
#
# Contains utilities for taking snapshots of the world in various states of
# generation and saving them as PNG images that make it easier to understand
# the world.
#
##############################################################################

import math

from PIL import Image
import numpy as np
from matplotlib.colors import LightSource, LinearSegmentedColormap

import generator.utils.util as util


def save_as_png(a, path):
    """ 
    Save a numpy array as a PNG image using RGB mode.


    :param a:   `array_like`    NumPy array populated with pixel RGB values.
    :param path:    `str`       The output path, relative to the root domain.

    :returns:   `void`
    """ 

    image = Image.fromarray(a.astype('uint8'), mode="RGB")
    image.save(path)


def biomes(world, biomes):
    """ 
    Take a snapshot of the world's biomes.

    :param world:   `World`     The world object with `world.biomes` populated.
    :param biomes:  `dict(Biome)`   A dict of `Biome` objects, keyed by `Biome.name`.

    :returns:   `void`
    """ 

    print("Snapshotting biomes...")
    pixels = [[ None for x in range(world.width * 10) ] for y in range(world.width * 10) ]
    for y in range(world.width * 10):
        for x in range(world.width * 10):
            pixels[y][x] = biomes[world.biomes[math.floor(y/10)][math.floor(x/10)]].color

    save_as_png(np.array(pixels), 'data/worlds/' + world.name + '/biomes.png')


def terrain(world): 
    """
    Save a snapshot of the world's terrain as a hillshaded PNG.

    :param world:   `World` The World object with `world.terrain` populated.

    :returns:   `void`
    """

    save_as_png(np.round(hillshaded(world.terrain) * 255), 'data/worlds/' + world.name  + '/terrain.png')


def water(world):
    save_as_png(np.round(watershaded(world.water) * 255), 'data/worlds/' + world.name + '/water.png')


def snapWater(water, filepath):
    save_as_png(np.round(watershaded(water)*255), filepath)

#  Borrowed from: https://github.com/dandrino/terrain-erosion-3-ways/
# Used by hillshaded to map terrain height values to colors. 
_TERRAIN_CMAP = LinearSegmentedColormap.from_list('my_terrain', [
    (0.00, (0.15, 0.3, 0.45)),
    (0.19, (0.25, 0.5, 1.00)),
    # (0.01, (0.15, 0.3, 0.15)),
    (0.20, (0.3, 0.45, 0.3)),
    (0.50, (0.5, 0.5, 0.35)),
    (0.80, (0.4, 0.36, 0.33)),
    (1.00, (1.0, 1.0, 1.0)),
])
#  Borrowed from: https://github.com/dandrino/terrain-erosion-3-ways/


def hillshaded(a, land_mask=None, angle=270):
    """
    Takes a NumPy array heightmap and uses it to create a hillshaded pixel map
    representing the heights in the heightmap.  Normalizes the heightmap to
    [0,1] before translating to pixels.

    :param a:   `array_like`    The heightmap, stored in a NumPy array.
    :param land_mask:           A numpy array of ??? structure representing water.
    :param angle:               The angle from which the light source shines on the terrain.

    :returns:   `array_like`    A NumPy array of pixels representing the map.
    """

    if land_mask is None: land_mask = np.ones_like(a)
    ls = LightSource(azdeg=angle, altdeg=30)
    land = ls.shade(a, cmap=_TERRAIN_CMAP, vert_exag=10.0,
                  blend_mode='overlay')[:, :, :3]
    water = np.tile((0.25, 0.35, 0.55), a.shape + (1,))
    return util.lerp(water, land, land_mask[:, :, np.newaxis])


_WATER_CMAP= LinearSegmentedColormap.from_list('my_terrain', [
    (0.00, (0.75, 0.9, 0.9)),
    (0.05, (0.3, 0.8, 0.8)),
    (0.10, (0.3, 0.7, 0.8)),
    (0.25, (0.3, 0.6, 0.8)),
    (0.50, (0.25, 0.5, 0.8)),
    (0.75, (0.2, 0.4, 0.8)),
    (1.00, (0.0, 0.0, 1.0)),
])


def watershaded(a, angle=270):
    ls = LightSource(azdeg=angle, altdeg=80)
    land = ls.shade(a, cmap=_WATER_CMAP, vert_exag=10.0,
                  blend_mode='overlay')[:, :, :3]
    return land
