# Get Profile Names

Get profile names

## `get_profile_names`

### Parameters

- `config` - a `dict` of awsume's configuration
- `arguments` - an `argparse.Namespace` object containing awsume's arguments

### Returns

- A `list` of profiles names in the following format:

```python
[
    'profile-name1',
    'profile-name2',
    '...',
]
```

### Example

```python
import argparse
from awsume.awsumepy import hookimpl

@hookimpl
def get_profile_names(config: dict, arguments: argparse.Namespace):
    return [
        'profile1',
        'profile2',
        'profile3',
    ]
```
