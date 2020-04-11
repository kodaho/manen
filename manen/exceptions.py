from selenium.webdriver.remote.webdriver import WebDriver


class ManenException(Exception):
    pass


class BrowserNotSupported(ManenException):
    def __init__(self, browser):
        super().__init__()
        self.browser = browser

    def __str__(self):
        return "The browser {} is not supported by the current of Navigator.".format(
            self.browser.upper()
        )


class DriverNotFound(ManenException):
    pass


class ElementNotFound(ManenException):
    def __init__(self, selectors, inside):
        super().__init__()
        self.selectors = selectors
        driver = inside if isinstance(inside, WebDriver) else inside.parent
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


class NavigatorNotDefined(ManenException):
    def __str__(self):
        return "No navigator has been defined to be used by the page object."


class PlatformNotRecognized(ManenException):
    def __init__(self, platform):
        super().__init__()
        self.platform = platform

    def __str__(self):
        return 'The platform "{}" is not recognized.'.format(self.platform)


class UnsettableElement(ManenException):
    def __init__(self, class_name):
        super().__init__()
        self.class_name = class_name

    def __str__(self):
        return "{} is a web element which cannot be set.".format(self.class_name)


class BadConfiguration(ManenException):
    pass


class UnknownSelectionMethod(ManenException):
    pass


class ElementNotVisible(ManenException):
    pass


class PageNotRecognized(ManenException):
    pass
