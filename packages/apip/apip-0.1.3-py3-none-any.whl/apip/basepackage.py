import dataclasses


@dataclasses.dataclass(frozen=True)
class BasePackage:
    """
    A base class for the Package class.

    :param name: The name of the package.
    :type name: str
    :param version: The version of the package.
    :type version: str
    :param author: The author of the package.
    :type author: str
    :param description: The description of the package.
    :type description: str
    :param license: The license of the package.
    :type license: str
    :param author_email: The email of the package's author.
    :type author_email: str
    :param classifiers: The classifiers of the package.
    :type classifiers: list
    :param homepage: The homepage of the package.
    :type homepage: str
    :param keywords: The keywords specified in the package.
    :type keywords: list
    :attr name: The name of the package.
    :attr version: The version of the package.
    """
    name: str
    version: str
    author: str = None
    summary: str = None
    description: str = None
    license: str = None
    author_email: str = None
    classifiers: list = None
    homepage: str = None
    keywords: list = None