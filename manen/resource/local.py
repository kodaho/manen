"""
manen.resource.local
====================
"""

from pathlib import Path
from typing import Optional

from ..exceptions import DriverNotFound
from ..helpers import PLATFORM_SYS


class LocalAsset:
    PATH = Path(__file__).parents[1] / "assets/drivers"

    @classmethod
    def list_drivers(
        cls,
        browser: str,
        os: Optional[str] = PLATFORM_SYS,
        version: Optional[str] = None,
    ):
        if os is None:
            os = "*"
        version = "*" if version is None else f"{version}*"
        drivers = list((cls.PATH / os.lower() / browser).glob(f"{version}/*"))
        if drivers:
            return [
                {
                    "path": str(path),
                    "version": path.parent.stem,
                    "browser": path.parents[1].stem,
                    "os": path.parents[2].stem,
                }
                for path in drivers
            ]
        raise DriverNotFound(
            'No driver found matching the query browser="{}", '.format(browser)
            + 'platform="{}" and version="{}".'.format(os, version)
        )
