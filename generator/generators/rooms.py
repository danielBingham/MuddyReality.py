import random, copy, glob, math

from game.library.models.room import Room
from game.library.models.room import Exit
from game.library.models.item import Item

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

def descriptionFromSlope(slope):
    if slope == 0:
        return "flat"

    description = ""
    if abs(slope) > 0 and abs(slope) <= 0.1:
        description = "gently sloped"
    elif abs(slope) > 0.1 and abs(slope) <= 0.25:
        description = "sloped"
    elif abs(slope) > 0.25 and abs(slope) <= 0.5:
        description = "moderately sloped"
    elif abs(slope) > 0.5 and abs(slope) <= 0.75:
        description = "steeply sloped"
    elif abs(slope) > 0.75 and abs(slope) <= 0.90:
        description = "extremely sloped"
    
    if slope < 0:
        description += " down"
    else:
        description += " up"

    return description

def generateSlopeDescription(world, y, x):
    height = world.terrain[y][x]

    slope_north = 0
    slope_east = 0
    slope_south = 0
    slope_west = 0

    if y > 0:
        slope_north = math.atan((height - world.terrain[y-1][x])/world.room_width)
    if y < world.width-1:
        slope_south = math.atan((height - world.terrain[y+1][x])/world.room_width)

    if x > 0:
        slope_west = math.atan((height - world.terrain[y][x-1])/world.room_width)
    if x < world.width-1:
        slope_east = math.atan((height - world.terrain[y][x+1])/world.room_width)

    description = "The land is %s to the north, %s to the east, %s to the south, %s to the west." % \
        (descriptionFromSlope(slope_north), descriptionFromSlope(slope_east), descriptionFromSlope(slope_south), descriptionFromSlope(slope_west))
    return description

def generateRooms(biomes, world):
  
    rooms = [[ None for x in range(world.width) ] for y in range(world.width) ]

    # Generate and populate the rooms.
    id = 1
    for y in range(world.width):
        for x in range(world.width):
            print("Generating (%d, %d) as Room(%d)..." % (x,y,id))
            biome = biomes[world.biomes[y][x]]
            height = world.terrain[y][x]

            room = Room()
            room.id = id

            title = random.randrange(0, len(biome.titles))
            room.title = biome.titles[title]

            initial = random.randrange(0, len(biome.descriptions['initial']))
            room.description = biome.descriptions['initial'][initial]

            number_of_flavor = random.randrange(0, len(biome.descriptions['flavor']))
            for flavor in random.sample(range(len(biome.descriptions['flavor'])), number_of_flavor):
                room.description += " " + biome.descriptions['flavor'][flavor]

            # Generate height descriptions.
            room.description += " " + generateSlopeDescription(world, y, x) 
            
            rooms[y][x] = room
            id += 1


    # Connect the rooms together.
    for y in range(len(rooms)):
        for x in range(len(rooms[y])):
            print("Connecting Room(%d)" % rooms[y][x].id)
            if x > 0:
                if not 'west' in rooms[y][x].exits:
                    exit = Exit(rooms[y][x])
                    exit.direction = 'west'
                    exit.room_to = rooms[y][x-1]
                    rooms[y][x].exits['west'] = exit 

                    exit = Exit(rooms[y][x-1])
                    exit.direction = 'east'
                    exit.room_to = rooms[y][x]
                    rooms[y][x-1].exits['east'] = exit
            
            if x < len(rooms)-1:
                if not 'east' in rooms[y][x].exits:
                    exit = Exit(rooms[y][x])
                    exit.direction = 'east'
                    exit.room_to = rooms[y][x+1]
                    rooms[y][x].exits['east'] = exit

                    exit = Exit(rooms[y][x+1])
                    exit.direction = 'west'
                    exit.room_to = rooms[y][x]
                    rooms[y][x+1].exits['west'] = exit

            if y > 0:
                if not 'north' in rooms[y][x].exits:
                    exit = Exit(rooms[y][x])
                    exit.direction = 'north'
                    exit.room_to = rooms[y-1][x]
                    rooms[y][x].exits['north'] = exit

                    exit = Exit(rooms[y-1][x])
                    exit.direction = 'south'
                    exit.room_to = rooms[y][x]
                    rooms[y-1][x].exits['south'] = exit

            if y < len(rooms[y])-1:
                if not 'south' in rooms[y][x].exits:
                    exit = Exit(rooms[y][x])
                    exit.direction = 'south'
                    exit.room_to = rooms[y+1][x]
                    rooms[y][x].exits['south'] = exit

                    exit = Exit(rooms[y+1][x])
                    exit.direction = 'north'
                    exit.room_to = rooms[y][x]
                    rooms[y+1][x].exits['north'] = exit

    items = loadItems()

    room_area = world.room_width * world.room_width
    # Populate the rooms
    for y in range(len(rooms)):
        for x in range(len(rooms[y])):
            print("Adding items to Room(%d)..." % (rooms[y][x].id))
            biome = biomes[world.biomes[y][x]]

            # Trees
            if biome.trees and biome.tree_density > 0:
                tree_coverage = 0
                while tree_coverage / room_area < biome.tree_density:
                    treeIndex = random.randrange(len(biome.trees))
                    treeId = biome.trees[treeIndex]
                    if treeId in items:
                        tree = instance(items, treeId)
                        rooms[y][x].items.append(tree)
                        tree_coverage += tree.width * tree.length
                    else:
                        print("Error! Tree Item(%s) not found for Biome(%s)." % (treeId, biome.name))
                        break



    for y in range(len(rooms)):
        for x in range(len(rooms[y])):
            print("Saving Room(%d)..." % rooms[y][x].id)
            rooms[y][x].save('data/worlds/' + world.name + '/rooms/')

    return [[ rooms[y][x].id for x in range(len(rooms[y])) ] for y in range(len(rooms)) ]





            

