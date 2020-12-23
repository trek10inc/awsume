import os, subprocess, sys
from pathlib import Path
from setuptools.command.install import install
from distutils.spawn import find_executable

from .main import run


class CustomInstall(install):
    def run(self):
        install.run(self)
        run()
