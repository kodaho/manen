Contributing
============

``manen`` is an open-source package meaning that you can contribute to the source
in order to add new features, fix bugs. The progress of the project will be tracked
directly in Github through issues. If you found any bug, don't hesitate to open an
issue (if one isn't opened yet about the same bug) or/and open a pull request.

Reproducing a development environment
-------------------------------------

``manen`` has been developed with Python 3.8, using Pipenv to manage the development
environment. If you want to help in the development of ``manen``, reproducing a dev
environment similar to the original one will be needed. To do so, you can whether
use Pipenv to recreate the environment with the command

.. code-block:: bash

    $ pipenv sync

Note that using Pipenv is not required. You can reproduce the development environment
by re-installing the same package specified in the setup file of the package

.. code-block:: bash

    $ pip install -e ".[doc,test,lint]"

This will install ``manen`` with extra dependencies for development workflows, described
in the next section.

Note that building the documentation will require to install `Pandoc <https://pandoc.org/>`_,
a universal document converter. All the instructions to do so can be found
`here <https://pandoc.org/installing.html>`_.


Development workflows
---------------------

Besides the core for the core of ``manen``, several workflows exists to document the code and
ensure code quality. Each workflow requires some dependencies which can be installed as extra
with ``pip``, with the command ``pip install -e .[{extra}]``.

Documentation
    Extra pip options: ``doc``

    Workflow used to build HTML pages for the documentation

    .. admonition:: Command
        :class: seealso

        **Build the documentation in one shot**

        .. code-block:: bash

            $ cd docs && make html

        **Build the documentation at any modifications**

        .. code-block:: bash

           $ pip install sphinx-autobuild
           $ sphinx-autobuild docs/source docs/build/html --watch manen/


Testing
    Extra pip options: ``test``

    Workflow that will run tests for the whole package.

    .. admonition:: Command
        :class: seealso

        **Launching all the tests**

        .. code-block:: bash

           $ pytest


Linting
    Extra pip options: ``lint``

    Workflow to ensure some syntaxical quality for the source code.

    .. admonition:: Command
        :class: seealso

        **Checking tha the imports are well sorted**

        .. code-block:: bash

            $ isort --check-only manen/

        **Linting all the files**

        .. code-block:: bash

            $ pylint -E --rcfile=./.pylintrc ./manen/
