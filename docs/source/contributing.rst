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
