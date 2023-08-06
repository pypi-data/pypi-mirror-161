# [darlog-py23](https://pypi.org/project/darlog-py23/)

A tiny compatibility module for cross-Python2/3 code.
It's not a replacement for neither ``six`` nor ``__future__`` modules but is more of an extension to them.

Defines the very basic stuff:

## Python version booleans
`PY2`, `PY3`, `PY310` - simple flags indicating whether you're running under Python 2, 3 or 3.10+.

## Strings
### `unicode`
Type alias:

* Python 2 - `unicode`
* Python 3 - `str`

### `to_least_str()`
Converts the given value to a string:

* Python 2: tries to turn to a `str`, `unicode` if fails.
* Python 3: just an alias for `str()`.

### `str_format()`
Formats a string and doesn't throw an error if any of the given arguments is unicode under Python 2. The resulting string is simply turned to unicode, too.

## DataClasses
### `@attrs` decorator
Tries to use `attr.s` and if it's not found, falls back to built-in decorator from Py3.10 and, finally to 3.7 implementation if available.

If none of those is found, applies the included dataclass implementation, the simplest possible one (`@dataclass_fallback`, see below) - as the last resort, just to avoid exceptions.

### `@dataclass` decorator
Similar to `@attrs`, but tries built-in `@dataclass` first.

I'd recommend using `@attrs` anyway, but here it is.

Tries to use the built-in decorator from Py3.10, falls back to 3.7 implementation, then to `attr.s`. And, finally, to the included `@dataclass_fallback`.

### `@dataclass_fallback` decorator
The minimal implementation of `dataclass` working in any Python version above 2.7. Implements only `init`, `repr` and `eq` features.

It doesn't do any "attribute is `Field` instance" stuff or any other `getattr`/`setattr` magic.

This is what both `@dataclass` and `@attrs` fall back to as the last resort. I don't know why would you need it explicitly, though - but here it is.

## Installation

```shell script
python -m pip install -U darlog-py23
```

## Development

You can clone the git repo and add the contents of `src/` directory to your python installation by running this command in the repo root:
```shell script
python -m pip install -e .[dev]
```

The version is specified in the main `__init__.py` file. To update the binary distribution (wheel), run:
```shell script
python setup.py bdist_wheel sdist
```
