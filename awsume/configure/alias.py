import os, pathlib
from distutils.spawn import find_executable

DEFAULT_ALIAS = 'alias awsume=". awsume"'
PYENV_ALIAS = r'alias awsume=". \$(pyenv which awsume)"'

def main(shell: str, alias_file: str):
    alias = PYENV_ALIAS if find_executable('pyenv') else DEFAULT_ALIAS
    alias_file = pathlib.Path(alias_file).expanduser()
    if alias in open(alias_file, 'r').read():
        print('Alias already in ' + alias_file)
    else:
        with open(alias_file, 'a') as f:
            f.write('\n#AWSume alias to source the AWSume script\n')
            f.write(alias)
            f.write('\n')
        print('Wrote alias to ' + alias_file)
