# encoding: utf-8
# SPDX-License-Identifier: LGPL-3.0-or-later

"""
Defines ``dataclass`` decorator regardless of Python version.
On versions below 3.7, attempts to use ``attr.s`` and falls back to an empty (dummy) decorator
if no implementation is found.

Similarly, it defines ``attrs`` which tries to fall back to ``dataclass`` if found.
"""

try:
	import typing as _t
	from typing import (
		Callable as _Callable,
		Union as _U,
		Protocol as _Protocol
	)

	# noinspection PyTypeHints
	_T = _t.TypeVar('T')
	# noinspection PyTypeHints
	_C = _t.TypeVar('C', bound=type)
	# noinspection PyTypeHints
	_Call = _t.TypeVar('Call', bound=callable)
except ImportError:
	pass

try:
	from dataclasses import dataclass as _dataclass_raw
	_dataclass_import_error = None
except ImportError as _e:
	_dataclass_import_error = _e

try:
	import attr as _attr
	_attrs_import_error = None
except ImportError as _e:
	_attrs_import_error = _e

from .__attrs import _determine_attrs_eq_order

import sys as _sys


PY310 = _sys.version_info[0:2] >= (3, 10)


def _dataclass_wrapper_py37(
	cls=None,
	init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False,
	match_args=True, kw_only=False, slots=False, **kwargs
):
	# type: (_C, bool, ...) -> _U[_C, _Callable[[_C], _C]]
	return _dataclass_raw(cls, init=init, repr=repr, eq=eq, order=order, unsafe_hash=unsafe_hash, frozen=frozen)

def _dataclass_wrapper_py310(
	cls=None,
	init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False,
	match_args=True, kw_only=False, slots=False, **kwargs
):
	# type: (_C, bool, ...) -> _U[_C, _Callable[[_C], _C]]
	return _dataclass_raw(
		cls, init=init, repr=repr, eq=eq, order=order, unsafe_hash=unsafe_hash, frozen=frozen,
		match_args=match_args, kw_only=kw_only, slots=slots,
	)

def _dataclass_with_attrs(
	cls=None,
	init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False,
	match_args=True, kw_only=False, slots=False, **kwargs
):
	# type: (_C, bool, ...) -> _U[_C, _Callable[[_C], _C]]
	decorator = _attr.s(
		auto_detect=False, init=init, repr=repr, eq=eq, order=order, hash=unsafe_hash,
		frozen=frozen, match_args=match_args, kw_only=kw_only, slots=slots,
	)

	if cls is None:
		return decorator
	return decorator(cls)


def dummy_decorator(func=None, **kwargs):
	# type: (_Call, ...) -> _U[_Call, _Callable[[_Call], _Call]]
	"""Decorator placeholder which does nothing."""
	def _wrap(f):
		# type: (_Call) -> _Call
		return f

	if func is None:
		return _wrap
	return _wrap(func)


def dummy_class_decorator(cls=None, **kwargs):
	# type: (_C, ...) -> _U[_C, _Callable[[_C], _C]]
	"""Same as ``dummy_decorator``, but type-hinted to be dealing with classes."""
	def _wrap(c):
		# type: (_C) -> _C
		return c

	if cls is None:
		return _wrap
	return _wrap(cls)


if _dataclass_import_error is None:
	dataclass = _dataclass_wrapper_py310 if PY310 else _dataclass_wrapper_py37
elif _attrs_import_error is None:
	dataclass = _dataclass_with_attrs
else:
	dataclass = dummy_class_decorator


def _attrs_with_dataclass_py37(
	maybe_cls=None,
	these=None, repr_ns=None,

	init=True, repr=True, eq=True, order=False, hash=None, frozen=False,
	match_args=True, kw_only=False, slots=False,

	cmp=None, weakref_slot=True, str=False, auto_attribs=False,
	cache_hash=False, auto_exc=False, auto_detect=False, collect_by_mro=False, getstate_setstate=None,
	on_setattr=None, field_transformer=None,
):
	# type: (_C, ...) -> _U[_C, _Callable[[_C], _C]]
	eq, order = _determine_attrs_eq_order(cmp, eq, order, None)
	repr = repr or str

	def wrap(cls):
		# type: (_C) -> _C
		cls = _dataclass_raw(
			cls, init=init, repr=repr, eq=eq, order=order, unsafe_hash=hash, frozen=frozen,
		)
		if str:
			cls.__str__ = cls.__repr__
		return cls

	if maybe_cls is None:
		return wrap
	return wrap(maybe_cls)


def _attrs_with_dataclass_py310(
	maybe_cls=None,
	these=None, repr_ns=None,

	init=True, repr=True, eq=True, order=False, hash=None, frozen=False,
	match_args=True, kw_only=False, slots=False,

	cmp=None, weakref_slot=True, str=False, auto_attribs=False,
	cache_hash=False, auto_exc=False, auto_detect=False, collect_by_mro=False, getstate_setstate=None,
	on_setattr=None, field_transformer=None,
):
	# type: (_C, ...) -> _U[_C, _Callable[[_C], _C]]
	eq, order = _determine_attrs_eq_order(cmp, eq, order, None)
	repr = repr or str

	def wrap(cls):
		# type: (_C) -> _C
		cls = _dataclass_raw(
			cls, init=init, repr=repr, eq=eq, order=order, unsafe_hash=hash, frozen=frozen,
			match_args=match_args, kw_only=kw_only, slots=slots,
		)
		if str:
			cls.__str__ = cls.__repr__
		return cls

	if maybe_cls is None:
		return wrap
	return wrap(maybe_cls)


if _attrs_import_error is None:
	attrs = _attr.s
elif _dataclass_import_error is None:
	attrs = _attrs_with_dataclass_py310 if PY310 else _attrs_with_dataclass_py37
else:
	attrs = dummy_class_decorator
