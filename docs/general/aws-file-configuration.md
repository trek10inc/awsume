# Configuring `~/.aws/`

You can read the official documentation for this [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html).

In a nutshell, you should have two files relevant to AWS on your machine:

- The Shared Credentials file (usually located in `~/.aws/credentials`)
- The Config file (usually located in `~/.aws/config`)

The credentials file stores things such as your access key ID, your secret access key, and your session token. The config file stores things such as mfa serial numbers, role arns, external IDs, default regions, etc.

Please refer to the official documentation (linked above) for any aws file-related problems.
