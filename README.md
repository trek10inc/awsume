# AWSume: AWS Assume Made Awesome
Utility for easily assuming AWS IAM roles from the command line

## Installation

Copy `awsume` to `/usr/local/bin`

`chmod 700 /usr/local/bin/asume`

`alias awsume='. awsume'`

## Setup

Add profiles to `~/.aws/config`

```
# ~/.aws/config
[profile internal-admin]
role_arn = arn:aws:iam::<my aws account id>/role/admin-role
mfa_serial = arn:aws:iam::<my aws account id>:mfa/joel
source_profile = joel

[profile client1-admin]
role_arn = arn:aws:iam::<client #1 account id>/role/admin-role
mfa_serial = arn:aws:iam::<your aws account id>:mfa/joel
source_profile = joel

[profile client2-admin]
role_arn = arn:aws:iam::<client #2 account id>/role/admin-role
mfa_serial = arn:aws:iam::<your aws account id>:mfa/joel
source_profile = joel
```

Add credentials to `~/.aws/credentials`

```
# ~/.aws/credential

[default]
aws_access_key_id = AKIAIOIEUFSN9EXAMPLE
aws_secret_access_key = wJalrXIneUATF/K7MDENG/jeuFHEnfEXAMPLEKEY

[joel]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

Usage: 

awsume profilename [show|refresh]

`awsume client1-admin` Exports into current shell, will ask for MFA if needed

`awsume client1-admin show` Outputs export statements to copy / paste into some other shell, will ask for MFA if needed

`awsume client1-admin refresh` Delete cached credentials and renew, should always prompt for mfa.

See our [blog](https://www.trek10.com/blog/awsume-aws-assume-made-awesome) for more details
