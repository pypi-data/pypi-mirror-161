Quickstart
==========

This page gives a quickstart guide to the basic features of the library.
It assumes you have the library already installed. If not, check the :doc:`installation`
portion.

A minimal example
-----------------
This will showcase a simple example and show the basic usage of the library.

.. code-block:: python

    import apip
    import asyncio

    client = apip.Client()
    package = asyncio.run(client.get_package('apip'))
    print(package.name)
    print(package.summary)
    print(package.version)
    package.install()

Let’s name this file example.py. Make sure not to name it apip.py as that’ll conflict with the library.

Here's what happens when you run this file:

.. code-block:: shell

    $ python3 apip.py
    apip
    An API wrapper for Pip and PyPi.
    0.0.1

or on Windows:

.. code-block:: shell

    $ py -3 apip.py
    apip
    An API wrapper for Pip and PyPi.
    0.0.1

Here's how it works:

1. The first line just imports the library. If this raises a
   `ModuleNotFoundError` or `ImportError`, you probably haven't installed the library yet.
   Check the :doc:`installation` section.
2. The second line creates a instance of a :ref:`Client`. This is used to interact
   with the PyPi API.
3. Next, we use the client to get the `apip` package through the PyPi API.
   this is a coroutine, so we need to use `asyncio.run` to run it.
   The result is a :ref:`Package` object.
4. We then print the name, summary, and version of the package.
5. Finally we use the `install` method to install the package.

Now, you can try playing around with your example.