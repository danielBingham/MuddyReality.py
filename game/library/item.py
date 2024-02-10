class ItemLibrary:
    """
    Library containing behavior for acting on and interacting with Items.
    """

    def __init__(self, library, store):
        self.library = library
        self.store = store

    def matchKeywords(self, keywords, to_match):
        while True:
            if to_match.startswith(keywords):
                return True

            token_end = to_match.find(' ')
            if token_end == -1:
                return False

            to_match = to_match[token_end:]

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
            if self.matchKeywords(keywords, item.name):
                count += 1
                if count < which:
                    continue
                else:
                    return item
            elif self.matchKeywords(keywords, item.keywords):
                count += 1
                if count < which:
                    continue
                else:
                    return item

        return None
