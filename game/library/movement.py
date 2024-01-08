import game.library.environment as environment

class MovementLibrary:
    
    def __init__(self, library, store):
        self.library = library
        self.store = store

    def move(self, direction, player, arguments):
        if not player.character.room:
            raise RuntimeException("Player should have a room if they're trying to move!")

        if player.character.position == player.character.POSITION_SLEEPING:
            player.write("You can't move in your sleep.")
            return

        room = player.character.room
        if direction in room.exits:
            if room.exits[direction].is_door and room.exits[direction].is_open == False:
                player.write("The " + room.exits[direction].name + " is closed.")
                return 

            player.write("You go " + direction + ".")
            self.leave(player.character, player.character.room, direction=direction)
            self.enter(player.character, room.exits[direction].room_to, direction=direction)
            player.character.reserves.calories -= 4
            player.write("\n" + player.character.room.describe(player), wrap=False)
        else:
            player.write("You can't got that way.")

    def enter(self, character, room, direction=''):
        room.occupants.append(character)
        character.room = room

        if direction:
            self.library.environment.writeToRoom(character, character.name.title() + " enters from the " + room.INVERT_DIRECTION[direction] + ".")
        else:
            self.library.environment.writeToRoom(character, character.name.title() + " enters.")

    def leave(self, character, room, direction=''):
        if direction:
            self.library.environment.writeToRoom(character, character.name.title() + " leaves to the " + direction + ".")
        else:
            self.library.environment.writeToRoom(character, character.name.title() + " leaves.")

        room.occupants.remove(character)
        character.room = None
