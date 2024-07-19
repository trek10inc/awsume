import fastentrypoints
from setuptools import setup, find_packages

import awsume
from awsume.configure.post_install import CustomInstall

setup(
    name=awsume.__NAME__,
    packages=find_packages(),
    version=awsume.__VERSION__,
    author=awsume.__AUTHOR__,
    author_email=awsume.__AUTHOR_EMAIL__,
    description=awsume.__DESCRIPTION__,
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    license=awsume.__LICENSE__,
    url=awsume.__HOMEPAGE__,
    install_requires=[
        'colorama',
        'boto3',
        'psutil',
        'pluggy',
        'pyyaml',
        'urllib3 >= 1.21.1, <= 1.24',
        'chardet >= 3.0.2, < 3.1.0',
        'setuptools; python_version >= "3.12"'
    ],
    extras_require={
        'saml': ['xmltodict'],
        'fuzzy': ['python-levenshtein'],
        'console': ['awsume-console-plugin'],
    },
    scripts=[
        'shell_scripts/awsume',
        'shell_scripts/awsume.ps1',
        'shell_scripts/awsume.bat',
        'shell_scripts/awsume.fish',
    ],
    entry_points={
        'console_scripts': [
            'awsumepy=awsume.awsumepy.main:main',
            'autoawsume=awsume.autoawsume.main:main',
            'awsume-configure=awsume.configure.main:main',
            'awsume-autocomplete=awsume_autocomplete:main',
        ],
    },
    python_requires='>=3.6',
    cmdclass={
        'install': CustomInstall,
    },
)
