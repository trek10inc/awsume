# Troubleshooting Awsume

::: warning
If none of these help you, feel free to [open an issue](https://github.com/trek10inc/awsume/issues/new)!
:::

## AWSume is installed, but when I run it, my environment is not updating with my profile's credentials

This is most likely due to an issue with the alias. You should have an alias `awsume='. awsume'` to source the awsume shell wrapper. Usually, the installation of AWSume will put that alias declaration within one of your login files, so make sure that the alias exists within your login file, such as `~/.bashrc`, `~/.bash_profile`, etc.

## I'm getting an installation error, "fatal error: Python.h No such file or directory"

This is an issue with `python-dev` not being installed on your system. Run your package manager to install `python-dev`, and make sure all of your packages are up-to-date before trying to install AWSume again. If you are running Python3, `python3-dev` is required. Some package managers might call the package `python-devel` or `python3-devel` (for Python3).

## I'm getting an installation error when pip is trying to uninstall six, I get "Operation not permitted"

Run your `pip install awsume` command with the option `--ignore-installed six`. The issue here is that OS X ships with `six-1.4.1` preinstalled. AWSume depends on boto3 and python-dateutil, which both depend on six >= 1.5. When installing AWSume, pip needs to uninstall six to upgrade it to the required version. However, due to Apple's "System Integrity Protection", not even root can modify/uninstall six. So, the only way around this is to ignore upgrading six when installing AWSume.

## I'm using Pyenv and my terminal closes whenever I run AWSume

This issue was fixed in release `1.3.1`. The issue is that the `awsume` command calls a shell script. Because of that, the way that Pyenv shims work, and the alias that sources AWSume, calling it would result in the shim, in bash, is sourced, and trying to execute python on a bash script, the terminal would close whenever running `awsume`. The solution implemented is to alter the alias to point to the `awsume` script within the `~/pyenv/versions/<VERSION>/bin/` directory, so that the `awsume` shim isn't being called anymore.
