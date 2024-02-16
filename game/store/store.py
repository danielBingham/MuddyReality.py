import glob, os

from game.store.models.world import World
from game.store.models.account import Account
from game.store.models.character import Character
from game.store.models.character import PlayerCharacter
from game.store.models.room import Room
from game.store.models.item import Item 


class ModelRepository:
    """
    Manages and provides access to a collection of models of type ``type``.

    Serves as a combination factory and repository for models of type ``type``,
    managing the dictionary of instances, allowing access to existing instances
    and creation of new ones.  

    Each instance stored represents a unique instance of that model - only one
    copy of that instance will ever exist in the game.

    Attributes
    ----------
    store: Store
        A reference back to the game store which contains this ModelRepository.
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

    def __init__(self, store, type):
        """Initialize the ModelRepository.

        Initializes the ModelRepository with its parent store and with the
        type of the model it will wrap.

        Parameters
        ----------
        store: Store
            The Store that will contain this ModelRepository.  Responsible
            for loading the repositories saved data files to populate it, and
            for saving the repositories contents back to those data files.
        type: Class 
           The class of Model that this repository will manage. 
        """

        self.store = store
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

        model = self.type()
        model.setId(id)
        self.add(model)
        return model 

    def load(self, path):
        """
        Load a model from a filepath.

        Parameters
        ----------
        path: string
            The filepath to the json data we want to load this model.
        """

        model = self.type()
        model.load(path)
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
    """
    Manages and provides access to a repository of model prototypes of type ``type``. 

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
            model = self.getById(id)
            instance = self.type()
            instance.fromJson(model.toJson())
            return instance
        else:
            return None


class Store:
    """
    A Storage object containing and providing access to the game's content.

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

    def __init__(self, world='base', data_directory='data/'):
        """
        Initialize the Store.

        Initializes the store by creating the repositories for each type of
        Model stored.  Also loads the commands.

        Parameters
        ----------
        world_time: GameTime
            The object storing the game time and allowing interaction with it.
        world:  string
            The name of the game world we want to load.
        data_directory: string
            The path to the data directory.
        """
        self.data_directory = 'data/'
        self.world = world

        self.players = []

        self.accounts = ModelRepository(self, Account) 
        self.characters = ModelRepository(self, PlayerCharacter)
        self.rooms = ModelRepository(self, Room) 
        self.npcs = PrototypeRepository(self, Character) 
        self.items = PrototypeRepository(self, Item) 

    def saveCharacter(self, character):
        """
        Save a character. Allows us to avoid hard coding the path to the
        character data anywhere we need to save the character.

        Parameters
        ----------
        character:  Character
            The character we'd like to save.
        """

        character_path = os.path.join(self.data_directory, 'characters/')
        character.save(character_path)

    def saveAccount(self, account):
        """
        Save an account.  Allows us to avoid hard coding the path to the
        account data anywhere we need to save an account.

        Parameters
        ----------
        account:    Account
            The account we'd like to save.
        """

        account_path = os.path.join(self.data_directory, 'accounts/')
        account.save(account_path)

    def load(self):
        """
        Populate the game store, loading the game world and all game data.
        """

        print("Loading the game store.")

        world_name = self.world
        world_path = os.path.join(self.data_directory, 'worlds', world_name, 'world.json')
        print("Loading the world from %s..." % world_path)
        self.world = World() 
        self.world.load(world_path)

        item_path = os.path.join(self.data_directory, 'items/')
        print("Loading items from %s..." % item_path)
        item_list = glob.glob(item_path + '**/*.json', recursive=True)
        for file_path in item_list:
            print("Loading item " + file_path + "...")
            self.items.load(file_path)

        npc_path = os.path.join(self.data_directory, 'npcs/')
        print("Loading non-player characters from %s..." % npc_path)
        npc_list = glob.glob(npc_path + '**/*.json', recursive=True)
        for file_path in npc_list:
            print("Loading npc %s..." % file_path)
            self.npcs.load(file_path)

        character_path = os.path.join(self.data_directory, 'characters/')
        print("Loading player characters from %s..." % character_path)
        character_list = glob.glob(character_path + '*.json')
        for file_path in character_list:
            print("Loading character %s..." % file_path)

            character = self.characters.load(file_path)

            print("Loading %s's inventory..." % character.name)
            inventory = character.inventory
            character.inventory = []
            for itemId in inventory:
                if self.items.hasId(itemId):
                    character.inventory.append(self.items.instance(itemId))

            print("Loading %s's equipment..." % character.name)
            for body_part in character.body.worn:
                itemId = character.body.worn[body_part]
                if self.items.hasId(itemId):
                    character.body.worn[body_part] = self.items.instance(itemId)

        account_path = os.path.join(self.data_directory, 'accounts/')
        print("Loading accounts from %s..." % account_path)
        account_list = glob.glob(account_path + '*.json') 
        for file_path in account_list:
            print("Loading account " + file_path + "...")
            account = self.accounts.load(file_path)

            characters = account.characters
            account.characters = {} 
            for name in characters:
                account.characters[name] = self.characters.getById(name)
                account.characters[name].account = account

        room_path = os.path.join(self.data_directory, 'worlds', self.world.name, 'rooms/')
        print("Loading rooms from %s..." % room_path)
        room_list = glob.glob(room_path + '*.json') 
        for file_path in room_list:
            print("Loading room " + file_path + "...")
            self.rooms.load(file_path)

        print("Connecting rooms and loading items into rooms...")
        for id in self.rooms.repo:
            room = self.rooms.getById(id)

            print("Connecting exits for Room(%s) '%s'..." % (str(id), room.title))
            for direction in room.exits:
                exit = room.exits[direction]
                exit.room_to = self.rooms.getById(exit.room_to)
                if Room.INVERT_DIRECTION[exit.direction] in exit.room_to.exits:
                    exit.exit_to = exit.room_to.exits[Room.INVERT_DIRECTION[exit.direction]]

            print("Loading items into Room(%s) '%s'..." % (str(id), room.title))
            items = room.items
            room.items = []
            for itemId in items:
                if self.items.hasId(itemId):
                    room.items.append(self.items.instance(itemId))
                else:
                    print("Error! No Item(%s) in Room(%s)." % (itemId, str(id))), 

            print("Loading characters into Room(%s) '%s'..." % (str(id), room.title))
            occupants = room.occupants
            room.occupants = []
            for characterId in occupants:
                if self.npcs.hasId(characterId):
                    room.occupants.append(self.npcs.instance(characterId))
                else:
                    print("Error! No NPC(%s) in Room(%s)." % (characterId, room.title))

        print("Connect player characters to the rooms they were in...")
        for id in self.characters.repo:
            character = self.characters.getById(id)

            if character.room:
                character.room = self.rooms.getById(character.room)




