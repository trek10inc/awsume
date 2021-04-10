# Shell Scripts

The shell scripts directory contains a list of shell scripts for various shells - (bash/zsh, PowerShell, and Windows Command Prompt). In the `setup.py` file, you'll notice the `scripts` keyword argument adding each of these scripts to the built package. This makes these shell scripts available whenever anyone installs awsume.

These scripts are necessary, in tandem with the alias that overrides `awsume` to a command that source's these shell scripts, to allow awsume to modify the parent shell's environment variables.

For Windows operating systems, an alias is unnecessary as an invoked `script.ps1` is able to modify its parent shell's environment variables.
