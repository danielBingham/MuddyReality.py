
class EnvironmentLibrary:

    def __init__(self, library, store):
        self.store = store
        self.library = library

    def writeToRoom(self, character, text):
        "Write a message to all occupants with players sharing the character's room, excluding character."

        for occupant in character.room.occupants:
            if occupant != character and occupant.player and occupant.position != occupant.POSITION_SLEEPING: 
                occupant.player.write(text)
