def findItemInInventory(player, keywords):
    """Find an item in a player's character's inventory.
    """

    for item in player.character.inventory:
        for key in item.keywords:
            if key.startswith(keywords):
                return item
    return None

