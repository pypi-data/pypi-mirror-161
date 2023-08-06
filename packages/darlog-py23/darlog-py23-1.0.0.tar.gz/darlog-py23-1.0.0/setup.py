#!/usr/bin/env python
# encoding: utf-8

"""
https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#setup-args
"""

import codecs
from os import path
import re

from setuptools import find_packages, setup

NAME = "darlog-py23"
KEYWORDS = ["2to3", "3to2", "six", "compatibility", "wrapper"]
CLASSIFIERS = [
	# https://pypi.org/classifiers/
	"Development Status :: 5 - Production/Stable",
	"Intended Audience :: Developers",
	"License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
	"Natural Language :: English",
	"Operating System :: OS Independent",
	"Programming Language :: Python",
	"Programming Language :: Python :: 2",
	"Programming Language :: Python :: 2.7",
	"Programming Language :: Python :: 3",
	"Programming Language :: Python :: 3.7",
	"Programming Language :: Python :: 3.8",
	"Programming Language :: Python :: 3.9",
	"Programming Language :: Python :: 3.10",
	"Topic :: Software Development :: Libraries :: Python Modules",
	"Typing :: Typed",
]
INSTALL_REQUIRES = ["six"]
EXTRAS_REQUIRE = {
	"dev": ["attrs"],
}

META_PATH = path.join("src", "darlog_py23", "__init__.py")

HERE = path.abspath(path.dirname(__file__))


def read_utf8(*parts):
	"""
	Copyright (c) 2015 Hynek Schlawack
	License: MIT

	Utility function borrowed from ``attrs`` package.

	Build an absolute path from *parts* and return the contents of the resulting file.
	"""
	with codecs.open(path.join(HERE, *parts), "rb", encoding="utf-8") as f:
		return f.read()


META_FILE = read_utf8(META_PATH)


def find_meta(meta):
	"""
	Copyright (c) 2015 Hynek Schlawack
	License: MIT

	Utility function borrowed from ``attrs`` package.

	Extract __*meta*__ from META_FILE.
	"""
	meta_match = re.search(
		r"^__{meta}__\s*=\s*['\"]([^'\"]*)['\"]".format(meta=meta), META_FILE, re.M
	)
	if meta_match:
		return meta_match.group(1)
	raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))


AUTHOR = find_meta("author")

LONG = read_utf8("README.md")

if __name__ == '__main__':
	setup(
		name=NAME,
		version=find_meta("version"),
		description=find_meta("description"),
		long_description=LONG,
		long_description_content_type="text/markdown",  # https://packaging.python.org/en/latest/specifications/core-metadata/#description-content-type-optional

		url=find_meta("url"),
		author=AUTHOR,
		maintainer=AUTHOR,
		license=find_meta("license"),

		classifiers=CLASSIFIERS,
		keywords=KEYWORDS,

		package_dir={"": "src"},
		packages=find_packages(where="src"),
		python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*, <4",
		install_requires=INSTALL_REQUIRES,
		extras_require=EXTRAS_REQUIRE,
	)
