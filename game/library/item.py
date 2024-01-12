class ItemLibrary:
    """
    Library containing behavior for acting on and interacting with Items.
    """

    def __init__(self, library, store):
        self.library = library
        self.store = store

    def findItemByKeywords(self, items, keywords):
        """
        Find an item from a list of items by searching its keywords

        Parameters
        ----------
        items:  Item[]
            The list of items we want to search using `keywords`.
        keywords:   string
            The keywords we want to search "item" for.

        Returns
        -------
        Item:   The item that matches `keywords` or `None`.
        """

        which = 1

        period = keywords.find('.')
        if period >= 0:
            tokens = keywords.split('.')
            which = int(tokens[0])

            keywords = tokens[1]

        count = 0
        for item in items:
            if item.name.startswith(keywords):
                count += 1
                if count < which:
                    continue
                else:
                    return item
            else:
                for keyword in item.keywords:
                    if keyword.startswith(keywords):
                        count += 1
                        if count < which:
                            continue
                        else:
                            return item
        return None
