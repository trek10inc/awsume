import argparse, os, sys, subprocess
from pathlib import Path
from distutils.spawn import find_executable

from . import alias, autocomplete

BASH_LOGIN_FILES = ['~/.bash_profile', '~/.bash_login', '~/.profile', '~/.bashrc']


def get_bash_file() -> str:
    paths = [str(Path(_).expanduser()) for _ in BASH_LOGIN_FILES]
    result = [_ for _ in paths if os.path.exists(_) and os.path.isfile(_) and os.access(_, os.R_OK)]
    if not result:
        default = paths[0]
        open(default, 'w').close()
        result = [default]
    return result[0]


def get_zsh_file() -> str:
    z_dot_dir = os.environ.get('ZDOTDIR', '~')
    zsh_file = str(Path(z_dot_dir + '/.zshenv').expanduser())
    if not os.path.exists(zsh_file) or not os.path.isfile(zsh_file):
        open(zsh_file, 'w').close()
    return zsh_file


def get_fish_functions_file() -> str:
    fish_functions = str(Path('~/.config/fish/functions/').expanduser())
    if not os.path.exists(str(fish_functions)):
        os.makedirs(str(fish_functions))
    fish_file = str(Path(fish_functions + '/awsume.fish').expanduser())
    if not os.path.exists(fish_file) or not os.path.isfile(fish_file):
        open(fish_file, 'w').close()
    return fish_file


def get_fish_completions_file() -> str:
    fish_completions = str(Path('~/.config/fish/completions/').expanduser())
    if not os.path.exists(str(fish_completions)):
        os.makedirs(str(fish_completions))
    fish_file = str(Path(fish_completions + '/awsume.fish').expanduser())
    if not os.path.exists(fish_file) or not os.path.isfile(fish_file):
        open(fish_file, 'w').close()
    return fish_file


def get_powershell_file() -> str:
    (powershell_file, _) = subprocess.Popen(['powershell', 'Write-Host $profile'], stdout=subprocess.PIPE, shell=True).communicate()
    if powershell_file:
        powershell_file = str(powershell_file.decode('ascii')).replace('\r\n', '').replace('\n', '')
        return powershell_file
    return None


def install(shell: str, alias_file: str, autocomplete_file: str):
    if alias_file:
        alias.main(shell, alias_file)
    if autocomplete_file:
        autocomplete.main(shell, autocomplete_file)


def setup_bash(alias_file: str, autocomplete_file: str):
    print('===== Setting up bash =====')
    bash_file = get_bash_file()
    alias_file = alias_file or bash_file
    autocomplete_file = autocomplete_file or bash_file
    if not bash_file:
        print('===== Could not locate bash file =====')
    install('bash', alias_file, autocomplete_file)


def setup_zsh(alias_file: str, autocomplete_file: str):
    print('===== Setting up zsh =====')
    zsh_file = get_zsh_file()
    alias_file = alias_file or zsh_file
    autocomplete_file = autocomplete_file or zsh_file
    if not zsh_file:
        print('===== Could not locate zsh file =====')
    install('zsh', alias_file, autocomplete_file)


def setup_fish(alias_file: str, autocomplete_file: str):
    print('===== Setting up fish =====')
    fish_functions_file = get_fish_functions_file()
    fish_completions_file = get_fish_completions_file()
    alias_file = alias_file or fish_functions_file
    autocomplete_file = autocomplete_file or fish_completions_file
    install('fish', alias_file, autocomplete_file)


def setup_powershell(alias_file: str, autocomplete_file: str):
    print('===== Setting up powershell =====')
    powershell_file = get_powershell_file()
    autocomplete_file = autocomplete_file or powershell_file
    if not powershell_file:
        print('===== Could not locate powershell file =====')
    install('powershell', None, autocomplete_file)


def parse_args(argv: sys.argv) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--shell',
        default=None,
        dest='shell',
        metavar='shell',
        help='The shell you will use awsume under',
        required=False,
        choices=['bash', 'zsh', 'fish', 'powershell']
    )
    parser.add_argument('--autocomplete-file',
        default=None,
        dest='autocomplete_file',
        metavar='autocomplete_file',
        required=False,
        help='The file you want the autocomplete script to be defined in',
    )
    parser.add_argument('--alias-file',
        default=None,
        dest='alias_file',
        metavar='alias_file',
        required=False,
        help='The file you want the alias to be defined in',
    )
    args = parser.parse_args(argv)

    if args.shell in ['powershell'] and args.alias_file:
        parser.error('No alias file is needed for shell: powershell')
    if not args.shell and (args.autocomplete_file or args.alias_file):
        parser.error('Cannot specify autocomplete file or alias file when not specifying shell')

    return args


def run(shell: str = None, alias_file: str = None, autocomplete_file: str = None):
    if os.environ.get('AWSUME_SKIP_ALIAS_SETUP'):
        print('===== Skipping Alias Setup =====')
        return
    setup_functions = {
        'bash': setup_bash,
        'zsh': setup_zsh,
        'powershell': setup_powershell,
        'fish': setup_fish,
    }
    if not shell:
        if find_executable('bash'):
            setup_functions['bash'](None, None)
        if find_executable('zsh'):
            setup_functions['zsh'](None, None)
        if find_executable('fish'):
            setup_functions['fish'](None, None)
        if find_executable('powershell'):
            setup_functions['powershell'](None, None)
    else:
        setup_functions[shell](alias_file, autocomplete_file)
    print('===== Finished setting up =====')


def main():
    args = parse_args(sys.argv[1:])
    run(args.shell, args.alias_file, args.autocomplete_file)
