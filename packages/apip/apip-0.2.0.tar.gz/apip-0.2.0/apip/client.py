from apip.abc.installer import Installer
import asyncio
import re


class Client(Installer):
    """
    The main class for the apip API wrapper. This class is used to interact with the Pip and PyPi API.

    :param index: The index to install the package from.
    :type index: str
    """

    def __init__(self, index="https://pypi.org/simple"):
        Installer.__init__(self, index)
        self.get = self._get

    async def list(self):
        """
        Lists all installed packages and returns them in a list of Package objects.

        :return: A list of Package objects for all installed packages.
        :rtype: list
        """
        packages = []
        output = asyncio.create_subprocess_shell(
            "pip list", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        output = output[1]
        output = " ".join(output.splitlines()[2:])
        output = re.findall("[a-zA-Z\d][^ \n]*", output)
        for index, item in enumerate(output[::2]):
            packages.append(self.get(item, output[index + 1]))
        return packages
