from unittest.mock import Mock

from game.library.library import Library
from game.store.store import Store
from game.player import Player
from game.store.models.character import PlayerCharacter
from game.account_menu.menu import AccountMenu

def test_kill():
    """
    Test kill appropriately kills a character.
    """

    store = Store('test', '')
    library = Library(store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.player = player

    store.players.append(player)

    library.character.kill(player.character)

    assert player.status == player.STATUS_ACCOUNT
    assert player.current_account_state == AccountMenu.NAME

def test_adjustSleep():
    """
    Test adjustSleep to determine if it appropriately adjusts sleep.
    """

    store = Store('test', '')
    library = Library(store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.player = player

    store.players.append(player)

    success = library.character.adjustSleep(player.character, -2)
    assert player.character.reserves.sleep == 14 
    assert success is True

    success = library.character.adjustSleep(player.character, 2)
    assert player.character.reserves.sleep == 16
    assert success is True

def test_adjustCalories():
    """
    Test adjustCalories to determine if it appropriately adjusts calories.
    """

    store = Store('test', '')
    library = Library(store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.player = player

    store.players.append(player)

    success = library.character.adjustCalories(player.character, -2)
    assert player.character.reserves.calories == 2398 
    assert success is True

    success = library.character.adjustCalories(player.character, 2)
    assert player.character.reserves.calories == 2400 
    assert success is True

def test_adjustCalories_past_zero():
    """
    Test adjustCalories down below zero.
    """

    store = Store('test', '')
    library = Library(store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.player = player

    store.players.append(player)

    player.character.reserves.calories = 0

    success = library.character.adjustCalories(player.character, -2400)
    assert player.character.reserves.calories == -2400 
    assert player.character.attributes.stamina == 9
    assert success is True

def test_adjustCalories_to_death():
    """
    Test adjusting calories to the point where it kills the character.
    """

    store = Store('test', '')
    library = Library(store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    character = PlayerCharacter()

    player.character = character
    character.player = player

    store.players.append(player)

    character.reserves.calories = -9*2400 

    success = library.character.adjustCalories(character, -2400)
    assert character.reserves.calories == -10*2400 
    assert character.attributes.stamina == 0 
    assert character.position == character.POSITION_DEAD
    assert character.player is None

    assert player.status == player.STATUS_ACCOUNT
    assert player.character is None

    assert success is True

def test_adjustThirst():
    """
    Test using adjustThirst to adjust the player's thirst reserve.
    """

    store = Store('test', '')
    library = Library(store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.player = player

    store.players.append(player)

    success = library.character.adjustThirst(player.character, -2)
    assert player.character.reserves.thirst == 3998  
    assert success is True

    success = library.character.adjustThirst(player.character, 2)
    assert player.character.reserves.thirst == 4000 
    assert success is True

def test_adjustThirst_past_zero():
    """
    Test using adjustThirst to adjust the player's thirst reserve below zero.
    """

    store = Store('test', '')
    library = Library(store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.player = player

    store.players.append(player)

    player.character.reserves.thirst = 0

    success = library.character.adjustThirst(player.character, -4000)
    assert player.character.reserves.thirst == -4000 
    assert player.character.attributes.stamina == 6 
    assert success is True

def test_adjustThirst_to_death():
    """
    Test adjusting thirst to the point where it kills the character.
    """

    store = Store('test', '')
    library = Library(store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    character = PlayerCharacter()

    player.character = character
    character.player = player

    store.players.append(player)

    character.reserves.thirst = 2*-4000 

    success = library.character.adjustThirst(character, -2000)
    assert character.reserves.thirst == -10000
    assert character.attributes.stamina == 0 
    assert character.position == character.POSITION_DEAD
    assert character.player is None

    assert player.status == player.STATUS_ACCOUNT
    assert player.character is None

    assert success is True

def test_adjustWind():
    """
    Test adjusting the character's wind reserve.
    """

    store = Store('test', '')
    library = Library(store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.player = player

    store.players.append(player)

    success = library.character.adjustWind(player.character, -2)
    assert player.character.reserves.wind == 28
    assert success is True

    success = library.character.adjustWind(player.character, 2)
    assert player.character.reserves.wind == 30 
    assert success is True

def test_adjustWind_boundaries():
    """
    Test adjusting the character's wind reserve.  Confirm it can't go over max_wind or negative.
    """

    store = Store('test', '')
    library = Library(store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.player = player

    store.players.append(player)

    success = library.character.adjustWind(player.character, -32)
    assert player.character.reserves.wind == 30 
    assert success is False 

    success = library.character.adjustWind(player.character, 2)
    assert player.character.reserves.wind == 30 
    assert success is True

def test_adjustEnergy():
    """
    Test adjusting the character's energy reserve.
    """

    store = Store('test', '')
    library = Library(store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.player = player

    store.players.append(player)

    success = library.character.adjustEnergy(player.character, -2)
    assert player.character.reserves.energy == 9998 
    assert success is True

    success = library.character.adjustEnergy(player.character, 2)
    assert player.character.reserves.energy == 10000 
    assert success is True

def test_adjustEnergy_boundaries():
    """
    Test adjusting the character's energy reserve.  Confirm it can't go over max_energy or negative.
    """

    store = Store('test', '')
    library = Library(store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.player = player

    store.players.append(player)

    success = library.character.adjustEnergy(player.character, -10002)
    assert player.character.reserves.energy == 10000 
    assert success is False 

    success = library.character.adjustEnergy(player.character, 2)
    assert player.character.reserves.energy == 10000 
    assert success is True

