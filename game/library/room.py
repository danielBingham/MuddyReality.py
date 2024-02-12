from textwrap import TextWrapper

from game.store.models.character import PlayerCharacter
from game.store.models.room import Room


class RoomLibrary:
    "Behavior for acting on and interacting with Rooms."

    # A static text wrapper we use to wrap descriptive text.
    wrapper = TextWrapper(width=80, replace_whitespace=False, initial_indent='', break_on_hyphens=False)

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

    def getColorString(self, room):
        return "\033[38;2;" + str(room.color[0]) + ";" + str(room.color[1]) + ";" + str(room.color[2]) + "m"

    def getColorReset(self):
        return "\033[0m"

    def describe(self, room, player):
        time = self.store.world.time

        output = ""

        if room.color and not time.night:
            output += self.getColorString(room)
        output += self.wrapper.fill(str(room.title)) 
        if room.color and not time.night:
            output += self.getColorReset() 

        output += "\n"

        if not time.night:
            output += self.wrapper.fill(str(room.description)) + "\n"
            output += "---\n"
            for occupant in room.occupants:
                if occupant != player.character:
                    output += occupant.name.title() + " is here.\n"

            for item in room.items:
                if self.library.item.groundAction(item):
                    output += "%s is %s here.\n" % (self.library.item.describe(item), self.library.item.groundAction(item))
                else:
                    output += "%s is here.\n" % (self.library.item.describe(item))

        output += "---\n"
        output += "Exits: "
        for direction in Room.DIRECTIONS:
            if direction not in room.exits:
                continue

            if not time.night:
                output += self.getColorString(room.exits[direction].room_to)
            if room.exits[direction].is_door:
                if room.exits[direction].is_open:
                    output += "(" + direction + ") "
                else:
                    output += "[" + direction + "] "
            else:
                output += direction + " "

            if not time.night:
                output += self.getColorReset()

        output += "\n"
        return output

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
