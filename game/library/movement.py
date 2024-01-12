class MovementLibrary:

    def __init__(self, library, store):
        self.library = library
        self.store = store

    def move(self, direction, player, arguments):
        if not player.character.room:
            raise RuntimeError("Player should have a room if they're trying to move!")

        if player.character.position == player.character.POSITION_SLEEPING:
            player.write("You can't move in your sleep.")
            return

        move_through = 1
        if player.character.speed == player.character.SPEED_RUNNING:
            move_through = 2
        elif player.character.speed == player.character.SPEED_SPRINTING:
            move_through = 4

        for iteration in range(move_through):
            if not self.moveInDirection(player, direction):
                return

    def moveInDirection(self, player, direction):
        room = player.character.room
        if direction in room.exits:
            if room.exits[direction].is_door and room.exits[direction].is_open is False:
                player.write("The way " + room.exits[direction] + " is closed.")
                return False 

            # These values are set based on time, not room size.
            #
            # 1 real life second is 1 game minute.  In general, if you
            # are spamming a direction as fast as you can, you'll be able
            # to spam through ~3 rooms in a single second. Suggesting you can
            # get through 1 game room in 20 game seconds.
            #
            # So we're setting these values to appropriate values for
            # 20 seconds of walking, 20 seconds of running, and 20 seconds
            # of sprinting.
            speed = ""
            if player.character.speed == player.character.SPEED_RUNNING:
                speed = "run"
                player.character.reserves.calories -= 4 
                player.character.reserves.energy -= 100 
                player.character.reserves.wind -= 1
            elif player.character.speed == player.character.SPEED_SPRINTING:
                speed = "sprint"
                player.character.reserves.calories -= 6 
                player.character.reserves.energy -= 150 
                player.character.reserves.wind -= 3
            else:
                speed = "walk"
                player.character.reserves.calories -= 1 
                player.character.reserves.energy -= 25 

            player.write("You %s %s." % (speed, direction))

            self.leave(player.character, player.character.room, speed=speed, direction=direction)
            self.enter(player.character, room.exits[direction].room_to, speed=speed, direction=direction)

            player.write("\n" + player.character.room.describe(player), wrap=False)
            return True
        else:
            player.write("You can't got that way.")
            return False

    def enter(self, character, room, speed='', direction=''):
        room.occupants.append(character)
        character.room = room

        if direction:
            self.library.room.writeToRoom(character, character.name.title() + " enters from the " + room.INVERT_DIRECTION[direction] + ".")
        else:
            self.library.room.writeToRoom(character, character.name.title() + " enters.")

    def leave(self, character, room, speed='', direction=''):
        if direction:
            self.library.room.writeToRoom(character, character.name.title() + " leaves to the " + direction + ".")
        else:
            self.library.room.writeToRoom(character, character.name.title() + " leaves.")

        room.occupants.remove(character)
        character.room = None
