

import hashlib

__all__ = ['sha256', 'sha256d']



def sha256(data):
    return hashlib.sha256(data).hexdigest()

def sha256d(data):
    return sha256(sha256(data))
