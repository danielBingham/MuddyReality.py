from game.library.validation.errors import ValidationError


class DataError(Exception):
    """
    Raised when the game's data cannot be loaded.

    Carries the problem that stopped the load, for the cases where nothing
    was raised to begin with - an exit pointing at a room that doesn't exist,
    say, which the loader notices for itself rather than catching.

    Attributes
    ----------
    problem:    LoadError
        What was wrong with the data.
    """

    def __init__(self, problem):
        self.problem = problem

        super(DataError, self).__init__(str(problem))


def describeException(exception):
    """
    Describe an exception raised while loading a data file, in a way that
    reads well in a list of problems with the data.

    Parameters
    ----------
    exception:  Exception
        The exception that was raised.

    Returns
    -------
    string
    """

    # A ValidationError already says where in the data the problem is and
    # what is wrong with it.  Its type adds nothing.
    if isinstance(exception, ValidationError):
        return str(exception)

    # Everything else is clearer with its type in front of it, since the
    # message on its own is often just a key or a bare value.
    return '%s: %s' % (type(exception).__name__, exception)


class LoadError:
    """
    Something wrong with the game's data, found while loading it.

    Attributes
    ----------
    path:   string | None
        The data file the problem is in.  None for a problem that isn't
        about any one file.
    message:    string
        What is wrong.
    fatal:  boolean
        Whether the load can carry on past this.  A file that wouldn't load
        is fatal - whatever needed it won't find it.  A room naming an item
        that doesn't exist is not - the room simply comes up without it,
        which is how the game has always treated it.
    cause:  Exception | None
        The exception that was raised, where there was one.  `LoadReporter`
        re-raises it, so that a server refusing to start still shows the
        traceback of the thing that actually went wrong.
    model:  type | None
        The model the file was being loaded into.  `data_validator.py` uses
        it to go looking for the rest of what is wrong with the file, rather
        than reporting only the problem that stopped it loading.
    """

    def __init__(self, path, message, fatal=True, cause=None, model=None):
        self.path = path
        self.message = message
        self.fatal = fatal
        self.cause = cause
        self.model = model

    def __str__(self):
        if self.path:
            return '%s: %s' % (self.path, self.message)

        return self.message


class LoadReporter:
    """
    Receives the progress of a `Store.load()`, and whatever it finds wrong
    with the data.

    This default is the one the game server wants.  It narrates the load, and
    it stops on the first problem it can't carry on past, because a server
    running on data it couldn't finish loading misbehaves in ways that are
    much harder to diagnose than a failure here.

    `data_validator.py` passes a reporter that writes the problems down and
    returns instead of raising, which is what lets a single run list
    everything in the data that needs fixing.  Every call to `error` in
    `Store.load` is written so that the load does something sensible if it
    does return.
    """

    def progress(self, message):
        """
        Report how far the load has got.

        Parameters
        ----------
        message:    string
            What the load is doing.

        Returns
        -------
        void
        """

        print(message)

    def error(self, problem):
        """
        Report a problem with the data.

        Parameters
        ----------
        problem:    LoadError
            What is wrong with the data.

        Returns
        -------
        void
            If the load may carry on.

        Raises
        ------
        Exception
            The exception that caused a fatal problem, so that the traceback
            points at what actually went wrong.
        DataError
            If a fatal problem had no exception behind it.
        """

        print('Error! %s' % problem)

        if not problem.fatal:
            return

        if problem.cause:
            raise problem.cause

        raise DataError(problem)
