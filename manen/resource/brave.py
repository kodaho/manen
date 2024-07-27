"""
manen.resource.brave
====================
"""

from .chrome import application as chrome_app
from .chrome import driver

__all__ = ("application", "driver")


class application(chrome_app):
    BINARIES = {
        "Darwin": "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    }
