import os

__all__ = ['default_data_directory']


def default_data_directory():
    return os.path.expanduser('~/.indiecoin/data')
