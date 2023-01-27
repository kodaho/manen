# Changelog

## [0.2.1] - (unreleased)

### Changed
- `download` CLI command no longer raise an error if a browser is not installed.
- Allow browser version to have only major and minor components.

### Fixed
- Fix listing of available Chromedriver versions to return most recent ones.


## [0.2.0] - 2022-02-19

### Changed

- Improve CLI command to download drivers executable (now launched with `manen driver download`).
- Rename `manen.page_object_model.DateTimeElement` (previously `DatetimeElement`).
- Rename `manen.page_object_model.DOMAccessor` (previously `DomAccessor`).

### Fixed

- Fix link to notebooks in the info section of User Guide

### Added

- Specify link to changelog in documentation in package metadata.
- Introduce new options in `manen driver download` to set the specifications of the drivers
  to be downloaded directly from the command line.
- Add exhaustivity in documentation of `manen.page_object_model` to describe
  private/special methods and classes other than the ones in `__all__`.

## [0.1.2] - 2022-02-19

**Fix bug in the download workflow of the CLI**

### Fixed

- Fix a `TypeError` in the download workflow (variable wrongly named)


## [0.1.1] - 2022-02-12

**Mainly documentation improvements**

### Changed

- Make documentation publicly available under
  [kodaho.github.io/manen](<https://kodaho.github.io/manen/>).
- Complete `README.md` page.
- Add the section `About the project` in the documentation (moved from home page).
- Complete user guides.
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
