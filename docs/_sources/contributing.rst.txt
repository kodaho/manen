Contributing
============

Manen is an open-source package meaning that you can contribute to the source code in order to
add new features, fix bugs.

Reproducing a development environment
-------------------------------------

Manen has been developed with Python 3.10, using rye as project manager. If you want to
contribute, you can fork the GitHub repository, and then spawn a development environment with the
following command (make sure that `rye is installed <https://rye.astral.sh/guide/installation/>`_
first):

.. code-block:: bash

    $ rye sync

.. note::

   Building the documentation requires `Pandoc <https://pandoc.org/>`_, a universal document
   converter. The instructions to install it are `here <https://pandoc.org/installing.html>`_.


If you want to include your modifications in the main repository, you can then open a pull
request.
