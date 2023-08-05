class PipException(Exception):
    """
    A base class for apip exceptions.
    """
    pass


class ConnectionException(PipException):
    """
    An exception raised when the API could not access the server.
    """
    pass


class PackageException(PipException):
    """
    A base exception for package errors.
    """
    pass


class PackageNotFoundException(PackageException):
    """
    An exception that is raised when the API could not find the package.
    """
    pass


class VersionNotFoundException(PackageException):
    """
    An exception raised when the version is not available for the specified package.
    """
    pass
