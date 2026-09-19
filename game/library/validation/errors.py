class ValidationError(Exception):
    """
    Raised when json data does not match the schema of the model it is being
    loaded into.

    Attributes
    ----------
    path:   string
        Where in the data the problem is, as a dotted path rooted at the model
        being validated.  Eg. `Item.traits.Harvestable.products[0].amount`.
    message:    string
        What is wrong with the data at `path`.
    """

    def __init__(self, path, message):
        self.path = path
        self.message = message

        super(ValidationError, self).__init__('%s: %s' % (path, message))


class MissingFieldError(ValidationError):
    'A field the model requires is absent from the data.'


class UnexpectedFieldError(ValidationError):
    'The data carries a field that the model has no place for.'


class FieldTypeError(ValidationError):
    "A field's value is not of the type the model declares for it."


class InvalidValueError(ValidationError):
    "A field's value is the right type, but not one the model allows."
