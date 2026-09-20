import json
import os

import pytest

from game.library.validation.errors import FieldTypeError
from game.library.validation.errors import InvalidValueError
from game.library.validation.errors import MissingFieldError
from game.library.validation.errors import UnexpectedFieldError

from game.store.models.room import WATER_TYPE_NAMES

from generator.store.biome import Biome
from generator.store.biome import Disruption


def biome_json(**overrides):
    """
    Build the json for a minimal valid Biome, with any of its fields replaced
    by `overrides`.
    """

    data = {
        "name": "plain",
        "color": [20, 230, 0],
        "titles": ["A Plain"],
        "descriptions": {
            "initial": ["A wide open plain."],
            "flavor": ["The grass is tall."],
        },
        "trees": [],
        "treeDensity": 0,
        "shrubs": [],
        "shrubDensity": 0,
        "herbs": [],
        "herbDensity": 0,
        "debris": [],
        "debrisDensity": 0,
        "water": "none",
        "succession": None,
        "successionTime": 0,
        "disruptions": {},
    }
    data.update(overrides)
    return data


def disruption_json(**overrides):
    data = {"chance": 0.01, "spread": 50, "biome": "burned-forest"}
    data.update(overrides)
    return data


###############################################################################
# The Biome schema
###############################################################################

def test_validate_returns_true_for_a_valid_biome():
    assert Biome().validate(biome_json()) is True


@pytest.mark.parametrize('field', sorted(Biome.SCHEMA))
def test_every_field_of_a_biome_is_required(field):
    # A biome is written by the generator, which writes all of them, so
    # there is no such thing as an optional one.
    data = biome_json()
    del data[field]

    with pytest.raises(MissingFieldError) as error:
        Biome().validate(data)

    assert error.value.path == 'Biome.%s' % field


def test_validate_raises_for_a_field_the_biome_has_no_place_for():
    with pytest.raises(UnexpectedFieldError) as error:
        Biome().validate(biome_json(tree_density=1))

    assert error.value.path == 'Biome.tree_density'


@pytest.mark.parametrize('field,value', [
    ('name', 7),
    ('color', 'green'),
    ('titles', 'A Plain'),
    ('descriptions', ['A wide open plain.']),
    ('trees', 'an oak tree'),
    ('treeDensity', 'thick'),
    ('water', 7),
    ('succession', 7),
    ('successionTime', 'ages'),
    ('disruptions', []),
])
def test_validate_raises_for_a_field_of_the_wrong_type(field, value):
    with pytest.raises(FieldTypeError) as error:
        Biome().validate(biome_json(**{field: value}))

    assert error.value.path == 'Biome.%s' % field


def test_a_density_may_be_a_whole_number_or_not():
    assert Biome().validate(biome_json(treeDensity=1)) is True
    assert Biome().validate(biome_json(treeDensity=1.5)) is True


def test_a_biome_may_grow_into_another_one_or_into_nothing():
    assert Biome().validate(biome_json(succession=None)) is True
    assert Biome().validate(biome_json(succession='forest')) is True


###############################################################################
# Water
#
# The generator writes a biome's water straight into the rooms it generates,
# so the two vocabularies have to be the same one.  They were separate lists
# once, and drifted, which left every generated world unloadable.
###############################################################################

@pytest.mark.parametrize('water', WATER_TYPE_NAMES)
def test_a_biome_takes_any_water_a_room_takes(water):
    assert Biome().validate(biome_json(water=water)) is True


def test_a_biome_does_not_take_water_a_room_would_not():
    with pytest.raises(InvalidValueError) as error:
        Biome().validate(biome_json(water='no-water'))

    assert error.value.path == 'Biome.water'
    assert "'none'" in error.value.message


def test_the_biomes_water_constants_are_the_rooms_water():
    assert Biome.WATER_NONE in WATER_TYPE_NAMES
    assert Biome.WATER_FRESH in WATER_TYPE_NAMES
    assert Biome.WATER_SALT in WATER_TYPE_NAMES


###############################################################################
# Descriptions
###############################################################################

def test_a_description_is_made_of_lists_of_sentences():
    with pytest.raises(FieldTypeError) as error:
        Biome().validate(biome_json(descriptions={"initial": "A plain.", "flavor": []}))

    assert error.value.path == 'Biome.descriptions.initial'


@pytest.mark.parametrize('part', Biome.DESCRIPTION_PARTS)
def test_a_biome_must_have_every_part_of_a_room_description(part):
    descriptions = {"initial": [], "flavor": []}
    del descriptions[part]

    with pytest.raises(MissingFieldError) as error:
        Biome().validate(biome_json(descriptions=descriptions))

    assert error.value.path == 'Biome.descriptions.%s' % part


###############################################################################
# Disruptions
###############################################################################

def test_a_biome_may_have_several_disruptions():
    assert Biome().validate(biome_json(disruptions={
        "fire": disruption_json(),
        "herbivore-herd": disruption_json(biome='meadow'),
    })) is True


def test_a_disruption_must_be_an_object():
    with pytest.raises(FieldTypeError) as error:
        Biome().validate(biome_json(disruptions={"fire": "burns"}))

    assert error.value.path == 'Biome.disruptions.fire'


@pytest.mark.parametrize('field', sorted(Disruption.SCHEMA))
def test_every_field_of_a_disruption_is_required(field):
    data = disruption_json()
    del data[field]

    with pytest.raises(MissingFieldError) as error:
        Biome().validate(biome_json(disruptions={"fire": data}))

    assert error.value.path == 'Disruption.%s' % field


def test_a_disruption_says_what_it_leaves_behind():
    with pytest.raises(FieldTypeError) as error:
        Biome().validate(biome_json(disruptions={"fire": disruption_json(biome=7)}))

    assert error.value.path == 'Disruption.biome'


def test_a_disruption_may_not_be_given_a_field_it_has_no_place_for():
    with pytest.raises(UnexpectedFieldError) as error:
        Biome().validate(biome_json(disruptions={"fire": disruption_json(heat=7)}))

    assert error.value.path == 'Disruption.heat'


###############################################################################
# Serialization
###############################################################################

def test_fromJson_validates_before_loading():
    biome = Biome()

    with pytest.raises(InvalidValueError):
        biome.fromJson(biome_json(water='no-water'))

    # The biome is left untouched by the failed load.
    assert biome.name == ''


def test_fromJson_loads_valid_data():
    biome = Biome().fromJson(biome_json(
        name='forest', trees=['an oak tree'], treeDensity=1.5, water='fresh',
        succession='ancient-forest', successionTime=50,
        disruptions={"fire": disruption_json()}))

    assert biome.name == 'forest'
    assert biome.trees == ['an oak tree']
    assert biome.tree_density == 1.5
    assert biome.water == 'fresh'
    assert biome.succession == 'ancient-forest'
    assert biome.succession_time == 50

    # The generator reads a disruption as the json it arrives as, rather than
    # as a Disruption, so that is how it is kept.
    assert biome.disruptions == {"fire": disruption_json()}


def test_fromJson_keeps_the_color_as_a_pixel():
    # The snapshot images are drawn with it, and a pixel is a tuple.
    assert Biome().fromJson(biome_json()).color == (20, 230, 0)


def test_toJson_output_passes_validation():
    biome = Biome().fromJson(biome_json(disruptions={"fire": disruption_json()}))

    assert Biome().validate(biome.toJson()) is True


def test_toJson_round_trips():
    data = biome_json(name='forest', water='salt', disruptions={"fire": disruption_json()})

    assert Biome().fromJson(data).toJson() == data


###############################################################################
# Files
###############################################################################

def test_load_reads_a_biome_from_a_file(tmp_path):
    path = str(tmp_path / 'plain.json')
    file = open(path, 'w')
    file.write(json.dumps(biome_json()))
    file.close()

    biome = Biome()

    assert biome.load(path) is True
    assert biome.name == 'plain'


def test_load_says_so_when_there_is_no_file(tmp_path):
    assert Biome().load(str(tmp_path / 'no-such-biome.json')) is False


def test_load_lets_what_is_wrong_with_a_biome_out(tmp_path):
    # This used to be swallowed and reported as a False, which left the
    # generator unable to say what was wrong and the data validator unable to
    # see it at all.
    path = str(tmp_path / 'plain.json')
    file = open(path, 'w')
    file.write(json.dumps(biome_json(water='no-water')))
    file.close()

    with pytest.raises(InvalidValueError) as error:
        Biome().load(path)

    assert error.value.path == 'Biome.water'


def test_save_writes_a_biome_it_can_read_back(tmp_path):
    directory = str(tmp_path / 'biomes') + os.sep

    Biome().fromJson(biome_json(disruptions={"fire": disruption_json()})).save(directory)

    assert Biome().load(os.path.join(directory, 'plain.json')) is True
