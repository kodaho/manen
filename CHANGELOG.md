# CHANGELOG

## [0.1.0] - 2021-??
This is the first release of the package named `manen`. This package is still
in development. For now, the only supported webdriver is Chrome.
### Added
- `manen.finder.finder.find` allows to easily get element(s) in a Webdriver page.
  This function support several very different use cases, mainly parametrized
  with the function arguments.
- `manen.resource` is module to easily interact with all the assets
    needed by `selenium`. Thanks to that, all the drivers required by Selenium
    to work will no longer causes issues.
- `manen.navigator` defined `ChromeNavigator`, an enhanced
    Selenium's webdriver
- `manen.page_object_model` is the implementation of page object modelling,
  described in Selenium documentation. Thanks to that, you can describe the
  DOM structure only with Python objects.
- A first version of `manen`'s CLI is shipped with the initial release in order
  to complement tools provided in `manen.navigator`
- A full documentation of the package will help getting started with `manen`
