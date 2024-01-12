import sys, glob, random

from generator.biome import Biome

initial_biomes_by_height = [ 
    {'height': 2000, 'biome': 'pioneer-meadow'}
]


def getInitialBiomeFromHeight(height):
    for item in initial_biomes_by_height:
        if height <= item['height']:
            return item['biome']
    return 'pioneer-meadow'


def spreadFire(depth, biomes, worldBiomes, iteration, x, y):
    if y < 0 or y >= len(worldBiomes):
        return

    if x < 0 or x >= len(worldBiomes[y]):
        return

    # Fire spread is limited by recursion, we're going to limit it to half the
    # recursion limit (500). 
    if depth >= 500:
        return

    current = worldBiomes[y][x]
    biome = biomes[current['name']]

    if "fire" in biome.disruptions:
        roll = random.randint(1, 100000) / 1000
        disruption = biome.disruptions['fire']

        if roll <= disruption['spread']:
            # print("Fire spread to (%d, %d) in %s, burned to %s..." % (y, x, current['name'], disruption['biome']))
            current['name'] = disruption['biome']
            current['last_succession'] = iteration

            try:
                spreadFire(depth+1, biomes, worldBiomes, iteration, x-1, y)
                spreadFire(depth+1, biomes, worldBiomes, iteration, x+1, y)
                spreadFire(depth+1, biomes, worldBiomes, iteration, x, y-1)
                spreadFire(depth+1, biomes, worldBiomes, iteration, x, y+1)
            except RecursionError:
                print("Recursion failed at depth %d" % depth)
                raise


def herdWander(depth, biomes, worldBiomes, iteration, x, y):
    if y < 0 or y >= len(worldBiomes):
        return False

    if x < 0 or x >= len(worldBiomes[y]):
        return False

    # Fire spread is limited by recursion, we're going to limit it to half the
    # recursion limit (500). 
    if depth >= 500:
        return False

    current = worldBiomes[y][x]
    biome = biomes[current['name']]

    if "herbivore-herd" in biome.disruptions:
        roll = random.randint(1, 100000) / 1000
        disruption = biome.disruptions['herbivore-herd']

        if roll <= disruption['spread']:
            # print("Fire spread to (%d, %d) in %s, burned to %s..." % (y, x, current['name'], disruption['biome']))
            current['name'] = disruption['biome']
            current['last_succession'] = iteration

            try:
                if herdWander(depth+1, biomes, worldBiomes, iteration, x-1, y):
                    return True 
                elif herdWander(depth+1, biomes, worldBiomes, iteration, x+1, y):
                    return True 
                elif herdWander(depth+1, biomes, worldBiomes, iteration, x, y-1):
                    return True 
                elif herdWander(depth+1, biomes, worldBiomes, iteration, x, y+1):
                    return True 
            except RecursionError:
                print("Recursion failed at depth %d" % depth)
                raise
    return False


def disrupt(biomes, worldBiomes, iteration, x, y):
    current = worldBiomes[y][x]
    biome = biomes[current['name']]

    # Handle Disruptions
    for name in biome.disruptions:
        roll = random.randint(1,100000) / 1000
        disruption = biome.disruptions[name]

        if name == 'fire' and roll <= disruption['chance']:
            # print("Fire ignited at (%d, %d) in %s, burned to %s..." % (y, x, current['name'], disruption['biome']))
            current['name'] = disruption['biome']
            current['last_succession'] = iteration


            spreadFire(1, biomes, worldBiomes, iteration, x-1, y)
            spreadFire(1,biomes, worldBiomes, iteration, x+1, y)
            spreadFire(1, biomes, worldBiomes, iteration, x, y-1)
            spreadFire(1, biomes, worldBiomes, iteration, x, y+1)

        if name == 'herbivore-herd' and roll <= disruption['chance']: 
            current['name'] = disruption['biome']
            current['last_succession'] = iteration

            if herdWander(1, biomes, worldBiomes, iteration, x-1, y):
                continue 
            elif herdWander(1, biomes, worldBiomes, iteration, x+1, y):
                continue 
            elif herdWander(1, biomes, worldBiomes, iteration, x, y-1):
                continue
            elif herdWander(1, biomes, worldBiomes, iteration, x, y+1):
                continue


def generateBiomes(biomes, world):
    worldBiomes = [[{'last_succession': 0, 'name': getInitialBiomeFromHeight(world.heights[y][x])} for x in range(len(world.heights[y]))] for y in range(len(world.heights))] 

    # Years to run the simulation
    iterations = 1000

    # Place rivers.
    for y in range(len(worldBiomes)):
        for x in range(len(worldBiomes[y])):
            if world.water[y][x] >= 0.3 and world.water[y][x] < 1:
                worldBiomes[y][x] = {'name': 'stream', 'last_succession': 0}
            elif world.water[y][x] >= 1 and world.water[y][x] < 2:
                worldBiomes[y][x] = {'name': 'river', 'last_succession': 0}
            elif world.water[y][x] >= 2:
                worldBiomes[y][x] = {'name': 'lake', 'last_succession': 0}

    for iteration in range(iterations):
        print("Succession: %d of %d years" % (iteration, iterations))
        for y in range(len(worldBiomes)):
            for x in range(len(worldBiomes[y])):
                current = worldBiomes[y][x]
                biome = biomes[current['name']]

                # Handle Successions
                if biome.succession and current['last_succession'] + biome.succession_time < iteration: 
                    worldBiomes[y][x]['name'] = biome.succession
                    worldBiomes[y][x]['last_succession'] = iteration

                disrupt(biomes, worldBiomes, iteration, x, y)

    return [[worldBiomes[y][x]['name'] for x in range(len(worldBiomes[y]))] for y in range(len(worldBiomes))]







