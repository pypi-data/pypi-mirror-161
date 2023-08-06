#!/usr/bin/env python
# encoding: utf-8

"""
https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#setup-args
"""

from os import path
import sys

from setuptools import find_packages, setup

import darlog_pypi

HERE = path.abspath(path.dirname(__file__))
SRC_DIR = "src"

sys.path.append(path.join(HERE, SRC_DIR))
import darlog_py23 as the_module


PACKAGES = find_packages(where=SRC_DIR)
NAME = darlog_pypi.module_name_to_project(PACKAGES[0])
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
PYTHON_REQUIRES = ">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*, <4"
INSTALL_REQUIRES = [
	# "six",
]
EXTRAS_REQUIRE = {
	"dev": [
		"attrs",

		"darlog-pypi",
	],
}


LONG_DESC = darlog_pypi.ReadmeUpdater.from_rel_path(HERE, "README.md", NAME).update_for_github().text_for_pypi()
SHORT_DESC = the_module.__doc__.strip()


if __name__ == '__main__':
	setup(
		name=NAME,
		version=the_module.__version__,
		description=SHORT_DESC,
		long_description=LONG_DESC,
		long_description_content_type="text/markdown",
			# https://packaging.python.org/en/latest/specifications/core-metadata/#description-content-type-optional

		url=the_module.__url__,
		author=the_module.__author__,
		maintainer=the_module.__author__,
		license=the_module.__license__,

		classifiers=CLASSIFIERS,
		keywords=KEYWORDS,

		package_dir={"": SRC_DIR},
		packages=PACKAGES,
		python_requires=PYTHON_REQUIRES,
		install_requires=INSTALL_REQUIRES,
		extras_require=EXTRAS_REQUIRE,
	)
