# Configuring `~/.aws/`

Credentials and configuration for AWS access are stored in the AWS "Shared Credentials and Config Files."

The credentials file (usually located in `~/.aws/credentials`) should contain things such as your access key ID, your secret access key, and your session token.

The config file (usually located in `~/.aws/config`) should store things such as MFA serial numbers, role arns, external IDs, default regions, etc.

A single AWS profile can be composed of a section that lives within each of those files (the section name for the config file will always be prefixed with `profile `, except for the default profile).

A simple profile without MFA or a configured region would look like this:

```ini
# ~/.aws/credentials
[dev]
aws_access_key_id = AKIA...
aws_secret_access_key = ABCD...
```

If you want to configure a default region for that profile, you would update your profile to look something like this:

```ini
# ~/.aws/credentials
[dev]
aws_access_key_id = AKIA...
aws_secret_access_key = ABCD...

# ~/.aws/config
[profile dev]
region = us-east-1
mfa_serial = arn:aws:iam::000000000000:mfa/devuser
```

If you want to include an MFA device on your profile to be prompted for an MFA token, you would update your profile to look something like this:

```ini
# ~/.aws/credentials
[dev]
aws_access_key_id = AKIA...
aws_secret_access_key = ABCD...

# ~/.aws/config
[profile dev]
region = us-east-1
mfa_serial = arn:aws:iam::000000000000:mfa/devuser
```

::: warning
Note: Only virtual MFA devices are supported by awsume at this time.
:::

Now let's say there's a cross-account role you want to be able to assume from that original `dev` profile, you'd add an additional profile so your aws files would look like this:

```ini
# ~/.aws/credentials
[dev]
aws_access_key_id = AKIA...
aws_secret_access_key = ABCD...

# ~/.aws/config
[profile dev]
region = us-east-1
mfa_serial = arn:aws:iam::000000000000:mfa/devuser

[profile myrole]
region = us-east-1
source_profile = dev
mfa_serial = arn:aws:iam::111111111111:role/myrole
```

::: tip For more information or other issues
You can read the official documentation for this [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html).
:::
