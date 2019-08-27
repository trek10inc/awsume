# Get Credentials

Get credentials

## `get_credentials`

### Parameters

- `config` - a `dict` of awsume's configuration
- `arguments` - an `argparse.Namespace` object containing awsume's arguments
- `profiles` - the collected aws profiles

### Returns

- A `dict` of aws credentials in the following format:

```python
{
  'AccessKeyId': '',
  'SecretAccessKey': '',
  'SessionToken': '',
  'Region': '',
}
```

### Example

```python
import argparse
from awsume.awsumepy import hookimpl

@hookimpl
def get_credentials(config: dict, arguments: argparse.Namespace, profiles: dict):
    # ... handle getting credentials
    return {
        'AccessKeyId': 'AKIA...',
        'SecretAccessKey': 'SECRET',
        'SessionToken': 'LONGSECRET',
        'Region': 'us-east-2',
    }
```

## `get_credentials_with_saml`

This hook will only be called when awsuem is given the `--with-saml` flag, and will prevent other `get_credentials...` hooks from being called. If there is only one role provided in the assertion, it will be used. If there are multiple and `--role-arn` is provided to awsume, it will use the closest match. If there are multiple and `--role-arn` is not provided, it will prompt the user for which role to use.

### Parameters

- `config` - a `dict` of awsume's configuration
- `arguments` - an `argparse.Namespace` object containing awsume's arguments
- `profiles` - the collected aws profiles

### Returns

- A `str` of the saml assertion:

```python
'PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZ...3NhbWwycDpSZXNwb25zZT4='
```

### Example

```python
import argparse
from awsume.awsumepy import hookimpl

@hookimpl
def get_credentials_with_saml(config: dict, arguments: argparse.Namespace, profiles: dict):
    # ... handle getting saml assertion
    saml_assertion = 'PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZ...3NhbWwycDpSZXNwb25zZT4='
    return saml_assertion
```

## `get_credentials_with_web_identity`

This hook will only be called when awsuem is given the `--with-web-identity` flag, and will prevent other `get_credentials...` hooks from being called.

### Parameters

- `config` - a `dict` of awsume's configuration
- `arguments` - an `argparse.Namespace` object containing awsume's arguments
- `profiles` - the collected aws profiles

### Returns

- A `dict` of aws credentials in the following format:

```python
{
  'AccessKeyId': '',
  'SecretAccessKey': '',
  'SessionToken': '',
  'Region': '',
}
```

### Example

```python
import argparse
from awsume.awsumepy import hookimpl

@hookimpl
def get_credentials_with_web_identity(config: dict, arguments: argparse.Namespace, profiles: dict):
    # ... handle getting credentials
    return {
        'AccessKeyId': 'AKIA...',
        'SecretAccessKey': 'SECRET',
        'SessionToken': 'LONGSECRET',
        'Region': 'us-east-2',
    }
```

## `pre_get_credentials`

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
def pre_get_credentials(config: dict, arguments: argparse.Namespace, credentials_file: str, config_file: str):
    safe_print('Before collecting aws profiles')
```

## `post_get_credentials`

### Parameters

- `config` - a `dict` of awsume's configuration
- `arguments` - an `argparse.Namespace` object containing awsume's arguments
- `profiles` - the collected aws profiles
- `credentials` - the returned aws credentials

### Returns

- Nothing

### Example

```python
import argparse
from awsume.awsumepy import hookimpl, safe_print

@hookimpl
def post_get_credentials(config: dict, arguments: argparse.Namespace, profiles: dict, credentials: dict)):
    safe_print('After collecting aws profiles')
```
