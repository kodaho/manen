# CHANGELOG

## [0.1.0] - 2022-02-??
This is the first release of `manen`. At this moment, the package is still
under development and so the public API might changed in the future.
### Added
- `manen.finder.find` allows to easily get element(s) in a Webdriver page.
  This function support several very different use cases, mainly parametrized
  with the function arguments.
- `manen.resource` is a module to easily interact with all the assets
    needed by `selenium`. Thanks to that, all the drivers required by Selenium
    to work will no longer causes issues.
- `manen.navigator` defined `ChromeNavigator`, an enhanced
    Selenium's webdriver
- `manen.page_object_model` is the implementation of page object modelling,
  described in Selenium documentation. Thanks to that, you can describe the
  DOM structure only with Python objects.
- a CLI is shipped with the initial release in order to perform operations such
  as downloading webdriver
