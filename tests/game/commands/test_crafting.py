from unittest.mock import Mock, call

from game.library.library import Library
from game.store.store import Store
from game.player import Player
from game.store.models.character import PlayerCharacter, Character
from game.store.models.room import Room
from game.store.models.item import Item

from game.commands.crafting import Craft

tool_json = {
    "name": "tool",
    "description": "a tool",
    "details": "A tool for testing.",
    "keywords": [ "tool" ],
    "length": 1,
    "width": 1,
    "height": 1,
    "weight": 1,
    "traits": {
        "Tool": {
            "type": "tool"
        },
        "Craftable": {
            "requiredMaterials": [
                {
                    "type": "material",
                    "length": 1,
                    "width": 1,
                    "height": 1,
                    "weight": 1
                }
            ],
            "requiredTools": []
        }
    }
}

tool_requiring_two_materials_json = {
    "name": "tool",
    "description": "a tool",
    "details": "A tool for testing.",
    "keywords": [ "tool" ],
    "length": 1,
    "width": 1,
    "height": 1,
    "weight": 1,
    "traits": {
        "Tool": {
            "type": "tool"
        },
        "Craftable": {
            "requiredMaterials": [
                {
                    "type": "material",
                    "length": 1,
                    "width": 1,
                    "height": 1,
                    "weight": 1
                },
                {
                    "type": "other material",
                    "length": 1,
                    "width": 1,
                    "height": 1,
                    "weight": 1
                }
            ],
            "requiredTools": []
        }
    }
}

craftable_material_requires_tool_json = {
    "name": "craftable material",
    "description": "a craftable material",
    "details": "A material that requires a tool to craft.",
    "keywords": [ "craftable material", "material" ],
    "length": 1,
    "width": 1,
    "height": 1,
    "weight": 1,
    "traits": {
        "Material": {
            "types": [ "material" ]
        },
        "Craftable": {
            "requiredMaterials": [
                {
                    "type": "material",
                    "length": 1,
                    "width": 1,
                    "height": 1,
                    "weight": 1
                }
            ],
            "requiredTools": [ "tool" ]
        }
    }
}

material_json = {
    "name": "material",
    "description": "a material",
    "details": "A material for testing.",
    "keywords": [ "material" ],
    "length": 1,
    "width": 1,
    "height": 1,
    "weight": 1,
    "traits": {
        "Material": {
            "types": [ "material" ]
        }
    }
}


def test_Craft_when_character_is_sleeping():
    """
    Test a player attempting to craft something when their character is asleep.
    """

    store = Store('test', '')
    library = Library(store)

    craft_command = Craft(library, store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.player = player

    player.character.position = player.character.POSITION_SLEEPING

    craft_command.execute(player, '')

    player.write.assert_called_once_with("You can't craft in your sleep.")


def test_Craft_when_called_with_no_arguments():
    """
    Test a player attempting to craft but forgetting the arguments.
    """

    store = Store('test', '')
    library = Library(store)

    craft_command = Craft(library, store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.player = player

    craft_command.execute(player, '')

    player.write.assert_called_once_with("Craft what with what?")


def test_Craft_when_called_without_with():
    """
    Test a player attempting to craft but forgetting the 'with' keyword that
    differentiates the craft target from the materials.
    """

    store = Store('test', '')
    library = Library(store)

    craft_command = Craft(library, store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.player = player

    craft_command.execute(player, 'tool material, material')

    player.write.assert_called_once_with("What do you want to craft with?")


def test_Craft_when_called_with_invalid_craft_target():
    """
    Test a player attempting to craft something that doesn't exist.
    """

    store = Store('test', '')
    library = Library(store)

    craft_command = Craft(library, store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.player = player

    craft_command.execute(player, 'tool with material, material')

    player.write.assert_called_once_with("Tool is not something you can craft.")


def test_Craft_when_craft_target_isnt_craftable():
    """
    Test a player attempting to craft something that exists, but isn't craftable. 
    """

    store = Store('test', '')

    item = Item()
    item.setId('tool')
    store.items.add(item)

    library = Library(store)

    craft_command = Craft(library, store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.player = player

    craft_command.execute(player, 'tool with material')

    player.write.assert_called_once_with("Tool is not something you can craft.")


def test_Craft_when_called_with_missing_materials():
    """
    Test a player attempting to craft something without the materials.
    """

    store = Store('test', '')

    tool = Item()
    tool.fromJson(tool_json)
    store.items.add(tool)

    library = Library(store)

    craft_command = Craft(library, store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.player = player

    craft_command.execute(player, 'tool with material')

    player.write.assert_has_calls([ 
        call("Couldn't find 'material' in your inventory."), 
        call("You don't have all the materials needed to craft tool.")
    ])


def test_Craft_missing_one_material():
    """
    Test a player attempting to craft something without one of the materials.
    """

    store = Store('test', '')

    tool = Item()
    tool.fromJson(tool_requiring_two_materials_json)
    store.items.add(tool)

    material = Item()
    material.fromJson(material_json)
    store.items.add(material)

    library = Library(store)

    craft_command = Craft(library, store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.player = player
    player.character.inventory.append(store.items.instance(material.getId()))

    craft_command.execute(player, 'tool with material, other material')

    player.write.assert_has_calls([ 
        call("Couldn't find 'other material' in your inventory."), 
        call("You don't have all the materials needed to craft tool.")
    ])


def test_Craft_missing_tool():
    """
    Test a player attempting to craft something without one of the required tools.
    """

    store = Store('test', '')

    craftable_material = Item()
    craftable_material.fromJson(craftable_material_requires_tool_json)
    store.items.add(craftable_material)

    tool = Item()
    tool.fromJson(tool_requiring_two_materials_json)
    store.items.add(tool)

    material = Item()
    material.fromJson(material_json)
    store.items.add(material)

    library = Library(store)

    craft_command = Craft(library, store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.player = player
    player.character.inventory.append(store.items.instance(material.getId()))

    craft_command.execute(player, 'craftable material with material, tool')

    player.write.assert_has_calls([
        call("Couldn't find 'tool' in your inventory."),
        call("You don't have all the tools needed to craft craftable material.")
    ])


def test_Craft_success_tool_requires_one_material():
    """
    Test a player successfully crafting a tool that requires one material.
    """

    store = Store('test', '')

    tool = Item()
    tool.fromJson(tool_json)
    store.items.add(tool)

    material = Item()
    material.fromJson(material_json)
    store.items.add(material)

    library = Library(store)

    craft_command = Craft(library, store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.player = player
    player.character.inventory.append(store.items.instance(material.getId()))

    player.character.room = Room()
    player.character.room.occupants.append(player.character)

    craft_command.execute(player, 'tool with material')

    player.write.assert_called_once_with("You craft tool.")
    assert len([ item for item in player.character.inventory if item.getId() == tool.getId() ]) == 1
    assert len([ item for item in player.character.inventory if item.getId() == material.getId() ]) == 0


def test_Craft_success_craftable_material_requries_material_and_tool():
    """
    Test a player successfully crafting a material that requires a tool and a material.
    """

    store = Store('test', '')

    craftable_material = Item()
    craftable_material.fromJson(craftable_material_requires_tool_json)
    store.items.add(craftable_material)

    tool = Item()
    tool.fromJson(tool_requiring_two_materials_json)
    store.items.add(tool)

    material = Item()
    material.fromJson(material_json)
    store.items.add(material)

    library = Library(store)

    craft_command = Craft(library, store)

    socket = Mock()
    player = Player(socket, None, None)
    player.write = Mock()

    player.character = PlayerCharacter()
    player.character.player = player
    player.character.inventory.append(store.items.instance(material.getId()))
    player.character.inventory.append(store.items.instance(tool.getId()))

    player.character.room = Room()
    player.character.room.occupants.append(player.character)

    craft_command.execute(player, 'craftable material with material, tool')

    player.write.assert_called_once_with("You craft craftable material.")
    assert len([ item for item in player.character.inventory if item.getId() == tool.getId() ]) == 1
    assert len([ item for item in player.character.inventory if item.getId() == material.getId() ]) == 0
    assert len([ item for item in player.character.inventory if item.getId() == craftable_material.getId() ]) == 1

