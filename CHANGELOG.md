# AWSume Changelog

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

### Added

- Adds new plugin system, built on the Yapsy plugin manager. Full documentation on the plugin system can be read [here](https://github.com/trek10inc/awsume/blob/master/PluginDocumentation.md)

## [1.1.7] - 2017-07-13 - Bug Fix

### Changed

- Fixed bug that writes the alias and comment on one line when doing a new install

## [1.1.6] - 2017-07-07 - Bug Fix

### Changed

- Fixed bug that resets environment variables even when you're using the `-h`, `-l`, `-v`, or `-k` (on a different profile than the current profile)

## [1.1.5] - 2017-07-07 - Bug Fix

### Changed

- Fixed list_profiles bug

## [1.1.4] - 2017-07-07 - Bug Fix

### Changed

- Fixed dependency bug

## [1.1.2] - 2017-07-07 - AutoAwsume

### Added

- Ability to start an auto-refresher for role credentials
  - One background process will auto-refresh multiple profiles
- Ability to stop auto-refreshing with the `-k` flag
  - Will only stop auto-refreshing the profile passed with the `-k` flag
  - If no profile passed with `-k` flag, all profiles will stop being auto-refreshed
  - When no more profiles are available to be auto-refreshed, the auto-refresher will stop itself
- Check the version of AWSume with `awsume -v`
- Get list of AWSume-able profiles, along with some useful information about each one, with the `-l` option
- Display at the end of running AWSume that lets the user know when their credentials will expire

### Changed

- Fixed redundant MFA prompt bug
- Replaced the `-n` option with an automatic check for `mfa_serial` in the config profile to determine if MFA is required for that profile


## [1.0.4] - 2017-06-30 - Bug Fixes

### Changed

- Fixes a couple of bugs

## [1.0.3] - 2017-06-28 - Bug Fixes

### Changed

- Fixed bug for Zsh users

## [1.0.2] - 2017-06-26 - Minor upgrades/bug fixes

### Added

- Correctly handles profiles that don't require MFA Authentication
- Use `-n` option if your profile doesn't require MFA

### Changed

- Handles Boto errors more thouroughly and cleanly

## [1.0.0] - 2017-06-14 - Initial Release

### Added

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
