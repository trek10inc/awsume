# `awsume-configure`

The `awsume-configure` command is intended to let you set up awsume on your own without having to reinstall awsume, just in case there was a problem during the initial installation of awsume.

## Usage

```
usage: awsume-configure [-h]
                        --shell shell
                        --autocomplete-file autocomplete_file
                        [--alias-file alias_file]

optional arguments:
  -h, --help                              show this help message and exit
  --shell shell                           The shell you will use awsume under
  --autocomplete-file autocomplete_file   The file you want the autocomplete script to be defined in
  --alias-file alias_file                 The file you want the alias to be defined in
```

---

Depending on your shell, there are a few things you'll need.

## Alias

The alias is required for unix-like systems and shells, including Bash and Zsh. It is not required for Windows-like shells such as PowerShell or Windows Command Prompt.

The alias should be defined in your shell's login file, so it gets loaded on every shell session. It should look something like this:

```bash
alias awsume=". awsume"
```

If you are using awsume through a [pyenv](https://github.com/pyenv/pyenv) environment, your alias should look like this:

```bash
alias awsume=". $(pyenv which awsume)"
```

However, if you use pyenv and also have installed awsume with [pipx](https://pypa.github.io/pipx/), you will need the original alias.

Awsume will try to give you the correct alias depending on your installation method, but sometimes things can go awry and require manual intervention.

## Autocomplete script

Autocomplete is currently only supported for Bash, Zsh, and Powershell.

### Bash

In Bash environments, the autocomplete script should look something like this:

```bash
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
```

It will attempt to load this into the first file it finds available of the following login files:

- `~/.bash_profile`
- `~/.bash_login`
- `~/.bashrc`

If you want this script in a different login file such as .profile, then you may manually add it into the necessary file.
### Zsh

In Zsh environments, the autocomplete script should look something like this:

```zsh
#compdef awsume
_arguments "*: :($(awsume-autocomplete))"
```

It will attempt to load this into `$ZDOTDIR/.zshenv`.

### PowerShell

For PowerShell environments, awsume will execute the following command to get the file to install the autocomplete script into:

```powershell
powershell $profile
```

The autocomplete script will look something like this:

```powershell
Register-ArgumentCompleter -Native -CommandName awsume -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    $(awsume-autocomplete) |
    Where-Object { $_ -like "$wordToComplete*" } |
    Sort-Object |
    ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
    }
}
```

---

Again, if anything went wrong during the initial installation, you can attempt to set up awsume manually with the `awsume-configure` command, passing in the locations in which to install each component.
