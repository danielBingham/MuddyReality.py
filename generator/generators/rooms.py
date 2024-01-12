import random, copy, glob, math

from game.store.models.room import Room
from game.store.models.room import Exit
from game.store.models.item import Item


def loadItems():
    print("Loading items...")
    items = {}
    item_list = glob.glob('data/items/**/*.json', recursive=True)
    for file_path in item_list:
        print("Loading item " + file_path + "...")
        item = Item()
        item.load(file_path)
        if not item.id in items:
            items[item.id] = item
        else:
            print("Error! Duplicate Item(%s)..." % item.id)

    return items


def instance(items, itemId):
    if itemId in items:
        return copy.deepcopy(items[itemId])
    else:
        print("Error!  Attempt to instance Item(%s) that does not exist." % itemId)
        return None


def populateItems(world, room, biome, items, itemIds, density):
    room_area = world.room_width ** 2

    coverage = 0
    while coverage / room_area < density:
        index = random.randrange(len(itemIds))
        itemId = itemIds[index]
        if itemId in items:
            item = instance(items, itemId)
            room.items.append(item)
            coverage += item.width * item.length
        else:
            print("Error! Item(%s) not found for Biome(%s)." % (itemId, biome.name))
            break


def dX(world, x, dx):
    if x+dx < 0:
        return world.width + (x+dx)
    if x+dx >= world.width:
        return x+dx - world.width 
    return x+dx


def dY(world, y, dy):
    if y+dy < 0:
        return world.width + (y+dy)
    if y+dy >= world.width:
        return y+dy - world.width
    return y+dy


def descriptionFromSlope(slope):
    if slope == 0:
        return "levels"

    direction = "up"
    if slope < 0:
        direction = "down"

    description = ""
    if abs(slope) > 0 and abs(slope) <= 0.1:
        description = "slopes %s gently" % direction
    elif abs(slope) > 0.1 and abs(slope) <= 0.25:
        description = "slopes %s slightly" % direction
    elif abs(slope) > 0.25 and abs(slope) <= 0.5:
        description = "slopes %s" % direction
    elif abs(slope) > 0.5 and abs(slope) <= 0.75:
        description = "slopes %s steeply" % direction
    elif abs(slope) > 0.75 and abs(slope) <= 0.90:
        description = "slopes %s precipitously" % direction

    return description


def generateNeighborDescription(world, rooms, y, x):
    height = world.terrain[y][x]

    slope_north = 0
    slope_east = 0
    slope_south = 0
    slope_west = 0

    description = ""

    dy = dY(world, y, -1)
    slope_north = math.atan((height - world.terrain[dy][x])/world.room_width)
    description += "The land to the north %s to %s. " % (descriptionFromSlope(slope_north), rooms[dy][x].title.lower()) 

    dx = dX(world, x, 1)
    slope_east = math.atan((height - world.terrain[y][dx])/world.room_width)
    description += "To the east it %s to %s. " % (descriptionFromSlope(slope_east), rooms[y][dx].title.lower())

    dy = dY(world, y, 1)
    slope_south = math.atan((height - world.terrain[dy][x])/world.room_width)
    description += "To the south it %s to %s. " % (descriptionFromSlope(slope_south), rooms[dy][x].title.lower())

    dx = dX(world, x, -1)
    slope_west = math.atan((height - world.terrain[y][dx])/world.room_width)
    description += "To the west it %s to %s. " % (descriptionFromSlope(slope_west), rooms[y][dx].title.lower())

    return description


def generateRooms(biomes, world):

    rooms = [[None for x in range(world.width)] for y in range(world.width)]

    # Generate and populate the rooms.
    id = 1
    for y in range(world.width):
        for x in range(world.width):
            print("Generating (%d, %d) as Room(%d)..." % (x, y, id))
            biome = biomes[world.biomes[y][x]]
            height = world.terrain[y][x]

            room = Room()
            room.id = id

            title = random.randrange(0, len(biome.titles))
            room.title = biome.titles[title]
            room.color = biome.color

            room.water_type = biome.water
            room.water = world.water[y][x]
            room.water_velocity = 0

            initial = random.randrange(0, len(biome.descriptions['initial']))
            room.description = biome.descriptions['initial'][initial]

            number_of_flavor = random.randrange(0, len(biome.descriptions['flavor']))
            for flavor in random.sample(range(len(biome.descriptions['flavor'])), number_of_flavor):
                room.description += " " + biome.descriptions['flavor'][flavor]

            rooms[y][x] = room
            id += 1

    for y in range(world.width):
        for x in range(world.width):
            room = rooms[y][x]

            room.description += " " + generateNeighborDescription(world, rooms, y, x)

    # Connect the rooms together.
    for y in range(len(rooms)):
        for x in range(len(rooms[y])):
            print("Connecting Room(%d)" % rooms[y][x].id)

            if not 'north' in rooms[y][x].exits:
                dy = dY(world, y, -1)

                exit = Exit(rooms[y][x])
                exit.direction = 'north'
                exit.room_to = rooms[dy][x]
                rooms[y][x].exits['north'] = exit

                exit = Exit(rooms[dy][x])
                exit.direction = 'south'
                exit.room_to = rooms[y][x]
                rooms[dy][x].exits['south'] = exit

            if not 'west' in rooms[y][x].exits:
                dx = dX(world, x, -1)

                exit = Exit(rooms[y][x])
                exit.direction = 'west'
                exit.room_to = rooms[y][dx]
                rooms[y][x].exits['west'] = exit 

                exit = Exit(rooms[y][dx])
                exit.direction = 'east'
                exit.room_to = rooms[y][x]
                rooms[y][dx].exits['east'] = exit

            if not 'east' in rooms[y][x].exits:
                dx = dX(world, x, 1)

                exit = Exit(rooms[y][x])
                exit.direction = 'east'
                exit.room_to = rooms[y][dx]
                rooms[y][x].exits['east'] = exit

                exit = Exit(rooms[y][dx])
                exit.direction = 'west'
                exit.room_to = rooms[y][x]
                rooms[y][dx].exits['west'] = exit

            if not 'south' in rooms[y][x].exits:
                dy = dY(world, y, 1)

                exit = Exit(rooms[y][x])
                exit.direction = 'south'
                exit.room_to = rooms[dy][x]
                rooms[y][x].exits['south'] = exit

                exit = Exit(rooms[dy][x])
                exit.direction = 'north'
                exit.room_to = rooms[y][x]
                rooms[dy][x].exits['north'] = exit

    items = loadItems()

    room_area = world.room_width * world.room_width
    # Populate the rooms
    for y in range(len(rooms)):
        for x in range(len(rooms[y])):
            print("Adding items to Room(%d)..." % (rooms[y][x].id))
            biome = biomes[world.biomes[y][x]]

            # Trees
            if biome.trees and biome.tree_density > 0:
                populateItems(world, rooms[y][x], biome, items, biome.trees, biome.tree_density)

            if biome.shrubs and biome.shrub_density > 0:
                populateItems(world, rooms[y][x], biome, items, biome.shrubs, biome.shrub_density)
            if biome.herbs and biome.herb_density > 0:
                populateItems(world, rooms[y][x], biome, items, biome.herbs, biome.herb_density)

            if biome.debris and biome.debris_density > 0:
                populateItems(world, rooms[y][x], biome, items, biome.debris, biome.debris_density)

    for y in range(len(rooms)):
        for x in range(len(rooms[y])):
            print("Saving Room(%d)..." % rooms[y][x].id)
            rooms[y][x].save('data/worlds/' + world.name + '/rooms/')

    return [[rooms[y][x].id for x in range(len(rooms[y]))] for y in range(len(rooms))]







