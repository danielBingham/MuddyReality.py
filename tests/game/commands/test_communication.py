from unittest.mock import Mock

from game.library.library import Library
from game.store.store import Store
from game.player import Player
from game.store.models.character import PlayerCharacter, Character
from game.store.models.room import Room
from game.store.models.world import World

from game.commands.communication import Say


def test_Say_to_empty_room():
    """
    Test the Say command when the player says something to an empty room.
    """

    store = Store('test', '')
    store.world = World()
    library = Library(store)

    say = Say(library, store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()

    player.character.room = Room()
    player.character.room.occupants.append(player.character)

    say.execute(player, 'Hello')

    player.write.assert_called_once_with('You say "Hello"')


def test_Say_to_player_populated_room():
    """
    Test the Say command when the player says something to a room populated by
    other players.
    """

    store = Store('test', '')
    store.world = World()
    library = Library(store)

    say = Say(library, store)

    room = Room()

    # Set up the speaking player.
    speakingPlayerSocket = Mock()
    speakingPlayer = Player(speakingPlayerSocket, None, None)
    speakingPlayer.write = Mock()

    speakingPlayer.character = PlayerCharacter()
    speakingPlayer.character.player = speakingPlayer
    speakingPlayer.character.name = 'speaker'

    speakingPlayer.character.room = room
    room.occupants.append(speakingPlayer.character)

    # Set up the listening player
    listeningPlayerSocket = Mock()
    listeningPlayer = Player(listeningPlayerSocket, None, None)
    listeningPlayer.write = Mock()

    listeningPlayer.character = PlayerCharacter()
    listeningPlayer.character.player = listeningPlayer

    listeningPlayer.character.room = room
    room.occupants.append(listeningPlayer.character)

    # Execute the say
    say.execute(speakingPlayer, 'Hello')

    # Check the results
    speakingPlayer.write.assert_called_once_with('You say "Hello"')
    listeningPlayer.write.assert_called_once_with('Speaker says "Hello"')


def test_Say_to_npc_populated_room():
    """
    Test the Say command when the player says something to a room populated by
    NPCs.
    """

    store = Store('test', '')
    store.world = World()
    library = Library(store)

    say = Say(library, store)

    room = Room()

    # Set up the speaking player.
    speakingPlayerSocket = Mock()
    speakingPlayer = Player(speakingPlayerSocket, None, None)
    speakingPlayer.write = Mock()

    speakingPlayer.character = PlayerCharacter()
    speakingPlayer.character.player = speakingPlayer
    speakingPlayer.character.name = 'speaker'

    speakingPlayer.character.room = room
    room.occupants.append(speakingPlayer.character)

    # Set up the listening NPC 
    character = Character()

    character.room = room
    room.occupants.append(character)

    # Execute the say
    say.execute(speakingPlayer, 'Hello')

    # Check the results
    speakingPlayer.write.assert_called_once_with('You say "Hello"')
