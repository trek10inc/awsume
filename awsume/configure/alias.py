import os, pathlib
from shutil import which

DEFAULT_ALIAS = 'alias awsume="source awsume"'
PYENV_ALIAS = r'alias awsume="source \$(pyenv which awsume)"'
PYENV_FISH_ALIAS = r'alias awsume="source (pyenv which awsume.fish)"'
FISH_ALIAS = r'alias awsume="source (which awsume.fish)"'

def main(shell: str, alias_file: str):
    alias_file = str(pathlib.Path(alias_file).expanduser())
    if shell == 'fish':
        if which('pyenv'):
            alias = PYENV_FISH_ALIAS
        else:
            alias = FISH_ALIAS
    else:
        if which('pyenv'):
            alias = PYENV_ALIAS
        else:
            alias = DEFAULT_ALIAS

    basedir = os.path.dirname(alias_file)
    if basedir and not os.path.exists(basedir):
        os.makedirs(basedir)
    open(alias_file, 'a').close()

    if alias in open(alias_file, 'r').read():
        print('Alias already in ' + alias_file)
    else:
        with open(alias_file, 'a') as f:
            f.write('\n#AWSume alias to source the AWSume script\n')
            f.write(alias)
            f.write('\n')
        print('Wrote alias to ' + alias_file)
