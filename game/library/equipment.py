def findItemInInventory(character, keywords):
    "Find an item in a character's inventory."

    for item in character.inventory:
        for key in item.keywords:
            if key.startswith(keywords):
                return item
    return None

