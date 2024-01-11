from game.library.items import ItemLibrary
from game.library.character import CharacterLibrary
from game.library.room import RoomLibrary

from game.library.movement import MovementLibrary

class Library:

    def __init__(self, store):
        self.store = store

        # Model libraries.  Libraries that contain behavior for interacting
        # with one of the game's models.
        self.character = CharacterLibrary(self, store)
        self.item = ItemLibrary(self, store) 
        self.room = RoomLibrary(self, store)

        # System libraries.  Libraries that contain beheavior related to one
        # of the game's systems.
        self.movement = MovementLibrary(self, store)
