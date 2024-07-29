About the project
=================

Why such package?
-----------------

The main motivation behind Manen is to provide a better developer experience when working on
browser automation and web scraping project. Most automation and scraping tools provide basic
methods to interact with the browser and with the DOM, but don't provide the structure to keep
the code clean and maintainable. Manen aims to be the interface between the core of the
automation tool (only Selenium is supported for now) and your tests and workflows logic; just
focus on your use case and let Manen handle the browser interactions.

The main answer to this objective is with the implementation of the Page Object Model design
pattern. This pattern is a way to organize your code by creating a class for each component of
your application, and to put all the interactions with the page in this class. Such classes
should be focus on the interactions with the page and not on the interactions with the DOM. The
latter is handled by Manen; you specify the selector and what you want to extract from each
element (the text, an integer, a date, the inner HTML), and Manen will do it for you. Special
objects like inputs also have their own Manen representation, so you can easily fill the value
in a Pythonic way. Besides, Manen provides what is called ``Browser``, which are basically a new
class based on Selenium WebDriver, but with some ameliorations and shortcuts.

Note that the design of the page object model implementation in Manen is fully based on type
annotations, largely inspired by Pydantic. This way, the developer experience is improved not
only during the runtime but also during the development, in your IDE.

Putting the page object model into practice isn't a new topic (quite old actually, Simon Stewart,
a lead in the Selenium project, wrote about it in 2009), but Manen aims to provide a modern and
Pythonic way to do it. Here are some articles and resources which inspired and drive the
development of the project:

* `Page object models, by Selenium <https://www.selenium.dev/documentation/en/guidelines_and_recommendations/page_object_models/>`_
* `Page Object, by Martin Fowler <https://martinfowler.com/bliki/PageObject.html>`_
* [in french] `Page Object Model : l'heure de la retraite ?, by Younup <https://www.younup.fr/blog/page-object-model-lheure-de-la-retraite>`_


Current status and roadmap
--------------------------

Manen is still in beta version, but it is already usable for some use cases. The solution Manen
aims to provide are implemented, but some elements can be missing before being fully usable. Some
improvements and features are already on the way (implement more DOM elements, compatibility with
other browser automation tools, etc.), all of them targeting the same objective: provide simple
yet powerful tools for browser automation.

If you are interested in the project, you can already use it and are more than welcome to provide
any feedbacks! You can use `GitHub issues <https://github.com/kodaho/manen/issues/>`_ to describe
your use case, your needs, or any bug you encountered. If you want to contribue to the project,
you can check the :ref:`Contributing` page of this documentation.

.. attention::

  Because Manen is still in beta, the API can change between minor versions. Keep an eye on the
  :ref:`Changelog` to see the changes between each release.
