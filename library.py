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
#import game.commands.crafting as crafting

class ModelRepository:
    """Manages and provides access to a collection of models of type ``type``.

    Serves as a combination factory and repository for models of type ``type``,
    managing the dictionary of instances, allowing access to existing instances
    and creation of new ones.  

    Each instance stored represents a unique instance of that model - only one
    copy of that instance will ever exist in the game.

    Attributes
    ----------
    library: Library
        A reference back to the game library which contains this ModelRepository.
    type: Object
        The class that this will be a collection of.  This is the object that
        we'll instantiate when adding new instances.
    repo: dictionary[type]
        A dictionary of instances of "type" keyed to each item's in-game ID
        number.  This represents the collection of all instances of that type
        of object that exist in the game.

    TODO This should be renamed.  This is really a KeyedCollection.  Or a
    ManagedDictionary.  Or a DatabaseTable.  In any case, "ModelRepository" is a bad
    name and we should find a better one.
        
    """

    def __init__(self, library, type):
        """Initialize the ModelRepository.

        Initializes the ModelRepository with its parent library and with the
        type of the model it will wrap.

        Parameters
        ----------
        library: Library
            The Library that will contain this ModelRepository.  Responsible
            for loading the repositories saved data files to populate it, and
            for saving the repositories contents back to those data files.
        type: Class 
           The class of Model that this repository will manage. 
        """

        self.library = library
        self.type = type
        
        self.repo = {}

    def add(self, model):
        """Add a model to the repository.

        Adds an instance of ``type`` to the repository, using its ID as the key.

        Parameters
        ----------
        model: <Type>
            An instance of model ``Type`` to be added to the repository.  Must
            have an ID set and a `getId` method implemented.
        """

        self.repo[model.getId()] = model
        return self

    def create(self, id):
        """Create an instance of model ``type`` identified by ``id`` and add it to the repository.

        Creates a new instance of model ``type`` identified by ``id``, adds it
        to the repository, and then returns it. 

        Parameters
        ----------
        id: integer or string
            The identifier we want to use to key this model.  In the case of a
            positive integer, it will be treated as an ID number.  In all other
            cases, it will be treated as a string identifier and converted to
            lower case.
        """

        # If we weren't given an integer id, then treat it as a string identifier.
        if not id.isdigit():
            id = str(id).lower()

        model = self.type(self.library)
        model.setId(id)
        self.add(model)
        return model 

    def getById(self, id):
        """Get the instance identified by ``id`` from the repository.

        Returns the instance identified by the integer ``id`` from the
        repository and returns it.  Returns ``None`` if no such instance
        exists.

        Parameters
        ----------
        id: integer or string
            The identification number of the model we'd like to retrieve.
        """

        if id in self.repo:
            return self.repo[id]
        else:
            return None

    def hasId(self, id):
        """Determine whether a model identified by ``id`` exists in the repository.

        Checks the repository for a model identified by ``id``.  Returns True
        if it finds one, False otherwise.

        Parameters
        ----------
        id: integer or string
            The identifier of the model we're seeking.
        """

        if id in self.repo:
            return True
        else:
            return False

class PrototypeRepository(ModelRepository):
    """Manages and provides access to a repository of model prototypes of type ``type``. 

    Extends ModelRepository to allow management of a collection of model
    prototypes of type ``type``.  This is a model where there can be 0..N
    copies of each prototypical instance stored in this repository.  Instances
    are not considered unique.  Also provides a method for creating new copies
    of the prototypes stored with in.

    For further information, see ModelRepository.
    """

    # Create a new instance of this model from the prototype.
    def instance(self, id):
        """Creates a new instance of a prototype in the repository.

        Attempts to create a new instance of a prototype identified by ``id``.
        If no such prototype is found in the repository, then returns None.
        Creates a deep copy of the prototype, so that it can act as a
        completely idependent instance of the model.
        
        Parameters
        ----------
        id: integer or string
            The identifier used to identify the model prototype we want to
            create an instance of.
        """

        if self.hasId(id):
            return copy.deepcopy(self.getById(id))
        else:
            return None

class Library:
    """A library object containing and providing access to the game's content.

    A database of all of the game's models - accounts, character, objects,
    locations, npcs, etc.  Also handles loading and saving of those models.

    Attributes
    ----------
    players: list<Player> 
        A list of players currently logged into the game and playing.
    commands: list<Command>
        A list of all commands the players may execute in the game.
    rooms: ModelRepository<Room> 
        A ModelRepository of all Room locations that exist in the game.
    mobs: ModelPrototypeRepository<Character>
        A ModelPrototypeRepository of all the NPC characters that can exist in
        the game.
    items: ModelPrototypeRepository<Item>
        A ModelPrototypeRepository of all the Items that can exist in the game.
    """

    def __init__(self):
        """Initialize the Library.

        Initializes the library by creating the repositories for each type of
        Model stored.  Also loads the commands.
        """

        self.players = []
        self.commands = {}

        self.loadCommands()

        self.accounts = ModelRepository(self, Account) 
        self.characters = ModelRepository(self, Character)
        self.rooms = ModelRepository(self, Room) 
        self.mobs = PrototypeRepository(self, Character) 
        self.items = PrototypeRepository(self, Item) 


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
        self.commands['examine'] = information.Examine(self)
        self.commands['say'] = communication.Say(self)
        self.commands['report'] = information.Report(self)
        self.commands['get'] = manipulation.Get(self)
        self.commands['drop'] = manipulation.Drop(self)
        self.commands['equipment'] = information.Equipment(self)
        self.commands['inventory'] = information.Inventory(self)
        self.commands['wield'] = manipulation.Wield(self)
        #self.commands['craft'] = crafting.Craft(self)

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

        # This runs the `connect()` method on every room we've loaded into the
        # Rooms repository.  This method creates object links for each of the
        # exits that go from one room to another, so that we can easily access
        # to the connected rooms with out having to search for the models.
        #
        # We can only run this once we've fully loaded all of the saved rooms
        # into the repository.  Otherwise, the room referenced by an exit may
        # not exist yet.
        print("Connecting rooms...")
        for id in self.rooms.repo:
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

