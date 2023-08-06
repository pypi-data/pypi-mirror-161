from .. import package
from . import errors
import asyncio
import aiohttp


class Installer:
    """
    A base class for installing packages from PyPi.

    :param index: The URL of the PyPi index.
    :type index: str
    """

    def __init__(self, index="https://pypi.org/simple"):
        self.index = index

    async def _get(self, pkg, version=None):
        """
        Returns a Package object for a given package name. Queries data from the PyPi API.

        :param pkg: The name of the package to get.
        :type pkg: str
        :param version: The version of the package to get.
        :type version: str
        :return: A Package object for the given package.
        :rtype: Package
        :raises PackageNotFoundException: The package was not found.
        """
        version = f"/{version}" if version else ""
        async with aiohttp.ClientSession() as client:
            async with client.get(
                f"https://pypi.org/pypi/{pkg}{version}/json"
            ) as response:
                if response.status == 404:
                    raise errors.PackageNotFoundException(
                        f"{pkg} is not a valid package!"
                    )
                data = await response.json()
                if data == {"message": "Not Found"}:
                    raise errors.PackageNotFoundException(
                        f"{pkg} is not a valid package!"
                    )
                return package.Package(
                    data["info"]["name"],
                    data["info"]["version"] if not version else version,
                    data["info"]["author"],
                    data["info"]["summary"],
                    data["info"]["description"],
                    data["info"]["license"],
                    data["info"]["author_email"],
                    data["info"]["classifiers"],
                    data["info"]["home_page"],
                    data["info"]["keywords"],
                    self.index,
                )

    def _err_checking(self, output, name, version):
        """
        Checks the output of a subprocess.run call for errors.

        :param output: The output of a subprocess.run call.
        :type output: str
        :raises PackageNotFoundException: The package was not found.
        :raises VersionNotFoundException: The version was not found.
        :raises ConnectionException: The connection to PyPi was unsuccessful.
        """
        name += f"=={version}"
        not_found = f"ERROR: Could not find a version that satisfies the requirement {name} (from versions: {version}) \
        \nERROR: No matching distribution found for {name}"
        if not_found in output:
            raise errors.PackageNotFoundException(f"{name} is not a valid package!")
        not_found = f"ERROR: No matching distribution found for {name}=={version}"
        if not_found in output:
            raise errors.VersionNotFoundException(f"{version} does not exist!")
        invalid_connection = f"WARNING: Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) \
        after connection broken by "
        not_found = f"ERROR: Could not find a version that satisfies the requirement {name} (from versions: {version})\
                \nERROR: No matching distribution found for {name}"
        if invalid_connection in output and not_found in output:
            raise errors.ConnectionException(
                f"PyPi could not be reached! Full error: {output}"
            )
        not_installable = f"ERROR: Directory '{name}' is not installable. Neither setup.py nor 'pyproject.toml' found."
        if not_installable in output:
            raise errors.PackageNotFoundException(f"{name} is not a valid package!")

    async def install(self, pkg, version=None):
        """
        Installs a package through the Pip API. Returns a Package object for the installed package.

        :param pkg: The package to install.
        :type pkg: str or Package
        :param version: The version of the package to install.
        :type version: str
        :return: A Package object for the installed package.
        :rtype: Package
        :raises PackageNotFoundException: The package was not found.
        :raises self.VersionNotFoundException: The version was not found.
        :raises ConnectionException: The connection to PyPi was unsuccessful.
        """
        version = f"=={version}" if version else ""
        pkg = await self._get(pkg, version) if isinstance(pkg, str) else pkg
        command = f"pip install --index-url {self.index} {pkg.name}{version}"
        out = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )  # we won't actually use stdout, it just stops it from printing to the console
        out = await out.communicate()
        self._err_checking(out[1].decode(), pkg.name, pkg.version)
        return pkg if isinstance(pkg, str) else pkg

    async def uninstall(self, pkg):
        """
        Uninstalls a package through the Pip API.

        :param pkg: The name of the package to uninstall.
        :raises PackageNotFoundException: The package was not found.
        """
        name = pkg.name if isinstance(pkg, package.Package) else pkg
        out = await asyncio.create_subprocess_shell(
            f"pip uninstall {name} -y",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )  # we won't actually use stdout, it just stops it from printing to the console
        out = await out.communicate()
        out = out[1].decode()
        not_installable = f"ERROR: Directory '{name}' is not installable. Neither setup.py nor 'pyproject.toml' \
                          found."
        if not_installable in out:
            raise errors.PackageNotFoundException(f"{name} is not a valid package!")
        invalid_package = f"WARNING: Skipping {name} as it is not installed."
        if invalid_package in out:
            raise errors.PackageNotFoundException(f"{name} is not installed!")
        return await self._get(name) if isinstance(pkg, str) else pkg
