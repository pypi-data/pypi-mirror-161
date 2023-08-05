.. currentmodule:: apip

API Reference
===============

The following section outlines the API of apip.

Version Related Info
---------------------

.. data:: __version__

    A string representation of the version. e.g. ``'1.0.0rc1'``. This is based
    off of :pep:`440`.

Client
--------

.. attributetable:: Client

.. autoclass:: Client
    :members:

.. _package:

Package
--------

.. attributetable:: Package

.. autoclass:: Package
    :members:

Exceptions
------------

The following exceptions are thrown by the library.

.. autoexception:: apip.errors.PipException
    :members:
    :show-inheritance:

.. autoexception:: apip.errors.ConnectionException
    :members:
    :show-inheritance:

.. autoexception:: apip.errors.PackageException
    :members:
    :show-inheritance:

.. autoexception:: apip.errors.PackageNotFoundException
    :members:
    :show-inheritance:

.. autoexception:: apip.errors.VersionNotFoundException
    :members:
    :show-inheritance:

Exception Hierarchy
~~~~~~~~~~~~~~~~~~~~~

.. exception_hierarchy::

    - :exc:`Exception`
        - :exc:`apip.errors.PipException`
            - :exc:`apip.errors.ConnectionException`
            - :exc:`apip.errors.PackageException`
                - :exc:`apip.errors.PackageNotFoundException`
                - :exc:`apip.errors.VersionNotFoundException`