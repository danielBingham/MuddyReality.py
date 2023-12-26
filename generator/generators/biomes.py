import glob
import random

from generator.biome import Biome

initial_biomes_by_height = [ 
    { 'height': 100, 'biome': 'ocean' },
    { 'height': 105, 'biome': 'beach' },
    { 'height': 1000, 'biome': 'meadow' }
]

def getInitialBiomeFromHeight(height):
    for item in initial_biomes_by_height:
        if height <= item['height']:
            return item['biome']
    return 'meadow'

def generateBiomes(biomes, world):
    worldBiomes = [ [ { 'last_succession': 0, 'name': getInitialBiomeFromHeight(world.terrain[x][y]) } for y in range(len(world.terrain[x])) ] for x in range(len(world.terrain)) ] 

    for iteration in range(100):
        print("Iteration: %d of %d" % (iteration, 100))
        for x in range(len(worldBiomes)):
            for y in range(len(worldBiomes[x])):
                current = worldBiomes[x][y]
                biome = biomes[current['name']]

                # Handle Successions
                if biome.succession and current['last_succession'] + biome.succession_time < iteration: 
                    print("%s succeeding to %s" % (biome.name, biome.succession))
                    worldBiomes[x][y]['name'] = biome.succession
                    worldBiomes[x][y]['last_succession'] = iteration

                current = worldBiomes[x][y]
                biome = biomes[current['name']]

                # Handle Disruptions
                for disruption in biome.disruptions:
                    roll = random.randint(1,100)

                    if roll <= disruption['chance']:
                        print("%s disruption in %s biome to %s biome" % (disruption['name'], biome.name, disruption['biome']))
                        worldBiomes[x][y]['name'] = disruption['biome']
                        worldBiomes[x][y]['last_succession'] = iteration

    return [[ worldBiomes[x][y]['name'] for y in range(len(worldBiomes[x])) ] for x in range(len(worldBiomes))]







