# encoding: utf-8
# SPDX-License-Identifier: LGPL-3.0-or-later

"""
"""

try:
	import typing as _t
except ImportError:
	pass

from .__py_ver import *


# noinspection PyBroadException
try:
	# noinspection PyShadowingBuiltins
	unicode = unicode
except Exception:
	# noinspection PyShadowingBuiltins
	unicode = str


def to_least_str(val):
	# type: (...) -> _t.AnyStr
	"""
	Python 2:
		* Try to convert to ``str()``. If fails, convert to ``unicode()``.
		*
			For custom classes inherited from either of them, try to preserve it
			(`unicode` subclass might be converted to regular `str` if possible).

	Python 3:
		Just an alias for ``str()``.
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


def str_format(format_pattern, *args, **kwargs):
	# type: (_t.AnyStr, _t.Any, _t.Any) -> _t.AnyStr
	"""
	Python 2:
		Unicode-safe string format. Just performs ``unicode.format()`` if ``str.format()`` fails.

	Python 3:
		Just an alias for ``str.format``.
	"""
	# noinspection PyBroadException
	try:
		return format_pattern.format(*args, **kwargs)
	except Exception:
		return unicode(format_pattern).format(*args, **kwargs)


if PY3:
	to_least_str = str
	str_format = str.format
