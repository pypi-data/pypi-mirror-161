# encoding: utf-8
# SPDX-License-Identifier: LGPL-3.0-or-later

"""
"""

import sys as _sys


PY2 = _sys.version_info[0] == 2
PY3 = _sys.version_info[0] == 3
PY310 = _sys.version_info[0:2] >= (3, 10)
