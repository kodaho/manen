class ManenException(Exception):
    pass


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
        selectors_as_list = "\n".join([f"> {selector}" for selector in self.selectors])
        context_string = (
            "Context of the exception:\n"
            + f"- Title page: {self.context['title']}\n"
            + f"- URL: {self.context['current_url']}"
        )
        return (
            f"Unable to find an element matching the selectors:\n{selectors_as_list}"
            "\n"
            f"{context_string}"
        )


class PollTimeoutException(TimeoutError, ManenException):
    pass
