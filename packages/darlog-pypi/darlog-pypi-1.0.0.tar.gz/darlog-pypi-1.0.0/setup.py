#!/usr/bin/env python
# encoding: utf-8

"""
https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#setup-args
"""

from os import path
import sys

from setuptools import find_packages, setup

HERE = path.abspath(path.dirname(__file__))
SRC_DIR = "src"

sys.path.append(path.join(HERE, SRC_DIR))
import darlog_pypi
the_module = darlog_pypi


PACKAGES = find_packages(where=SRC_DIR)
NAME = darlog_pypi.module_name_to_project(PACKAGES[0])
KEYWORDS = ["utility", "pypi", "publishing", "setuptools", "pip"]
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
	"Topic :: Software Development :: Libraries :: Python Modules",
	"Typing :: Typed",
]
PYTHON_REQUIRES = ">=2.7"
INSTALL_REQUIRES = []
EXTRAS_REQUIRE = {
	"dev": [],
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
