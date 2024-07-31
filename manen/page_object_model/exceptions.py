from manen.exceptions import ManenException


class TypeConfigError(TypeError, ManenException):
    def __init__(self, field, types):
        self.field = field
        self.types = types

    def __str__(self):
        return (
            f"Field '{self.field}' should have exactly one non-None type in its annotation, but "
            f"get {self.types}"
        )


class SelectorConfigError(ValueError, ManenException):
    def __init__(self, field):
        self.field = field

    def __str__(self):
        return f"At least one selector should be specified in the annotation of '{self.field}'"
