## Installation

pip3 install pyconfighelper

## Documentation

See the pydoc command: `pydoc3 pyconfighelper`

## Usage Example

```
import logging
from pyconfighelper import ConfigHelper

helper = ConfigHelper(
    environment='test',
    kms_project='my-google-cloud-platform-project',
    kms_location='global',
    kms_key_ring='my-kms-key-ring',
    kms_key='my-kms-key-name',
    log_level=logging.DEBUG)

# This token should be stored in a secure location to be
# consumed by your runtime environment. The encode_secret() method
# is intended as a utility to generate tokens, not a runtime method.
#
# Replace <github_user> and <github_secret> with your values.
token = helper.encode_secret('<github_user>:<github_secret>')

# Replace <github_user>, <github_repo>, and <path_to_config> with your values
base_github_url = 'https://api.github.com/repos/<github_user>/<github_repo>/contents/<path_to_config>'

config = helper.get_config(base_github_url, token)

print(config)
```
