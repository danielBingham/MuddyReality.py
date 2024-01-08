

class ItemLibrary:

    def __init__(self, library, store):
        self.library = library
        self.store = store

    def findItemByKeywords(self, items, keywords):
        """
        Find an item from a list of items by searching its keywords

        :param items:
        :param keywords:
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
