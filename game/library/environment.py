def findItemInRoom(character, keywords):
    "Find an item in the character's current room given a set of keywords."

    for item in character.room.items:
        for key in item.keywords:
            if key.startswith(keywords):
                return item
    return None

def writeToRoom(character, text):
    "Write a message to all occupants with players sharing the character's room, excluding character."

    for occupant in character.room.occupants:
        if occupant != character and occupant.player and occupant.position != occupant.POSITION_SLEEPING: 
            occupant.player.write(text)
