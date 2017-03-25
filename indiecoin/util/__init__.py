import hashlib
import json
import os

from . import ecdsa
from . import serialization
from .hash import sha256, sha256d

__all__ = [
    'default_data_directory'
]

def default_data_directory():
	return os.path.expanduser('~/.indiecoin/data')