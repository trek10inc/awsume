# AWSume: AWS Assume Made Awesome
Utility for easily assuming AWS IAM roles from the command line, now in Python!

## macOS / Linux Installation

### Fast Install

Run the command for your shell then start a new shell:

bash: `command-to-install-awsume-in-bash`

zsh: `command-to-install-awsume-in-zsh`

### Manual Steps

Copy `awsume.py` and `awsume.sh` to `/usr/local/bin`

Run these commands

`chmod 700 /usr/local/bin/awsume.py`

`chmod 700 /usr/local/bin/awsume.sh`

`alias awsume='. awsume'`

## Windows Installation

### Command Prompt / PowerShell

Copy 

`awsume.bat` (for Command Prompt), or

`awsume.ps1` (for PowerShell)

 to a folder on your machine, along with `awsume.py`.

Add the folder to `Path` in the user variables section of environment variables.

## Setup

Add profiles to

`~/.aws/config` (for macOS / Linux)

`%userprofile%\.aws\config` (for Windows)

##### ~/.aws/config

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

##### ~/.aws/credential

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
```

Examples:

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

See our [blog](https://www.trek10.com/blog/awsume-aws-assume-made-awesome) for more details