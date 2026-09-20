from __future__ import annotations

import types

from game.library.validation.errors import (
    FieldTypeError, InvalidValueError, MissingFieldError, UnexpectedFieldError
)
from game.library.validation.check_type import (
    checkType, describeValue
)


class Validator:
    """
    The schema for a single json field, built by chaining the checks its value
    must pass.

    Attributes
    ----------
    checks: list[callable]
        The checks to run against the field's value, in the order they were
        added.  Each is called as `check(value, path)` and raises a
        `ValidationError` if the value doesn't pass.
    is_required:    boolean
        Whether the field must be present in the data.  Set by `isRequired`,
        and read by whoever is walking the data, since `validate` only ever
        sees values that are there.  Fields are optional until marked.
    """

    def __init__(self):
        self.checks = []
        self.is_required = False

    def check(self, check):
        """
        Add a check to run against the field's value.

        The building block the other builder methods are written in terms of,
        and the way to attach a one off check that doesn't warrant a builder
        method of its own.

        Parameters
        ----------
        check:  callable
            Called as `check(value, path)`, raising a `ValidationError` if the
            value doesn't pass.  Its return value is ignored.

        Returns
        -------
        Validator: `self`, so that checks may be chained.
        """

        self.checks.append(check)
        return self

    def isRequired(self):
        """
        The field must be present in the data.

        Sets `is_required` rather than adding a check, since an absent field
        never reaches `validate`.

        Returns
        -------
        Validator: `self`, so that checks may be chained.
        """

        self.is_required = True
        return self

    def isType(self, field_type):
        """
        The field's value must have type `field_type`.

        Parameters
        ----------
        field_type: type | callable
            The type, written the way the model's type hint for the field is
            written.  Eg. `str`, `float`, `list[str]`, `dict[str, str]`,
            `str | None` for a value that may be null, or another model class
            for a nested object, which is validated against its own schema.

            A model that has not been defined yet may be named by a function
            returning the type, as in `lambda: list[Item]`, which is not
            called until the value is validated.

        Returns
        -------
        Validator: `self`, so that checks may be chained.
        """

        def check(value, path):
            checkType(value, resolveType(field_type), path)

        return self.check(check)

    def isOneOf(self, allowed):
        """
        The field's value must be one of `allowed`.

        Parameters
        ----------
        allowed:    list
            Every value the field may hold.

        Returns
        -------
        Validator: `self`, so that checks may be chained.
        """

        def check(value, path):
            if value not in allowed:
                raise InvalidValueError(path, 'expected one of %s, found %s.'
                                        % (', '.join(repr(option) for option in allowed),
                                           describeValue(value)))

        return self.check(check)

    def validate(self, value, path='value'):
        """
        Run this field's checks against `value`.

        Parameters
        ----------
        value:  any
            The value decoded from json.
        path:   string
            Where `value` sits in the data, used in any error raised.

        Returns
        -------
        True
            If `value` passes every check.  Never returns anything else; a
            value that fails raises.

        Raises
        ------
        ValidationError
            From the first check `value` fails.
        """

        for check in self.checks:
            check(value, path)

        return True


# TODO TECHDEBT This allows us to reference types in checks that haven't been
# defined yet to avoid definition loops or import loops. It's pretty hacky and
# there's surely a better way to do this.
def resolveType(field_type):
    """
    Resolve a type that was deferred behind a function, so that a schema may
    refer to a model that has not been defined yet.

    Parameters
    ----------
    field_type: type | callable
        The type to resolve.  Returned unchanged unless it is a function, in
        which case the function is called and its result returned.

    Returns
    -------
    type
    """

    if isinstance(field_type, types.FunctionType):
        return field_type()

    return field_type


def validateModel(model, data, path=None):
    """
    Validate json data against the schema `model` declares.

    Walks the schema, skipping optional fields that are absent, running each
    present field's validator against its value, and finally checking that the
    data carries nothing the schema has no place for.

    Parameters
    ----------
    model:  type
        The model class whose `SCHEMA` the data is checked against.
    data:   dict
        The json data to check.
    path:   string | None
        Where `data` sits within a larger structure, used in any error raised.
        Defaults to the model's name, which is what it should be when the
        model is the outermost one being validated.

    Returns
    -------
    True
        If `data` is valid.  Never returns anything else; invalid data raises.

    Raises
    ------
    ValidationError
        If `data` doesn't match the schema.
    """

    if path is None:
        path = model.__name__

    schema = model.SCHEMA

    if not isinstance(data, dict):
        raise FieldTypeError(path, 'expected %s data, found %s.'
                             % (model.__name__, describeValue(data)))

    for name in schema:
        validator = schema[name]

        if name not in data:
            if validator.is_required:
                raise MissingFieldError('%s.%s' % (path, name),
                                        '%s requires this field.' % model.__name__)
            continue

        validator.validate(data[name], '%s.%s' % (path, name))

    for name in data:
        if name not in schema:
            raise UnexpectedFieldError('%s.%s' % (path, name),
                                       '%s has no such field.' % model.__name__)

    return True
