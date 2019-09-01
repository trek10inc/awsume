# Non-Interactive Awsume

You can use awsume in your python scripts to get a boto3 session for any profile you want.

For example, to do this in a python script:

```bash
awsume profile --region us-west-2 --role-duration 2000 --refresh
```

you would do this:

```python
from awsume.awsumepy import awsume

session = awsume('profile', '-r', region='us-west-2', mfa_token='123123')

# The `session` is a boto3.Session object
client = session.client('sts')
result = client.get_caller_identity()
```

This function call delegates to awsume's main driver, so it'll take advantage of all the caching, plugins, and other good parts of awsume for you. The `awsume` function definition looks like this:

```python
def awsume(profile_name: str = None, *args: list, **kwargs: dict) -> boto3.Session:
```

- **profile_name** The name of the profile to awsume
- **args** You can supply a list of command-line flags to awsume (like `-r` to force_refresh your credentials)
- **kwargs** You can supply a list of long command-line flags to awsume

For any keyword argument supplied, it will be converted from `this_case` to `--this-case` before being sent to the awsume driver. This means that the following two lines are identical:

```python
awsume('profile', '--mfa-token', '123123')
awsume('profile', mfa_token='123123')
```

If you specify a keyword argument to be a boolean, it will not pass the value to awsume, instead treating the argument like a on/off flag. The following two lines are identical:

```python
awsume('profile', refresh=True)
```

```bash
awsume profile --refresh
```

## Notes

Note, that awsume was developed as a command-line tool, so there may be some strange behaviour with certain commands. For instance, if you run this:

```python
from awsume.awsumepy import awsume

session = awsume('profile', '-l')
client = session.client('sts')
result = client.get_caller_identity()
print(result)
```

awsume will be told to list the available profiles and exit, since that's what the `-l` flag is meant to do. So this will exit your script before it creates a client and prints the caller's identity.

This functionality is intended for situations where you want a boto3 session for any given profile.
