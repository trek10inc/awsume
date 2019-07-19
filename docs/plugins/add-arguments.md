# Add Arguments

You can add your own custom arguments to awsume.

## `add_arguments`

### Parameters

- `parser` - an `argparse.ArgumentParser` object

### Returns

- Nothing

### Example

```python
import argparse
from awsume.awsumepy import hookimpl

@hookimpl
def add_arguments(parser: argparse.ArgumentParser):
    try:
        parser.add_argument('--test')
    except argparse.ArgumentError:
        # handle argument already taken here
        pass
```

::: tip
It's recommended to add a `try`/`except` around the addition of arguments like below in order to prevent awsume from ceasing to function for users of your plugin if your plugin's arguments conflict with another installed plugin's arguments.
:::

## `pre_add_arguments`

### Parameters

- `config` - a `dict` of awsume's configuration

### Returns

- Nothing

### Example

```python
import argparse
from awsume.awsumepy import hookimpl, safe_print

@hookimpl
def pre_add_arguments(config: dict):
    safe_print('Before adding arguments')
```

## `post_add_arguments`

### Parameters

- `config` - a `dict` of awsume's configuration
- `arguments` - an `argparse.Namespace` object containing awsume's arguments
- `parser` - an `argparse.ArgumentParser` object

### Returns

- Nothing

### Example

```python
import argparse
from awsume.awsumepy import hookimpl, safe_print

@hookimpl
def post_add_arguments(config: dict, arguments: argparse.Namespace, parser: argparse.ArgumentParser):
    if arguments.test:
        safe_print('Custom flag was triggered')
```
