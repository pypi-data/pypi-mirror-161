from .installer import Installer
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
            "pip list",
            stdout=asyncio.subprocess.PIPE
        )
        output = output.stdout.decode()
        output = ' '.join(output.splitlines()[2:])
        output = re.findall('(?! )[a-zA-Z\d\.\-]*', output)
        it = iter(output)
        joined = [[a, b] for a, b in zip(it, it)]
        for index, item in enumerate(joined):
            if item == "":
                output.pop(index)
                continue
            packages.append(self.get(item[0]))
        return packages
