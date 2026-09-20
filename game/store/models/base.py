from __future__ import annotations

import os
import json

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from game.library.validation.validator import Validator


class JsonSerializable:
    'An object that may be serialized to JSON for storage in the filesystem.'

    # The json fields that will be serialized, with their validators.
    SCHEMA: ClassVar[dict[str, Validator]] = {}

    def __init__(self):
        pass

    def validate(self, data) -> bool:
        """
        Validate that `data` is valid serialized data for this serializable.

        Parameters
        ----------
        data:   dict
            The json data to validate

        Returns
        -------
        True
            If `data` is valid.

        Raises
        ------
        ValidationError
            If `data` does not match `SCHEMA`.
        """

        return True

    def toJson(self):
        """
        Convert this object to JSON for storage.

        Returns
        -------
        dict
            A dictionary containing the json data that can be directly written
            as JSON.
        """

        return {}

    def fromJson(self, data):
        """
        Convert this object from JSON to load it from storage. Takes a
        dictionary loaded directly from the JSON and loads it into this object.

        Parameters
        ----------
        data:   dict
            The json data loaded from file.

        Returns
        -------
        self
            A self reference to enable chaining.
        """

        return self


class Model(JsonSerializable):

    def __init__(self):
        self.id = ''

    def getId(self):
        return self.id

    def setId(self, id):
        self.id = id
        return self

    def save(self, base_path='data/'):
        if not os.path.exists(base_path):
            os.mkdir(base_path)

        filename = ''
        if isinstance(self.id, int):
            filename = base_path + str(self.id) + '.json'
        elif isinstance(self.id, str):
            filename = base_path + self.id + '.json'
        else:
            raise TypeError('Invalid id type.')

        file = open(filename, 'w')
        try:
            json.dump(self.toJson(), file)
        finally:
            file.close()

        return self

    def load(self, file_path):
        file = open(file_path, 'r')
        try:
            self.fromJson(json.load(file))
        finally:
            file.close()

        return self


class NamedModel(Model):

    def __init__(self):
        super(NamedModel, self).__init__()
        self.name = ''

    def setId(self, id):
        self.id = id
        self.name = id
        return self
