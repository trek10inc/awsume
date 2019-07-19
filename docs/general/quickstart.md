# Quick Start

## Installation

Awsume can be installed via the following command:

```
pip install awsume
```

::: warning
Awsume version 4 and up requires Python 3.5+
:::

## Alias Setup

If you're running on a unix-like system, you must have an alias setup for awsume, that may or may not look something like this:

```bash
alias awsume=". awsume"
```

Awsume will make an attempt to place this in a login script such as your `~/.bash_profile` or `~/.bashrc` when it's being installed, so you may need to restart your terminal or re-source your login file.

If this automatic installation is causing you problems, you can disable it through setting an environment variable like this:

```bash
AWSUME_SKIP_ALIAS_SETUP=true pip install awsume
```

Sometimes, however, things (such as file permission issues) can prevent awsume from injecting the alias. If this is the case, we provided a utility to setup the alias after the fact, so check out the `awsume-configure` guide [here](./awsume-configure.md).

For debug purposes, in order to get output from the post_install setup, you must use pip's `-v` flag like this:

```bash
pip install awsume -v
```

## Quick Usage

Once you have your alias setup, awsume can now work.

Run the following command and you'll be able to execute commands and run scripts with that profile's credentials.

```bash
awsume <profile_name>
```

Read more about awsume's usage [here](./usage.md).
