from .abc.basepackage import BasePackage
from .abc.installer import Installer
from .abc import errors
import asyncio


class Package(BasePackage, Installer):
    def __init__(
        self,
        name,
        version,
        author=None,
        summary=None,
        description=None,
        license=None,
        author_email=None,
        classifiers=None,
        homepage=None,
        keywords=None,
        index="https://pypi.org/simple",
    ):
        BasePackage.__init__(
            self,
            name,
            version,
            author,
            summary,
            description,
            license,
            author_email,
            classifiers,
            homepage,
            keywords,
        )
        Installer.__init__(self, index)

    async def install(self):
        """
        Installs itself through the Pip API. Returns itself.

        :return: A Package object for the installed package.
        :rtype: Package
        :raises PackageNotFoundException: The package was not found.
        :raises self.VersionNotFoundException: The version was not found.
        :raises ConnectionException: The connection to PyPi was unsuccessful.
        """
        version = f"=={self.version}" if self.version else ""
        command = f"pip install --index-url {self.index} {self.name}{version}"
        out = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )  # we won't actually use stdout, it just stops it from printing to the console
        out = await out.communicate()
        self._err_checking(out[1].decode(), self.name, self.version)
        return self

    async def uninstall(self):
        """
        Uninstalls itself through the Pip API.

        :raises PackageNotFoundException: The package was not found.
        """
        out = await asyncio.create_subprocess_shell(
            f"pip uninstall {self.name} -y",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )  # we won't actually use stdout, it just stops it from printing to the console
        out = await out.communicate()
        out = out[1].decode()
        invalid_package = f"WARNING: Skipping {self.name} as it is not installed."
        if invalid_package in out:
            raise errors.PackageNotFoundException(f"{self.name} is not installed!")
        return self
