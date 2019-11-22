import argparse
import logging
from pyconfighelper import ConfigHelper

parser = argparse.ArgumentParser()
parser.add_argument('--path', required=True, help='The path to the JSON file to be encrypted. E.g., ./configs/test/config.json')
parser.add_argument('--kms_project', required=True, help='')
parser.add_argument('--kms_location', required=True, help='')
parser.add_argument('--kms_key_ring', required=True, help='')
parser.add_argument('--kms_key_name', required=True, help='')
parser.add_argument('--debug_level')

args = parser.parse_args()

helper = ConfigHelper(**vars(args))
helper.encrypt_config(args.path)
