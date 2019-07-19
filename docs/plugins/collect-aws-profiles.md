# Collect AWS Profiles

Collect AWS Profiles

## `collect_aws_profiles`

### Parameters

- `config` - a `dict` of awsume's configuration
- `parser` - an `argparse.ArgumentParser` object
- `credentials_file` - the path to the aws shared credentials file to be used
- `config_file` - the path to the aws config file to be used

### Returns

- A `dict` of profiles in the following format:

```python
{
  'profile_name': {
    'profile_key': 'profile_value',
  },
}
```

Review the [official documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) for the various acceptable `profile_key`s.

### Example

```python
import argparse
from awsume.awsumepy import hookimpl

@hookimpl
def collect_aws_profiles(config: dict, arguments: argparse.Namespace, credentials_file: str, config_file: str):
    return {
        'profile1': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
            'region': 'us-west-2',
        },
        'profile2': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
            'mfa_serial': 'arn:aws:iam::123123123123:mfa/user',
        },
        'profile3': {
            'role_arn': 'AKIA...',
            'mfa_serial': 'arn:aws:iam::123123123123:mfa/user',
            'source_profile': 'profile2',
        },
    }
```

## `pre_collect_aws_profiles`

### Parameters

- `config` - a `dict` of awsume's configuration
- `parser` - an `argparse.ArgumentParser` object
- `credentials_file` - the path to the aws shared credentials file to be used
- `config_file` - the path to the aws config file to be used

### Returns

- Nothing

### Example

```python
import argparse
from awsume.awsumepy import hookimpl, safe_print

@hookimpl
def pre_collect_aws_profiles(config: dict, arguments: argparse.Namespace, credentials_file: str, config_file: str):
    safe_print('Before collecting aws profiles')
```

## `post_collect_aws_profiles`

### Parameters

- `config` - a `dict` of awsume's configuration
- `arguments` - an `argparse.Namespace` object containing awsume's arguments
- `profiles` - the collected aws profiles

### Returns

- Nothing

### Example

```python
import argparse
from awsume.awsumepy import hookimpl, safe_print

@hookimpl
def post_collect_aws_profiles(config: dict, arguments: argparse.Namespace, profiles: dict):
    safe_print('After collecting aws profiles')
```
