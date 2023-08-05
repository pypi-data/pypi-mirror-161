# TODO: test uninstall (doesn't want to work)

import apip
import asyncio

def test():
    client = apip.Client()
    passing = True

    try:
        asyncio.run(client.install("test"))
        print("Error handling test failed")
        passing = False
    except apip.errors.PackageNotFoundException:
        print("Errors handling test passed")

    try:
        asyncio.run(client.install("testingpkg"))
        import testingpkg
        passing = testingpkg.test()
        print("Installation test passed")
    except apip.errors.PackageNotFoundException:
        print("Installation test failed")
        passing = False
    except ImportError:
        print("Installation test failed")
        passing = False

    try:
        package = apip.Package("testingpkg", "0.0.1")
        package2 = asyncio.run(client.get("testingpkg"))
        passing = package.name == package2.name and package.version == package2.version
        print("Package get test passed")
    except apip.errors.PackageNotFoundException:
        print("Package get test failed")
        passing = False

    return passing
