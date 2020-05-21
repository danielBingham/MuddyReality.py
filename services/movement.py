class MovementService:
    'Provides functions allowing a character to move about.'

    def enter(character, room, direction=''):
        for occupant in room.occupants:
            if occupant.player:
                if direction:
                    occupant.player.write(character.name.title() + " enters from the " + room.INVERT_DIRECTION[direction] + ".")
                else:
                    occupant.player.write(character.name.title() + " enters.")
        room.occupants.append(character)
        character.room = room

    def leave(character, room, direction=''):
        room.occupants.remove(character)
        character.room = None
        for occupant in room.occupants:
            if occupant.player:
                if direction:
                    occupant.player.write(character.name.title() + " leaves to the " + direction + ".")
                else:
                    occupant.player.write(character.name.title() + " leaves.")
