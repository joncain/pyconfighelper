"""
pyconfighelper

Retrieve an encrypted JSON configuration file from Github and decrypt it. Encryption/Decryption is performed via Google Cloud KMS keys.
"""

import logging
from google.cloud import kms_v1 as kms
import base64
import json
import requests
import os
from cryptography.fernet import Fernet
from pathlib import Path


class ConfigHelper:
    def __init__(self, **kwargs):
        """
        Setup internal variables and logger.

        Keyword arguments:
        kms_project -- Google Cloud Platform project
        kms_location -- Google Cloud Location
        kms_key_ring -- Google Cloud KMS Key Ring
        kms_key_name -- Google Cloud KMS Key
        log_level -- Preferred logging level (default logging.WARNING)
        """

        log_level = kwargs.get('log_level') if kwargs.get('log_level') != None else logging.WARNING

        formatter = logging.Formatter('%(name)s %(levelname)s: %(message)s')
        handler = logging.StreamHandler()
        handler.setLevel(log_level)
        handler.setFormatter(formatter)
        self._log = logging.getLogger('ConfigHelper')
        self._log.setLevel(log_level)
        self._log.addHandler(handler)

        try:
            self._kms_project = kwargs['kms_project']
            self._kms_location = kwargs['kms_location']
            self._kms_key_ring = kwargs['kms_key_ring']
            self._kms_key_name = kwargs['kms_key_name']
        except KeyError:
            self._log.exception('Missing required kwarg')

        self._client = kms.KeyManagementServiceClient()

    def get_kek_path(self):
        """Build Google Cloud KMS Crypto Key path."""
        path = self._client.crypto_key_path_path(self._kms_project, self._kms_location, self._kms_key_ring, self._kms_key_name)
        self._log.debug('kek_path: %s', path)
        return path

    def get_remote_file(self, url, token):
        """
        Get Github file contents specified by url.

        Keyword arguments:
        url -- Github url of file to get
        token -- A token string produced by the encode_secret() method
        """
        self._log.debug('Getting remote file: %s', url)
   
        try:
            resp = requests.get(url, headers={'Authorization':'Basic {}'.format(self.decode_token(token))})
            self._log.debug('response status_code: %s', resp.status_code)

            if resp.status_code == 200:
                payload = resp.json()
                self._log.debug('response json: %s', payload)
                return base64.b64decode(payload['content'])
            else:
                resp.raise_for_status()
        except Exception:
            self._log.exception('Error getting remote file: %s.', url)

    def encrypt(self, text):
        """
        Encrypt text using Google Cloud KMS key.
        
        Keyword arguments:
        text -- string to be encrypted
        """
        response = self._client.encrypt(self.get_kek_path(), text.encode('utf-8'))
        return response.ciphertext

    def decrypt(self, bytes):
        """
        Decrypt bytes using Google Cloud KMS key.

        Keyword arguments:
        bytes -- bytes object to be decrypted
        """
        response = self._client.decrypt(self.get_kek_path(), bytes)
        return response.plaintext

    def encode_secret(self, secret):
        """
        Encrypt/Encode the secret and return a token.
        
        Keyword arguments:
        secret -- Basic access authentication string in the form of github_user:github_secret
        """
        encoded_secret = base64.b64encode(secret.encode('ascii'))
        encrypted_secret = self.encrypt(encoded_secret.decode('ascii'))
        return base64.b64encode(encrypted_secret).decode('utf-8')

    def decode_token(self, token):
        """
        Decode/Decrypt token to a Basic access authentication format.
        
        Keyword arguments:
        token -- A token string produced by the encode_secret() method
        """
        decoded_token = base64.b64decode(token)
        return self.decrypt(decoded_token).decode('utf-8')

    def get_config(self, base_url, token):
        """
        Get encrypted configuration file from Github, decrypt it, and return a Dictionary.

        Keyword arguments:
        base_url -- The base github URL for the `config.enc` and `dek.enc` files
        """
        self._log.debug('base_url: %s', base_url)

        if base_url.endswith('/') == False:
            base_url += '/'

        encrypted_dek = self.get_remote_file(base_url + 'dek.enc', token)

        if encrypted_dek == None:
            raise ValueError('dek.enc file could not be retrieved. Check previous log entries for HTTP errors.')

        dek = self.decrypt(encrypted_dek)
        self._log.debug('dek: %s', dek)

        encrypted_config = self.get_remote_file(base_url + 'config.enc', token)

        if encrypted_config == None:
            raise ValueError('config.enc file could not be retrieved. Check previous log entries for HTTP errors.')

        f = Fernet(dek)
        decrypted_config = f.decrypt(encrypted_config)
        config = json.loads(decrypted_config)
        return config

    def encrypt_config(self, config_file_path):
        """
        Encrypt JSON configuration file. Output dek.enc and config.enc
        files that are to be uploaded to Github.

        Keyword arguments:
        config_file_path -- The path to the JSON file to be encrypted.
        """
        fs = open(config_file_path, mode='r')
        config = fs.read()

        try:
            json.loads(config)
        except:
            self._log.debug('config: %s', config)
            self._log.exception('Config contents could not be parsed as JSON.')

        output_path = os.path.dirname(fs.name)
        self._log.debug('output_path: %s', output_path)

        # Generate a dek.enc file
        dek = Fernet.generate_key()
        encrypted_dek = self.encrypt(dek.decode('utf-8'))
        dek_path = Path(os.path.join(output_path, 'dek.enc'))
        with dek_path.open(mode='wb') as f:
            f.write(encrypted_dek)

        # Encrypt and write config.enc file
        f = Fernet(dek)
        encrypted_config = f.encrypt(config.encode('utf-8'))
        cfg_path = Path(os.path.join(output_path, 'config.enc'))
        with cfg_path.open(mode='wb',) as f:
            f.write(encrypted_config)