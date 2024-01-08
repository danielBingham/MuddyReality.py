from game.library.movement import MovementLibrary
from game.library.items import ItemLibrary
from game.library.environment import EnvironmentLibrary

class Library:

    def __init__(self, store):
        self.store = store

        self.movement = MovementLibrary(self, store)
        self.items = ItemLibrary(self, store) 
        self.environment = EnvironmentLibrary(self, store)
