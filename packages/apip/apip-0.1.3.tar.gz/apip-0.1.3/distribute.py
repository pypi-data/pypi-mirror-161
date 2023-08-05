import subprocess
import tests

if tests.test():
    print("Tests passed")
    print("Uploading package")
    subprocess.run(["sh", "./distribute.sh"])