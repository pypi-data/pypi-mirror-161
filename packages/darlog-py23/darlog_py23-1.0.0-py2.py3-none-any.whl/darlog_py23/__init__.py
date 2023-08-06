# encoding: utf-8
# SPDX-License-Identifier: LGPL-3.0-or-later

"""
A tiny compatibility module for cross-Python2/3 code.
It's not a replacement for neither ``six`` nor ``__future__`` modules but is more of an extension to them.
"""

from .__dataclass_attrs import *
from .__str import *


__version__ = "1.0.0"

__description__ = "A tiny compatibility module for cross-Python2/3 code"
__url__ = "https://github.com/Lex-DRL/darlog-py23"
__uri__ = __url__

__author__ = 'Lex Darlog (DRL)'

__license__ = "LGPL-3.0-or-later"
__copyright__ = "Copyright (c) 2022 Lex Darlog"
