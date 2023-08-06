# [darlog-py23](https://pypi.org/project/darlog-py23/)

A tiny compatibility module for cross-Python2/3 code.
It's not a replacement for neither ``six`` nor ``__future__`` modules but is more of an extension to them.

Currently, defines only a few functions:

## Contents

### `to_least_str`
Converts the given value to a string:

* Python 2: tries to turn to a `str`, `unicode` if fails.
* Python 3: just an alias for `str()`.

### `@dataclass` decorator
Tries to use the built-in decorator from Py3.10, falls back to 3.7 implementation and, finally, to `attr.s` if available.

If none of those is found, applies a dummy decorator (which does nothing) - just to avoid exceptions.

### `@attrs` decorator
Similarly, tries to use `attr.s` and falls back to built-in `dataclass` (if available) or just a dummy decorator as a last resort.

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
