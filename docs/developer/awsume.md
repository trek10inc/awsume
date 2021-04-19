# Awsume

This is the main package for the awsume application

```python
awsume # root package
├── __init__.py
├── __data__.py # contains package information, helpful for quickly deriving the version, package name, etc
├── awsumepy # the core awsume package
├── autoawsume # the package for any autoawsume logic
└── configure # A peripheral package to help set up shell login files with the alias and autocomplete definitions
```

## `awsumepy`

This is the core package for awsume.

### main

You'll notice the main entrypoint for the CLI (from the `setup.py` file):

```python
    entry_points={
        'console_scripts': [
            'awsumepy=awsume.awsumepy.main:main',
```

The `awsumepy` command points to the `awsume.awsumepy.main` file's `main` function. That main function includes a small bit of logger config (to help `--info` and `--debug` logs show before the main logger configuration gets invoked), and a call to the `run_awsume` function, which takes a list of arguments. The `run_awsume` function initializes an awsume "app" class, and executes the `.run` method on it.

### awsume

The `awsume/awsumepy/awsume.py` file is the entrypoint for non-interactive calls to awsume (calling via python import). It calls the app class's `.run` method like the `main.py` file.

### app

From there, you'll find the awsume app class defined in the `app.py` file. The class has a couple of methods on it - the main one being `run`. Each method on the app class is a different phase in an execution of awsume. The phases generally follow this order:

1. initialization
1. argument handling - handle any argument special cases, normalization, or defaults population
1. profile collection - collect the available profiles
1. credential retrieval - retrieve credentials for the target profile
1. credential export - export those credentials to the parent shell through a shell wrapper

#### Initialization

The initialization that happens includes things like setting up the pluggy plugin manager, reading awsume's configuration file, and discovering how awsume was invoked (interactively or non-interactively).

Most of the core logic to awsume is contained in default plugins, which are registered with the plugin manager at initialization time. These default plugins can be found in the `default_plugins.py` file. You'll notice these are invoked through the `self.plugin_manager.hook.<plugin_name>()` function calls in the awsume app.

#### Argument Handling

Arguments are handled through argparse. Arguments are established through the `add_arguments` plugin hook. If there was an argument passed that does not warrant credential awsumption (like `--list-profiles`/`-l` or `--unset`/`-u`), an `exceptions.EarlyExit` exception will be raised to tell awsume that nothing further is necessary to be done. This exception is caught towards the end of the `app.run` method.

<details>
<summary><i>Non-interactive argument handling</i></summary>

If you're invoking non-interactively through the python `import` (i.e. `from awsume.awsumepy import awsume`) arguments by default are treated as command-line arguments, so you can call it like this:

```python
awsume('myprofile', '--role-duration', '43200')
```

There is also a transformation that happens on incoming arguments to make it a little more pythonic, so any keyword arguments (`role_duration=43200`) are converted into command-line arguments `--role-duration 43200`, any boolean keyword arguments are treated as a flag (`with_saml=True` -> `--with-saml`).

</details>

#### Profile Collection

From this high level app class, the process of gathering profiles is calling the plugin manager hooks and not much else. In case there are multiple plugins returning credentials the profiles will be aggregated together. So if two plugins generate a profile with the same name they will be merged in the final result.

#### Credential Retrieval

Credential retrieval is one of the core parts of awsume. There are a few possible credential retrieval plugins that could be defined - the base `get_credentials`, a `get_credentials_with_saml`, and `get_credentials_with_web_identity`. The saml credential gathering requires a bit more logic to handle selecting the right role and principal from the saml assertion. Review the default plugins for how `get_credentials` is implemented.

#### Credential Export

The credential export process takes the form of printing units of data separated by space. The first is a flag to tell the shell wrapper what the rest of the data will look like.

The credential export could also take the form of creating/updating an awsume-managed profile in the credentials file (using the `--output-profile`/`-o` argument).

For non-interactive calls, a boto3 session object will be returned, with the `credentials` dictionary tacked on as the `.awsume_credentials` property on the session object.

### default_plugins

This file contains all of the default plugins, or default functionality that can be extended with plugins.

In this file, you can see exactly what arguments are added, how they're handled, how aws profiles are collected from the shared config and credentials profiles, how those profiles are constructed, and how they're used in the rest of the applicaiton.

The `get_credentials` plugin is where a lot of complexity lies. You'll notice it first compiles a role chain (chain of profiles from one `source_profile` to the other, allows awsumeing a role with the credentials of another, as many times as needed). And for each profile in that chain, it performs a function call to get those credentials.

There's a lot of different options for the kinds of profiles you could awsume. Your profile could have a `credential_process`, be a "user" profile (with access keys) or a "role" profile (with a `role_arn`), it could be a "role" profile with a `source_profile` or it could have a `credential_source` property.

On top of this, awsume is designed to help users with MFA by taking advantage of 12 hour long session tokens (get MFA-authenticated user credentials that are valid for 12 hours, use those credentials each hour to assume the role you want, without needing to re-enter MFA every hour).

There are a lot of peripheral `get_credentials_...` functions defined here in an attempt to help make things a little easier to read.

### lib

This package serves as a central location for modules that are used throughout the awsume application. It includes modules that help abstract AWS API calls, manage awsume's configuration, define custom exceptions, the logger, and logic used to interact with the aws shared credentials and config files.

## `autoawsume`

The autoawsume package defines the entrypoint for autoawsume and all of the code required to execute it.

## `configure`

This package contains the code that gets executed to help users setup their login files with the alias and autocomplete definitions.

It follows the same pattern as the `awsumepy` package in that the `main.py` function defines the console entrypoint for invoking the `awsume-configure` command.

The logic for configuring the autocomplete script and alias differs from shell to shell, and is handled in the `autocomplete.py` and `alias.py` modules respectively.

A `post_install.py` module declares the custom install command class that's used by the `setup.py` file to perform the first attempt at setting up the environment.
