import os, subprocess, sys
from pathlib import Path
from setuptools.command.install import install
from distutils.spawn import find_executable

from .main import run

BASH_LOGIN_FILES = ['~/.bash_profile', '~/.bash_login', '~/.profile', '~/.bashrc']


class CustomInstall(install):
    def get_bash_file(self) -> str:
        paths = [str(Path(_).expanduser()) for _ in BASH_LOGIN_FILES]
        result = [_ for _ in paths if os.path.exists(_) and os.path.isfile(_) and os.access(_, os.R_OK)]
        if not result:
            default = paths[0]
            open(default, 'w').close()
            result = [default]
        return result[0]

    def get_zsh_file(self) -> str:
        z_dot_dir = os.environ.get('ZDOTDIR', '~')
        zsh_file = str(Path(z_dot_dir + '/.zshenv').expanduser())
        if not os.path.exists(zsh_file) or not os.path.isfile(zsh_file):
            open(zsh_file, 'w').close()
        return zsh_file

    def run(self):
        install.run(self)
        if os.environ.get('AWSUME_SKIP_ALIAS_SETUP'):
            print('===== Skipping Alias Setup =====')
            return
        if find_executable('bash'):
            print('===== Setting up bash =====')
            bash_file = self.get_bash_file()
            run('bash', bash_file, bash_file)
        if find_executable('zsh'):
            print('===== Setting up zsh =====')
            zsh_file = self.get_zsh_file()
            run('zsh', zsh_file, zsh_file)
        if find_executable('powershell'):
            print('===== Setting up powershell =====')
            (powershell_file, _) = subprocess.Popen(['powershell', 'Write-Host $profile'], stdout=subprocess.PIPE, shell=True).communicate()
            if powershell_file:
                powershell_file = str(powershell_file.decode('ascii')).replace('\r\n', '').replace('\n', '')
                run('powershell', None, powershell_file)
            else:
                print('===== Could not locate powershell file =====')
        print('===== Finished setting up =====', file=sys.stderr)
