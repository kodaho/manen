About the project
=================

Why such package?
-----------------

Manen has been designed to keep every project using Selenium simple and to
speed up the development of these projects. Working with :py:mod:`selenium` can quickly
lead to non beautiful code because Selenium project often merge two functionalities:

#. **Browser interactions**: This part of the code is in charge of defining how to
   retrieve and interact with web elements. The retrieval is done with selectors
   (XPath, CSS, tag name...) and once you got the elements, the next step can be to
   extract some attributes from these elements (a text, an integer, a timestamp, an
   image, a form...).
#. **Workflow definition**: Clicking with some elements, filling a form, checking the
   value displayed: the logic here will implement the different pipelines to solve your
   specific use cases.

Manen helps for the first functionality, the browser interactions. Each
package have its own set of features:

- :py:mod:`~manen.finder` defines a helper function allowing to easily find one or
  several elements in a page.
- :py:mod:`~manen.page_object_model` implements a quite complete list of classes
  you can use to easily interact with the DOM structure; it is basically an
  implementation of the `page object model <https://www.selenium.dev/documentation/en/
  guidelines_and_recommendations/page_object_models/>`_
  described in official documentation of Selenium.
- :py:mod:`~manen.browser` defines new browser classes by enriching Selenium
  :py:class:`~selenium.webdriver.remote.webdriver.WebDriver` with a
  :py:mod:`~manen.browser.BrowserMixin`.

At the end, Manen can be used for various use cases: testing, heavy process
automation or scraping. Note that the goal behind Manen is to have a
production-ready tool.


Current status and roadmap
--------------------------

Manen is still under active development but has been used on some private projects
for quite a time.

Feebacks are more than welcome so don't hesitate to open a Github issue if you
have any questions or concerns about the project!

Because manen uses `semantic versioning <https://semver.org>`_, it will keep 0
as major version until it is ready for the first stable release.

.. note:: There is no guarantee that the API will remain the same. The current
   architecture is probably the definitive one, but some breaking changes can
   be introduced if needed. Any change will be detailed in the ChangeLog page.

No roadmap because it is still a "side project" but you can follow the project through
this documentation and Github's issues.

See :ref:`Contributing` if you want to participate to this project.
