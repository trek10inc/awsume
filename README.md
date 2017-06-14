# AWSume: AWS Assume Made Awesome
Utility for easily assuming AWS IAM roles from the command line, now in Python!

## Linux / macOS Installation

##### Run these commands:

1. To install AWSumePy:
`pip install awsumepy`
2. To grab the AWSume shell script:
`curl https://raw.githubusercontent.com/trek10inc/awsume/awsumePy/awsumepy/shellScripts/awsume.sh > /usr/local/bin/awsume`
3. To set executable permissions:
`chmod 700 /usr/local/bin/awsume`
4. To set the alias
    - For all future shells:
        - BASH on Linux: `echo "alias awsume='. awsume'" >> ~/.bashrc`
        - BASH on macOS: `echo "alias awsume='. awsume'" >> .bash_profile`
        - ZSH on Linux: `echo "alias awsume='. awsume'" >> ~/.zshrc`
        - ZSH on macOS: `echo "alias awsume='. awsume'" >> .zshrc`
    - For only the current shell:
        - `alias awsume='. awsume'`
5. Now you're ready to use AWSume!

## Windows Installation

##### Run these commands:

1. To install AWSumePy:
`pip install awsumepy`
2. To grab the AWSume shell script:
    - PowerShell: Copy `/awsumepy/awsume.ps1` to a folder on your system
    - Command Prompt: Copy `/awsumepy/awsume.bat` to a folder on your system
3. To add a folder to your `PATH` environment variable:
    - Right click on `This PC` or `My Computer` from the start menu.
    - On the left side, click on `Advanced System Settings`
    - Under the `Advanced` tab, click the `Environment Variables...` button on the bottom
    - For a global installation:
        - Within the `System variables` groupbox, select the `Path` system variable.
        - With the `Path` system variable selcted, click on the `Edit...` button on the bottom.
        - Click the `New` button on the right, and enter the directory to the folder you made for *AWSume*
    - For a user installation:
        - Within the `User variables for [username]` groupbox, select the `Path` system variable.
        - With the `Path` system variable selcted, click on the `Edit...` button beneath that groupbox.
        - Click the `New` button on the right, and enter the directory to the folder you made for *AWSume*
4. Now you're ready to use AWSume!

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

##### ~/.aws/credentials

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