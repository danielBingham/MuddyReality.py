from game.library.validation.errors import FieldTypeError, ValidationError

import types
import typing

# Human readable names for the json types, keyed by the python type they
# arrive as.  Looked up by exact type rather than `isinstance`, so that a
# boolean is described as a boolean and not as an integer.
TYPE_NAMES = {
    type(None): 'null',
    bool: 'a boolean',
    int: 'an integer',
    float: 'a number',
    str: 'a string',
    list: 'a list',
    dict: 'an object',
}

# The same names in the plural, for describing what a list holds.
TYPE_NAMES_PLURAL = {
    type(None): 'nulls',
    bool: 'booleans',
    int: 'integers',
    float: 'numbers',
    str: 'strings',
    list: 'lists',
    dict: 'objects',
}

def isUnion(field_type):
    """
    Is `field_type` a union of several types, such as `str | None`?

    Parameters
    ----------
    field_type: type

    Returns
    -------
    boolean
    """

    return (isinstance(field_type, types.UnionType)
            or typing.get_origin(field_type) is typing.Union)

def describeType(field_type, plural=False):
    """
    Describe a schema type in a way that can be read in an error message.

    Parameters
    ----------
    field_type: type
        A resolved type, as `isType` was given.
    plural: boolean
        Describe several of the type rather than one of it, for saying what a
        list holds.

    Returns
    -------
    string
    """

    names = TYPE_NAMES_PLURAL if plural else TYPE_NAMES

    if field_type is None:
        return names[type(None)]

    if isUnion(field_type):
        return ' or '.join(describeType(arm, plural) for arm in typing.get_args(field_type))

    origin = typing.get_origin(field_type)
    arguments = typing.get_args(field_type)

    if origin is list:
        if arguments:
            return 'a list of %s' % describeType(arguments[0], plural=True)
        return names[list]

    if origin is dict:
        if arguments:
            return 'an object of %s' % describeType(arguments[1], plural=True)
        return names[dict]

    if field_type in names:
        return names[field_type]

    return '%s data' % field_type.__name__

def describeValue(value):
    """
    Describe a value found in the data in a way that can be read in an error
    message.

    Parameters
    ----------
    value:  any
        A value decoded from json.

    Returns
    -------
    string
    """

    name = TYPE_NAMES.get(type(value), 'a %s' % type(value).__name__)

    if value is None:
        return name

    text = repr(value)
    if len(text) > 40:
        text = text[:37] + '...'

    return '%s (%s)' % (name, text)

def checkType(value, field_type, path):
    """
    Check that `value` has type `field_type`, descending into lists, objects
    and nested models.

    Parameters
    ----------
    value:  any
        The value decoded from json.
    field_type: type
        The resolved type the schema declares for it.
    path:   string
        Where `value` sits in the data, used in any error raised.

    Returns
    -------
    void

    Raises
    ------
    ValidationError
        If `value` doesn't match `field_type`.
    """

    def fail():
        raise FieldTypeError(path, 'expected %s, found %s.'
                             % (describeType(field_type), describeValue(value)))

    if field_type is None or field_type is type(None):
        if value is not None:
            fail()
        return

    # A union matches if any one of its arms does.  Report the union as a
    # whole rather than the failure of each arm, which reads better for the
    # `x | None` unions the models use.
    if isUnion(field_type):
        for arm in typing.get_args(field_type):
            try:
                checkType(value, arm, path)
                return
            except ValidationError:
                continue
        fail()

    origin = typing.get_origin(field_type)
    arguments = typing.get_args(field_type)

    # For a list, there will be 0 or 1 arguments that will be either a single
    # type or a union of types.
    if origin is list:
        if not isinstance(value, list):
            fail()
        if arguments:
            for index in range(len(value)):
                checkType(value[index], arguments[0], '%s[%d]' % (path, index))
        return

    # For a dictionary, if there are arguments they represent the key and the
    # value type.
    if origin is dict:
        if not isinstance(value, dict):
            fail()
        if arguments:
            for key in value:
                checkType(key, arguments[0], '%s (key %r)' % (path, key))
                checkType(value[key], arguments[1], '%s.%s' % (path, key))
        return

    # Booleans are a subclass of int in python, but they are a separate type
    # in json, so neither may stand in for the other.
    if field_type is bool:
        if not isinstance(value, bool):
            fail()
        return

    if field_type is int:
        if isinstance(value, bool) or not isinstance(value, int):
            fail()
        return

    # Json makes no distinction between `2` and `2.0`, so a whole number is a
    # valid value for a field declared as a float.
    if field_type is float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            fail()
        return

    if not isinstance(value, field_type):
        fail()
