from pathlib import Path

AWSUME_DIR = Path('~/.awsume').expanduser()
AWSUME_CONFIG = Path('~/.awsume' + '/config.yaml').expanduser()

DEFAULT_CREDENTIALS_FILE = Path('~/.aws/credentials').expanduser()
DEFAULT_CONFIG_FILE = Path('~/.aws/config').expanduser()

AWSUME_CACHE_DIR = Path('~/.awsume/cache').expanduser()
