# AWSume: AWS Assume Made Awesome

Utility for easily assuming AWS IAM roles from the command line, now in Python!

## What is AWSume?

AWSume is a cross-platform (Mac, Linux, Windows) command-line tool that makes assuming AWS roles and setting user credentials from the AWS CLI easy! It works by scanning your `.aws/config` and `.aws/credentials` files for the profile you give it, making AWS calls to get that profile's credentials, and exporting those credentials to your shell's environment variables. Then, any AWS CLI calls you make in that shell will be under the profile you gave AWSume.

## Installation

### Pip Installation

AWSume has been conveniently wrapped into a Python package and installable with just one simple command:

``` bash
pip install awsume
```

The installer places the python and shell scripts into your python directory. If you're using `Bash` or `Zsh`, the installer will add an alias definition (sources awsume when it's called) to their resource control file, either `.bash_alias`, `.bashrc`, `.bash_profile`, or `.zshrc`. When uninstalling AWSume, the alias definition will not be removed.

Once you have AWSume installed, you're ready to set up AWSume!

## Setup

### Configuring Using The AWS CLI

`aws configure set <key> <value> --profile <profile_name>`

Where:

- `key` is what you would like to set within the `config`/`credentials` file, such as:
  - `aws_access_key_id`, `aws_secret_access_key`, `region`, `output`, `mfa_serial`, `role_arn`, or `source_profile`
- `value` is the value you'd like to set the `key` to
- `profile_name` is the name of the profile you are creating
  - `profile_name` is what you will pass into AWSume

### Configuring Manually

Add profiles to

`~/.aws/config` (for macOS / Linux)

`%userprofile%\.aws\config` (for Windows)

#### ~/.aws/config

``` ini
[default]
region = us-east-1
[profile internal-admin]
role_arn = arn:aws:iam::<your aws account id>:role/admin-role
source_profile = joel
region = us-east-1
[profile client1-admin]
role_arn = arn:aws:iam::<client #1 account id>:role/admin-role
mfa_serial = arn:aws:iam::<your aws account id>:mfa/joel
source_profile = joel
region = us-west-2
[profile client2-admin]
role_arn = arn:aws:iam::<client #2 account id>:role/admin-role
mfa_serial = arn:aws:iam::<your aws account id>:mfa/joel
source_profile = joel
region = us-east-1
```

Add credentials to

`~/.aws/credentials` (for macOS / Linux)

`%userprofile%\.aws\credentials` (for Windows)

#### ~/.aws/credentials

``` ini
[default]
aws_access_key_id = AKIAIOIEUFSN9EXAMPLE
aws_secret_access_key = wJalrXIneUATF/K7MDENG/jeuFHEnfEXAMPLEKEY
[joel]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

### Plugins

AWSume is now extensible. It now comes with a built-in plugin manager! To get started developing plugins, check out our [plugin documentation](https://github.com/trek10inc/awsume/blob/master/PluginDocumentation.md).

#### AWSume Console Plugin

To demonstrate the plugin manager, we've extended the functionality of AWSume through the AWSume Console plugin. This plugin will open the AWS console to the assumed role. Read about it [here](https://github.com/trek10inc/awsume/blob/master/examplePlugin/awsumeConsole.md)

### Example Usages

`awsume client1-source-profile`
Exports `client1-source-profile` credentials into current shell, will ask for MFA if needed

`awsume client1-source-profile -n`
Exports `client1-source-profile` credentials into current shell, will usually not ask for MFA, but it will if `client1-source-profile` is a role profile instead of a source profile, and requires MFA

`awsume client1-admin`
Exports `client1-admin` credentials into current shell, will ask for MFA if needed

`awsume`
Exports the default profile's credentials into current shell, will ask for MFA if needed

`awsume -d`
Exports the default profile's credentials into current shell, will ask for MFA if needed

`awsume client1-admin -s`
Outputs export commands to shell, useful if you want to copy / paste into some other shell, will ask for MFA if needed

`awsume client1-admin -r`
Delete cached credentials and refresh, will always prompt for MFA.

`awsume client1-admin -a`
Exports auto-refresh profile to shell's `AWS_DEFAULT_PROFILE` and `AWS_PROFILE` environment variables, creates a profile in the `.aws/credentials` file called `auto-refresh-client1-admin` that contains profile's role credentials, and spawns a background process to auto-refresh those role credentials when they expire, for as long as the role's source profile is valid.

`awsume client1-admin -k`
Removes the `auto-refresh-client1-admin` profile from the `.aws/credentials` file. If no more `auto-refresh-` profiles are left in the `.aws/credentials` file, the auto-refreshing background process will be killed.

`awsume -k`
Removes all `auto-refresh-` profiles from the `.aws/credentials` file, and kills the auto-refreshing background process.

See our blog posts [AWSume](https://www.trek10.com/blog/awsume-aws-assume-made-awesome/) and [AWSume - Now in Python](https://www.trek10.com/blog/awsume-now-in-python/) for more details.
