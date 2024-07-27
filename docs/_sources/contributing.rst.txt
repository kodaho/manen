Contributing
============

``manen`` is an open-source package meaning that you can contribute to the source
in order to add new features, fix bugs. The progress of the project will be tracked
directly in Github through issues. If you found any bug, don't hesitate to open an
issue (if one isn't opened yet about the same bug) or/and open a pull request.

Reproducing a development environment
-------------------------------------

``manen`` has been developed with Python 3.10, using rye as project manager. If you
want to contribute to ``manen``, you can reproduce a development environment with the
following command (make sure you have `rye installed <https://rye.astral.sh/guide/installation/>`_
first):

.. code-block:: bash

    $ rye sync --all-features

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

        **Build the documentation**

        .. code-block:: bash

            $ cd docs && make html

        **Trigger a build of the documentation for any changes in the source**

        `sphinx-autobuild <https://pypi.org/project/sphinx-autobuild/>`_ can be used to launch
        a process that will watch any modification in the source files of the package or
        documentation and re-build the HTML pages at each event.

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
