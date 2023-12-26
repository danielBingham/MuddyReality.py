import random, copy, glob

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

def generateRooms(biomes, world):
  
    rooms = [[ None for y in range(world.width) ] for x in range(world.width) ]

    # Generate and populate the rooms.
    id = 1
    for x in range(world.width):
        for y in range(world.width):
            print("Generating (%d, %d) as Room(%d)..." % (x,y,id))
            biome = biomes[world.biomes[x][y]]
            height = world.terrain[x][y]

            room = Room()
            room.id = id

            title = random.randrange(0, len(biome.titles))
            room.title = biome.titles[title]

            description = random.randrange(0, len(biome.descriptions))
            room.description = biome.descriptions[description]

            print("Created Room(%s) with Description(%s)" % (room.title, room.description))
            rooms[x][y] = room
            id += 1


    # Connect the rooms together.
    for x in range(len(rooms)):
        for y in range(len(rooms[x])):
            print("Connecting Room(%d)" % rooms[x][y].id)
            if x > 0:
                if not 'west' in rooms[x][y].exits:
                    exit = Exit(rooms[x][y])
                    exit.direction = 'west'
                    exit.room_to = rooms[x-1][y]
                    rooms[x][y].exits['west'] = exit 

                    exit = Exit(rooms[x-1][y])
                    exit.direction = 'east'
                    exit.room_to = rooms[x][y]
                    rooms[x-1][y].exits['east'] = exit
            
            if x < len(rooms)-1:
                if not 'east' in rooms[x][y].exits:
                    exit = Exit(rooms[x][y])
                    exit.direction = 'east'
                    exit.room_to = rooms[x+1][y]
                    rooms[x][y].exits['east'] = exit

                    exit = Exit(rooms[x+1][y])
                    exit.direction = 'west'
                    exit.room_to = rooms[x][y]
                    rooms[x+1][y].exits['west'] = exit

            if y > 0:
                if not 'north' in rooms[x][y].exits:
                    exit = Exit(rooms[x][y])
                    exit.direction = 'north'
                    exit.room_to = rooms[x][y-1]
                    rooms[x][y].exits['north'] = exit

                    exit = Exit(rooms[x][y-1])
                    exit.direction = 'south'
                    exit.room_to = rooms[x][y]
                    rooms[x][y-1].exits['south'] = exit

            if y < len(rooms[x])-1:
                if not 'south' in rooms[x][y].exits:
                    exit = Exit(rooms[x][y])
                    exit.direction = 'south'
                    exit.room_to = rooms[x][y+1]
                    rooms[x][y].exits['south'] = exit

                    exit = Exit(rooms[x][y+1])
                    exit.direction = 'north'
                    exit.room_to = rooms[x][y]
                    rooms[x][y+1].exits['north'] = exit

    items = loadItems()

    # Populate the rooms
    for x in range(len(rooms)):
        for y in range(len(rooms[x])):
            print("Adding items to Room(%d)..." % (rooms[x][y].id))
            biome = biomes[world.biomes[x][y]]

            # Trees
            if biome.trees and biome.tree_density > 0:
                tree_coverage = 0
                while tree_coverage / 10000 < biome.tree_density:
                    treeIndex = random.randrange(len(biome.trees))
                    treeId = biome.trees[treeIndex]
                    if treeId in items:
                        tree = instance(items, treeId)
                        rooms[x][y].items.append(tree)
                        tree_coverage += tree.width * tree.length
                    else:
                        print("Error! Tree Item(%s) not found for Biome(%s)." % (treeId, biome.name))
                        break



    for x in range(len(rooms)):
        for y in range(len(rooms[x])):
            print("Saving Room(%d)..." % rooms[x][y].id)
            rooms[x][y].save('data/worlds/' + world.name + '/rooms/')

    return [[ rooms[x][y].id for y in range(len(rooms[x])) ] for x in range(len(rooms)) ]





            

