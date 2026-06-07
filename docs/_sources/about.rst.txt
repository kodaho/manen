About the project
=================

Why such package?
-----------------

Manen exists to make browser automation and web scraping a better experience. Most tools offer
only basic methods to interact with the browser and the DOM, leaving you without the structure
needed to keep your code clean and maintainable. Manen sits between the automation core (only
Selenium for now) and your tests and workflows, so you can focus on your use case and let it
handle the browser interactions.

At its heart is the Page Object Model design pattern: you create one class per component of your
application and gather all of its page interactions there. Those classes stay focused on the
page, while Manen takes care of the DOM. You simply declare a selector and what to extract from
each element (its text, an integer, a date, the inner HTML), and Manen does the rest. Special
elements such as inputs also have their own representation, so you can fill in values the
Pythonic way. Manen further ships a ``Browser`` class, built on the Selenium WebDriver but with
added improvements and shortcuts.

This Page Object Model implementation is driven entirely by type annotations, largely inspired by
Pydantic, which improves the developer experience both at runtime and while coding in your IDE.

The Page Object Model is hardly new; Simon Stewart, a lead on the Selenium project, wrote about
it back in 2009, but Manen brings a modern, Pythonic take. The following articles and resources
inspired and guide the project:

* `Page object models, by Selenium <https://www.selenium.dev/documentation/en/guidelines_and_recommendations/page_object_models/>`_
* `Page Object, by Martin Fowler <https://martinfowler.com/bliki/PageObject.html>`_
* [in french] `Page Object Model : l'heure de la retraite ?, by Younup <https://www.younup.fr/blog/page-object-model-lheure-de-la-retraite>`_


Current status
--------------

Manen is still in beta, yet already usable for many cases. Its core solutions are in place, and
more features can still be added: support for backends other than Selenium, interactivity with
more DOM elements...
