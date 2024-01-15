from unittest.mock import Mock

from game.heartbeat import Heartbeat
from game.library.library import Library
from game.store.store import Store
from game.player import Player
from game.store.models.character import PlayerCharacter

from game.interpreters.command.command import Command

def test_advanceActions_should_step():
    """
    Test advanceAction in a case where it should just advance a step.
    """

    store = Store('test', '')
    library = Library(store)

    heartbeat = Heartbeat(store, library, 10)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    dummyCommand = Command(store, library)
    dummyCommand.execute = Mock()
    dummyCommand.step = Mock()
    dummyCommand.finish = Mock()

    player.character = PlayerCharacter()

    player.character.action = dummyCommand
    player.character.action_time = 2
    player.character.action_data = {}

    store.players.append(player)

    heartbeat.advanceActions()

    assert player.character.action_time == 1
    player.write.assert_called_once_with(".", wrap=False)
    assert player.prompt.is_off is True
    player.character.action.step.assert_called_once_with(player)

def test_advanceActions_should_finish():
    """
    Test advanceAction in a case where it should finish the action.
    """


    store = Store('test', '')
    library = Library(store)

    heartbeat = Heartbeat(store, library, 10)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    dummyCommand = Command(store, library)
    dummyCommand.execute = Mock()
    dummyCommand.step = Mock()
    dummyCommand.finish = Mock()

    player.character = PlayerCharacter()

    player.character.action = dummyCommand
    player.character.action_time = 1
    player.character.action_data = {}

    store.players.append(player)

    heartbeat.advanceActions()

    dummyCommand.finish.assert_called_once_with(player)
    assert player.character.action is None
    assert player.character.action_time == 0
    assert player.prompt.is_off is False 

def test_advanceAction_skips_players_without_characters():
    """
    Test advanceAction with a player at the account menu.
    """


    store = Store('test', '')
    library = Library(store)

    heartbeat = Heartbeat(store, library, 10)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    dummyCommand = Command(store, library)
    dummyCommand.execute = Mock()
    dummyCommand.step = Mock()
    dummyCommand.finish = Mock()

    store.players.append(player)

    heartbeat.advanceActions()

    dummyCommand.step.assert_not_called()
    assert player.prompt.is_off is False 

def test_advanceAction_skips_characters_with_no_action():
    """
    Test advanceAction with a character not working an action.
    """

    store = Store('test', '')
    library = Library(store)

    heartbeat = Heartbeat(store, library, 10)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    dummyCommand = Command(store, library)
    dummyCommand.execute = Mock()
    dummyCommand.step = Mock()
    dummyCommand.finish = Mock()

    player.character = PlayerCharacter()

    player.character.action = None 
    player.character.action_time = 0
    player.character.action_data = {}

    store.players.append(player)

    heartbeat.advanceActions()

    dummyCommand.step.assert_not_called()
    dummyCommand.finish.assert_not_called()
    assert player.character.action is None
    assert player.character.action_time == 0
    assert player.prompt.is_off is False 

def test_calculateReserves_character_is_standing():
    """
    Test calculateReserves for a character with full reserves who is standing.
    """

    store = Store('test', '')
    library = Library(store)

    heartbeat = Heartbeat(store, library, 10)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.position = player.character.POSITION_STANDING

    store.players.append(player)

    heartbeat.calculateReserves()

    assert player.character.reserves.calories == 2398
    assert player.character.reserves.thirst == 3998
    assert player.character.reserves.wind == 30
    assert player.character.reserves.energy == 10000


def test_calculateReserves_character_with_low_reseves_who_is_standing():
    """
    Test calculateReserves for a character with low reserves who is standing.
    """

    store = Store('test', '')
    library = Library(store)

    heartbeat = Heartbeat(store, library, 10)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.position = player.character.POSITION_STANDING

    player.character.reserves.calories = 2
    player.character.reserves.thirst = 2
    player.character.reserves.wind = 0
    player.character.reserves.energy = 0

    store.players.append(player)

    heartbeat.calculateReserves()

    assert player.character.reserves.calories == 0 
    assert player.character.reserves.thirst == 0 
    assert player.character.reserves.wind == 3 
    assert player.character.reserves.energy == 0 

def test_calculateReserves_character_who_is_resting():
    """
    Test calculateReserves for a character with full reserves who is resting.
    """

    store = Store('test', '')
    library = Library(store)

    heartbeat = Heartbeat(store, library, 10)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.position = player.character.POSITION_RESTING

    store.players.append(player)

    heartbeat.calculateReserves()

    assert player.character.reserves.calories == 2398
    assert player.character.reserves.thirst == 3998
    assert player.character.reserves.wind == 30
    assert player.character.reserves.energy == 10000


def test_calculateReserves_character_with_low_reseves_who_is_resting():
    """
    Test calculateReserves for a character with low reserves who is resting.
    """

    store = Store('test', '')
    library = Library(store)

    heartbeat = Heartbeat(store, library, 10)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.position = player.character.POSITION_RESTING

    player.character.reserves.calories = 2
    player.character.reserves.thirst = 2
    player.character.reserves.wind = 0
    player.character.reserves.energy = 0

    store.players.append(player)

    heartbeat.calculateReserves()

    assert player.character.reserves.calories == 0 
    assert player.character.reserves.thirst == 0 
    assert player.character.reserves.wind == 5 
    assert player.character.reserves.energy == 100 

def test_calculateSleep_character_who_is_standing():
    """
    Test calculateSleep with a character with full reserves who is standing.
    """

    store = Store('test', '')
    library = Library(store)

    heartbeat = Heartbeat(store, library, 10)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.position = player.character.POSITION_STANDING

    store.players.append(player)

    heartbeat.calculateSleep()

    assert player.character.reserves.sleep == 15
    assert player.character.reserves.energy == 10000
    assert player.character.position == player.character.POSITION_STANDING


def test_calculateSleep_character_who_is_sleeping():
    """
    Test calculateSleep with a character with full reserves who is sleeping.
    """

    store = Store('test', '')
    library = Library(store)

    heartbeat = Heartbeat(store, library, 10)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.position = player.character.POSITION_SLEEPING

    store.players.append(player)

    heartbeat.calculateSleep()

    assert player.character.reserves.sleep == 18 
    assert player.character.reserves.energy == 10000
    assert player.character.position == player.character.POSITION_STANDING
    player.write.assert_called_once_with("You awaken, fully rested.")


def test_calculateSleep_character_with_low_reserves_who_is_standing():
    """
    Test calculateSleep with a character with low reserves who is standing.
    """

    store = Store('test', '')
    library = Library(store)

    heartbeat = Heartbeat(store, library, 10)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.position = player.character.POSITION_STANDING

    player.character.reserves.sleep = 1
    player.character.reserves.energy = 0

    store.players.append(player)

    heartbeat.calculateSleep()

    assert player.character.reserves.sleep == 0 
    assert player.character.reserves.energy == 0 
    assert player.character.position == player.character.POSITION_STANDING


def test_calculateSleep_character_with_low_reserves_who_is_sleeping():
    """
    Test calculateSleep with a character with low reserves who is sleeping.
    """

    store = Store('test', '')
    library = Library(store)

    heartbeat = Heartbeat(store, library, 10)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.position = player.character.POSITION_SLEEPING

    player.character.reserves.sleep = 0
    player.character.reserves.energy = 0

    store.players.append(player)

    heartbeat.calculateSleep()

    assert player.character.reserves.sleep == 2 
    assert player.character.reserves.energy == 625 
    assert player.character.position == player.character.POSITION_SLEEPING
