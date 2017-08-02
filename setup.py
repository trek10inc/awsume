import atexit, os
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.install_scripts import install_scripts

version = '1.2.1'

class CustomInstall(install):
    def run(self):
        def _post_install():
            #cross platform home folder
            homefolder = os.path.expanduser('~')
            #alias string to add
            alias = 'alias awsume=". awsume"\n'
            rc_file = ""

            #the possible bash rc files
            if os.path.exists(os.path.abspath('%s/.bash_aliases' % homefolder)):
                rc_file = os.path.abspath('%s/.bash_aliases' % homefolder)
            elif os.path.exists(os.path.abspath('%s/.bashrc' % homefolder)):
                rc_file = os.path.abspath('%s/.bashrc' % homefolder)
            elif os.path.exists(os.path.abspath('%s/.bash_profile' % homefolder)):
                rc_file = os.path.abspath('%s/.bash_profile' % homefolder)
            #the possible zsh rc files
            if os.path.exists(os.path.abspath('%s/.zshrc' % homefolder)):
                rc_file = os.path.abspath('%s/.zshrc' % homefolder)
            elif os.path.exists(os.path.abspath('%s/.zshenv' % homefolder)):
                rc_file = os.path.abspath('%s/.zshenv' % homefolder)
            elif os.path.exists(os.path.abspath('%s/.zprofile' % homefolder)):
                rc_file = os.path.abspath('%s/.zprofile' % homefolder)

            #now add the alias to the user's rc file
            if os.path.exists(rc_file):
                with open(rc_file, 'r') as f:
                    lines = f.readlines()
                    if alias not in lines:
                        out = open(rc_file, 'a')
                        out.write("#AWSume alias to source the AWSume script\n")
                        out.write(alias)
                        out.close()
        atexit.register(_post_install)
        install.run(self)

class CustomInstallScripts(install_scripts):
    def run(self):
        def _post_install_scripts():
            #make sure awsume is executable
            execpath = '/usr/local/bin/awsume'
            if os.path.exists(execpath):
                os.chmod(execpath, int('755', 8))
        atexit.register(_post_install_scripts)
        install_scripts.run(self)

setup(
    name="awsume",
    packages=find_packages(exclude=("*test*", "./awsume/test*", "./awsume/testAwsume.py")),
    version=version,
    author="Trek10, Inc",
    author_email="package-management@trek10.com",
    description="Utility for easily assuming AWS IAM roles from the command line, now in Python!",
    long_description=open('README.rst').read(),
    license="MIT",
    url='https://github.com/trek10inc/awsume',
    download_url='https://github.com/trek10inc/awsume/archive/' + version + '.tar.gz',
    scripts=[
        'awsume/shellScripts/awsume',
        'awsume/shellScripts/awsume.ps1',
        'awsume/shellScripts/awsume.bat',
    ],
    include_package_data=True,
    install_requires=[
        'python-dateutil',
        'boto3',
        'psutil',
        'yapsy'
    ],
    entry_points={
        "console_scripts": [
            'awsumepy=awsume.awsumepy:main',
            'autoAwsume=awsume.autoAwsume:main'
        ]
    },
    cmdclass={
        'install': CustomInstall,
        'install_scripts': CustomInstallScripts,
    },
)
