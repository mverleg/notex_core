
"""
	Parse packages and versions, which follow pip format.
"""

from argparse import ArgumentTypeError
from logging import warning
from re import fullmatch, findall, match  #todo: not in python 2.7


class VersionRangeMismatch(Exception):
	""" Tried to add range selections that don't overlap """


class VersionFormatError(Exception):
	""" Could not correctly interpret the package and/or version descrition string """


def intify(itrbl):
	return [int(val) if val else None for val in itrbl]


class VersionRange():
	"""
	Represent a range of versions. Versions have the format 'int.int' in this class.

	More deeply nested versions are explicitly assumed to be bugfixes that are otherwise
	compatible. Selection on those should therefore never be needed.

	Relies on Python tuple ordering: (1, 2) < (2, 1) and (1, 2) < (1, 3)
	"""
	def __init__(self, selections = '==*'):
		"""
		:param selections: A selection string, like '>=1.3,<2.0'.
		"""
		self.min = None
		self.min_inclusive = True
		self.max = None
		self.max_inclusive = True
		for version in selections.split(','):
			try:
				self.add_selection(version, conflict = 'error')
			except VersionRangeMismatch:
				raise VersionRangeMismatch('"{0:s}" contains conflicting directives'.format(selections))

	@classmethod
	def raw(cls, min = None, max = None, min_inclusive = True, max_inclusive = True, conflict = 'warning'):
		inst = cls('')
		assert type(min_inclusive) is bool and type(max_inclusive) is bool
		assert (min is None or type(min) is tuple) and (max is None or type(max) is tuple)
		assert (min is None or len(min) == 2) and (max is None or len(max) == 2)
		inst.update_values(min = min, max = max, min_inclusive = min_inclusive, max_inclusive = max_inclusive)
		return inst

	def update_values(self, min = None, max = None, min_inclusive = None, max_inclusive = None, conflict = 'warning'):
		"""
		Update the boundaries, handling possible conflicts.

		:param conflict: What to do in case of failure: 'silent', 'warning' or 'error'.
		"""
		def handle_conflict(msg):
			if conflict == 'ignore':
				return
			elif conflict == 'warning':
				warning(msg)
			elif conflict == 'error':
				raise VersionRangeMismatch(msg)
			else:
				raise NotImplementedError('Unknown conflict mode "{0:s}"'.format(conflict))
		if max is not None or max_inclusive is not None:
			""" New values have been provided. """
			if self.max is None:
				""" There is no old value, so simply update (inclusive doesn't matter in this case). """
				self.max = max
				self.max_inclusive = max_inclusive
			elif max < self.max or (max == self.max and max_inclusive and not self.max_inclusive):
				""" There is an old value, but ours is narrower, so we should update. """
				conflict = False
				if self.min is not None:
					if max < self.min:
						conflict = True
					elif max == self.min:
						if max_inclusive or self.min_inclusive:
							conflict = True
				if conflict:
					""" The values of max and min create an empty range; update the lower one (which is the minimum). """
					print('max updated from', self.max, self.max_inclusive, 'to', max, max_inclusive, '(conflict mode)')  #todo
					handle_conflict('Maximum {0:d} conflicts with minimum {1:d}; maximum (highest value) takes precedence.'.format(max, self.min))
					self.min = max
					self.min_inclusive = True
				else:
					""" The value of max and min are not in conflict; simply update. """
					print('max updated from', self.max, self.max_inclusive, 'to', max, max_inclusive)  #todo
				self.max = max
				self.max_inclusive = max_inclusive
			else:
				""" The old value was narrower, so we ignore this new value. (This is no cause for a warning). """
				print('max NOT updated from', self.max, self.max_inclusive, 'to', max, max_inclusive)  #todo
		if min is not None or min_inclusive is not None:
			""" New values have been provided. """
			if self.min is None:
				""" There is no old value, so simply update (inclusive doesn't matter in this case). """
				self.min = min
				self.min_inclusive = min_inclusive
			elif min > self.min or (min == self.min and min_inclusive and not self.min_inclusive):
				""" There is an old value, but ours is narrower, so we should update. """
				conflict = False
				if self.max is not None:
					if min > self.max:
						conflict = True
					elif min == self.max:
						if min_inclusive or self.max_inclusive:
							conflict = True
				if conflict:
					""" The values of max and min create an empty range; update the lower one (which is the minimum). """
					handle_conflict('Minimum {0:d} conflicts with maximum {1:d}; minimum (highest value) takes precedence.'.format(min, self.max))
					self.max = min
					self.max_inclusive = True
				""" Update to the target values independent of conflict """
				self.max = max
				self.max_inclusive = max_inclusive


	def add_selection(self, selection, conflict = 'warning'):
		"""
		Restrict the range given a selection string

		:param selection: A single selection (without comma), like '>=1.3'.
		:param conflict: What to do in case of failure: 'silent', 'warning' or 'error'.
		"""
		# def handle_single_digit(digit, lower_open = False, upper_open = False):
		# 	if not lower_open:
		# 		self.min = (digit, 0)
		# 		self.min_inclusive = True
		# 	if not upper_open:
		# 		self.max = (digit + 1, 0)
		# 		self.max_inclusive = False
		selection = selection.replace(' ', '')
		if not selection:
			return
		if selection.count('.') > 1:
			raise VersionFormatError('Version string "{0:s}" is incorrect. Perhaps it contains a version longer than 2 numbers' +
				'(e.g. "3.14)" which is intentionally not supported. Version numbers beyond the second are for bugfixes only.'.format(selection))
		regex = r'^[><=]=?\d+(?:\.\d*)?$'
		if not match(regex, selection):
			raise VersionFormatError('Version string "{0:s}" not properly formatted according to "{1:s}".'.format(selection, regex))
		if selection.startswith('='):
			if '*' in selection:
				if match('^==?\*$', selection):
					return
				found = findall(r'^==?(\d+)\.\*$', selection)
				if not found:
					raise VersionFormatError('Version "{0:s}" not understood; * can appear as "==*" or "==nr.*" only.'.format(selection))
				major = int(found[0])
				self.update_values(min = (major, 0), max = (major + 1, 0), min_inclusive = True, max_inclusive = False, conflict = conflict)
			else:
				found = findall(r'^==?(\d+)(?:\.(\d*))?$', selection)
				if not found:
					raise VersionFormatError('Version "{0:s}" not understood; expecting "==nr" or "==nr.nr".'.format(selection))
				major, minor = intify(found[0])
				if minor is None:
					self.update_values(min = (major, 0), max = (major + 1, 0), min_inclusive = True, max_inclusive = False, conflict = conflict)
				else:
					self.update_values(min = (major, minor), max = (major, minor), min_inclusive = True, max_inclusive = True, conflict = conflict)
		if selection.startswith('>'):
			incl = selection.startswith('>=')
			found = findall(r'^>=?(\d+)(?:\.(\d*))?$', selection)
			if not found:
				raise VersionFormatError('Version "{0:s}" not understood; expecting "nr" or "nr.nr" after the > or >=.'.format(selection))
			major, minor = intify(found[0])
			if minor:
				self.update_values(min = (major, minor), min_inclusive = incl, conflict = conflict)
			else:
				if incl:
					self.update_values(min = (major, 0), min_inclusive = True, conflict = conflict)
				else:
					self.update_values(min = (major + 1), min_inclusive = False, conflict = conflict)
		if selection.startswith('<'):
			incl = selection.startswith('<=')
			found = findall(r'^<=?(\d+)(?:\.(\d*))?$', selection)
			if not found:
				raise VersionFormatError('Version "{0:s}" not understood; expecting "nr" or "nr.nr" after the < or <=.'.format(selection))
			major, minor = intify(found[0])
			""" Note that this is easier than for > because <7 is <7.0 whereas >7 is >=8.0"""
			self.update_values(max = (major, minor or 0), max_inclusive = incl, conflict = conflict)
		#todo: version numbers longer than 2

	def choose(self, versions):
		"""
		Choose the highest version in the range.

		:param versions: Iterable of available versions.
		"""
		raise NotImplementedError('')
		#todo: try the first higher version
		#todo: if no higher versions, try the first lower one

	def __eq__(self, other):
		if not type(self) is type(other):
			return False
		properties = ['min', 'max']
		if self.min is not None:
			properties.append('min_inclusive')
		if self.max is not None:
			properties.append('max_inclusive')
		for property in properties:
			if not getattr(self, property) == getattr(other, property):
				return False
		return True

	def tuple_to_str(self, tup):
		if tup[1] is None:
			return '{0:d}.*'.format(*tup)
		return '{0:d}.{1:d}'.format(*tup)

	def __str__(self):
		if self.min == self.max:
			if self.max is None:
				return '==*'
			return '=={0:s}'.format(self.tuple_to_str(self.max))
		if self.min is not None:
			repr = ['>']
			if self.min_inclusive:
				repr.append('=')
			repr.append(self.tuple_to_str(self.min))
			if self.max is not None:
				repr.append(',')
		if self.max is not None:
			repr = ['<']
			if self.max_inclusive:
				repr.append('=')
			repr.append(self.tuple_to_str(self.max))
		return ''.join(repr)


def parse_dependency(txt):
	txt = txt.split('#')[0]
	try:
		package = findall(r'^([a-zA-Z0-9_\-]*)[><=*\\z]', txt)[0]
		versions = findall(r'^[a-zA-Z0-9_\-]*([><=*][><=*0-9. ]*)$', txt)[0]
	except IndexError:
		raise VersionFormatError('Given text "{0:s}" does not seem to be formatted correctly'.format(txt))
	vrange = VersionRange(versions)
	return package, vrange


def regex_str(pattern): #todo: tmp
	def match_str(value):
		if fullmatch(pattern, value):
			return value
		raise ArgumentTypeError('Input "{0:s}" does not match the required format "{1:s}".'.format(value, pattern))
	return match_str


