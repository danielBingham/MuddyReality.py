import json
import glob
import copy

from models.account import Account
from models.character import Character
from models.room import Room
from models.item import Item 

import game.commands.communication as communication 
import game.commands.information as information 
import game.commands.movement as movement
import game.commands.manipulation as manipulation

class ModelIndex:
    """Wraps and provides access to a collection of models of a certain type.

    Serves as a wrapper around models of a certain type, managing the
    dictionary of instances, allowing access to existing instances and reation
    of new ones.  In a Model index, each instance stored represents a unique
    instance of that model - only one copy of that instance will ever exist in
    the game.

    Attributes
    ----------
    library: Library
        A reference back to the game library which contains this ModelIndex.
    type: Object
        The class that this will be a collection of.  This is the object that
        we'll instantiate when adding new instances.
    index: dictionary[type]
        A dictionary of instances of "type" keyed to each item's in-game ID
        number.  This represents the collection of all instances of that type
        of object that exist in the game.

    TODO This should be renamed.  This is really a KeyedCollection.  Or a
    ManagedDictionary.  Or a DatabaseTable.  In any case, "ModelIndex" is a bad
    name and we should find a better one.
        
    """

    def __init__(self, library, type):
        self.library = library
        self.type = type
        
        self.index = {}

    def add(self, model):
        self.index[model.getId()] = model
        return self

    def create(self, id):
        model = self.type(self.library)
        model.setId(id)
        self.add(model)
        return model 

    def getById(self, id):
        if id in self.index:
            return self.index[id]
        else:
            return None

    def hasId(self, id):
        if id in self.index:
            return True
        else:
            return False

class NamedModelIndex(ModelIndex):
    """A model collection that uses the name of the object as the key.

    Extends ModelIndex, but uses the name of the object as the key rather than
    its in-game id.

    TODO Rename me. See TODO on ModelIndex. 
    """

    def create(self, id):
        id = str(id).lower()
        return super(NamedModelIndex, self).create(id)

class PrototypeIndex(ModelIndex):

    # Create a new instance of this model from the prototype.
    def instance(self, id):
        if self.hasId(id):
            return copy.deepcopy(self.getById(id))
        else:
            return None

class Library:
    """A library object containing and providing access to the game's content.

    Effectively an ingame database of all of the games models - accounts,
    character, objects, locations, and npcs.  Also handles loading and saving
    of those models.

    Attributes
    ----------
    players: list[Player]
        A list of players currently logged into the game and playing.
    commands: list[Command]
        A list of all commands the players may execute in the game.
    rooms: list[Room]
        A list of all Room locations that exist in the game.

    TODO Finish me.  Also probably rename me.  Database?  Library works well
    enough, but there's probably a better name.
    """

    def __init__(self):
        self.players = []
        self.commands = {}

        self.loadCommands()

        self.accounts = NamedModelIndex(self, Account) 
        self.characters = NamedModelIndex(self, Character)
        self.rooms = ModelIndex(self, Room) 
        self.mobs = {}
        self.items = PrototypeIndex(self, Item) 


    def loadCommands(self):
        """Loads the game's command objects.

        The command objects are loaded into a list keyed by the in-game command
        used to execute them.

        Order is important here, because it will be the order in which
        commands are matched.  So if someone just types "n", they'll get
        "north" before they get any of the other commands starting with "n".
        You'll want to order these to optimize player shortcut by putting more
        used commands above less used commands.
        """

        self.commands['north'] = movement.North(self)
        self.commands['east'] = movement.East(self)
        self.commands['south'] = movement.South(self)
        self.commands['west'] = movement.West(self)
        self.commands['up'] = movement.Up(self)
        self.commands['down'] = movement.Down(self)
        self.commands['open'] = manipulation.Open(self)
        self.commands['close'] = manipulation.Close(self)
        self.commands['look'] = information.Look(self)
        self.commands['say'] = communication.Say(self)
        self.commands['report'] = information.Report(self)
        self.commands['get'] = manipulation.Get(self)
        self.commands['drop'] = manipulation.Drop(self)
        self.commands['equipment'] = information.Equipment(self)
        self.commands['inventory'] = information.Inventory(self)
        self.commands['wield' ] = manipulation.Wield(self)

    def getCommand(self, command_name):
        if command_name in self.commands:
            return self.commands[command_name]
        else:
            return None

    def findCommand(self, input):
        command_list = list(self.commands.keys())
        for command in command_list:
            if command.startswith(input):
                return self.commands[command]

        return None

    def load(self):
        print("Loading the game library.")

        print("Loading items...")
        item_list = glob.glob(Item.getBasePath() + '*.json')
        for file_path in item_list:
            print("Loading item " + file_path + "...")
            item = Item(self)
            item.load(file_path)
            self.items.add(item)

        print("Loading rooms...")
        room_list = glob.glob(Room.getBasePath() + '*.json') 
        for file_path in room_list:
            print("Loading room " + file_path + "...")
            room = Room(self)
            room.load(file_path)
            self.rooms.add(room)

        print("Connecting rooms...")
        for id in self.rooms.index:
            self.rooms.getById(id).connect()

        print("Loading characters...")
        character_list = glob.glob(Character.getBasePath() + '*.json')
        for file_path in character_list:
            print("Loading character " + file_path + "...")
            character = Character(self)
            character.load(file_path)
            self.characters.add(character)

        print("Loading accounts...")
        account_list = glob.glob(Account.getBasePath() + '*.json') 
        for file_path in account_list:
            print("Loading account " + file_path + "...")
            account = Account(self)
            account.load(file_path)
            self.accounts.add(account)

