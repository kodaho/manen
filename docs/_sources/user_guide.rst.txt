User Guide
==========

This user guide section is designed to help you get the most out of Manen. It intends to be
accessible to beginners or advanced users, and to be as practical as possible, with concrete
examples and explanations.

Each one of the main feature of Manen is detailed in a separate guide:

#. a guide to get acquainted with the DOM exploration feature provided by
   :py:mod:`manen.finder.find`
#. a guide to understand the advantages of using a :py:class:`~manen.browser.ChromeBrowser`
   compared to a :py:class:`~selenium.webdriver.remote.webdriver.WebDriver`
#. a guide explaining how to use the page object model with Manen

Each guide can be read quite independently from each other, but it is advised to read them all to
have a good overview of all the features provided by Manen. Note that the guide on page object
model requires to be familiar with the `find` function, given that it is used behind the scenes.

Don't hesitate to copy the code examples, edit them and run them in your own environment to get
familiar with the library.

.. hint::

   All the user guides are available as notebooks on `GitHub <https://github.com/kodaho/manen/tree/main/
   docs/source/user_guide>`_. You can download them and run them locally to get a good start for
   playground environment.

These user guides can be completed with real-world examples available in the
`examples folder <https://github.com/kodaho/manen/tree/main/examples/>`_ of the source code
repository.

Getting familiar with Manen
---------------------------

.. toctree::
   :maxdepth: 2

   ./user_guide/dom_exploration
   ./user_guide/browser
   ./user_guide/page_object_model
