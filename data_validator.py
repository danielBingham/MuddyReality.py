###############################################################################
# Validate the Game's Data
#
# Loads the whole data library the way the game server does, links it
# together, and reports everything wrong with it rather than stopping at the
# first problem.  Invoked through `main.py`:
#
#   python3 main.py validator [validator arguments]
#
# Exits non-zero when the data has problems, so that `build.sh` fails on it.
###############################################################################

import glob
import json
import os

from game.library.validation.errors import ValidationError

from game.store.loading import LoadError
from game.store.loading import LoadReporter
from game.store.loading import describeException

from game.store.models.item import Item
from game.store.models.item import TRAITS
from game.store.models.room import Exit
from game.store.models.room import Room

from game.store.store import Store

from generator.store.biome import Biome


class ProblemCollector(LoadReporter):
    """
    A `LoadReporter` that writes down everything wrong with the data instead
    of stopping at the first problem.

    This is the whole difference between validating the data and running the
    server on it.  The server wants to fail fast, because it can't do its job
    on data it couldn't finish loading.  The validator wants the opposite: a
    list long enough to work through in one sitting.

    Attributes
    ----------
    verbose:    boolean
        Whether to narrate the load, file by file, the way the server does.
    problems:   list[LoadError]
        Everything found wrong with the data, in the order it was found.
    """

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.problems = []

        # The problems already recorded, as (path, message).  The data is
        # loaded once per world, and the items, npcs, characters and accounts
        # are the same for all of them, so without this a problem in an item
        # would be reported once per world.
        self.seen = set()

    def progress(self, message):
        if self.verbose:
            print(message)

    def error(self, problem):
        """
        Record what is wrong with the file a problem was found in.

        Never raises, which is what lets `Store.load` carry on to the end.

        Parameters
        ----------
        problem:    LoadError
            What is wrong with the data.

        Returns
        -------
        void
        """

        for found in inspect(problem):
            self.record(found)

    def record(self, problem):
        """
        Add a problem to the list, unless it is already on it.

        The one place anything is dropped as a repeat, so that everywhere
        else is free to report the same thing twice.

        Parameters
        ----------
        problem:    LoadError
            What is wrong with the data.

        Returns
        -------
        void
        """

        seen = (problem.path, problem.message)
        if seen in self.seen:
            return

        self.seen.add(seen)
        self.problems.append(problem)


def checker(model, data):
    """
    A callable that validates `data` against `model`, for collecting a list
    of checks to run.

    Parameters
    ----------
    model:  JsonSerializable
        The model to validate against.
    data:   dict
        The json to validate.

    Returns
    -------
    callable
    """

    return lambda: model.validate(data)


def takeApart(model, data):
    """
    Take a file's json apart into the pieces that validate independently of
    one another.

    A model stops at the first problem it finds, so one bad trait hides every
    other problem in the item carrying it, and one bad exit hides the rest of
    the exits out of a room.  Checking each piece on its own is what gets the
    whole list out of a single run.

    Parameters
    ----------
    model:  type
        The model the file is loaded into.
    data:   dict
        The json read from the file.

    Yields
    ------
    (string | None, callable)
        Where in the file the piece sits, for a piece whose own errors
        wouldn't say, and a callable that validates it.
    """

    if not isinstance(data, dict):
        return

    if issubclass(model, Item):
        # An item validates its own fields and then each of its traits, so
        # the traits are what it stops short of.  A trait's errors already
        # name the trait, so they need no label.
        yield None, checker(Item(), data)

        traits = data.get('traits')
        if isinstance(traits, dict):
            for name in traits:
                # A trait that doesn't exist has nothing to check it
                # against.  The item itself has already said so.
                if name in TRAITS:
                    yield None, checker(TRAITS[name](), traits[name])
        return

    if issubclass(model, Room):
        # A room validates its own fields and leaves its exits to `fromJson`,
        # which builds each one and has it validate itself.  Every exit
        # reports its problems the same way, so they are labelled with the
        # direction they go.
        yield None, checker(Room(), data)

        exits = data.get('exits')
        if isinstance(exits, dict):
            for direction in exits:
                yield 'Room.exits.%s' % direction, checker(Exit(None), exits[direction])
        return


def relabel(error, label):
    """
    Rewrite the path of an error found in a piece of a file, so that it says
    where in the file that piece was.

    An exit reports its problems as `Exit.is_door`, which reads the same for
    every exit out of a room.  Rooted at the room, it becomes
    `Room.exits.east.is_door`, which says which one.

    Parameters
    ----------
    error:  ValidationError
        The error the piece raised.
    label:  string
        Where the piece sits in the file.

    Returns
    -------
    string
    """

    # Everything after the model's own name, which `label` replaces.
    field = error.path.partition('.')[2]

    if field:
        return '%s.%s: %s' % (label, field, error.message)

    return '%s: %s' % (label, error.message)


def readJson(path):
    """
    Read a json file, for a second look at one that wouldn't load.

    Parameters
    ----------
    path:   string
        The filepath to read.

    Returns
    -------
    dict | list | None
        What the file holds, or None if it couldn't be read.
    """

    try:
        file = open(path, 'r')
        try:
            return json.load(file)
        finally:
            file.close()
    except Exception:
        return None


def inspect(problem):
    """
    Everything wrong with the file a problem was found in, rather than only
    the problem that stopped it loading.

    Parameters
    ----------
    problem:    LoadError
        The problem the loader found.

    Returns
    -------
    list[LoadError]
        Everything wrong with the file.  The problem as it came for one that
        isn't about a file, one the loader found while linking the data
        together rather than while reading it, or one in a file that can't be
        taken apart - whatever stopped that file being read will stop it
        again, so the problem in hand is the whole story.
    """

    if not problem.path or not problem.model:
        return [problem]

    data = readJson(problem.path)
    if data is None:
        return [problem]

    # The model stopped at the first problem it found, which is a problem one
    # of its pieces finds again.  Both are reported, and the collector drops
    # the second as the repeat it is.
    found = []
    for label, check in takeApart(problem.model, data):
        try:
            check()
        except ValidationError as error:
            message = relabel(error, label) if label else str(error)
            found.append(LoadError(problem.path, message, fatal=problem.fatal, cause=error))

    if not found:
        return [problem]

    return found


def validateBiomes(data_directory, reporter):
    """
    Load every biome, so that the data the world generator reads is checked
    along with the data the server reads.

    Parameters
    ----------
    data_directory: string
        The path to the data directory.
    reporter:   LoadReporter
        Receives the progress of the load and anything found wrong.

    Returns
    -------
    integer
        How many biome files were read.
    """

    biome_path = os.path.join(data_directory, 'biomes/')
    reporter.progress("Loading biomes from %s..." % biome_path)

    biome_list = sorted(glob.glob(biome_path + '**/*.json', recursive=True))
    for file_path in biome_list:
        reporter.progress("Loading biome %s..." % file_path)
        try:
            Biome().load(file_path)
        except Exception as exception:
            reporter.error(LoadError(file_path, describeException(exception),
                                     cause=exception, model=Biome))

    return len(biome_list)


def findWorlds(data_directory, world=None):
    """
    The worlds to validate.

    Parameters
    ----------
    data_directory: string
        The path to the data directory.
    world:  string | None
        The name of a single world to validate.  Every world found under
        `data/worlds/` is validated when this is None.

    Returns
    -------
    list[string]
        The world names, in alphabetical order.
    """

    if world:
        return [world]

    worlds_path = os.path.join(data_directory, 'worlds')
    if not os.path.isdir(worlds_path):
        return []

    # A directory without a `world.json` isn't a world.  The generator writes
    # that file first, so a world part way through being generated is skipped
    # rather than reported as broken.
    return sorted(name for name in os.listdir(worlds_path)
                  if os.path.isfile(os.path.join(worlds_path, name, 'world.json')))


def countFiles(data_directory, *path):
    """
    How many json files there are under a directory of the data library.

    Parameters
    ----------
    data_directory: string
        The path to the data directory.
    *path:  string
        The directory to count, relative to the data directory.

    Returns
    -------
    integer
    """

    directory = os.path.join(data_directory, *path)
    return len(glob.glob(os.path.join(directory, '**/*.json'), recursive=True))


def validate(data_directory='data/', world=None, verbose=False):
    """
    Load the data library and collect everything wrong with it.

    Parameters
    ----------
    data_directory: string
        The path to the data directory.
    world:  string | None
        The name of a single world to validate.  Every world is validated
        when this is None.
    verbose:    boolean
        Narrate the load, file by file, the way the server does.

    Returns
    -------
    (ProblemCollector, dict)
        Everything found wrong with the data, and a count of what was
        checked, keyed by what it was.
    """

    collector = ProblemCollector(verbose)

    counts = {}
    counts['biomes'] = validateBiomes(data_directory, collector)
    counts['items'] = countFiles(data_directory, 'items')
    counts['npcs'] = countFiles(data_directory, 'npcs')
    counts['characters'] = countFiles(data_directory, 'characters')
    counts['accounts'] = countFiles(data_directory, 'accounts')

    worlds = findWorlds(data_directory, world)
    counts['worlds'] = len(worlds)
    counts['rooms'] = 0

    for name in worlds:
        counts['rooms'] += countFiles(data_directory, 'worlds', name, 'rooms')

        # A store of its own for each world, since a store holds one world's
        # rooms.  The items, npcs, characters and accounts are shared, so they
        # are loaded again for each - the collector drops the repeats.
        Store(name, data_directory).load(collector)

    return collector, counts


def describeCounts(counts):
    """
    Describe what was checked, for the line above the results.

    Parameters
    ----------
    counts: dict
        A count of what was checked, keyed by what it was.

    Returns
    -------
    string
    """

    def plural(count, name):
        return '%d %s' % (count, name if count == 1 else name + 's')

    return ', '.join([
        plural(counts['items'], 'item'),
        plural(counts['npcs'], 'npc'),
        plural(counts['characters'], 'character'),
        plural(counts['accounts'], 'account'),
        plural(counts['biomes'], 'biome'),
        plural(counts['worlds'], 'world'),
        plural(counts['rooms'], 'room'),
    ])


def report(collector, counts):
    """
    Print the results of the validation: what was checked, and everything
    found wrong with it, grouped by the file it is in.

    Parameters
    ----------
    collector:  ProblemCollector
        Everything found wrong with the data.
    counts: dict
        A count of what was checked, keyed by what it was.

    Returns
    -------
    void
    """

    print("Checked %s." % describeCounts(counts))

    if not collector.problems:
        print("No problems found.")
        return

    # Grouped by file, so that fixing them means opening each file once.
    # `None` collects the problems that aren't about any one file.
    by_file = {}
    for problem in collector.problems:
        by_file.setdefault(problem.path, []).append(problem)

    files = sorted(path for path in by_file if path is not None)
    if None in by_file:
        files.append(None)

    print()
    print("Found %d problem%s in %d file%s:"
          % (len(collector.problems), '' if len(collector.problems) == 1 else 's',
             len(files), '' if len(files) == 1 else 's'))

    for path in files:
        print()
        print("  %s" % (path if path else 'the world as a whole'))
        for problem in by_file[path]:
            print("      %s" % problem.message)


def run(arguments):
    """
    Validate the game's data.

    Parameters
    ----------
    arguments: argparse.Namespace
        The parsed command line arguments for the `validator` command, as
        defined in `main.py`.

    Returns
    -------
    integer
        The exit status.  0 if the data loaded cleanly, 1 if it did not, so
        that `build.sh` fails on data that needs fixing.
    """

    print("Validating the data in %s..." % arguments.data)

    collector, counts = validate(arguments.data, arguments.world, arguments.verbose)

    report(collector, counts)

    if collector.problems:
        return 1

    return 0
