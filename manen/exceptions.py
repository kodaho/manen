"""
manen.exceptions
================

Exceptions raised by :py:mod:`manen`.
"""


class ManenException(Exception):
    """Basic exception."""


class DriverNotFound(ManenException):
    """Can not find a driver executable used by the web drivers."""


class ElementNotFound(ManenException):
    """Can not find inside a specific container an element matching the selectors."""

    def __init__(self, selectors, driver):
        super().__init__()
        self.selectors = selectors
        self.context = {
            "title": driver.title,
            "current_url": driver.current_url,
        }

    def __str__(self):
        selectors_as_list = "\n".join(
            ["> {}".format(selector) for selector in self.selectors]
        )
        context_string = (
            "\n\nContext of the exception:\n"
            + "- Title page: {}\n".format(self.context["title"])
            + "- URL: {}".format(self.context["current_url"])
        )
        return (
            "Unable to find inside document an element matching the "
            "selectors :\n{}".format(selectors_as_list)
        ) + context_string


class PlatformNotRecognized(ManenException):
    """Can not clearly identify the platform running the code."""

    def __init__(self, platform):
        super().__init__()
        self.platform = platform

    def __str__(self):
        return 'The platform "{}" is not recognized.'.format(self.platform)


class UnsettableElement(ManenException):
    """Cannot set a value to an instance of
    :py:class:`manen.page_object_model.Element`.
    """

    def __init__(self, class_name):
        super().__init__()
        self.class_name = class_name

    def __str__(self):
        return "{} is a web element which cannot be set.".format(self.class_name)
