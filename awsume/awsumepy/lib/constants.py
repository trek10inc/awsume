from pathlib import Path
import os

IS_USING_XDG_CONFIG_HOME = bool(os.getenv('XDG_CONFIG_HOME'))
IS_USING_XDG_DATA_HOME = bool(os.getenv('XDG_DATA_HOME'))
IS_USING_XDG_CACHE_HOME = bool(os.getenv('XDG_CACHE_HOME'))

AWSUME_DIR_LEGACY_PATH = Path('~/.awsume').expanduser()
AWSUME_CONFIG_LEGACY_PATH = Path('~/.awsume' + '/config.yaml').expanduser()
AWSUME_CACHE_DIR_LEGACY_PATH = Path('~/.awsume/cache').expanduser()

if IS_USING_XDG_CONFIG_HOME:
    XDG_CONFIG_HOME = Path(os.getenv('XDG_CONFIG_HOME')).expanduser()
    AWSUME_CONFIG = XDG_CONFIG_HOME / 'awsume/config.yaml'
else:
    AWSUME_CONFIG = AWSUME_CONFIG_LEGACY_PATH

if IS_USING_XDG_DATA_HOME:
    XDG_DATA_HOME = Path(os.getenv('XDG_DATA_HOME')).expanduser()
    AWSUME_DIR = XDG_DATA_HOME / 'awsume'
else:
    AWSUME_DIR = AWSUME_DIR_LEGACY_PATH

if IS_USING_XDG_CACHE_HOME:
    XDG_CACHE_HOME = Path(os.getenv('XDG_CACHE_HOME')).expanduser()
    AWSUME_CACHE_DIR = XDG_CACHE_HOME / 'awsume'
else:
    AWSUME_CACHE_DIR = AWSUME_CACHE_DIR_LEGACY_PATH

DEFAULT_CREDENTIALS_FILE = Path('~/.aws/credentials').expanduser()
DEFAULT_CONFIG_FILE = Path('~/.aws/config').expanduser()

AWSUME_LOG_DIR = AWSUME_DIR / 'logs'
AWSUME_LOG_DIR.mkdir(parents=True, exist_ok=True)
AWSUME_LOG_FILE = AWSUME_LOG_DIR / 'awsume.log'
AWSUME_AUTOCOMPLETE_FILE = AWSUME_DIR / 'autocomplete.json'
