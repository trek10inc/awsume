from setuptools.command.install import install

from .main import run


class CustomInstall(install):
    def run(self):
        install.run(self)
        run()
