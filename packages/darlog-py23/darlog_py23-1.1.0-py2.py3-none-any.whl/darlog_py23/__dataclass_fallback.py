# encoding: utf-8
# SPDX-License-Identifier: LGPL-3.0-or-later

"""The last resort dataclass implementation."""

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

from .__str import str_format as _format


def _repr_attr(self, attr_nm):
	val = getattr(self, attr_nm)
	return _format('{}={}', attr_nm, repr(val))


def _repr_attr_list(self, attribs_list):
	# type: (_t.Iterable[str], _T) -> str
	arg_strings = (_repr_attr(self, nm) for nm in attribs_list)
	return _format('{}({})', self.__class__.__name__, ', '.join(arg_strings))


def _repr_func_from_attr_list(
	attribs_list,  # type: _t.Iterable[str]
):
	def _repr(self):
		return _repr_attr_list(self, attribs_list)
	return _repr


def _repr_from_slots(cls):
	# type: (_C) -> _C
	setattr(cls, '__repr__', _repr_func_from_attr_list(cls.__slots__))
	return cls


@_repr_from_slots
class _DataclassParams(object):
	__slots__ = (
		'init',
		'repr', 'eq', 'order', 'unsafe_hash', 'frozen',
		'match_args', 'kw_only', 'slots',
	)

	def __init__(
		self,
		init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False,
		match_args=True, kw_only=False, slots=False, **kwargs
	):
		self.init = bool(init)
		self.repr = bool(repr)
		self.eq = bool(eq)
		self.order = bool(order)
		self.unsafe_hash = bool(unsafe_hash)
		self.frozen = bool(frozen)

		self.match_args = bool(match_args)
		self.kw_only = bool(kw_only)
		self.slots = bool(slots)


_DC_PARAMS = '__dataclass_params__'
_DC_FIELDS_TUPLE = '__dataclass_fields_tuple__'  # NON-default! Stored "just in case".


def _class_field_items(cls):
	# type: (_C) -> _t.Tuple[_t.Tuple[str, _t.Any], ...]
	field_names = (x for x in dir(cls) if not x.startswith('_'))
	field_items = (
		(k, getattr(cls, k, None)) for k in field_names
	)
	return tuple(
		(k, v) for k, v in field_items
		if not callable(v)
	)


def _process_class(
	cls,  # type: _C
	**dc_kwargs
):
	"""The main implementation of dataclass."""
	dc_params = _DataclassParams(**dc_kwargs)
	setattr(cls, _DC_PARAMS, dc_params)

	field_names = tuple(k for k, v in _class_field_items(cls))
	field_names_set = set(field_names)

	setattr(cls, _DC_FIELDS_TUPLE, field_names)

	def _init(self, **init_kwargs):
		for k, v in init_kwargs.items():
			if k not in field_names_set:
				raise TypeError(_format(
					"No such field in dataclass {}: {}", self.__class__.__name__, repr(k)
				))
			setattr(self, k, v)

	def as_tuple(self):
		return tuple(
			getattr(self, x, None) for x in field_names
		)

	def _eq(self, other):
		if other.__class__ is not self.__class__:
			return NotImplemented
		return as_tuple(self) == as_tuple(other)

	for do_attach, method_name, func in (
		(dc_params.init, '__init__', _init),
		(dc_params.repr, '__repr__', _repr_func_from_attr_list(field_names)),
		(dc_params.eq, '__eq__', _eq),
	):
		if do_attach:
			setattr(cls, method_name, func)

	return cls


def dataclass_fallback(
	cls=None,
	init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False,
	match_args=True, kw_only=False, slots=False, **kwargs
):
	# type: (_C, ...) -> _U[_C, _Callable[[_C], _C]]
	"""
	A simplest possible re-implementation as fallback when neither built-in ``dataclass`` nor ``attr.s`` are available.

	It should be used only as the very last resort.
	It doesn't provide any of advanced features and currently implements only:
		* init
		* repr
		* eq

	All the other arguments do nothing and are there just for signature consistency.
	"""
	def wrap(cls):
		return _process_class(
			cls,
			init=init, repr=repr, eq=eq, order=order, unsafe_hash=unsafe_hash, frozen=frozen,
			match_args=match_args, kw_only=kw_only, slots=slots, **kwargs
		)

	if cls is None:
		return wrap
	return wrap(cls)
