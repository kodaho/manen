# CHANGELOG

## WIP
- Compatibility with Selenium core features:
    - https://www.browserstack.com/guide/selenium-grid-tutorial
    - https://www.selenium.dev/downloads/
    - https://www.browserstack.com/guide/selenium-webdriver-tricks

## [0.1.0] - 2020-04
This is the first release of the package named `manen`. This package is still
in development. For now, the only webdriver you can work with is Chrome.
### Added
- Add `manen.finder.find` function to easily get element(s) in a Webdriver page
    of `selenium` element.
- Add `manen.resource` module to easily interact with all the assets
    needed by `selenium`
- Add `manen.navigator` module which `Navigator` object (an enhanced
    Selenium's webdriver)
- Add `manen.dom` module which defines several objects to build `Page`
    objects (which ease the way to work with Selenium)
- Add first version of `manen`'s CLI.
