import os, pathlib

from awsume.awsumepy.lib.constants import AWSUME_DIR

BASH_AUTOCOMPLETE_SCRIPT = """
_awsume() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts=$(awsume-autocomplete)
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}
complete -F _awsume awsume
"""

ZSH_AUTOCOMPLETE_SCRIPT = """
#Auto-Complete function for AWSume
fpath=(~/.awsume/zsh-autocomplete/ $fpath)
"""

ZSH_AUTOCOMPLETE_FUNCTION = """#compdef awsume
_arguments "*: :($(awsume-autocomplete))"
"""

FISH_AUTOCOMPLETE_SCRIPT = """
complete -f --command awsume --arguments '(awsume-autocomplete)'
"""

POWERSHELL_AUTOCOMPLETE_SCRIPT = """
Register-ArgumentCompleter -Native -CommandName awsume -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    $(awsume-autocomplete) |
    Where-Object { $_ -like "$wordToComplete*" } |
    Sort-Object |
    ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
    }
}
"""

SCRIPTS = {
    'bash': BASH_AUTOCOMPLETE_SCRIPT,
    'zsh': ZSH_AUTOCOMPLETE_SCRIPT,
    'powershell': POWERSHELL_AUTOCOMPLETE_SCRIPT,
    'fish': FISH_AUTOCOMPLETE_SCRIPT,
}

def main(shell: str, autocomplete_file: str):
    autocomplete_file = str(pathlib.Path(autocomplete_file).expanduser())
    autocomplete_script = SCRIPTS[shell]

    basedir = os.path.dirname(autocomplete_file)
    if basedir and not os.path.exists(basedir):
        os.makedirs(basedir)
    open(autocomplete_file, 'a').close()

    if autocomplete_script in open(autocomplete_file, 'r').read():
        print('Autocomplete script already in ' + autocomplete_file)
    else:
        with open(autocomplete_file, 'a') as f:
            f.write('\n#Auto-Complete function for AWSume')
            f.write(autocomplete_script)
        print('Wrote autocomplete script to ' + autocomplete_file)

    # install autocomplete function if zsh
    if shell == 'zsh':
        zsh_autocomplete_function_file = AWSUME_DIR / 'zsh-autocomplete/_awsume'
        if not zsh_autocomplete_function_file.is_file():
            zsh_autocomplete_function_file.open('w').close()
        if ZSH_AUTOCOMPLETE_FUNCTION in zsh_autocomplete_function_file.open('r').read():
            print('Zsh function already in ' + zsh_autocomplete_function_file)
        else:
            with zsh_autocomplete_function_file.open('a') as f:
                f.write(ZSH_AUTOCOMPLETE_FUNCTION)
            print('Wrote zsh function to ' + str(zsh_autocomplete_function_file))
