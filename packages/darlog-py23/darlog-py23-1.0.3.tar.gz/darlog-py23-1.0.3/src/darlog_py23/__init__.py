# encoding: utf-8
# SPDX-License-Identifier: LGPL-3.0-or-later

"""
A tiny compatibility module for cross-Python2/3 code.
"""

from .__dataclass_attrs import *
from .__str import *


__version_info__ = (1, 0, 3)
__version__ = ".".join(str(x) for x in __version_info__)

__url__ = "https://github.com/Lex-DRL/darlog-py23"
__uri__ = __url__

__author__ = 'Lex Darlog (Lex-DRL)'

__license__ = "LGPL-3.0-or-later"
__copyright__ = "Copyright (c) 2022 Lex Darlog"
