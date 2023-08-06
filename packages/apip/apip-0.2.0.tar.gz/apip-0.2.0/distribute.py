import subprocess
import tests
import pathlib

path = pathlib.Path(__file__).parent.resolve() / "apip"

if tests.test():
    print("Tests passed")
    print("Uploading package")
    subprocess.run(["python", "-m", "black", path])  # requires black
    subprocess.run(["sh", "./distribute.sh"])
