# AWSume: AWS Assume Made Awesome

Utility for easily assuming AWS IAM roles from the command line, now in Python!

## Installation

AWSume has been conveniently wrapped into a Python package and installable with just one simple command:

`pip install awsume`

This will install AWSume from from the Python Package Index. The installer places the python and shell scripts into your python directory. If you're using `Bash` or `Zsh`, the installer will add an alias definition to their resource control file, either `.bash_alias`, `.bashrc`, `.bash_profile`, or `.zshrc`. When uninstalling AWSume, the alias definition will not be removed.

Once you have AWSume installed, you're ready to set up AWSume!

***NOTE**: You must have Python and Pip installed in order to use AWSume. Get them [here](https://www.python.org).*

***NOTE**: Make sure your Python PATH environment variables are set.*

***NOTE**: For Linux / macOS users, restart your terminal after installing to ensure the alias to AWSume is active*

## Setup

Add profiles to

`~/.aws/config` (for macOS / Linux)

`%userprofile%\.aws\config` (for Windows)

Add source profiles to

`~/.aws/credentials` (for macOS / Linux)

`%userprofile%\.aws\credentials` (for Windows)

### ~/.aws/config

```
[profile internal-admin]
role_arn = arn:aws:iam::<your aws account id>/role/admin-role
source_profile = joel
region = us-east-1

[profile client1-admin]
role_arn = arn:aws:iam::<client #1 account id>/role/admin-role
mfa_serial = arn:aws:iam::<your aws account id>:mfa/joel
source_profile = joel
region = us-west-2

[profile client2-admin]
role_arn = arn:aws:iam::<client #2 account id>/role/admin-role
mfa_serial = arn:aws:iam::<your aws account id>:mfa/joel
source_profile = joel
region = us-east-1
```

Add credentials to

`~/.aws/credentials` (for macOS / Linux)

`%userprofile%\.aws\credentials` (for Windows)

### ~/.aws/credentials

```
[default]
aws_access_key_id = AKIAIOIEUFSN9EXAMPLE
aws_secret_access_key = wJalrXIneUATF/K7MDENG/jeuFHEnfEXAMPLEKEY

[joel]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

Usage:

```
awsume [profilename] [-d] [-s] [-r]
    profilename     The profile name (default if left blank)
    -d              Use the default profile
    -s              Show the commands to assume the role
    -r              Force refresh the session
    -n              Attempt to use AWSume without prompting for MFA
```

Examples:

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

See our [blog](https://www.trek10.com/blog/awsume-aws-assume-made-awesome) for more details.
