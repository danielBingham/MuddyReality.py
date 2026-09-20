import os
import json

from game.library.validation.errors import MissingFieldError
from game.library.validation.validator import Validator
from game.library.validation.validator import validateModel

from game.store.models.base import JsonSerializable
from game.store.models.room import WATER_TYPE_NAMES
from game.store.models.room import WaterType


class Disruption(JsonSerializable):
    """
    An event that can turn one biome into another - a fire that burns a
    forest down to a meadow, say.

    A biome keeps its disruptions as the raw json the generator reads them
    out of, rather than as objects, so this exists to give their shape a
    schema and a name.
    """

    SCHEMA = {
        # The chance of the disruption starting in a room in any one year, as
        # a percentage.
        "chance": Validator().isType(float).isRequired(),

        # The chance of the disruption spreading from a room to the one next
        # to it, as a percentage.
        "spread": Validator().isType(float).isRequired(),

        # The name of the biome a disrupted room is left as.
        "biome": Validator().isType(str).isRequired(),
    }

    def validate(self, data):
        """
        Validate that `data` is valid Disruption json.

        Parameters
        ----------
        data:   dict
            The json data to validate.

        Returns
        -------
        True
            If `data` is valid.

        Raises
        ------
        ValidationError
            If `data` does not match `SCHEMA`.
        """

        return validateModel(type(self), data)


class Biome(JsonSerializable):

    # The generator writes a biome's water straight into the rooms it
    # generates, so the two vocabularies have to be the same one.  They were
    # separate lists once, and drifted, which left every generated world
    # unloadable.
    WATER_NONE = WaterType.NONE
    WATER_FRESH = WaterType.FRESH
    WATER_SALT = WaterType.SALT

    # The parts of `descriptions` the room generator reads.  A biome missing
    # either of them would generate rooms with no description at all.
    DESCRIPTION_PARTS = ['initial', 'flavor']

    SCHEMA = {
        "name": Validator().isType(str).isRequired(),

        # The biome's color on the generated map, as RGB.
        "color": Validator().isType(list[int]).isRequired(),

        "titles": Validator().isType(list[str]).isRequired(),

        # The sentences a room's description is assembled out of, keyed by the
        # part they play in it.  `validate` checks the keys, which a schema
        # has no way to speak about.
        "descriptions": Validator().isType(dict[str, list[str]]).isRequired(),

        # The `name` of each Item that can grow or lie in this biome.
        "trees": Validator().isType(list[str]).isRequired(),
        "shrubs": Validator().isType(list[str]).isRequired(),
        "herbs": Validator().isType(list[str]).isRequired(),
        "debris": Validator().isType(list[str]).isRequired(),

        # How densely each layer grows.  1.0 is as dense as the layer's full
        # canopy allows.  (multiple of full canopy)
        "treeDensity": Validator().isType(float).isRequired(),
        "shrubDensity": Validator().isType(float).isRequired(),
        "herbDensity": Validator().isType(float).isRequired(),
        "debrisDensity": Validator().isType(float).isRequired(),

        "water": Validator().isType(str).isOneOf(WATER_TYPE_NAMES).isRequired(),

        # The `name` of the biome this one grows into, or null for one that
        # doesn't.
        "succession": Validator().isType(str | None).isRequired(),

        # How long this biome takes to grow into the next. (years)
        "successionTime": Validator().isType(float).isRequired(),

        # Each disruption validates itself in `validate`, so the schema only
        # checks that each one is the object a Disruption loads from.
        "disruptions": Validator().isType(dict[str, Disruption]).isRequired(),
    }

    def __init__(self):

        # The name of the biome.
        self.name = ''
        self.color = ()

        self.titles = []
        self.descriptions = []

        # An array of Item.id that represents trees that can spawn in this
        # biome.
        self.trees = []

        # The density at which trees grow in this biome.
        #
        # For values less than 1.0, trees will be spread out and the canopy
        # will have frequent breaks.
        #
        # 1.0 - Trees will grow to the maximum density allowed by their full
        # canopy.  Rooms are 100m x 100m, so a tree with a 50m canopy can spawn
        # 2 to a room.
        #
        # Values over 1.0 mean trees grow closer together than their full
        # canopy and will spawn more densly.
        self.tree_density = 0

        # An array of shrubs that can spawn in this biome.
        self.shrubs = []

        # The density of the shrub layer.  See `tree_density`.
        self.shrub_density = 0

        # An array of herbs that can spawn in this biome.
        self.herbs = []

        # The density of the herb layer.  See `tree_density`.
        self.herb_density = 0

        # An array of debris that can spawn on the floor of this biome.
        self.debris = []

        self.debris_density = 0

        # Is there water in this biome?  How much?
        self.water = Biome.WATER_NONE

        ###  Biome Evolution ###
        # Values managing the way the biome evolves over time.
        ###

        # What biome does this biome eventually evolve into?
        self.succession = None

        # How long does it take this biome to evolve in 1 years.
        self.succession_time = 0

        # A list of disruptions that can occur.  Each list item includes the
        # chance of the disruption as a percentage, its name, the the biome that results.
        # { name: 'forest fire', chance: 10, biome: 'meadow' }
        self.disruptions = []

    def validate(self, data):
        """
        Validate that `data` is valid Biome json.

        Parameters
        ----------
        data:   dict
            The json data to validate.

        Returns
        -------
        True
            If `data` is valid.

        Raises
        ------
        ValidationError
            If `data` does not match `SCHEMA`, if a disruption does not match
            `Disruption.SCHEMA`, or if the biome doesn't have all the parts a
            room description is assembled out of.
        """

        validateModel(type(self), data)

        for part in Biome.DESCRIPTION_PARTS:
            if part not in data['descriptions']:
                raise MissingFieldError(
                    'Biome.descriptions.%s' % part,
                    'a room description is assembled out of %s, so a biome must have all of them.'
                    % ', '.join(repr(name) for name in Biome.DESCRIPTION_PARTS))

        for name in data['disruptions']:
            Disruption().validate(data['disruptions'][name])

        return True

    def toJson(self):
        json = {}

        json['name'] = self.name

        # `fromJson` keeps the color as a tuple, because the snapshot images
        # are drawn with it and a pixel is a tuple.  Json has only one kind
        # of sequence, so it is written back out as a list - which is also
        # what makes what this writes something it would accept.
        json['color'] = list(self.color)

        json['titles'] = self.titles
        json['descriptions'] = self.descriptions

        json['trees'] = self.trees
        json['treeDensity'] = self.tree_density

        json['shrubs'] = self.shrubs
        json['shrubDensity'] = self.shrub_density

        json['herbs'] = self.herbs
        json['herbDensity'] = self.herb_density

        json['debris'] = self.debris
        json['debrisDensity'] = self.debris_density

        json['water'] = self.water

        json['succession'] = self.succession
        json['successionTime'] = self.succession_time

        json['disruptions'] = self.disruptions

        return json

    def fromJson(self, data):

        self.validate(data)

        self.name = data['name']
        self.color = tuple(data['color'])

        self.titles = data['titles']
        self.descriptions = data['descriptions']

        self.trees = data['trees']
        self.tree_density = data['treeDensity']

        self.shrubs = data['shrubs']
        self.shrub_density = data['shrubDensity']

        self.herbs = data['herbs']
        self.herb_density = data['herbDensity']

        self.debris = data['debris']
        self.debris_density = data['debrisDensity']

        self.water = data['water']

        self.succession = data['succession']
        self.succession_time = data['successionTime']

        # The generator reads these as the json objects they arrive as, so
        # they are kept that way rather than loaded into Disruptions.
        self.disruptions = data['disruptions']

        return self

    def save(self, base_path='data/biomes/'):
        if not os.path.exists(base_path):
            os.mkdir(base_path)

        file = open(base_path + self.name + '.json', 'w')
        try:
            json.dump(self.toJson(), file)
        except Exception:
            raise
        finally:
            file.close()

        return self

    def load(self, path):
        """
        Load this biome from the json file at `path`.

        Parameters
        ----------
        path:   string
            The filepath to the json data we want to load this biome from.

        Returns
        -------
        boolean
            True if the biome was loaded.  False if there was no file at
            `path`.

        Raises
        ------
        Exception
            Whatever went wrong reading the file or loading the data.  This
            used to be swallowed and reported as a False, which left the
            generator unable to say what was wrong with a biome, and
            `data_validator.py` unable to see it at all.
        """

        if not os.path.exists(path):
            return False

        file = open(path, 'r')
        try:
            self.fromJson(json.load(file))
        finally:
            file.close()

        return True
