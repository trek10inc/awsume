# Updating to Awsume Version 4

Awsume v4 does things a little differently than previous versions. This guide should help you if you're updating awsume from an earlier version.

::: warning
If you run into any issues, feel free to [open an issue](https://github.com/trek10inc/awsume/issues/new)!
:::

## Plugin System

Awsume changed plugin systems. Where we previously used [Yapsy](https://pypi.org/project/Yapsy/) we're now using [Pluggy](https://pluggy.readthedocs.io/en/latest/).

Awsume used to store plugins in your home directory: `~/.aws/awsumePlugins`. This is no longer the case. Plugins are now actual python packages, installed via `pip` or some other python package installer. For this reason, you no longer need the `~/.aws/awsumePlugins` directory, so this can be emptied and deleted.

## Login Profile Cleanup

Awsume now _correctly_ prioritizes bash login files. There was a consistent bug in previous versions that would place the alias and autocomplete script definitions in the `~/.bashrc`, even in OS X (where the `~/.bashrc` is not loaded on login by default), causing awsume to not "just work." The awsume post-install configuration will now prioritize the `~/.bash_profile` over the `~/.bashrc` (read more about that [here](https://www.gnu.org/software/bash/manual/html_node/Bash-Startup-Files.html)). For this reason you might see doubling of the alias/autocomplete definitions, so you can clean up the unused ones.

## Autocomplete script

Related to login profile cleanup, the autocomplete script has changed. This is due to a refactor that migrated all autocomplete code out of awsume's core and made use of [fastentrypoints](https://pypi.org/project/fastentrypoints/), so that autocomplete would execute faster. So if you see multiple, _slightly different_ autocomplete script definitions for awsume, make sure to keep the one that has the `awsume-autocomplete` command.

## Cache and Config

Awsume now makes use of an `~/.awsume/` directory for storing cache and config. This means that you can migrate your settings from `~/.aws/awsume.json` to `~/.awsume/config.yaml`.

Awsume will now no longer use the `~/.aws/cli/cache/` directory for it's own caching, so you can clear out all of those old awsume cache files.

## Awsume configuration

If anything went wrong with awsume's installation, you can now run the configuration commands outside of `pip install` with `awsume-configure`. Read more about it [here](/utilities/awsume-configure).
