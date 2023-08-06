""" This code is DEPRECATED! It has been replaced by a direct call to
typhoon-allure which is automatically put in the system PATH.

Consider removing this.
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import subprocess
import sys
import os
import shutil


if shutil.which("typhoon-allure") is not None:
    exe = "typhoon-allure"
else:
    try:
        old_typhoon = os.environ["TYPHOON"]
        exe = f'"{os.path.join(old_typhoon, "allure", "bin", "allure_typhoon.bat")}"'
    except KeyError:
        raise Exception('Could not find typhoon-allure. Make sure Typhoon HIL Control Center is properly installed.')


def main():
    arg1 = sys.argv[1]
    cwd = os.getcwd()
    abs_path = os.path.join(cwd, arg1)
    print("Absolute test report path: {}".format(abs_path))
    subprocess.call(f'{exe} serve "{abs_path}"')


if __name__ == "__main__":
    main()
