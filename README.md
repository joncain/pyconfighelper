## Installation

pip3 install pyconfighelper

## Documentation

See the pydoc command: `pydoc3 pyconfighelper`

## Example Usage

```
import logging
from pyconfighelper import ConfigHelper

helper = ConfigHelper(
    kms_project='my-google-cloud-platform-project',
    kms_location='global',
    kms_key_ring='my-kms-key-ring',
    kms_key_name='my-kms-key-name',
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

## Encrypting Configs

This command encrypts a JSON configuration file. It outputs two files (dek.enc, config.enc) that are to be uploaded to Github.

`python3 -m pyconfighelper.encryptconfig --path ./config.json --kms_project myproject --kms_location global --kms_key_ring mykeyring --kms_key_name mykeyname`

## Suggested Reading
https://cloud.google.com/kms/docs/encrypt-decrypt

https://cloud.google.com/kms/docs/envelope-encryption