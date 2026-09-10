import warnings
from awsume import __data__

__VERSION__ = __data__.version
__NAME__ = __data__.name
__AUTHOR__ = __data__.author
__AUTHOR_EMAIL__ = __data__.author_email
__DESCRIPTION__ = __data__.description
__LICENSE__ = __data__.license
__HOMEPAGE__ = __data__.homepage
__MESSAGE__ = __data__.message

warnings.warn(
    "AWSume is no longer actively maintained. We recommend migrating to the AWS CLI (https://aws.amazon.com/cli/). "
    "The project will remain on PyPI as-is. Feel free to fork it at https://github.com/trek10inc/awsume.",
    DeprecationWarning,
    stacklevel=2,
)
