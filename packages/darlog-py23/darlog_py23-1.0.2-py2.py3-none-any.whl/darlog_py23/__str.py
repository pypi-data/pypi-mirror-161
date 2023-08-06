# encoding: utf-8
# SPDX-License-Identifier: LGPL-3.0-or-later

"""
"""

import sys as _sys

try:
	import typing as _t
except ImportError:
	pass


def to_least_str(val):
	# type: (...) -> _t.AnyStr
	"""
	Python 2:
		* Try to convert to `str()`. If fails, convert to `unicode()`.
		*
			For custom classes inherited from either of them, try to preserve it
			(`unicode` subclass might be converted to regular `str` if possible).

	Python 3:
		Just an alias for `str()`.
	"""
	if isinstance(val, str):
		return val

	# noinspection PyBroadException
	try:
		return str(val)
	except Exception:
		if isinstance(val, unicode):
			return val
		return unicode(val)


PY3 = _sys.version_info[0] == 3

if PY3:
	to_least_str = str
