from pathlib import Path
import os

XDG_CONFIG_HOME = Path('~/.config').expanduser()
if os.getenv('XDG_CONFIG_HOME'):
    XDG_CONFIG_HOME = Path(os.getenv('XDG_CONFIG_HOME')).expanduser()

XDG_DATA_HOME = Path('~/.local/share').expanduser()
if os.getenv('XDG_DATA_HOME'):
    XDG_DATA_HOME = Path(os.getenv('XDG_DATA_HOME')).expanduser()

XDG_CACHE_HOME = Path('~/.cache').expanduser()
if os.getenv('XDG_CACHE_HOME'):
    XDG_CACHE_HOME = Path(os.getenv('XDG_CACHE_HOME')).expanduser()

AWSUME_CONFIG = Path(str(XDG_CONFIG_HOME) + '/awsume/config.yaml')
AWSUME_DIR = Path(str(XDG_DATA_HOME) + '/awsume')
AWSUME_CACHE_DIR = Path(str(XDG_CACHE_HOME) + '/awsume')

DEFAULT_CREDENTIALS_FILE = Path('~/.aws/credentials').expanduser()
DEFAULT_CONFIG_FILE = Path('~/.aws/config').expanduser()

