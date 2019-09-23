# Awsume Changelog

## [4.1.4] - 2019-09-23 - Bug Fix

- Fixed profile validation bug, validates fuzzy-matched profile if enabled

## [4.1.3] - 2019-09-17 - Bug Fix

- Fixed library bug
- [#65](https://github.com/trek10inc/awsume/pull/65) Adds support for SAML profiles
- [#66](https://github.com/trek10inc/awsume/issues/66) Fixed role_duration profile property bug
- Adds `--principal-arn` to be used with saml role choices
- Fuzzy match config now affects selecting a saml role if `--principal-arn` and `--role-arn` are specified
- Fixed expiration log for non-role profiles without mfa
- Adds config `get` and `list` operations

## [4.1.2] - 2019-09-12 - Bug Fix

- Removed signal catch
- Removed printing expirations from non-interactive calls
- [!63](https://github.com/trek10inc/awsume/pull/63) Adds support for SAML 1 in addition to SAML 2

## [4.1.1] - 2019-09-01 - Bug Fix

- Fixed setting overriding cached region

## [4.1.0] - 2019-09-01 - Non-Interactive Awsume Update

- Adds support for using awsume from python scripts in a non-interactive way
- Adds fuzzy-match functionality to help match small typos to the intended profile name
- Fixes default profile region bug, will now successfully use the default profile's region as the region to use
  - Also adds `region` global configuration property

## [4.0.6] - 2019-08-19 - Bug Fix

- Fixed bug impacting Windows Powershell installs

## [4.0.5] - 2019-08-19 - Bug Fix

- Fixed python 3.5.7 dateutil incompatibility

## [4.0.4] - 2019-08-19 - Bug Fix

- Fixed zsh environment variable issue

## [4.0.3] - 2019-08-18 - Bug Fix

- Fixed ksh_arrays bug for zsh profiles

## [4.0.2] - 2019-08-15 - Bug Fix

- Fixed support for zsh autocomplete

## [4.0.1] - 2019-08-15 - Bug Fix

- Fixed support for zsh shells
  - Zsh shells index from 1, which threw off the `awsume` shell wrapper

## [4.0.0] - 2019-08-15 - Major Refactor

- New plugin system: "pluggy"
  - Define plugins as python packages that can be `pip installed`
- Allows support for SAML and Web Identity plugins
- Allows piping credentials into stdin (in json format such as from an `aws sts get-federation-token` call)
- Allows json input from the `--json` flag
- Allows using an external ID from the cli
- Allows using a role arn from the CLI using a targeted source-profile or current credentials
  - This allows you to role chain as much as you want
- Makes autocomplete faster through the use of an autocomplete cache file and using `fastentrypoints` to skip the `pkg_resources` import
  - Plugins must implement a `get_profile_names` method which will be used to update this file
  - The `--refresh-autocomplete` must be called to update the file
- If you run `awsume -l more` it will make additional calls to AWS to get more information about each profile
  - Currently this means calling get-caller-identity to get the account ID if one cannot be determined from an mfa_serial or role_arn
- Allows passing region in from the CLI, using that region to make aws sts calls and export to the environment
- Supports the `AWS_SHARED_CREDENTIALS_FILE` and `AWS_CONFIG_FILE` environment variables when pulling in the profiles
- Allows you to specify custom config and credentials files with the `--config-file` and `--credentials-file` flags
- Refactors awsume's global configuration, so that plugins can now use it too
  - Implements a "reset" or "clear" function: `awsume --config clear role-duration` to set the role-duration config back to default
  - JSON config values allowed
- New cache directory at `~/.awsume`
  - No longer overrides the awscli `~/.aws/cli/cache` directory to be used for awsume
- New `awsume-configure` cli to set up awsume's alias and autocomplete after installation without needing to reinstall awsume
- Allows for the `AWSUME_SKIP_ALIAS_SETUP` variable to make `pip install awsume` skip running `awsume-configure`
- Handles debug/info logging at the start of awsume's execution

## [3.2.9] - 2019-7-03 - Various Improvements

- [#43](https://github.com/trek10inc/awsume/pull/43) For Windows Command Prompt users, saves tmp.txt to aws folder
- [#40](https://github.com/trek10inc/awsume/pull/40) Adds Fish script
- [#48](https://github.com/trek10inc/awsume/pull/48) Allows MFA token to be passed via CLI args
- [#56](https://github.com/trek10inc/awsume/pull/56) Allows calling assume-role with external ID from profile
- [#56](https://github.com/trek10inc/awsume/pull/56) If a profile has a session token, it will use it instead of making the call to get the session token

## [3.2.8] - 2018-4-30 - Bug Fixes

- Creates a dedicated "Unset environment variables" flag
  - `awsume -u` will now unset any AWS or AWSUME environment variables
  - `awsume -u -s` will now show the commands required to unset any AWS or AWSUME environment variables

## [3.2.7] - 2018-4-27 - Bug Fixes

- Prevents installer from creating multiple alias when installing under multiple python versions with pyenv
  - The alias for pyenv installations will now look like this:
  - `alias awsume='. $(pyenv which awsume)'`

## [3.2.6] - 2018-4-27 - Bug Fixes

- Ensures that safe_printing will print to `sys.stderr`

## [3.2.5] - 2018-4-23 - Bug Fixes

- On installations with pyenv, uses correct pyenv root
- Loads awsume options _after_ validating that the aws directories exist

## [3.2.4] - 2018-4-20 - Plugin Error Improvement

- Doesn't display the entire dump of the traceback when an error occurs while loading plugins, will now only display the error message itself
  - If the error is an `ImportError` due to a package not being installed, a custom message will be displayed to install that package

## [3.2.2 - 3.2.3] - 2018-4-13 - Bug Fix

- When using the `-s` flag, it now properly checks to make sure the region is returned from awsume before displaying the commands to set your environment

## [3.2.1] - 2018-4-13 - Bug fixes

- Fixes bug where credentials would be mixed up in the `-s` flag output

## [3.2.0] - 2018-4-13 - Adds custom role session duration support

- There are three ways to use AWSume to call `assume-role` with a custom `duration-seconds`, each with a different priority
  - Using the `--role-duration` flag
    - highest priority
    - `awsume client-dev --role-duration 43200`
    - This will call assume-role with the given value as the `duration-seconds` in the api call
    - Must be between 0 and 43200 (setting it to 0 will always call assume-role without the duration-seconds)
  - Setting a custom aws profile attribute
    - medium priority
    - Setting an individual profile's `role_duration` option will always use the extended duration when `awsume`ing that profile
      ``` ini
      [profile client-dev]
      role_arn = EXAMPLE
      source_profile = my-profile
      role_duration = 43200
      ```
    - NOTE: *This is not a canonical AWS option*
    - Setting to 0 will disable it
  - Setting the global `role-duration` AWSume option
    - lowest priority
    - `awsume --config role-duration 43200`
    - Setting this option will cause AWSume to always use the extended duration (unless the given profile option or cli flag is 0)
    - Setting this option to 0 will disable it
  - NOTE: *if the given role duration is more than the role's configured "Maximum CLI/API Session Duration", an error will be thrown and an attempt at calling `awsume` without a custom role duration will automatically be made*
  - Custom duration role credentials will be cached and used on subsequent `awsume` calls (using a custom role duration) so long as they are valid and not yet expired
- Updates the `--config-help` output to display the current settings
- Disables colored output on Windows
- For plugins: Catches `botocore.exceptions.ParamValidationError` when calling `get-session-token` and `assume-role` and will raise the appropriate AWSume error

## [3.1.0] - 2018-4-6 - Adds global options and color

- Adds a global options
  - A JSON file located here: `~/.aws/awsume.json`
  - Stores AWSume's configuration options
  - Can configure an option with `awsume --config option_name value`
  - Can list options and current settings with `awsume --config-help`
- Adds colored output (on by default)
  - Can disable with `awsume --config colors false`
- For plugins: modifies the `safe_print` function
  - defined: `safe_print(text, end, color, style)`
  - you can pass color codes to print in color
  - backwards compatible with old definition `safe_print(text, end)`

## [3.0.10] - 2018-3-19 - Bug Fixes

- Fixes datetime format for non-mfa required profiles

## [3.0.9] - 2018-3-16 - Bug Fixes

- Exports `AWS_REGION` and `AWS_DEFAULT_REGION` when using autoawsume

## [3.0.5-3.0.8] - 2018-3-15 - Bug Fixes

- Renames `autoAwsume` to `autoawsume`
  - There were a few bugs with having an upper-case letter that would sometimes cause errors when trying to uninstall awsume, so we renamed it to be all lower-case

## [3.0.4] - 2018-3-15 - Bug Fixes

- Removes the dependency for `python-dateutil` which causes bugs with boto3's dependencies

## [3.0.3] - 2018-3-13 - Bug Fixes

- Fixes writing __name__ under each profile
- Fixes session expiration type as string when reading from cache
- Adds more logs

## [3.0.2] - 2018-3-09 - Bug Fixes

- Fixes line endings

## [3.0.1] - 2018-3-01 - Bug Fixes

- Fixes writing alias multiple times

## [3.0.0] - 2018-2-28 - Bug Fixes, Refactoring

- Refactored much of `awsumepy` and the plugin system to be more general and allow more types of plugins
  - Utilizes callbacks and error catching better
  - Adds custom exceptions
  - Now combines credentials and config profiles under the same name
  - Now merges source_profile credentials into their role profiles - everything you'll need is in the given profile
  - Adds `--install-plugin` flag to download/install plugins from given urls
  - Adds `--delete-plugin` flag to delete a plugin given the name
  - Adds `--plugin-info` to display important information on currently-installed plugins
- Moved the `out_data` class into the AWSume app object
  - New format for exporting data:
  ``` python
  {
    'AWSUME_FLAG' : 'Awsume',
    'AWSUME_DATA' : [
      'AWSUME_1',
      'AWSUME_2',
      'AWSUME_3',
      'AWSUME_4',
      'AWSUME_5'
    ]
  }
  ```
- Adds `__exit_awsume` callback to stop a `^C` from spamming your terminal
- The `mfa_serial` of the source profile will be used if the role profile doesn't have an `mfa_serial`

## [2.1.5] - 2018-2-5 - Bug Fix

- Adds newlines around alias definition and auto-complete function declaration when adding to `.bashrc` and other login files

## [2.1.4] - 2018-1-22 - Bug Fix

- Fixes compatibility issues with Git Bash / MINGW64

## [2.1.3] - 2018-1-12 - Bug Fix

- Removes ^M from the shell script

## [2.1.2] - 2018-1-12 - Profile listing output to stdout

- Profile listing outputs to stdout instead of stderr, which is good for using with grep
- Account numbers, when readily available from `mfa_serial` or `role_arn`, will be displayed in the listing too

## [2.1.1] - 2017-12-8 - Bug Fix

- Fixes bug that incorrectly names the `AWSUME_PROFILE` environment variable

## [2.1.0] - 2017-12-8 - SessionName CLI support

- Pull Request from @giuliocalzolari
- Adds ability to set the session name in the CLI

## [2.0.0] - 2017-12-8 - Breaking Changes

- Changes to how plugin functions are to be implemented
- Includes the new `out_data` object that is used to send data to the shell wrappers. It is important that you understand how AWSume and the shell wrappers work before using this.

## [1.3.2] - 2017-10-30 - Region Change

- When using AWSume on a profile in which the region is absent, AWSume will pull the region from the default profile and set the `AWS_REGION` environment variable to that

## [1.3.1] - 2017-10-13 - Bug Fix

- Adds compatibility with pyenv installations
  - Since `awsume` is actually a shell script, and not a python script, pyenv would crash your terminal when calling awsume, this update fixes this issue

## [1.3.0] - 2017-10-06 - Auto-Complete

- Adds auto-completion/tab-completion for Bash, Zsh, and Powershell
- Adds new flag, `--rolesusers`, which is used for only listing the names of each awsume-able profile
- Adds new plugin function type, "rolesusers_func", which is meant for any plugins to list their awsume-able profiles

## [1.2.7] - 2017-09-14 - Bug Fix

- Fixes a list profiles bug

## [1.2.6] - 2017-09-14 - Bug Fix

- Fixes logging bug that causes an error when killing autoAwsume

## [1.2.5] - 2017-09-06 - Bug Fix

- Fixes issue where awsuming with command prompt would not set environment variables

## [1.2.4] - 2017-08-18 - Logging

- Adds two new command-line options: `--info` and `--debug`, both used for logging purposes.
- `--info` will list only basic information about each step in the AWSume process
- `--debug` will list detailed information about what is happening during AWSume's runtime. It will definitely spam your screen if you don't direct it's output elsewhere: most commonly `awsume --debug 2> logs.txt`

## [1.2.3] - 2017-08-16 - Bug Fix

- Fixed bug in which running `awsume -l` would crash for Python 3 users

## [1.2.2] - 2017-08-15 - Compatibility

- Fixed issues around Python 3 compatibility. All features should be compatible with both Python 2 and 3
- Fixed edge case in which there is an auto-refresh role profile in the user's credentials file that the user no longer has permission to assume

## [1.2.1] - 2017-08-02 - Bug Fix

- Fixed logging issue with the plugin manager

## [1.2.0] - 2017-07-28 - Plugin System

- Adds new plugin system, built on the Yapsy plugin manager. Full documentation on the plugin system can be read [here](https://github.com/trek10inc/awsume/blob/master/PluginDocumentation.md)

## [1.1.7] - 2017-07-13 - Bug Fix

- Fixed bug that writes the alias and comment on one line when doing a new install

## [1.1.6] - 2017-07-07 - Bug Fix

- Fixed bug that resets environment variables even when you're using the `-h`, `-l`, `-v`, or `-k` (on a different profile than the current profile)

## [1.1.5] - 2017-07-07 - Bug Fix

- Fixed list_profiles bug

## [1.1.4] - 2017-07-07 - Bug Fix

- Fixed dependency bug

## [1.1.2] - 2017-07-07 - AutoAwsume

- Ability to start an auto-refresher for role credentials
  - One background process will auto-refresh multiple profiles
- Ability to stop auto-refreshing with the `-k` flag
  - Will only stop auto-refreshing the profile passed with the `-k` flag
  - If no profile passed with `-k` flag, all profiles will stop being auto-refreshed
  - When no more profiles are available to be auto-refreshed, the auto-refresher will stop itself
- Check the version of AWSume with `awsume -v`
- Get list of AWSume-able profiles, along with some useful information about each one, with the `-l` option
- Display at the end of running AWSume that lets the user know when their credentials will expire
- Fixed redundant MFA prompt bug
- Replaced the `-n` option with an automatic check for `mfa_serial` in the config profile to determine if MFA is required for that profile

## [1.0.4] - 2017-06-30 - Bug Fixes

- Fixes a couple of bugs

## [1.0.3] - 2017-06-28 - Bug Fixes

- Fixed bug for Zsh users

## [1.0.2] - 2017-06-26 - Minor upgrades/bug fixes

- Correctly handles profiles that don't require MFA Authentication
- Use `-n` option if your profile doesn't require MFA
- Handles Boto errors more thouroughly and cleanly

## [1.0.0] - 2017-06-14 - Initial Release

- Cross-Platform compatibility (Mac, Windows, Linux)
  - Compatible with Bash, Zsh, PowerShell, and Windows Command Prompt
- AWSumePy: the core of AWSume, a Python script
- Simple to install with `pip install awsume`
- AWSume shell-script wrappers made to call AWSume for each platform
- Aliases set in rc files during install, may need to restart shell after install
- Will use the default profile when no profile name is given
- With the `-s` flag, the script will display the commands required to set your profile
- With the `-r` flag, the script will force-refresh your credentials, even if you still have valid credentials cached
- Display usage tips with the `-h` flag
