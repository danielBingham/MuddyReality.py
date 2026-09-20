import pytest

from game.library.validation.errors import MissingFieldError

from game.store.loading import DataError
from game.store.loading import LoadError
from game.store.loading import LoadReporter
from game.store.loading import describeException


###############################################################################
# LoadError
###############################################################################

def test_a_problem_in_a_file_reads_as_the_file_and_the_problem():
    problem = LoadError('data/items/rock.json', 'Item.name: Item requires this field.')

    assert str(problem) == 'data/items/rock.json: Item.name: Item requires this field.'


def test_a_problem_that_is_not_about_a_file_reads_as_itself():
    problem = LoadError(None, 'No Character(gird) found.')

    assert str(problem) == 'No Character(gird) found.'


def test_a_problem_is_fatal_unless_it_says_otherwise():
    assert LoadError('data/items/rock.json', 'broken').fatal is True
    assert LoadError('data/items/rock.json', 'broken', fatal=False).fatal is False


###############################################################################
# describeException
###############################################################################

def test_a_validation_error_describes_itself():
    error = MissingFieldError('Item.name', 'Item requires this field.')

    # Its type adds nothing to what it already says.
    assert describeException(error) == 'Item.name: Item requires this field.'


def test_any_other_exception_is_described_with_its_type():
    # A model with no schema yet raises a KeyError for a field it needs,
    # which is just the key on its own without it.
    assert describeException(KeyError('name')) == "KeyError: 'name'"
    assert describeException(TypeError('not a dict')) == 'TypeError: not a dict'


###############################################################################
# LoadReporter
#
# The default reporter, which is the one the game server wants: narrate the
# load, and stop on the first problem it can't carry on past.
###############################################################################

def test_the_reporter_narrates_the_load(capsys):
    LoadReporter().progress('Loading items from data/items/...')

    assert capsys.readouterr().out == 'Loading items from data/items/...\n'


def test_the_reporter_raises_what_stopped_a_file_loading():
    error = MissingFieldError('Item.name', 'Item requires this field.')
    problem = LoadError('data/items/rock.json', str(error), cause=error)

    # The exception itself, rather than something wrapped around it, so that
    # the traceback still points at what actually went wrong.
    with pytest.raises(MissingFieldError) as raised:
        LoadReporter().error(problem)

    assert raised.value is error


def test_the_reporter_raises_for_a_fatal_problem_that_had_no_exception():
    # Nothing raises for an exit that leads nowhere.  The loader notices it
    # for itself.
    problem = LoadError('data/worlds/base/rooms/1.json',
                        "the 'east' exit leads to Room(99), which does not exist.")

    with pytest.raises(DataError) as raised:
        LoadReporter().error(problem)

    assert raised.value.problem is problem
    assert str(raised.value) == str(problem)


def test_the_reporter_carries_on_past_a_problem_that_is_not_fatal(capsys):
    problem = LoadError('data/worlds/base/rooms/1.json',
                        'there is no Item(a rock) to put in this room.', fatal=False)

    # A room comes up without an item it couldn't find rather than refusing
    # to come up at all, which is how the game has always treated it.
    LoadReporter().error(problem)

    assert 'there is no Item(a rock) to put in this room.' in capsys.readouterr().out


def test_the_reporter_prints_every_problem_it_is_given(capsys):
    with pytest.raises(DataError):
        LoadReporter().error(LoadError('data/items/rock.json', 'broken'))

    assert 'Error! data/items/rock.json: broken' in capsys.readouterr().out
