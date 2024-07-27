class Action:
    """Enable to interact with an input by calling a method of the WebElement. This is
    intended to be used by a subtype of :py:class:`~manen.page_object_model.Element`
    which can be set.

    Example::

        >>> page.query = "python manen"
        >>> page.query = Action("submit")
    """

    def __init__(self, method: str, *args, **kwargs):
        """
        Args:
            method (str): name of the method to call. This should be a method ones
                of a method of :py:class:`selenium.webdriver.remote.webelement.WebElement`
            *args (Any): positional arguments called with the method
            **kwargs : keyword arguments called with the method
        """
        self.method = method
        self.args = args
        self.kwargs = kwargs
