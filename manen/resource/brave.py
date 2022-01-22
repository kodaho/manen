from .chrome import application as chrome_app, driver


class application(chrome_app):
    BINARIES = {
        "Darwin": "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    }
