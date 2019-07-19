import os, pathlib
from distutils.spawn import find_executable

DEFAULT_ALIAS = 'alias awsume=". awsume"'
PYENV_ALIAS = r'alias awsume=". \$(pyenv which awsume)"'

def main(shell: str, alias_file: str):
    alias_file = str(pathlib.Path(alias_file).expanduser())
    alias = PYENV_ALIAS if find_executable('pyenv') and not find_executable('pipx') else DEFAULT_ALIAS

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
