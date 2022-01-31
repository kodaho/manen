"""
manen.resource.local
====================
"""

from pathlib import Path
from typing import Optional

from ..exceptions import DriverNotFound
from ..helpers import PLATFORM


class LocalAsset:
    PATH = Path(__file__).parents[1] / "assets/drivers"

    @classmethod
    def list_drivers(
        cls,
        browser: str,
        platform_system: Optional[str] = PLATFORM.system,
        version: Optional[str] = None,
    ):
        if platform_system is None:
            platform_system = "*"
        version = "*" if version is None else f"{version}*"
        drivers = list(
            (cls.PATH / platform_system.lower() / browser).glob(f"{version}/*")
        )
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
            + 'platform="{}" and version="{}".'.format(platform_system, version)
        )
