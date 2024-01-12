from game.store.models.character import PlayerCharacter

class RoomLibrary:
    "Behavior for acting on and interacting with Rooms."

    def __init__(self, library, store):
        """
        Initialize the Room Library

        Parameters
        ----------
        library:    Library
            A reference the core library, allowing access to other libraries.
        store:  Store
            The game store.
        """

        self.store = store
        self.library = library

    def writeToRoom(self, character, text):
        """
        Write a message to all occupants with players sharing the character's
        room, excluding character.

        Parameters
        ----------
        character:  Character
            The character who is originating the message in some way.  They won't receive the message.
        text:   string
            The message to send to all other occupants of `character`'s room.

        Returns
        -------
        void
        """

        for occupant in character.room.occupants:
            if occupant != character and isinstance(occupant, PlayerCharacter) \
                    and occupant.player and occupant.position != occupant.POSITION_SLEEPING: 
                occupant.player.write(text)

    def findOccupantByKeywords(self, room, keywords):
        """
        Find an occupant of the room described by `keywords`.

        Parameters
        ----------
        room:   Room
            The room to search for occupants with `keywords`.
        keywords:   string
            The keywords to use to search `room` for occupants.

        Returns
        -------
        Character:  The matched occupant, or `None`.
        """

        for occupant in self.occupants:
            if occupant.name.startswith(keywords):  
                return occupant 
        return None 
