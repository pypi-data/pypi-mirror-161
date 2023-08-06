# encoding: utf-8
# SPDX-License-Identifier: LGPL-3.0-or-later

"""
Lex Darlog's tools library automating packages publication to pypi.org
"""

__version_info__ = (1, 0, 0)
__version__ = ".".join(str(x) for x in __version_info__)

__url__ = "https://github.com/Lex-DRL/darlog-pypi"
__uri__ = __url__

__author__ = 'Lex Darlog (Lex-DRL)'

__license__ = "LGPL-3.0-or-later"
__copyright__ = "Copyright (c) 2022 Lex Darlog"


from codecs import open as _open
from itertools import chain as _chain
from os import path as _path
import re as _re

try:
	import typing as _t
except ImportError:
	pass

# noinspection PyBroadException
try:
	_unicode = unicode
except Exception:
	_unicode = str


def format_str_or_unicode(format_pattern, *args, **kwargs):
	# type: (_t.AnyStr, _t.Any, _t.Any) -> _t.AnyStr
	# noinspection PyBroadException
	try:
		return format_pattern.format(*args, **kwargs)
	except Exception:
		return _unicode(format_pattern).format(*args, **kwargs)


class ReadmeUpdater(object):
	"""
	Allows easily read `README` inside `setup.py`, updating the file itself (it's title) in the process.

	As a result, you have github and pypi descriptions back-linking to each other.
	"""

	title_re = _re.compile('^(?P<indent>\\s*)\\#[^\\#]')  # '{indent}#...', single '#'
	# ReadmeUpdater.title_re = title_re

	url_github = 'https://github.com/{github_user}/{package}'
	url_pypi = 'https://pypi.org/project/{package}/'

	# We can't use dataclasses due to python2 compatibility (and we don't want to add unnecessary dependencies), so...
	def __init__(
		self,
		file_path,  # type: str
		package,  # type: str
		encoding="utf-8", github_user='Lex-DRL', title_format='{indent}# [{package}]({url})',
	):
		# self = ReadmeUpdater
		# package = 'darlog'
		# file_path = path.join(HERE, "README.md")

		self.__file_lines = None
		self.file_path = file_path.replace('\\', '/').rstrip('/')
		self.encoding = encoding

		self.package = package
		self.github_user = github_user
		self.title_format = title_format

	@classmethod
	def from_rel_path(
		cls,
		repo_root,  # type: str
		rel_file_path,  # type: str
		package,  # type: str
		**kwargs
	):
		return cls(_path.join(repo_root, rel_file_path), package, **kwargs)

	@property
	def lines_from_file(self):
		# type: () -> _t.List[_t.AnyStr]
		"""Cached file lines."""
		if self.__file_lines is None:
			with _open(self.file_path, "rb", encoding=self.encoding) as f:
				self.__file_lines = [x.rstrip() for x in f.readlines()]
		return self.__file_lines

	def __replaced_title(self, url_format=url_github):
		# type: (str) -> _t.List[_t.AnyStr]
		"""Reformat the line containing title."""
		# self.lines_from_file = self.__file_lines
		# url_format = self.url_github

		title_re = self.title_re
		lines_iter = iter(self.lines_from_file)

		def gen_till_replaced():
			for line in lines_iter:
				match = title_re.match(line)
				if match:
					url = format_str_or_unicode(url_format, github_user=self.github_user, package=self.package)
					yield format_str_or_unicode(
						self.title_format, package=self.package, url=url, **match.groupdict()  # defines `indent` kwarg
					)
					return
				yield line

		return list(
			_chain(gen_till_replaced(), lines_iter)
		)

	@property
	def lines_for_github(self):
		# type: () -> _t.List[_t.AnyStr]
		return self.__replaced_title(url_format=self.url_pypi)

	@property
	def lines_for_pypi(self):
		# type: () -> _t.List[_t.AnyStr]
		return self.__replaced_title(url_format=self.url_github)

	@staticmethod
	def __out_lines(lines):
		# type: (_t.List[_t.AnyStr]) -> _t.Generator[_unicode]
		out_format = _unicode('{}\n')
		return (out_format.format(x) for x in lines)

	def update_for_github(self):
		new_lines = self.lines_for_github
		# new_lines = __replaced_title(self, url_format=self.url_pypi)
		with _open(self.file_path, "wb", encoding=self.encoding) as f:
			f.writelines(self.__out_lines(new_lines))
		return self

	def text_for_pypi(self):
		# type: () -> _unicode
		new_lines = self.lines_for_pypi
		return _unicode('').join(self.__out_lines(new_lines))


def module_name_to_project(name):
	# type: (str) -> str
	return name.replace('_', '-')
