User Guide
==========

.. todo::

    Write `User Guide` documentation


Start working with ``manen``
----------------------------

Manage resource with the CLI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use `Navigator`, an enhanced `WebDriver`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Easily find what you are looking for
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Advanced Usage
--------------

Manage all your driver assets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Make a clear distinction between how to select and what to select
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. tab:: selectors.yaml

    .. code-block:: yaml

        name: Blog
        meta:
            url: blog.manen.co
        articles:
            selectors: article
            elements:
                title: h1
                n_likes: span.n_likes
                tags:
                    - span.tags
                    - span.themes   # Backup if span.tags doesn't work
                updated_at: p.date


.. tab:: page_pom.py

    .. code-block:: python

        from manen import page_object_model as pom

        class BlogPage(pom.Page):
            class Articles(pom.Regions):
                title = pom.TextElement()
                n_likes = pom.IntegerElement()
                tags = pom.TextElements(default=[])
                updated_at = pom.DateElement()
            articles = Articles()
