import glob
import random

from generator.biome import Biome

initial_biomes_by_height = [ 
    { 'height': 0, 'biome': 'pioneer-meadow' }
]

def getInitialBiomeFromHeight(height):
    for item in initial_biomes_by_height:
        if height <= item['height']:
            return item['biome']
    return 'meadow'

def spreadFire(biomes, worldBiomes, iteration, x, y):
    if y < 0 or y >= len(worldBiomes):
        return

    if x < 0 or x >= len(worldBiomes[y]):
        return

    current = worldBiomes[y][x]
    biome = biomes[current['name']]
    
    if "fire" in worldBiomes[y][x].disruptions:
        roll = random.randint(1, 100)
        disruption = biomes.disruptions['fire']

        if roll <= disruption['spread']:
            current['name'] = disruption['biome']
            current['last_succession'] = iteration

            spreadFire(biomes, worldBiomes, iteration, x-1, y)
            spreadFire(biomes, worldBiomes, iteration, x+1, y)
            spreadFire(biomes, worldBiomes, iteration, x, y-1)
            spreadFire(biomes, worldBiomes, iteration, x, y+1)


def disrupt(biomes, worldBiomes, iteration, x, y):
    current = worldBiomes[y][x]
    biome = biomes[current['name']]

    # Handle Disruptions
    for name in biome.disruptions:
        roll = random.randint(1,100)
        disruption = biome.disruptions[name]

        if disruption["name"] == 'fire' and roll <= disruption['ignition']:
            current['name'] = disruption['biome']
            current['last_succession'] = iteration

            spreadFire(biomes, worldBiomes, iteration, x-1, y)
            spreadFire(biomes, worldBiomes, iteration, x+1, y)
            spreadFire(biomes, worldBiomes, iteration, x, y-1)
            spreadFire(biomes, worldBiomes, iteration, x, y+1)


def generateBiomes(biomes, world):
    worldBiomes = [ [ { 'last_succession': 0, 'name': getInitialBiomeFromHeight(world.heights[y][x]) } for x in range(len(world.heights[y])) ] for y in range(len(world.heights)) ] 

    # Place rivers.
    for y in range(len(worldBiomes)):
        for x in range(len(worldBiomes[y])):
            if  world.water[y][x] >= 0.3 and world.water[y][x] < 1:
                worldBiomes[y][x] = { 'name': 'stream', 'last_succession': 0 }
            elif world.water[y][x] >= 1 and world.water[y][x] < 2:
                worldBiomes[y][x] = { 'name': 'river', 'last_succession': 0 }
            elif world.water[y][x] >= 2:
                worldBiomes[y][x] = { 'name': 'lake', 'last_succession': 0 }

    for iteration in range(200):
        print("Iteration: %d of %d" % (iteration, 200))
        for y in range(len(worldBiomes)):
            for x in range(len(worldBiomes[y])):
                current = worldBiomes[y][x]
                biome = biomes[current['name']]

                # Handle Successions
                if biome.succession and current['last_succession'] + biome.succession_time < iteration: 
                    worldBiomes[y][x]['name'] = biome.succession
                    worldBiomes[y][x]['last_succession'] = iteration

                disrupt(biomes, worldBiomes, iteration, x, y)

    return [[ worldBiomes[y][x]['name'] for x in range(len(worldBiomes[y])) ] for y in range(len(worldBiomes))]







