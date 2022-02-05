About the project
=================

Why such package?
-----------------

Design to be be simple and speed up your development with Selenium.
Hide complexity to work with Selenium.

It was originally built to have faster development process when using Selenium. Working with
Selenium often requires to have a source code having two functionalities:

- the first one is relative to the interactions with the browser, materialized with the
  WebDriver. Here, you need to define how you will retrieve the elements in the DOM, manage
  exceptions if an element is not found... You should specify selectors that can evolve
  through times.
- second element is your custom workflow: click here, retrieve this element, fill this form

``manen`` = a solution for the first point (and only the first point)

It can be used to design applications for testing, heavy process automatisation or legal scraping. Note that the goal behind `manen` is to have a production-ready tool, not to develop a package that can only be used locally.

Among the features, you will find:

- a helper tool to find and download all drivers needed by Selenium; no need to
  find the right driver compatible with the installed browser, :py:mod:`manen`
  will do it for you!
- a quite complete list of classes you can use to easily interact with the DOM
  structure: it is basically an implementation of the
  `page object model <https://www.selenium.dev/documentation/en/guidelines_and_recommendations/page_object_models/>`_)
  described in official documentation of Selenium.
- an enhanced WebDriver, build around the one defined by Selenium, allowing you
  to perform some basic actions quite quickly.

.. admonition:: Where does the name come from?
   :class: note

   An explanation about the name...


Current status and roadmap
--------------------------

:py:mod:`manen` is still under active development but has been used on some
private projects for quite a time.

Feebacks are more than welcome so don't hesitate to open a Github issue if you
have any questions or concerns about the project!

Because manen uses `semantic versioning <https://semver.org>`_, it will keep 0
as major version until it is ready for the first stable release.

.. note:: There is no guarantee that the API will remain the same. The current
   architecture is probably the definitive one, but some breaking changes can
   be introduced if needed. Any change will be detailed in the ChangeLog page.

No roadmap because it is still a "side project" but you can follow the project through this
documentation and Github's issues.

See :ref:`Contributing` if you want to participate to this project.
