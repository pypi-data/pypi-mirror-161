# encoding: utf-8
# SPDX-License-Identifier: MIT

"""
Copyright (c) 2015 Hynek Schlawack
License: MIT

This module contains copies of some essential functions from the ``attrs`` package.
They're used to make ``dataclass`` fallback behave similarly to ``attrs``.
"""

__url__ = "https://www.attrs.org/"
__uri__ = __url__
__author__ = "Hynek Schlawack"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2015 Hynek Schlawack"


def _determine_attrs_eq_order(cmp, eq, order, default_eq):
	"""
	Validate the combination of *cmp*, *eq*, and *order*. Derive the effective
	values of eq and order.  If *eq* is None, set it to *default_eq*.
	"""
	if cmp is not None and any((eq is not None, order is not None)):
		raise ValueError("Don't mix `cmp` with `eq' and `order`.")

	# cmp takes precedence due to bw-compatibility.
	if cmp is not None:
		return cmp, cmp

	# If left None, equality is set to the specified default and ordering
	# mirrors equality.
	if eq is None:
		eq = default_eq

	if order is None:
		order = eq

	if eq is False and order is True:
		raise ValueError("`order` can only be True if `eq` is True too.")

	return eq, order
