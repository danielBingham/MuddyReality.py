def findItemInRoom(player, keywords):
    'Find an item in the players current room given a set of keyword'

    for item in player.character.room.items:
        for key in item.keywords:
            if key.startswith(keywords):
                return item
    return None

def writeToRoom(player, text):
    """Write a message to all occupants sharing the player's room, excluding player.
    """

    for occupant in player.character.room.occupants:
        if occupant.player and occupant.player != player:
            occupant.player.write(text)
