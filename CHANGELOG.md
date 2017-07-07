# AWSume Changelog

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

### Removed

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
