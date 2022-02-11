# Changelog

## [0.1.1] - 2022-02-12

**Mainly documentation improvements**

### Changed

- Make documentation publicly available under
  [kodaho.github.io/manen](<https://kodaho.github.io/manen/>).
- Complete `README.md` page.
- Add the section `About the project` in the documentation (moved from home page).
- Complete User Guide section.
- Rewording and reformatting of several sections.

## [0.1.0] - 2022-01-31

**First release of** `manen`

### Added

- `manen.finder.find` allows to easily get element(s) in a WebDriver
  page. This function support several very different use cases, thanks to several
  arguments that can be passed to the function.
- `manen.resource` is a module to easily interact with all the assets
  needed by Selenium. It allows for example to download the drivers, executable
  required to launch a WebDriver.
- `manen.browser` defined `manen.browser.ChromeBrowser`
  and `manen.browser.BraveBrowser`, an enhanced Selenium WebDriver.
- `manen.page_object_model` is the implementation of [page object
  modelling described in Selenium documentation](https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/).
  Thanks to that, you can describe and interact with the DOM structure through
  Python classes.
- a CLI is shipped with the initial release in order to download
  drivers files.
