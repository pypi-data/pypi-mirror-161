from .basepackage import BasePackage
from .installer import Installer


class Package(BasePackage, Installer):
    def __init__(self, name, version, author=None, summary=None, description=None, license=None, author_email=None,
                 classifiers=None, homepage=None, keywords=None, index="https://pypi.org/simple"):
        BasePackage.__init__(self, name, version, author, summary, description, license, author_email, classifiers,
                             homepage, keywords)
        Installer.__init__(self, index)
