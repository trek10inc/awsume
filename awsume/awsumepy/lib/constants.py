from pathlib import Path
import os

if os.getenv('XDG_CONFIG_HOME'):
    XDG_CONFIG_HOME = Path(os.getenv('XDG_CONFIG_HOME')).expanduser()
    AWSUME_CONFIG = Path(str(XDG_CONFIG_HOME) + '/awsume/config.yaml')
else:
    AWSUME_CONFIG = Path('~/.awsume' + '/config.yaml').expanduser()

if os.getenv('XDG_DATA_HOME'):
    XDG_DATA_HOME = Path(os.getenv('XDG_DATA_HOME')).expanduser()
    AWSUME_DIR = Path(str(XDG_DATA_HOME) + '/awsume')
else:
    AWSUME_DIR = Path('~/.awsume').expanduser()

if os.getenv('XDG_CACHE_HOME'):
    XDG_CACHE_HOME = Path(os.getenv('XDG_CACHE_HOME')).expanduser()
    AWSUME_CACHE_DIR = Path(str(XDG_CACHE_HOME) + '/awsume')
else:
    AWSUME_CACHE_DIR = Path('~/.awsume/cache').expanduser()

DEFAULT_CREDENTIALS_FILE = Path('~/.aws/credentials').expanduser()
DEFAULT_CONFIG_FILE = Path('~/.aws/config').expanduser()

AWSUME_CONFIG_LEGACY_PATH = Path('~/.awsume' + '/config.yaml').expanduser()
IS_USING_XDG_CONFIG_HOME = bool(os.getenv('XDG_CONFIG_HOME'))

AWSUME_CACHE_DIR_LEGACY_PATH = Path('~/.awsume/cache').expanduser()
IS_USING_XDG_CACHE_HOME = bool(os.getenv('XDG_CACHE_HOME'))

AWSUME_DIR_LEGACY_PATH = Path('~/.awsume').expanduser()
IS_USING_XDG_DATA_HOME = bool(Path('~/.awsume').expanduser())
