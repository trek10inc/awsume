# Catch Exceptions

Catch exceptions

## `catch_profile_not_found_exception`

This will be called when a `ProfileNotFoundError` is raised. That should be raised if a required profile is unable to be found, for instance if you run `awsume <profile>` where `<profile>` is not found in any of the profile sources.

### Parameters

- `config` - a `dict` of awsume's configuration
- `arguments` - an `argparse.Namespace` object containing awsume's arguments
- `profiles` - the collected aws profiles
- `error` - the raised error / exception

### Returns

Nothing

### Example

```python
import argparse
from awsume.awsumepy import hookimpl, safe_print

@hookimpl
def catch_profile_not_found_exception(config: dict, arguments: argparse.Namespace, profiles: dict, error: Exception):
    safe_print('Uh oh, a profile was not found')
```

## `catch_invalid_profile_exception`

This will be called when a `InvalidProfileError` is raised. That should be raised if a profile is incorrectly configured, such as a profile that has an `aws_access_key_id` but not an `aws_secret_access_key`.

### Parameters

- `config` - a `dict` of awsume's configuration
- `arguments` - an `argparse.Namespace` object containing awsume's arguments
- `profiles` - the collected aws profiles
- `error` - the raised error / exception

### Returns

Nothing

### Example

```python
import argparse
from awsume.awsumepy import hookimpl, safe_print

@hookimpl
def catch_invalid_profile_exception(config: dict, arguments: argparse.Namespace, profiles: dict, error: Exception):
    safe_print('Uh oh, a profile was not found')
```

## `catch_user_authentication_error`

This will be called when a `UserAuthenticationError` is raised. That should be raised when a call to get a user's session token fails.

### Parameters

- `config` - a `dict` of awsume's configuration
- `arguments` - an `argparse.Namespace` object containing awsume's arguments
- `profiles` - the collected aws profiles
- `error` - the raised error / exception

### Returns

Nothing

### Example

```python
import argparse
from awsume.awsumepy import hookimpl, safe_print

@hookimpl
def catch_user_authentication_error(config: dict, arguments: argparse.Namespace, profiles: dict, error: Exception):
    safe_print('Uh oh, a profile was not found')
```

## `catch_role_authentication_error`

This will be called when a `RoleAuthenticationError` is raised. That should be raised when a call to assume a role fails.

### Parameters

- `config` - a `dict` of awsume's configuration
- `arguments` - an `argparse.Namespace` object containing awsume's arguments
- `profiles` - the collected aws profiles
- `error` - the raised error / exception

### Returns

Nothing

### Example

```python
import argparse
from awsume.awsumepy import hookimpl, safe_print

@hookimpl
def catch_role_authentication_error(config: dict, arguments: argparse.Namespace, profiles: dict, error: Exception):
    safe_print('Uh oh, a profile was not found')
```
