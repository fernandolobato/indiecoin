# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import indiecoin

from indiecoin import *

GENESIS_BLOCK_HASH = '1465242b9a4e246136f1d76344d625efff9acb6b33525eed1c1373b9225a21c2'
PUBLIC_KEY_GENESIS = '005ec5005a6e1dc0fad36333b839f5351190090cd3ed57879a0b664f1504fe04f108e586112033129ddb28653f0289f417c354cb358df7adb9ca4a8007777daedd5d01e0b49e11e51dce33063c0241f03ed0afa5f1e11a577b96e580fec6c1cc9f047c22b9881da9bbf9818f00a69005607d72b75d42f954621df4591f56a246fdda3837'
PRIVATE_KEY_GENESIS = '00111d177ecf44401f55ef98d9a06884b21c640606b64d0692f9c9ad2959af10b93530fb8d117e29c6a728b6298dfd49e2b7d427ad3e7b81c6ceb93b8b76f48b4d3e'