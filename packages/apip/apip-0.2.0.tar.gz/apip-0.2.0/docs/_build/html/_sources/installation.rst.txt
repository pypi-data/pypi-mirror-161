Installation
========================
This page will guide you through the installation of the library.


Requirements
----------------

apip requires Python 3.8 to work properly. It is not compatible with
older versions of Python, such as Python 3.7 and Python 2.7.

Installing
----------------

The simplest way to install the library is to use pip:
.. code-block:: shell

    $ python3 -m pip install apip

If you are using Windows, then the following command should be used.
.. code-block:: shell

    $ py -3 -m pip install apip

Using Virtual Environments
----------------------------
Sometimes you don't want your main Python installation to be cluttered,
and isolate some packages from other projects. You also might not have
permissions to install system-wide packages. Because of this, the
standard library comes with a concept called virtual environments
to maintain these seperate versions.

A more in-depth tutorial is found on :doc:`py:tutorial/venv`.

However, for the quick and dirty:

1. Go to your project's working directory:

    .. code-block:: shell

        $ cd your-bot-source
        $ python3 -m venv bot-env

2. Activate the virtual environment:

    .. code-block:: shell

        $ source bot-env/bin/activate

    On Windows you activate it with:

    .. code-block:: shell

        $ bot-env\Scripts\activate.bat

3. Use pip like usual:

    .. code-block:: shell

        $ (venv) pip install -U apip

Congratulations. You now have a virtual environment all set up.
