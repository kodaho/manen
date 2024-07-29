"""Testing that Python can effectively read all the source code and that the
structure of the package is correct.
"""

from importlib import import_module
from pkgutil import iter_modules

import pytest


def get_all_modules(package_name: str) -> list[str]:
    """Retrieve all the modules and packages from a given package. This is a
    recursive function meaning that the sub-packages will also be inspected.

    Args:
        package_name (str): the name of the parent package to inspect
    Returns:
        list[str]: list of all sub-packages/modules.
    """
    output = [package_name]
    package = import_module(package_name)
    for _, child, is_package in iter_modules(package.__path__):
        if is_package:
            output.extend(get_all_modules(f"{package_name}.{child}"))
        else:
            output.append(f"{package_name}.{child}")
    return output


@pytest.mark.parametrize("module_name", get_all_modules("manen"))
def test_able_to_import(module_name):
    """Test that a Manen module can be correctly imported."""
    assert import_module(module_name)
