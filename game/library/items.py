
def findItemByKeywords(items, keywords):
    """Find an item from a list of items by searching its keywords
    """

    for item in items:
        if item.name.startswith(keywords):
            return item
        else:
            for keyword in item.keywords:
                if keyword.startswith(keywords):
                    return item
    return None
