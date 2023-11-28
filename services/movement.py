import services.environment as environment

def enter(character, room, direction=''):
    room.occupants.append(character)
    character.room = room

    if direction:
        environment.writeToRoom(character, character.name.title() + " enters from the " + room.INVERT_DIRECTION[direction] + ".")
    else:
        environment.writeToRoom(character, character.name.title() + " enters.")

def leave(character, room, direction=''):
    room.occupants.remove(character)
    character.room = None

    if direction:
        environment.writeToRoom(character, character.name.title() + " leaves to the " + direction + ".")
    else:
        environment.writeToRoom(character, character.name.title() + " leaves.")
