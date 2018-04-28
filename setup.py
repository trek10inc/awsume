import atexit
import os
import subprocess
import json
from distutils.spawn import find_executable
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.install_scripts import install_scripts

PACKAGE = json.load(open('package.json'))
HOME_FOLDER = os.path.expanduser('~')

BASH_AUTOCOMPLETE_SCRIPT = """
_awsume() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts=$(awsumepy --rolesusers)
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}
complete -F _awsume awsume
"""
ZSH_AUTOCOMPLETE_SCRIPT = """#compdef awsume
_arguments "*: :($(awsumepy --rolesusers))"
"""
POWERSHELL_AUTOCOMPLETE_SCRIPT = """
Register-ArgumentCompleter -Native -CommandName awsume -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    $(awsumepy --rolesusers) |
    Where-Object { $_ -like "$wordToComplete*" } |
    Sort-Object |
    ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
    }
}
"""

class CustomInstall(install):
    """Run the post-install scripts to load in autocomplete, alias, and anything else for awsume."""
    def get_awsume_alias(self):
        """Return the alias for awsume.
        If pyenv is being used, return an alias to the current python installation's awsume."""
        awsume_alias = 'alias awsume=". awsume"'
        if find_executable('pyenv'):
            awsume_alias = 'alias awsume=". \$(pyenv which awsume)"'
        return awsume_alias

    def install_alias(self, file_path, alias):
        """Install the given aliad to the given file.
        Add a comment above the alias so that users know what it's for."""
        with open(file_path, 'r') as read_f:
            contents = read_f.read()
            if alias not in contents:
                out = open(file_path, 'a')
                out.write('\n')
                out.write('#AWSume alias to source the AWSume script')
                out.write('\n')
                out.write(alias)
                out.write('\n')
                out.close()

    def install_bash_script(self, file_path, script):
        """Install AWSume's auto-complete to bash rc file."""
        with open(file_path, 'r') as read_f:
            contents = read_f.read()
            if script not in contents:
                out = open(file_path, 'a')
                out.write('\n')
                out.write('#Auto-Complete function for AWSume')
                out.write('\n')
                out.write(script)
                out.write('\n')
                out.close()

    def install_zsh_script(self, zsh_script, rc_file, function_path):
        """Install AWSume's auto-complete to zsh rc file."""
        if not os.path.exists(function_path):
            os.makedirs(function_path)

        #add the directory to fpath
        with open(rc_file, 'r') as original:
            data = original.read()
            original.close()
        fpath_line = 'fpath=(' + function_path + ' $fpath)'
        if fpath_line not in data:
            with open(rc_file, 'a') as modified:
                modified.write(fpath_line)
                modified.close()

        func_file = function_path + '/_awsume'
        with open(func_file, 'w+') as read_f:
            content = read_f.read()
            if not zsh_script in content:
                out = open(func_file, 'a')
                out.write(zsh_script + '\n')
                out.close()

    def install_powershell_script(self, script, powershell_file):
        """Install AWSume's auto-complete to powershell profile."""
        contents = open(powershell_file, 'w+').read()
        if script not in contents:
            out = open(powershell_file, 'a+')
            out.write('\n')
            out.write(script)
            out.write('\n')
            out.close()

    def get_bash_file(self, homefolder):
        """Return the path to the user's bash rc file."""
        rc_file = os.path.abspath('%s/.bashrc' % homefolder)
        if os.path.exists(os.path.abspath('%s/.bash_aliases' % homefolder)):
            rc_file = os.path.abspath('%s/.bash_aliases' % homefolder)
        elif os.path.exists(os.path.abspath('%s/.bashrc' % homefolder)):
            rc_file = os.path.abspath('%s/.bashrc' % homefolder)
        elif os.path.exists(os.path.abspath('%s/.bash_profile' % homefolder)):
            rc_file = os.path.abspath('%s/.bash_profile' % homefolder)
        elif os.path.exists(os.path.abspath('%s/.profile' % homefolder)):
            rc_file = os.path.abspath('%s/.profile' % homefolder)
        elif os.path.exists(os.path.abspath('%s/.login' % homefolder)):
            rc_file = os.path.abspath('%s/.login' % homefolder)
        return rc_file

    def get_zsh_file(self, homefolder):
        """Return the path to the user's zsh rc file."""
        rc_file = os.path.abspath('%s/.zshrc' % homefolder)
        if os.path.exists(os.path.abspath('%s/.zshrc' % homefolder)):
            rc_file = os.path.abspath('%s/.zshrc' % homefolder)
        elif os.path.exists(os.path.abspath('%s/.zshenv' % homefolder)):
            rc_file = os.path.abspath('%s/.zshenv' % homefolder)
        elif os.path.exists(os.path.abspath('%s/.zprofile' % homefolder)):
            rc_file = os.path.abspath('%s/.zprofile' % homefolder)
        elif os.path.exists(os.path.abspath('%s/.zlogin' % homefolder)):
            rc_file = os.path.abspath('%s/.zlogin' % homefolder)
        return rc_file

    def ensure_executable(self):
        """Make sure AWSume is executable"""
        (awsume_path, _) = subprocess.Popen(["which", "awsume"], stdout=subprocess.PIPE).communicate()
        awsume_path = awsume_path.strip()
        if os.path.exists(awsume_path):
            os.chmod(awsume_path, int('755', 8))

    def run(self):
        def _post_install():
            """Run post-install operations"""
            awsume_alias = self.get_awsume_alias()

            # install to bash
            bash_rc_file = self.get_bash_file(HOME_FOLDER)
            self.install_alias(bash_rc_file, awsume_alias)
            self.install_bash_script(bash_rc_file, BASH_AUTOCOMPLETE_SCRIPT)

            # install to zsh
            if find_executable('zsh'):
                zsh_rc_file = self.get_zsh_file(HOME_FOLDER)
                function_path = os.path.abspath('/usr/local/share/zsh/site-functions')
                self.install_alias(zsh_rc_file, awsume_alias)
                self.install_zsh_script(ZSH_AUTOCOMPLETE_SCRIPT, zsh_rc_file, function_path)

            # install to powershell
            if find_executable('powershell'):
                (file_name, _) = subprocess.Popen(["powershell", "$profile"], stdout=subprocess.PIPE, shell=True).communicate()
                file_name = str(file_name.decode('ascii')).replace('\r\n', '')
                self.install_powershell_script(POWERSHELL_AUTOCOMPLETE_SCRIPT, file_name)

            # make executable
            self.ensure_executable()
        atexit.register(_post_install)
        install.run(self)

setup(
    name=PACKAGE['name'],
    packages=['awsume'],
    version=PACKAGE['version'],
    author=PACKAGE['author']['name'],
    author_email=PACKAGE['author']['email'],
    description=PACKAGE['description'],
    license=PACKAGE['license'],
    url=PACKAGE['homepage'],
    package_data={'awsume': ['package.json']},
    include_package_data=True,
    install_requires=[
        'boto3',
        'psutil',
        'yapsy',
        'future',
        'colorama',
    ],
    scripts=[
        'awsume/shellScripts/awsume',
        'awsume/shellScripts/awsume.ps1',
        'awsume/shellScripts/awsume.bat',
    ],
    entry_points={
        "console_scripts": [
            'awsumepy=awsume.awsumepy:main',
            'autoawsume=awsume.autoawsume:main',
        ]
    },
    cmdclass={
        'install': CustomInstall,
    },
)
